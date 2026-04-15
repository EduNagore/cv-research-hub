"""Decision support schemas."""
from typing import List, Optional

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    """Request for decision support."""
    # Task specification
    task_type: str = Field(..., description="Type of task: classification, detection, segmentation, etc.")
    
    # Data characteristics
    dataset_size: str = Field(..., description="small, medium, large")
    annotation_amount: str = Field(..., description="none, limited, moderate, abundant")
    image_type: str = Field(..., description="natural, medical, histopathology, dermatology, satellite, etc.")
    dimensionality: str = Field(..., description="2d, 3d, video")
    
    # Requirements
    need_interpretability: bool = False
    real_time_required: bool = False
    accuracy_priority: str = Field(..., description="speed, balanced, accuracy")
    
    # Problem type
    problem_type: str = Field(..., description="discriminative, generative, both")
    
    # Constraints
    compute_budget: Optional[str] = Field(None, description="limited, moderate, abundant")
    memory_constraints: Optional[str] = Field(None, description="strict, moderate, relaxed")


class Recommendation(BaseModel):
    """Single recommendation."""
    approach_family: str
    description: str
    recommended_models: List[str]
    relevant_papers: List[dict]
    strengths: List[str]
    limitations: List[str]
    practical_notes: str
    suitability_score: float  # 0-1


class DecisionResponse(BaseModel):
    """Response for decision support."""
    # Input summary
    task_summary: str
    
    # Recommendations
    primary_recommendations: List[Recommendation]
    alternative_approaches: List[Recommendation]
    
    # Practical guidance
    data_preparation_tips: List[str]
    training_considerations: List[str]
    evaluation_metrics: List[str]
    
    # Related resources
    suggested_reading: List[dict]
    useful_repositories: List[dict]
    
    # Trade-offs summary
    trade_offs_summary: str
