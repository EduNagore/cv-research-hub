"""Celery tasks for background jobs."""
from app.tasks.ingestion_tasks import (
    daily_ingestion_task,
    refresh_github_metadata_task,
    recalculate_scores_task,
    generate_trends_task,
)

__all__ = [
    "daily_ingestion_task",
    "refresh_github_metadata_task",
    "recalculate_scores_task",
    "generate_trends_task",
]
