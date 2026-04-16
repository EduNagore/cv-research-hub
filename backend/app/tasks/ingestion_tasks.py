"""Celery tasks for ingestion and background jobs."""
import asyncio
from datetime import datetime

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.services.ingestion_runner import run_ingestion_job
from app.services.ingestion import IngestionService

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "cv_research_hub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
)


def get_async_session() -> AsyncSession:
    """Get async database session."""
    return AsyncSessionLocal()


@celery_app.task(bind=True, max_retries=3)
def daily_ingestion_task(self):
    """Daily ingestion task."""
    async def run():
        try:
            return await run_ingestion_job(
                lambda service: service.run_full_ingestion(),
                job_name="daily_ingestion",
            )
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)
    
    return asyncio.run(run())

@celery_app.task(bind=True, max_retries=3)
def refresh_github_metadata_task(self):
    """Refresh GitHub metadata task."""
    async def run():
        try:
            return await run_ingestion_job(
                lambda service: service.refresh_github_metadata(),
                job_name="refresh_github_metadata",
            )
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)
    
    return asyncio.run(run())


@celery_app.task(bind=True, max_retries=3)
def recalculate_scores_task(self):
    """Recalculate all scores task."""
    async def run():
        try:
            return await run_ingestion_job(
                lambda service: service.recalculate_all_scores(),
                job_name="recalculate_scores",
            )
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)
    
    return asyncio.run(run())


@celery_app.task(bind=True, max_retries=3)
def generate_trends_task(self):
    """Generate trends from recent items."""
    async def run():
        async with AsyncSessionLocal() as session:
            try:
                from app.services.trend_service import TrendService
                
                service = TrendService(session)
                results = await service.generate_trends()
                return {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "results": results,
                }
            except Exception as exc:
                await session.rollback()
                raise self.retry(exc=exc, countdown=60)
    
    return asyncio.run(run())


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "daily-ingestion": {
        "task": "app.tasks.ingestion_tasks.daily_ingestion_task",
        "schedule": 86400.0,  # Daily
        "options": {"queue": "ingestion"},
    },
    "refresh-github-metadata": {
        "task": "app.tasks.ingestion_tasks.refresh_github_metadata_task",
        "schedule": 21600.0,  # Every 6 hours
        "options": {"queue": "ingestion"},
    },
    "recalculate-scores": {
        "task": "app.tasks.ingestion_tasks.recalculate_scores_task",
        "schedule": 43200.0,  # Every 12 hours
        "options": {"queue": "ingestion"},
    },
    "generate-trends": {
        "task": "app.tasks.ingestion_tasks.generate_trends_task",
        "schedule": 86400.0,  # Daily
        "options": {"queue": "trends"},
    },
}
