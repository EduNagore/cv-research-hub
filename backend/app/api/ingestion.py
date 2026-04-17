"""Ingestion API routes."""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.models.category import Category
from app.models.research_item import ResearchItem, SourceType
from app.services.content_filters import gemini_discovered_filter
from app.services.ingestion import IngestionService
from app.services.ingestion_runner import run_ingestion_job

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def _validate_ingestion_token(x_ingestion_token: Optional[str]) -> None:
    """Require a shared secret for ingestion-mutating endpoints when configured."""
    expected_token = settings.INGESTION_TRIGGER_TOKEN
    if not expected_token:
        return
    if x_ingestion_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid ingestion trigger token")


async def _run_source_ingestion(
    source: str,
    category_slug: Optional[str] = None,
    *,
    reset_gemini: bool = False,
) -> dict:
    """Run a source-specific ingestion task with its own DB session."""
    logger.info("Starting source ingestion", extra={"source": source, "category_slug": category_slug})
    async with AsyncSessionLocal() as session:
        service = IngestionService(session)
        if source == "arxiv":
            result = await service.ingest_arxiv()
        elif source == "github":
            result = await service.ingest_github()
        elif source == "paperswithcode":
            result = await service.ingest_papers_with_code()
        elif source == "gemini":
            result = (
                await service.ingest_gemini_category(category_slug)
                if category_slug
                else await service.ingest_gemini_discovery(reset_existing=reset_gemini)
            )
        else:
            raise ValueError(f"Unknown source: {source}")
        await session.commit()
        logger.info("Completed source ingestion", extra={"source": source, "category_slug": category_slug})
        return {
            "success": True,
            "job": source,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
        }


async def _run_full_ingestion(*, reset_gemini: bool = False) -> dict:
    """Run the full ingestion pipeline in its own DB session."""
    logger.info("Starting full ingestion")
    if not settings.GEMINI_ENABLE_FULL_REFRESH:
        return {
            "success": True,
            "job": "full_ingestion",
            "timestamp": datetime.utcnow().isoformat(),
            "result": {
                "source": "gemini_discovery",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "error": "Full Gemini refresh is disabled.",
            },
        }
    result = await run_ingestion_job(
        lambda service: service.run_full_ingestion(reset_gemini=reset_gemini),
        job_name="full_ingestion",
    )
    logger.info("Completed full ingestion")
    return result


async def _run_background_job(job_name: str, func, *args, **kwargs) -> None:
    """Run a background ingestion job with logging."""
    try:
        logger.info("Background job started", extra={"job_name": job_name})
        await func(*args, **kwargs)
        logger.info("Background job completed", extra={"job_name": job_name})
    except Exception:
        logger.exception("Background job failed", extra={"job_name": job_name})
        raise


async def _run_refresh_github_metadata() -> dict:
    """Run GitHub metadata refresh in its own DB session."""
    return await run_ingestion_job(
        lambda service: service.refresh_github_metadata(),
        job_name="refresh_github_metadata",
    )


async def _run_recalculate_scores() -> dict:
    """Run relevance score recalculation in its own DB session."""
    return await run_ingestion_job(
        lambda service: service.recalculate_all_scores(),
        job_name="recalculate_scores",
    )


