"""Pydantic schemas for API requests and responses."""
from app.schemas.research_item import (
    ResearchItemBase,
    ResearchItemCreate,
    ResearchItemUpdate,
    ResearchItemInDB,
    ResearchItemResponse,
    ResearchItemListResponse,
    ResearchItemFilter,
)
from app.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryInDB,
    CategoryResponse,
)
from app.schemas.tag import (
    TagBase,
    TagCreate,
    TagResponse,
)
from app.schemas.user_item import (
    UserItemBase,
    UserItemCreate,
    UserItemUpdate,
    UserItemResponse,
)
from app.schemas.trend import (
    TrendBase,
    TrendResponse,
    TrendStatistics,
)
from app.schemas.comparison import (
    ComparisonBase,
    ComparisonResponse,
)
from app.schemas.dashboard import (
    DashboardStats,
    DailySummary,
    CategoryCount,
)
from app.schemas.decision_support import (
    DecisionRequest,
    DecisionResponse,
    Recommendation,
)

__all__ = [
    "ResearchItemBase",
    "ResearchItemCreate",
    "ResearchItemUpdate",
    "ResearchItemInDB",
    "ResearchItemResponse",
    "ResearchItemListResponse",
    "ResearchItemFilter",
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryInDB",
    "CategoryResponse",
    "TagBase",
    "TagCreate",
    "TagResponse",
    "UserItemBase",
    "UserItemCreate",
    "UserItemUpdate",
    "UserItemResponse",
    "TrendBase",
    "TrendResponse",
    "TrendStatistics",
    "ComparisonBase",
    "ComparisonResponse",
    "DashboardStats",
    "DailySummary",
    "CategoryCount",
    "DecisionRequest",
    "DecisionResponse",
    "Recommendation",
]
