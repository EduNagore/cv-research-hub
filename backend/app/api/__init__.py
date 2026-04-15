"""API routes."""
from fastapi import APIRouter

from app.api import dashboard, research_items, categories, tags, user_items, trends, comparisons, decision_support, ingestion

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(research_items.router, prefix="/items", tags=["research-items"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(user_items.router, prefix="/user-items", tags=["user-items"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["comparisons"])
api_router.include_router(decision_support.router, prefix="/decision-support", tags=["decision-support"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
