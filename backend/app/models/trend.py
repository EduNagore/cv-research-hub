"""Trend model for tracking research trends."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrendType(str, PyEnum):
    """Types of trends."""
    ARCHITECTURE = "architecture"
    TOPIC = "topic"
    METHOD = "method"
    DATASET = "dataset"
    BENCHMARK = "benchmark"
    KEYWORD = "keyword"
    AUTHOR = "author"
    LAB = "lab"


class TrendPeriod(str, PyEnum):
    """Trend periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class Trend(Base):
    """Trend model for tracking research trends over time."""
    
    __tablename__ = "trends"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Trend identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trend_type: Mapped[TrendType] = mapped_column(SQLEnum(TrendType), nullable=False, index=True)
    period: Mapped[TrendPeriod] = mapped_column(SQLEnum(TrendPeriod), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Metrics
    frequency: Mapped[int] = mapped_column(Integer, default=0)  # How many times it appeared
    growth_rate: Mapped[Optional[float]] = mapped_column(Float)  # Growth from previous period
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Related items
    related_item_ids: Mapped[Optional[list]] = mapped_column(JSON)
    related_papers_count: Mapped[int] = mapped_column(Integer, default=0)
    related_models_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Additional data
    description: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    
    def __repr__(self) -> str:
        return f"<Trend(id={self.id}, name='{self.name}', type='{self.trend_type.value}')>"
