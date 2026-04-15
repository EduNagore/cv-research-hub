"""Helpers for running ingestion jobs with their own DB session."""
from datetime import datetime
from typing import Any, Awaitable, Callable

from app.core.database import AsyncSessionLocal
from app.services.ingestion import IngestionService


async def run_ingestion_job(
    job: Callable[[IngestionService], Awaitable[Any]],
    *,
    job_name: str,
) -> dict:
    """Run an ingestion-related job inside its own DB session."""
    async with AsyncSessionLocal() as session:
        service = IngestionService(session)
        result = await job(service)
        await session.commit()
        return {
            "success": True,
            "job": job_name,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
        }
