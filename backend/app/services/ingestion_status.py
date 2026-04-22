"""Helpers for persisting ingestion snapshot status."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion_status import IngestionStatus


class IngestionStatusService:
    """Persist and retrieve the latest status for ingestion scopes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def build_scope_key(source: str, category_slug: Optional[str] = None) -> str:
        return f"{source}:{category_slug}" if category_slug else source

    async def mark_started(
        self,
        source: str,
        category_slug: Optional[str] = None,
        *,
        started_at: Optional[datetime] = None,
    ) -> IngestionStatus:
        status = await self._get_or_create(source, category_slug)
        status.last_started_at = started_at or datetime.utcnow()
        status.last_status = "running"
        status.last_error = None
        await self.db.flush()
        return status

    async def mark_completed(
        self,
        source: str,
        category_slug: Optional[str] = None,
        *,
        completed_at: Optional[datetime] = None,
        status_value: str = "success",
        error: Optional[str] = None,
        result: Optional[dict[str, Any]] = None,
    ) -> IngestionStatus:
        status = await self._get_or_create(source, category_slug)
        status.last_completed_at = completed_at or datetime.utcnow()
        status.last_status = status_value
        status.last_error = error
        status.last_result = result
        await self.db.flush()
        return status

    async def _get_or_create(self, source: str, category_slug: Optional[str]) -> IngestionStatus:
        scope_key = self.build_scope_key(source, category_slug)
        result = await self.db.execute(
            select(IngestionStatus).where(IngestionStatus.scope_key == scope_key)
        )
        status = result.scalar_one_or_none()
        if status is None:
            status = IngestionStatus(
                scope_key=scope_key,
                source=source,
                category_slug=category_slug,
            )
            self.db.add(status)
            await self.db.flush()
        return status
