"""Comparison model for approach comparisons."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import DateTime, Float, Integer, String, Text, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MaturityLevel(str, PyEnum):
    """Maturity levels for approaches."""
    EXPERIMENTAL = "experimental"
    RESEARCH = "research"
    BETA = "beta"
    PRODUCTION = "production"
    MATURE = "mature"


class ComputationalCost(str, PyEnum):
    """Computational cost levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Comparison(Base):
    """Comparison model for storing approach comparisons."""
    
    __tablename__ = "comparisons"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Basic info
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    task: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(Text)
    strengths: Mapped[Optional[List[str]]] = mapped_column(JSON)
    limitations: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Technical details
    architecture_family: Mapped[Optional[str]] = mapped_column(String(100))
    computational_cost: Mapped[Optional[ComputationalCost]] = mapped_column(SQLEnum(ComputationalCost))
    maturity_level: Mapped[Optional[MaturityLevel]] = mapped_column(SQLEnum(MaturityLevel))
    
    # Performance metrics (stored as JSON for flexibility)
    performance_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Use cases
    best_use_cases: Mapped[Optional[List[str]]] = mapped_column(JSON)
    not_recommended_for: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Requirements
    dataset_size_requirements: Mapped[Optional[str]] = mapped_column(String(255))
    annotation_requirements: Mapped[Optional[str]] = mapped_column(String(255))
    hardware_requirements: Mapped[Optional[str]] = mapped_column(Text)
    
    # Links
    paper_url: Mapped[Optional[str]] = mapped_column(String(1000))
    code_url: Mapped[Optional[str]] = mapped_column(String(1000))
    documentation_url: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Related items
    related_research_item_ids: Mapped[Optional[List[int]]] = mapped_column(JSON)
    
    # Metadata
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<Comparison(id={self.id}, model='{self.model_name}', task='{self.task}')>"
