"""Scoring service for calculating relevance scores."""
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import get_settings
from app.models.research_item import ResearchItem, SourceType

settings = get_settings()


class ScoringService:
    """Service for calculating relevance scores."""
    
    def __init__(self):
        self.weights = {
            "recency": settings.SCORE_RECENCY_WEIGHT,
            "code": settings.SCORE_CODE_WEIGHT,
            "source": settings.SCORE_SOURCE_WEIGHT,
            "impact": settings.SCORE_IMPACT_WEIGHT,
            "clarity": settings.SCORE_CLARITY_WEIGHT,
        }
    
    async def calculate_score(self, item: ResearchItem) -> float:
        """Calculate overall relevance score for an item."""
        # Calculate individual components
        recency_score = self._calculate_recency_score(item.published_date)
        code_score = self._calculate_code_score(item)
        source_score = self._calculate_source_score(item.source)
        impact_score = self._calculate_impact_score(item)
        clarity_score = self._calculate_clarity_score(item)
        
        # Store individual scores
        item.recency_score = recency_score
        item.code_availability_score = code_score
        item.source_quality_score = source_score
        item.impact_score = impact_score
        item.clarity_score = clarity_score
        
        # Calculate weighted overall score
        overall_score = (
            recency_score * self.weights["recency"] +
            code_score * self.weights["code"] +
            source_score * self.weights["source"] +
            impact_score * self.weights["impact"] +
            clarity_score * self.weights["clarity"]
        )
        
        # Normalize to 0-100
        item.relevance_score = min(100.0, max(0.0, overall_score * 100))
        
        return item.relevance_score
    
    def _calculate_recency_score(self, published_date: datetime) -> float:
        """Calculate recency score (0-1)."""
        now = datetime.utcnow()
        age_days = (now - published_date.replace(tzinfo=None)).days
        
        # Exponential decay
        if age_days <= 0:
            return 1.0
        elif age_days <= 7:
            return 0.9
        elif age_days <= 30:
            return 0.7
        elif age_days <= 90:
            return 0.5
        elif age_days <= 180:
            return 0.3
        else:
            return 0.1
    
    def _calculate_code_score(self, item: ResearchItem) -> float:
        """Calculate code availability score (0-1)."""
        score = 0.0
        
        # Base score for having code
        if item.code_url:
            score += 0.3
        
        # Higher score for GitHub
        if item.github_url:
            score += 0.3
            
            # Bonus for official code
            if item.is_official_code:
                score += 0.2
            
            # Bonus for GitHub stars
            if item.github_stars:
                if item.github_stars >= 1000:
                    score += 0.2
                elif item.github_stars >= 100:
                    score += 0.1
                elif item.github_stars >= 10:
                    score += 0.05
        
        return min(1.0, score)
    
    def _calculate_source_score(self, source: SourceType) -> float:
        """Calculate source quality score (0-1)."""
        source_scores = {
            SourceType.CONFERENCE: 1.0,
            SourceType.JOURNAL: 1.0,
            SourceType.ARXIV: 0.8,
            SourceType.PAPERS_WITH_CODE: 0.85,
            SourceType.OPENREVIEW: 0.85,
            SourceType.HUGGINGFACE: 0.75,
            SourceType.GITHUB: 0.7,
            SourceType.OTHER: 0.5,
        }
        
        return source_scores.get(source, 0.5)
    
    def _calculate_impact_score(self, item: ResearchItem) -> float:
        """Calculate likely impact score (0-1)."""
        score = 0.5  # Base score
        
        # Boost for having a model name (likely a new architecture)
        if item.model_name:
            score += 0.1
        
        # Boost for venue (if available)
        if item.venue:
            top_venues = [
                "cvpr", "iccv", "eccv", "neurips", "icml", "iclr",
                "tpami", "ijcv", "tip",
            ]
            if any(v in item.venue.lower() for v in top_venues):
                score += 0.2
        
        # Boost for GitHub popularity
        if item.github_stars:
            if item.github_stars >= 5000:
                score += 0.2
            elif item.github_stars >= 1000:
                score += 0.1
        
        # Boost for comprehensive links
        link_count = sum([
            bool(item.paper_url),
            bool(item.code_url),
            bool(item.project_page_url),
            bool(item.demo_url),
        ])
        score += link_count * 0.025
        
        return min(1.0, score)
    
    def _calculate_clarity_score(self, item: ResearchItem) -> float:
        """Calculate clarity of contribution score (0-1)."""
        score = 0.5  # Base score
        
        # Boost for having summaries
        if item.short_summary:
            score += 0.15
        if item.full_summary:
            score += 0.1
        if item.why_it_matters:
            score += 0.1
        if item.problem_solved:
            score += 0.1
        
        # Boost for having abstract
        if item.abstract and len(item.abstract) > 100:
            score += 0.05
        
        return min(1.0, score)
    
    def adjust_score_for_trending(self, item: ResearchItem, trending_factor: float) -> None:
        """Adjust score based on trending status."""
        # Boost score for trending items
        boost = trending_factor * 10  # Up to 10 point boost
        item.relevance_score = min(100.0, item.relevance_score + boost)
