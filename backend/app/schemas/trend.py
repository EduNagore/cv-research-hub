"""Trend schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.trend import TrendPeriod, TrendType


class TrendBase(BaseModel):
    """Base trend schema."""
    name: str
    trend_type: TrendType
    period: TrendPeriod
    period_start: datetime
    period_end: datetime


class TrendResponse(TrendBase):
    """Trend response schema."""
    id: int
    slug: str
    frequency: int
    growth_rate: Optional[float] = None
    popularity_score: float
    related_papers_count: int
    related_models_count: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class TrendStatistics(BaseModel):
    """Trend statistics."""
    top_architectures: List[TrendResponse]
    top_topics: List[TrendResponse]
    top_methods: List[TrendResponse]
    top_datasets: List[TrendResponse]
    emerging_keywords: List[TrendResponse]
    period: TrendPeriod
