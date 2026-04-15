"""Research item schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
    SourceType,
    StatusLabel,
)


class ResearchItemBase(BaseModel):
    """Base research item schema."""
    title: str = Field(..., min_length=1, max_length=500)
    source: SourceType
    published_date: datetime
    contribution_type: ContributionType


class ResearchItemCreate(ResearchItemBase):
    """Schema for creating research items."""
    # Core identification
    slug: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    
    # Publication info
    authors: Optional[List[str]] = None
    author_affiliations: Optional[List[str]] = None
    
    # Content
    abstract: Optional[str] = None
    short_summary: Optional[str] = None
    full_summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    problem_solved: Optional[str] = None
    contribution_description: Optional[str] = None
    use_cases: Optional[List[str]] = None
    
    # Links
    paper_url: Optional[str] = None
    abstract_url: Optional[str] = None
    code_url: Optional[str] = None
    github_url: Optional[str] = None
    project_page_url: Optional[str] = None
    demo_url: Optional[str] = None
    
    # Classification
    modality: Optional[ModalityType] = None
    architecture_family: Optional[ArchitectureFamily] = None
    model_name: Optional[str] = None
    
    # Status
    status_label: StatusLabel = StatusLabel.NEW
    is_official_code: bool = False
    is_unofficial_reimplementation: bool = False
    
    # GitHub metadata
    github_stars: Optional[int] = None
    github_forks: Optional[int] = None
    github_language: Optional[str] = None
    
    # Scoring
    relevance_score: float = 0.0
    
    # Venue info
    venue: Optional[str] = None
    venue_type: Optional[str] = None
    
    # Categories and tags
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class ResearchItemUpdate(BaseModel):
    """Schema for updating research items."""
    title: Optional[str] = None
    short_summary: Optional[str] = None
    full_summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    problem_solved: Optional[str] = None
    contribution_description: Optional[str] = None
    status_label: Optional[StatusLabel] = None
    relevance_score: Optional[float] = None
    github_stars: Optional[int] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class CategoryBrief(BaseModel):
    """Brief category info."""
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class TagBrief(BaseModel):
    """Brief tag info."""
    id: int
    name: str
    slug: str
    color: Optional[str] = None
    
    class Config:
        from_attributes = True


class ResearchItemInDB(ResearchItemBase):
    """Schema for research items from database."""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResearchItemResponse(ResearchItemInDB):
    """Full research item response schema."""
    # Source info
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    
    # Publication info
    authors: Optional[List[str]] = None
    author_affiliations: Optional[List[str]] = None
    
    # Content
    abstract: Optional[str] = None
    short_summary: Optional[str] = None
    full_summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    problem_solved: Optional[str] = None
    contribution_description: Optional[str] = None
    use_cases: Optional[List[str]] = None
    
    # Links
    paper_url: Optional[str] = None
    abstract_url: Optional[str] = None
    code_url: Optional[str] = None
    github_url: Optional[str] = None
    project_page_url: Optional[str] = None
    demo_url: Optional[str] = None
    
    # Classification
    modality: Optional[ModalityType] = None
    architecture_family: Optional[ArchitectureFamily] = None
    model_name: Optional[str] = None
    
    # Status
    status_label: StatusLabel
    is_official_code: bool
    is_unofficial_reimplementation: bool
    
    # GitHub metadata
    github_stars: Optional[int] = None
    github_forks: Optional[int] = None
    github_last_updated: Optional[datetime] = None
    github_language: Optional[str] = None
    
    # Scoring
    relevance_score: float
    recency_score: float
    code_availability_score: float
    source_quality_score: float
    impact_score: float
    clarity_score: float
    
    # Venue info
    venue: Optional[str] = None
    venue_type: Optional[str] = None
    
    # Categories and tags
    categories: List[CategoryBrief] = []
    tags: List[TagBrief] = []
    
    # User interaction (if available)
    is_favorite: Optional[bool] = None
    is_bookmarked: Optional[bool] = None
    user_status: Optional[str] = None


class ResearchItemListResponse(BaseModel):
    """Response for list of research items."""
    items: List[ResearchItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ResearchItemFilter(BaseModel):
    """Filter parameters for research items."""
    search: Optional[str] = None
    category: Optional[str] = None
    source: Optional[SourceType] = None
    contribution_type: Optional[ContributionType] = None
    status_label: Optional[StatusLabel] = None
    modality: Optional[ModalityType] = None
    architecture_family: Optional[ArchitectureFamily] = None
    has_code: Optional[bool] = None
    has_github: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    sort_by: str = "published_date"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20