@router.post("/trigger")
async def trigger_ingestion(
    background_tasks: BackgroundTasks,
    source: Optional[str] = None,
    category_slug: Optional[str] = None,
    wait: bool = False,
    reset_gemini: bool = False,
    x_ingestion_token: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual ingestion."""
    _validate_ingestion_token(x_ingestion_token)
    try:
        if source:
            if source == "arxiv":
                result = await _run_source_ingestion("arxiv")
            elif source == "github":
                result = await _run_source_ingestion("github")
            elif source == "paperswithcode":
                result = await _run_source_ingestion("paperswithcode")
            elif source == "gemini":
                if not settings.GEMINI_ENABLE_MANUAL_REFRESH:
                    raise HTTPException(
                        status_code=400,
                        detail="Manual Gemini refresh is disabled. The site refreshes automatically once per day.",
                    )
                if category_slug and not settings.GEMINI_ENABLE_CATEGORY_REFRESH:
                    raise HTTPException(
                        status_code=400,
                        detail="Category refresh is disabled. The site refreshes automatically once per day.",
                    )
                if not category_slug and settings.GEMINI_ENABLE_FULL_REFRESH and not wait:
                    background_tasks.add_task(
                        _run_background_job,
                        "gemini_full_refresh",
                        _run_source_ingestion,
                        "gemini",
                        None,
                        reset_gemini=reset_gemini,
                    )
                    return {
                        "success": True,
                        "message": "Full Gemini refresh started in background",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                result = await _run_source_ingestion("gemini", category_slug, reset_gemini=reset_gemini)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
            
            return {
                "success": True,
                "message": (
                    f"Ingestion triggered for {source} category {category_slug}"
                    if source == "gemini" and category_slug
                    else f"Ingestion triggered for {source}"
                ),
                "timestamp": datetime.utcnow().isoformat(),
                "result": result.get("result"),
            }
        else:
            if settings.GEMINI_ENABLE_FULL_REFRESH and not wait:
                background_tasks.add_task(
                    _run_background_job,
                    "full_ingestion",
                    _run_full_ingestion,
                    reset_gemini=reset_gemini,
                )
                return {
                    "success": True,
                    "message": "Full ingestion started in background",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            result = await _run_full_ingestion(reset_gemini=reset_gemini)
            return {
                "success": True,
                "message": (
                    "Full ingestion completed"
                    if settings.GEMINI_ENABLE_FULL_REFRESH
                    else "Full Gemini refresh is disabled."
                ),
                "timestamp": datetime.utcnow().isoformat(),
                "result": result.get("result"),
            }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {exc}",
        ) from exc


@router.get("/status")
async def get_ingestion_status(
    db: AsyncSession = Depends(get_db),
):
    """Get ingestion status."""
    gemini_filter = gemini_discovered_filter()
    status = {}
    for source in SourceType:
        latest_result = await db.execute(
            select(func.max(ResearchItem.last_ingested_at))
            .where(ResearchItem.source == source)
        )
        count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .where(ResearchItem.source == source)
        )
        latest_ingestion = latest_result.scalar_one_or_none()
        total_items = count_result.scalar_one() or 0
        status[source.value] = {
            "latest_ingestion": latest_ingestion.isoformat() if latest_ingestion else None,
            "total_items": total_items,
            "configured": (
                True
                if source in {SourceType.ARXIV, SourceType.PAPERS_WITH_CODE}
                else bool(settings.GITHUB_TOKEN) if source == SourceType.GITHUB
                else False
            ),
        }

    gemini_latest_result = await db.execute(
        select(func.max(ResearchItem.last_ingested_at)).where(gemini_filter)
    )
    gemini_total_result = await db.execute(
        select(func.count(ResearchItem.id)).where(gemini_filter)
    )
    gemini_latest = gemini_latest_result.scalar_one_or_none()

    categories_result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.display_order)
    )
    gemini_categories = []
    for category in categories_result.scalars().all():
        category_count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .join(ResearchItem.categories)
            .where(Category.id == category.id, gemini_filter)
        )
        category_latest_result = await db.execute(
            select(func.max(ResearchItem.last_ingested_at))
            .join(ResearchItem.categories)
            .where(Category.id == category.id, gemini_filter)
        )
        category_latest = category_latest_result.scalar_one_or_none()
        gemini_categories.append(
            {
                "name": category.name,
                "slug": category.slug,
                "item_count": category_count_result.scalar() or 0,
                "latest_ingestion": category_latest.isoformat() if category_latest else None,
            }
        )
    
    return {
        "sources": status,
        "gemini_discovery": {
            "configured": bool(settings.GEMINI_API_KEY),
            "model": settings.GEMINI_MODEL,
            "results_per_category": settings.GEMINI_RESULTS_PER_CATEGORY,
            "lookback_days": settings.GEMINI_LOOKBACK_DAYS,
            "full_refresh_enabled": settings.GEMINI_ENABLE_FULL_REFRESH,
            "category_refresh_enabled": settings.GEMINI_ENABLE_CATEGORY_REFRESH,
            "manual_refresh_enabled": settings.GEMINI_ENABLE_MANUAL_REFRESH,
            "latest_ingestion": gemini_latest.isoformat() if gemini_latest else None,
            "total_items": gemini_total_result.scalar() or 0,
            "categories": gemini_categories,
        },
        "last_check": datetime.utcnow().isoformat(),
    }


@router.post("/refresh-github-metadata")
async def refresh_github_metadata(
    background_tasks: BackgroundTasks,
    x_ingestion_token: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Refresh GitHub metadata for all items."""
    _validate_ingestion_token(x_ingestion_token)
    background_tasks.add_task(_run_refresh_github_metadata)
    
    return {
        "success": True,
        "message": "GitHub metadata refresh triggered",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/recalculate-scores")
async def recalculate_scores(
    background_tasks: BackgroundTasks,
    x_ingestion_token: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Recalculate relevance scores for all items."""
    _validate_ingestion_token(x_ingestion_token)
    background_tasks.add_task(_run_recalculate_scores)
    
    return {
        "success": True,
        "message": "Score recalculation triggered",
        "timestamp": datetime.utcnow().isoformat(),
    }
