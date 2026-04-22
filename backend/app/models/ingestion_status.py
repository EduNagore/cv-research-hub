"""Persistent ingestion snapshot status records."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IngestionStatus(Base):
    """Track the latest known status for an ingestion scope."""

    __tablename__ = "ingestion_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    scope_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category_slug: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    last_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_status: Mapped[str] = mapped_column(String(32), default="idle", nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    last_result: Mapped[Optional[dict]] = mapped_column(JSON)
