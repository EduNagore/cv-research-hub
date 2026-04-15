"""Dashboard schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CategoryCount(BaseModel):
    """Category with item count."""
    name: str
    slug: str
    count: int
    icon: Optional[str] = None


class DailySummary(BaseModel):
    """Daily summary for dashboard."""
    date: datetime
    total_new_items: int
    top_papers_count: int
    new_models_count: int
    new_datasets_count: int
    new_benchmarks_count: int
    category_breakdown: List[CategoryCount]


class TopItemBrief(BaseModel):
    """Brief info for top items."""
    id: int
    title: str
    slug: str
    source: str
    published_date: datetime
    relevance_score: float
    short_summary: Optional[str] = None
    github_stars: Optional[int] = None
    categories: List[str] = []
    tags: List[str] = []


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    # Daily summary
    daily_summary: DailySummary
    
    # Top items
    top_10_today: List[TopItemBrief]
    most_promising_papers: List[TopItemBrief]
    useful_repositories: List[TopItemBrief]
    new_architectures: List[TopItemBrief]
    new_benchmarks_datasets: List[TopItemBrief]
    
    # What to look at
    worth_looking_at: List[TopItemBrief]
    
    # Overall stats
    total_items: int
    total_papers: int
    total_models: int
    total_datasets: int
    total_repositories: int
    
    # Recent activity
    items_last_7_days: int
    items_last_30_days: int
    latest_ingestion_at: Optional[datetime] = None
    
    # Sources
    sources_breakdown: dict
