"""Helpers for selecting Gemini-discovered content."""
from app.models.research_item import ResearchItem


def gemini_discovered_filter():
    """Return a SQLAlchemy filter for items created by Gemini discovery."""
    return ResearchItem.source_id.ilike("gemini_%")
