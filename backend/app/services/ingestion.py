"""Ingestion service for collecting data from various sources."""
import asyncio
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.category import Category
from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
    ResearchItem,
    SourceType,
    StatusLabel,
)
from app.models.tag import Tag
from app.services.classification import ClassificationService
from app.services.gemini_discovery import GeminiDiscoveryService
from app.services.scoring import ScoringService

settings = get_settings()


class IngestionService:
    """Service for ingesting research items from various sources."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.classification_service = ClassificationService()
        self.scoring_service = ScoringService()
        self.batch_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    async def run_full_ingestion(self) -> Dict:
        """Run the Gemini-driven ingestion flow."""
        results = {
            "gemini_discovery": await self.ingest_gemini_discovery(),
        }
        
        # Post-processing
        await self.deduplicate_items()
        await self.recalculate_all_scores()
        
        return results

    async def ingest_gemini_discovery(self) -> Dict:
        """Discover recent items with Gemini and store them as research items."""
        service = GeminiDiscoveryService(self.db, batch_id=self.batch_id)
        result = await service.run_daily_discovery()
        await self.db.commit()
        return result

    async def ingest_gemini_category(self, category_slug: str) -> Dict:
        """Discover recent items with Gemini for a single category."""
        service = GeminiDiscoveryService(self.db, batch_id=self.batch_id)
        result = await service.run_category_discovery(category_slug)
        await self.db.commit()
        return result
    
    async def ingest_arxiv(self, days_back: int = 7) -> Dict:
        """Ingest papers from arXiv."""
        # arXiv categories for computer vision and related fields
        categories = [
            "cs.CV",  # Computer Vision
            "cs.LG",  # Machine Learning
            "cs.AI",  # Artificial Intelligence
            "eess.IV",  # Image and Video Processing
        ]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        total_ingested = 0
        total_skipped = 0
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for category in categories:
                try:
                    # Build arXiv API query
                    query = f"cat:{category} AND submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {end_date.strftime('%Y%m%d')}2359]"
                    
                    url = "http://export.arxiv.org/api/query"
                    params = {
                        "search_query": query,
                        "start": 0,
                        "max_results": settings.ARXIV_MAX_RESULTS_PER_QUERY,
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                    }
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    # Parse XML response
                    root = ET.fromstring(response.content)
                    
                    # Define namespace
                    ns = {
                        "atom": "http://www.w3.org/2005/Atom",
                        "arxiv": "http://arxiv.org/schemas/atom",
                    }
                    
                    entries = root.findall("atom:entry", ns)
                    
                    for entry in entries:
                        try:
                            # Extract data
                            title = entry.find("atom:title", ns)
                            title_text = title.text.strip() if title is not None else ""
                            
                            summary = entry.find("atom:summary", ns)
                            abstract = summary.text.strip() if summary is not None else ""
                            
                            published = entry.find("atom:published", ns)
                            published_date = datetime.fromisoformat(
                                published.text.replace("Z", "+00:00")
                            ) if published is not None else datetime.utcnow()
                            
                            # Get authors
                            authors = []
                            for author in entry.findall("atom:author", ns):
                                name = author.find("atom:name", ns)
                                if name is not None:
                                    authors.append(name.text)
                            
                            # Get arXiv ID
                            id_elem = entry.find("atom:id", ns)
                            arxiv_id = ""
                            if id_elem is not None:
                                arxiv_id = id_elem.text.split("/")[-1]
                            
                            # Get links
                            paper_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                            abstract_url = f"https://arxiv.org/abs/{arxiv_id}"
                            
                            # Check for duplicates
                            existing = await self.db.execute(
                                select(ResearchItem).where(
                                    ResearchItem.source_id == arxiv_id
                                )
                            )
                            if existing.scalar_one_or_none():
                                total_skipped += 1
                                continue
                            
                            # Generate slug
                            slug = self._generate_slug(title_text, arxiv_id)
                            
                            # Classify the paper
                            classification = await self.classification_service.classify(
                                title=title_text,
                                abstract=abstract,
                            )
                            
                            # Create research item
                            item = ResearchItem(
                                title=title_text,
                                slug=slug,
                                source=SourceType.ARXIV,
                                source_id=arxiv_id,
                                source_url=abstract_url,
                                published_date=published_date,
                                authors=authors,
                                abstract=abstract,
                                short_summary=classification.get("short_summary"),
                                full_summary=classification.get("full_summary"),
                                why_it_matters=classification.get("why_it_matters"),
                                paper_url=paper_url,
                                abstract_url=abstract_url,
                                contribution_type=classification.get(
                                    "contribution_type", ContributionType.PAPER
                                ),
                                modality=classification.get("modality"),
                                architecture_family=classification.get("architecture_family"),
                                model_name=classification.get("model_name"),
                                status_label=StatusLabel.NEW,
                                ingestion_batch_id=self.batch_id,
                                raw_metadata={
                                    "arxiv_id": arxiv_id,
                                    "category": category,
                                },
                            )
                            
                            self.db.add(item)
                            await self.db.flush()
                            
                            # Assign categories and tags
                            await self._assign_categories_and_tags(
                                item, classification.get("categories", []), classification.get("tags", [])
                            )
                            
                            # Calculate initial score
                            await self.scoring_service.calculate_score(item)
                            
                            total_ingested += 1
                            
                        except Exception as e:
                            print(f"Error processing arXiv entry: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Error ingesting from arXiv category {category}: {e}")
                    continue
        
        await self.db.commit()
        
        return {
            "source": "arxiv",
            "ingested": total_ingested,
            "skipped": total_skipped,
            "batch_id": self.batch_id,
        }
    
    async def ingest_papers_with_code(self, days_back: int = 7) -> Dict:
        """Ingest from Papers with Code API."""
        total_ingested = 0
        total_skipped = 0
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Get recent papers with code
                url = "https://paperswithcode.com/api/v1/papers/"
                params = {
                    "items_per_page": settings.PAPERS_WITH_CODE_MAX_RESULTS,
                    "page": 1,
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                papers = data.get("results", [])
                
                for paper in papers:
                    try:
                        paper_id = paper.get("id", "")
                        title = paper.get("title", "")
                        abstract = paper.get("abstract", "")
                        
                        # Check for duplicates
                        existing = await self.db.execute(
                            select(ResearchItem).where(
                                ResearchItem.source_id == f"pwc_{paper_id}"
                            )
                        )
                        if existing.scalar_one_or_none():
                            total_skipped += 1
                            continue
                        
                        # Get GitHub URL if available
                        github_url = paper.get("github_url", "")
                        
                        # Get published date
                        published_date = datetime.utcnow()
                        if paper.get("published"):
                            try:
                                published_date = datetime.fromisoformat(
                                    paper["published"].replace("Z", "+00:00")
                                )
                            except:
                                pass
                        
                        # Generate slug
                        slug = self._generate_slug(title, f"pwc_{paper_id}")
                        
                        # Classify
                        classification = await self.classification_service.classify(
                            title=title,
                            abstract=abstract,
                        )
                        
                        # Create item
                        item = ResearchItem(
                            title=title,
                            slug=slug,
                            source=SourceType.PAPERS_WITH_CODE,
                            source_id=f"pwc_{paper_id}",
                            source_url=f"https://paperswithcode.com/paper/{paper_id}",
                            published_date=published_date,
                            authors=paper.get("authors", []),
                            abstract=abstract,
                            short_summary=classification.get("short_summary"),
                            github_url=github_url,
                            is_official_code=bool(github_url),
                            contribution_type=classification.get(
                                "contribution_type", ContributionType.PAPER
                            ),
                            modality=classification.get("modality"),
                            architecture_family=classification.get("architecture_family"),
                            model_name=classification.get("model_name"),
                            status_label=StatusLabel.NEW,
                            ingestion_batch_id=self.batch_id,
                        )
                        
                        self.db.add(item)
                        await self.db.flush()
                        
                        # Assign categories and tags
                        await self._assign_categories_and_tags(
                            item, classification.get("categories", []), classification.get("tags", [])
                        )
                        
                        # Calculate score
                        await self.scoring_service.calculate_score(item)
                        
                        total_ingested += 1
                        
                    except Exception as e:
                        print(f"Error processing PwC paper: {e}")
                        continue
                
            except Exception as e:
                print(f"Error ingesting from Papers with Code: {e}")
        
        await self.db.commit()
        
        return {
            "source": "papers_with_code",
            "ingested": total_ingested,
            "skipped": total_skipped,
            "batch_id": self.batch_id,
        }
    
    async def ingest_github(self, days_back: int = 7) -> Dict:
        """Ingest trending repositories from GitHub."""
        if not settings.GITHUB_TOKEN:
            return {
                "source": "github",
                "ingested": 0,
                "skipped": 0,
                "error": "GitHub token not configured",
            }
        
        total_ingested = 0
        total_skipped = 0
        
        # Keywords for computer vision repositories
        queries = [
            "computer vision",
            "deep learning image",
            "pytorch vision",
            "tensorflow image",
            "object detection",
            "image segmentation",
            "diffusion model",
            "vision transformer",
        ]
        
        headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for query in queries:
                try:
                    url = "https://api.github.com/search/repositories"
                    params = {
                        "q": f"{query} created:>{(datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')}",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": settings.GITHUB_MAX_REPOS_PER_QUERY // len(queries),
                    }
                    
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    
                    data = response.json()
                    repos = data.get("items", [])
                    
                    for repo in repos:
                        try:
                            repo_id = str(repo.get("id", ""))
                            full_name = repo.get("full_name", "")
                            
                            # Check for duplicates
                            existing = await self.db.execute(
                                select(ResearchItem).where(
                                    ResearchItem.source_id == f"gh_{repo_id}"
                                )
                            )
                            if existing.scalar_one_or_none():
                                total_skipped += 1
                                continue
                            
                            title = repo.get("name", "")
                            description = repo.get("description", "") or ""
                            
                            # Generate slug
                            slug = self._generate_slug(title, f"gh_{repo_id}")
                            
                            # Classify
                            classification = await self.classification_service.classify(
                                title=title,
                                abstract=description,
                            )
                            
                            # Parse created date
                            created_at = datetime.utcnow()
                            if repo.get("created_at"):
                                try:
                                    created_at = datetime.fromisoformat(
                                        repo["created_at"].replace("Z", "+00:00")
                                    )
                                except:
                                    pass
                            
                            # Create item
                            item = ResearchItem(
                                title=title,
                                slug=slug,
                                source=SourceType.GITHUB,
                                source_id=f"gh_{repo_id}",
                                source_url=repo.get("html_url", ""),
                                published_date=created_at,
                                abstract=description,
                                short_summary=classification.get("short_summary"),
                                github_url=repo.get("html_url", ""),
                                github_stars=repo.get("stargazers_count", 0),
                                github_forks=repo.get("forks_count", 0),
                                github_language=repo.get("language", ""),
                                is_official_code=True,
                                contribution_type=classification.get(
                                    "contribution_type", ContributionType.REPOSITORY
                                ),
                                modality=classification.get("modality"),
                                architecture_family=classification.get("architecture_family"),
                                status_label=StatusLabel.NEW,
                                ingestion_batch_id=self.batch_id,
                            )
                            
                            self.db.add(item)
                            await self.db.flush()
                            
                            # Assign categories and tags
                            await self._assign_categories_and_tags(
                                item, classification.get("categories", []), classification.get("tags", [])
                            )
                            
                            # Calculate score
                            await self.scoring_service.calculate_score(item)
                            
                            total_ingested += 1
                            
                        except Exception as e:
                            print(f"Error processing GitHub repo: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Error ingesting from GitHub: {e}")
                    continue
        
        await self.db.commit()
        
        return {
            "source": "github",
            "ingested": total_ingested,
            "skipped": total_skipped,
            "batch_id": self.batch_id,
        }
    
    async def refresh_github_metadata(self) -> Dict:
        """Refresh GitHub metadata for all items with GitHub URLs."""
        if not settings.GITHUB_TOKEN:
            return {"refreshed": 0, "error": "GitHub token not configured"}
        
        result = await self.db.execute(
            select(ResearchItem).where(ResearchItem.github_url.isnot(None))
        )
        items = result.scalars().all()
        
        refreshed = 0
        headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for item in items:
                try:
                    # Extract owner/repo from GitHub URL
                    match = re.search(r"github\.com/([^/]+)/([^/]+)", item.github_url or "")
                    if not match:
                        continue
                    
                    owner, repo = match.groups()
                    repo = repo.replace(".git", "")
                    
                    url = f"https://api.github.com/repos/{owner}/{repo}"
                    
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        item.github_stars = data.get("stargazers_count", item.github_stars)
                        item.github_forks = data.get("forks_count", item.github_forks)
                        item.github_language = data.get("language", item.github_language)
                        
                        if data.get("pushed_at"):
                            try:
                                item.github_last_updated = datetime.fromisoformat(
                                    data["pushed_at"].replace("Z", "+00:00")
                                )
                            except:
                                pass
                        
                        refreshed += 1
                
                except Exception as e:
                    print(f"Error refreshing GitHub metadata for {item.github_url}: {e}")
                    continue
        
        await self.db.commit()
        
        return {"refreshed": refreshed}
    
    async def deduplicate_items(self) -> Dict:
        """Deduplicate research items."""
        # Find potential duplicates based on title similarity
        result = await self.db.execute(select(ResearchItem))
        items = result.scalars().all()
        
        duplicates_found = 0
        
        # Simple deduplication based on exact title match
        title_map = {}
        for item in items:
            normalized_title = self._normalize_title(item.title)
            if normalized_title in title_map:
                # Mark as duplicate
                original = title_map[normalized_title]
                item.canonical_id = original.id
                item.is_canonical = False
                duplicates_found += 1
            else:
                title_map[normalized_title] = item
        
        await self.db.commit()
        
        return {"duplicates_found": duplicates_found}
    
    async def recalculate_all_scores(self) -> Dict:
        """Recalculate relevance scores for all items."""
        result = await self.db.execute(select(ResearchItem))
        items = result.scalars().all()
        
        for item in items:
            await self.scoring_service.calculate_score(item)
        
        await self.db.commit()
        
        return {"recalculated": len(items)}
    
    def _generate_slug(self, title: str, unique_id: str) -> str:
        """Generate a URL-friendly slug."""
        # Normalize title
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug[:100]  # Limit length
        
        # Add hash for uniqueness
        hash_suffix = hashlib.md5(unique_id.encode()).hexdigest()[:8]
        return f"{slug}-{hash_suffix}"
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication."""
        # Remove common suffixes/prefixes and normalize
        normalized = title.lower()
        normalized = re.sub(r'[^\w]', '', normalized)
        return normalized
    
    async def _assign_categories_and_tags(
        self,
        item: ResearchItem,
        category_names: List[str],
        tag_names: List[str],
    ) -> None:
        """Assign categories and tags to an item."""
        # Assign categories
        for category_name in category_names:
            result = await self.db.execute(
                select(Category).where(
                    or_(
                        Category.name.ilike(category_name),
                        Category.slug.ilike(category_name),
                    )
                )
            )
            category = result.scalar_one_or_none()
            
            if category and category not in item.categories:
                item.categories.append(category)
                category.item_count += 1
        
        # Assign tags
        for tag_name in tag_names:
            result = await self.db.execute(
                select(Tag).where(Tag.name.ilike(tag_name))
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                # Create new tag
                tag = Tag(
                    name=tag_name,
                    slug=self._generate_slug(tag_name, tag_name),
                )
                self.db.add(tag)
                await self.db.flush()
            
            if tag not in item.tags:
                item.tags.append(tag)
                tag.item_count += 1
