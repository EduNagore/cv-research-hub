"""Helpers for selecting Gemini-discovered content."""
from sqlalchemy import func, select, true

from app.models.research_item import ResearchItem


def gemini_discovered_filter():
    """Return a SQLAlchemy filter for items created by Gemini discovery."""
    return ResearchItem.source_id.ilike("gemini_%")


async def get_preferred_content_filter(db):
    """Prefer Gemini-discovered content when available, otherwise fall back to all items."""
    gemini_filter = gemini_discovered_filter()
    result = await db.execute(
        select(func.count(ResearchItem.id)).where(gemini_filter)
    )
    has_gemini_items = (result.scalar() or 0) > 0
    return gemini_filter if has_gemini_items else true(), has_gemini_items
