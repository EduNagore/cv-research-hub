"""Gemini-powered discovery of fresh research items."""
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
from app.services.scoring import ScoringService

settings = get_settings()


class GeminiDiscoveryService:
    """Discover fresh research items by prompting Gemini per category."""

    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, db: AsyncSession, *, batch_id: Optional[str] = None):
        self.db = db
        self.batch_id = batch_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.classification_service = ClassificationService()
        self.scoring_service = ScoringService()

    async def run_daily_discovery(self) -> Dict[str, Any]:
        """Query Gemini once per active category and persist discovered items."""
        if not settings.GEMINI_API_KEY:
            return {
                "source": "gemini_discovery",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "error": "Gemini API key not configured",
            }

        result = await self.db.execute(
            select(Category).where(Category.is_active.is_(True)).order_by(Category.display_order, Category.id)
        )
        categories = result.scalars().all()
        return await self._run_for_categories(categories)

    async def run_category_discovery(self, category_slug: str) -> Dict[str, Any]:
        """Query Gemini for a single active category and persist discovered items."""
        if not settings.GEMINI_API_KEY:
            return {
                "source": "gemini_discovery",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "error": "Gemini API key not configured",
            }

        result = await self.db.execute(
            select(Category)
            .where(Category.is_active.is_(True), Category.slug == category_slug)
            .order_by(Category.display_order, Category.id)
        )
        categories = result.scalars().all()
        if not categories:
            raise ValueError(f"Unknown or inactive category: {category_slug}")

        return await self._run_for_categories(categories)

    async def _run_for_categories(self, categories: List[Category]) -> Dict[str, Any]:
        """Execute Gemini discovery for the provided categories."""

        ingested = 0
        updated = 0
        skipped = 0
        category_results: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=90.0) as client:
            for category in categories:
                try:
                    items = await self._discover_for_category(client, category)
                    cat_ingested = 0
                    cat_updated = 0
                    cat_skipped = 0

                    for payload in items:
                        outcome = await self._save_discovered_item(payload, category)
                        if outcome == "ingested":
                            ingested += 1
                            cat_ingested += 1
                        elif outcome == "updated":
                            updated += 1
                            cat_updated += 1
                        else:
                            skipped += 1
                            cat_skipped += 1

                    category_results.append(
                        {
                            "category": category.slug,
                            "received": len(items),
                            "ingested": cat_ingested,
                            "updated": cat_updated,
                            "skipped": cat_skipped,
                        }
                    )
                except Exception as exc:
                    category_results.append(
                        {
                            "category": category.slug,
                            "received": 0,
                            "ingested": 0,
                            "updated": 0,
                            "skipped": 0,
                            "error": str(exc),
                        }
                    )

        return {
            "source": "gemini_discovery",
            "ingested": ingested,
            "updated": updated,
            "skipped": skipped,
            "batch_id": self.batch_id,
            "categories": category_results,
        }

    async def _discover_for_category(self, client: httpx.AsyncClient, category: Category) -> List[Dict[str, Any]]:
        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            "You are curating a computer vision research tracker. "
                            "Use Google Search grounding to find recent, real, verifiable items and return only JSON."
                        )
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": self._build_prompt(category)}],
                }
            ],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "items": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "title": {"type": "STRING"},
                                    "item_type": {"type": "STRING"},
                                    "primary_url": {"type": "STRING"},
                                    "paper_url": {"type": "STRING"},
                                    "code_url": {"type": "STRING"},
                                    "project_page_url": {"type": "STRING"},
                                    "authors": {"type": "ARRAY", "items": {"type": "STRING"}},
                                    "published_at": {"type": "STRING"},
                                    "summary": {"type": "STRING"},
                                    "why_it_matters": {"type": "STRING"},
                                    "problem_solved": {"type": "STRING"},
                                    "contribution_description": {"type": "STRING"},
                                    "use_cases": {"type": "ARRAY", "items": {"type": "STRING"}},
                                    "category_slugs": {"type": "ARRAY", "items": {"type": "STRING"}},
                                    "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
                                    "contribution_type": {"type": "STRING"},
                                    "modality": {"type": "STRING"},
                                    "architecture_family": {"type": "STRING"},
                                    "model_name": {"type": "STRING"},
                                    "source_name": {"type": "STRING"},
                                },
                                "required": ["title", "primary_url", "summary"],
                            },
                        }
                    },
                    "required": ["items"],
                },
            },
        }

        response = await client.post(
            self.API_URL_TEMPLATE.format(model=settings.GEMINI_MODEL),
            headers={"x-goog-api-key": settings.GEMINI_API_KEY},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        text = self._extract_text_response(data)
        parsed = json.loads(text)
        items = parsed.get("items", [])

        if not isinstance(items, list):
            return []

        normalized_items = []
        for item in items[: settings.GEMINI_RESULTS_PER_CATEGORY]:
            if isinstance(item, dict) and item.get("title") and item.get("primary_url") and item.get("summary"):
                normalized_items.append(item)

        return normalized_items

    def _build_prompt(self, category: Category) -> str:
        return (
            f"Find up to {settings.GEMINI_RESULTS_PER_CATEGORY} genuinely recent items from the last "
            f"{settings.GEMINI_LOOKBACK_DAYS} days for the computer vision category '{category.name}' "
            f"(slug: {category.slug}). Category description: {category.description or 'N/A'}. "
            "Search for a balanced mix of papers, technical articles, repositories, model releases, and architecture writeups "
            "that are relevant to researchers and builders. Exclude low-quality SEO pages, duplicates, and unverifiable claims. "
            "For each item, provide the main URL plus paper/code/project links when available, compact summaries, why it matters, "
            "use cases, classification hints, and tags. Return strict JSON only."
        )

    def _extract_text_response(self, response_data: Dict[str, Any]) -> str:
        candidates = response_data.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        text_chunks = [part.get("text", "") for part in parts if part.get("text")]
        if not text_chunks:
            raise ValueError("Gemini returned no text content")

        return "\n".join(text_chunks).strip()

    async def _save_discovered_item(self, payload: Dict[str, Any], category: Category) -> str:
        primary_url = payload.get("primary_url", "").strip()
        title = payload.get("title", "").strip()
        if not primary_url or not title:
            return "skipped"

        source_id = self._build_source_id(primary_url, title)
        existing = await self.db.execute(
            select(ResearchItem).where(
                or_(
                    ResearchItem.source_id == source_id,
                    ResearchItem.source_url == primary_url,
                )
            )
        )
        item = existing.scalar_one_or_none()

        combined_text = "\n\n".join(
            filter(
                None,
                [
                    payload.get("summary", ""),
                    payload.get("why_it_matters", ""),
                    payload.get("problem_solved", ""),
                    payload.get("contribution_description", ""),
                ],
            )
        )
        classification = await self.classification_service.classify(title=title, abstract=combined_text)

        category_slugs = payload.get("category_slugs") or []
        category_slugs = [slug for slug in category_slugs if isinstance(slug, str)]
        if category.slug not in category_slugs:
            category_slugs.append(category.slug)

        tag_names = payload.get("tags") or []
        tag_names = [tag for tag in tag_names if isinstance(tag, str)]

        published_date = self._parse_datetime(payload.get("published_at"))
        contribution_type = self._parse_enum(
            ContributionType,
            payload.get("contribution_type"),
            classification.get("contribution_type", ContributionType.PAPER),
        )
        modality = self._parse_enum(ModalityType, payload.get("modality"), classification.get("modality"))
        architecture = self._parse_enum(
            ArchitectureFamily,
            payload.get("architecture_family"),
            classification.get("architecture_family", ArchitectureFamily.OTHER),
        )

        data = {
            "title": title,
            "source": SourceType.OTHER,
            "source_id": source_id,
            "source_url": primary_url,
            "published_date": published_date,
            "authors": payload.get("authors") or None,
            "abstract": payload.get("summary"),
            "short_summary": self._truncate(payload.get("summary"), 320) or classification.get("short_summary"),
            "full_summary": payload.get("summary") or classification.get("full_summary"),
            "why_it_matters": payload.get("why_it_matters") or classification.get("why_it_matters"),
            "problem_solved": payload.get("problem_solved"),
            "contribution_description": payload.get("contribution_description"),
            "use_cases": payload.get("use_cases") or None,
            "paper_url": payload.get("paper_url"),
            "code_url": payload.get("code_url"),
            "github_url": payload.get("code_url") if "github.com" in (payload.get("code_url") or "") else None,
            "project_page_url": payload.get("project_page_url"),
            "contribution_type": contribution_type,
            "modality": modality,
            "architecture_family": architecture,
            "model_name": payload.get("model_name") or classification.get("model_name"),
            "status_label": StatusLabel.NEW,
            "is_official_code": bool(payload.get("code_url")),
            "ingestion_batch_id": self.batch_id,
            "last_ingested_at": datetime.utcnow(),
            "raw_metadata": {
                "discovered_via": "gemini",
                "item_type": payload.get("item_type"),
                "category_slug": category.slug,
                "source_name": payload.get("source_name"),
                "primary_url": primary_url,
            },
        }

        if item is None:
            item = ResearchItem(
                slug=self._generate_slug(title, source_id),
                **data,
            )
            self.db.add(item)
            await self.db.flush()
            await self._assign_categories_and_tags(item, category_slugs, tag_names + classification.get("tags", []))
            await self.scoring_service.calculate_score(item)
            return "ingested"

        for field, value in data.items():
            setattr(item, field, value)

        await self._assign_categories_and_tags(item, category_slugs, tag_names + classification.get("tags", []))
        await self.scoring_service.calculate_score(item)
        return "updated"

    def _build_source_id(self, primary_url: str, title: str) -> str:
        base = primary_url or title
        digest = hashlib.md5(base.encode("utf-8")).hexdigest()[:12]
        return f"gemini_{digest}"

    def _generate_slug(self, title: str, unique_id: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        slug = slug[:100]
        hash_suffix = hashlib.md5(unique_id.encode("utf-8")).hexdigest()[:8]
        return f"{slug}-{hash_suffix}"

    def _truncate(self, value: Optional[str], max_length: int) -> Optional[str]:
        if not value:
            return value
        return value if len(value) <= max_length else value[: max_length - 3].rstrip() + "..."

    def _parse_datetime(self, value: Optional[str]) -> datetime:
        if not value:
            return datetime.utcnow()

        cleaned = value.strip()
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return parsed
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            return datetime.utcnow()

    def _parse_enum(self, enum_cls, value: Optional[str], fallback):
        if isinstance(value, str):
            normalized = value.strip().lower().replace(" ", "_")
            for member in enum_cls:
                if member.value == normalized:
                    return member
        return fallback

    async def _assign_categories_and_tags(
        self,
        item: ResearchItem,
        category_names: List[str],
        tag_names: List[str],
    ) -> None:
        for category_name in dict.fromkeys(category_names):
            result = await self.db.execute(
                select(Category).where(
                    or_(
                        Category.name.ilike(category_name),
                        Category.slug.ilike(category_name),
                    )
                )
            )
            matched_category = result.scalar_one_or_none()
            if matched_category and matched_category not in item.categories:
                item.categories.append(matched_category)
                matched_category.item_count += 1

        for tag_name in dict.fromkeys(tag_names):
            normalized = tag_name.strip()
            if not normalized:
                continue

            result = await self.db.execute(select(Tag).where(Tag.name.ilike(normalized)))
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(
                    name=normalized,
                    slug=self._generate_slug(normalized, normalized),
                )
                self.db.add(tag)
                await self.db.flush()

            if tag not in item.tags:
                item.tags.append(tag)
                tag.item_count += 1
