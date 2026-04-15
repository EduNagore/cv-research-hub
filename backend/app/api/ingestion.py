"""Ingestion API routes."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.models.research_item import ResearchItem, SourceType
from app.services.ingestion_runner import run_ingestion_job

router = APIRouter()
settings = get_settings()


async def _run_source_ingestion(source: str) -> dict:
    """Run a source-specific ingestion task with its own DB session."""
    async with AsyncSessionLocal() as session:
        service = IngestionService(session)
        if source == "arxiv":
            result = await service.ingest_arxiv()
        elif source == "github":
            result = await service.ingest_github()
        elif source == "paperswithcode":
            result = await service.ingest_papers_with_code()
        else:
            raise ValueError(f"Unknown source: {source}")
        await session.commit()
        return {
            "success": True,
            "job": source,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
        }


async def _run_full_ingestion() -> dict:
    """Run the full ingestion pipeline in its own DB session."""
    return await run_ingestion_job(
        lambda service: service.run_full_ingestion(),
        job_name="full_ingestion",
    )


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
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual ingestion."""
    if source:
        if source == "arxiv":
            background_tasks.add_task(_run_source_ingestion, "arxiv")
        elif source == "github":
            background_tasks.add_task(_run_source_ingestion, "github")
        elif source == "paperswithcode":
            background_tasks.add_task(_run_source_ingestion, "paperswithcode")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
        
        return {
            "success": True,
            "message": f"Ingestion triggered for {source}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        # Trigger all sources
        background_tasks.add_task(_run_full_ingestion)
        
        return {
            "success": True,
            "message": "Full ingestion triggered for all sources",
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/status")
async def get_ingestion_status(
    db: AsyncSession = Depends(get_db),
):
    """Get ingestion status."""
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
    
    return {
        "sources": status,
        "last_check": datetime.utcnow().isoformat(),
    }


@router.post("/refresh-github-metadata")
async def refresh_github_metadata(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Refresh GitHub metadata for all items."""
    background_tasks.add_task(_run_refresh_github_metadata)
    
    return {
        "success": True,
        "message": "GitHub metadata refresh triggered",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/recalculate-scores")
async def recalculate_scores(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Recalculate relevance scores for all items."""
    background_tasks.add_task(_run_recalculate_scores)
    
    return {
        "success": True,
        "message": "Score recalculation triggered",
        "timestamp": datetime.utcnow().isoformat(),
    }
