"""Helpers for selecting Gemini-discovered content."""
from sqlalchemy import or_

from app.models.research_item import ResearchItem


def gemini_discovered_filter():
    """Return a SQLAlchemy filter for items created by Gemini discovery."""
    return or_(
        ResearchItem.source_id.ilike("gemini_%"),
        ResearchItem.raw_metadata.contains({"discovered_via": "gemini"}),
    )
