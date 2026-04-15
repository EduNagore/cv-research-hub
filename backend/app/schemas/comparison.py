"""Comparison schemas."""
from typing import List, Optional

from pydantic import BaseModel

from app.models.comparison import ComputationalCost, MaturityLevel


class ComparisonBase(BaseModel):
    """Base comparison schema."""
    model_name: str
    task: str
    description: Optional[str] = None


class ComparisonResponse(ComparisonBase):
    """Comparison response schema."""
    id: int
    slug: str
    strengths: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    architecture_family: Optional[str] = None
    computational_cost: Optional[ComputationalCost] = None
    maturity_level: Optional[MaturityLevel] = None
    performance_metrics: Optional[dict] = None
    best_use_cases: Optional[List[str]] = None
    not_recommended_for: Optional[List[str]] = None
    dataset_size_requirements: Optional[str] = None
    annotation_requirements: Optional[str] = None
    hardware_requirements: Optional[str] = None
    paper_url: Optional[str] = None
    code_url: Optional[str] = None
    documentation_url: Optional[str] = None
    view_count: int
    
    class Config:
        from_attributes = True


class ComparisonFilter(BaseModel):
    """Filter for comparisons."""
    task: Optional[str] = None
    architecture_family: Optional[str] = None
    maturity_level: Optional[MaturityLevel] = None
    computational_cost: Optional[ComputationalCost] = None
