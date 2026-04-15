"""Comparisons API routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.comparison import Comparison, ComputationalCost, MaturityLevel
from app.schemas.comparison import ComparisonResponse, ComparisonFilter

router = APIRouter()


@router.get("", response_model=List[ComparisonResponse])
async def list_comparisons(
    task: Optional[str] = None,
    architecture_family: Optional[str] = None,
    maturity_level: Optional[MaturityLevel] = None,
    computational_cost: Optional[ComputationalCost] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[ComparisonResponse]:
    """List comparisons with filtering."""
    query = select(Comparison).where(Comparison.is_published == True)
    
    if task:
        query = query.where(Comparison.task.ilike(f"%{task}%"))
    
    if architecture_family:
        query = query.where(Comparison.architecture_family == architecture_family)
    
    if maturity_level:
        query = query.where(Comparison.maturity_level == maturity_level)
    
    if computational_cost:
        query = query.where(Comparison.computational_cost == computational_cost)
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    comparisons = result.scalars().all()
    
    return {
        "items": [ComparisonResponse(**c.to_dict()) for c in comparisons],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/tasks")
async def get_available_tasks(
    db: AsyncSession = Depends(get_db),
):
    """Get list of available tasks for comparison."""
    result = await db.execute(
        select(Comparison.task)
        .where(Comparison.is_published == True)
        .distinct()
    )
    tasks = [row[0] for row in result.all()]
    
    return {"tasks": tasks}


@router.get("/by-task/{task}")
async def get_comparisons_by_task(
    task: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all comparisons for a specific task."""
    result = await db.execute(
        select(Comparison)
        .where(
            Comparison.task == task,
            Comparison.is_published == True,
        )
        .order_by(desc(Comparison.view_count))
    )
    comparisons = result.scalars().all()
    
    return {
        "task": task,
        "comparisons": [
            {
                "id": c.id,
                "model_name": c.model_name,
                "slug": c.slug,
                "description": c.description,
                "strengths": c.strengths,
                "limitations": c.limitations,
                "architecture_family": c.architecture_family,
                "computational_cost": c.computational_cost.value if c.computational_cost else None,
                "maturity_level": c.maturity_level.value if c.maturity_level else None,
                "performance_metrics": c.performance_metrics,
                "best_use_cases": c.best_use_cases,
                "not_recommended_for": c.not_recommended_for,
                "paper_url": c.paper_url,
                "code_url": c.code_url,
                "view_count": c.view_count,
            }
            for c in comparisons
        ],
    }


@router.get("/{slug}", response_model=ComparisonResponse)
async def get_comparison(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ComparisonResponse:
    """Get a single comparison by slug."""
    result = await db.execute(
        select(Comparison).where(Comparison.slug == slug)
    )
    comparison = result.scalar_one_or_none()
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    # Increment view count
    comparison.view_count += 1
    await db.commit()
    
    return ComparisonResponse(**comparison.to_dict())
