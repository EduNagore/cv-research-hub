"""Trends API routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trend import Trend, TrendPeriod, TrendType
from app.schemas.trend import TrendResponse, TrendStatistics

router = APIRouter()


@router.get("", response_model=List[TrendResponse])
async def list_trends(
    trend_type: Optional[TrendType] = None,
    period: TrendPeriod = TrendPeriod.WEEKLY,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[TrendResponse]:
    """List trends."""
    query = select(Trend).where(Trend.period == period)
    
    if trend_type:
        query = query.where(Trend.trend_type == trend_type)
    
    query = query.order_by(desc(Trend.popularity_score)).limit(limit)
    
    result = await db.execute(query)
    trends = result.scalars().all()
    return [TrendResponse(**t.to_dict()) for t in trends]


@router.get("/statistics", response_model=TrendStatistics)
async def get_trend_statistics(
    period: TrendPeriod = TrendPeriod.WEEKLY,
    db: AsyncSession = Depends(get_db),
) -> TrendStatistics:
    """Get comprehensive trend statistics."""
    # Get top architectures
    arch_result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == TrendType.ARCHITECTURE,
            Trend.period == period,
        )
        .order_by(desc(Trend.popularity_score))
        .limit(10)
    )
    top_architectures = [TrendResponse(**t.to_dict()) for t in arch_result.scalars().all()]
    
    # Get top topics
    topic_result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == TrendType.TOPIC,
            Trend.period == period,
        )
        .order_by(desc(Trend.popularity_score))
        .limit(10)
    )
    top_topics = [TrendResponse(**t.to_dict()) for t in topic_result.scalars().all()]
    
    # Get top methods
    method_result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == TrendType.METHOD,
            Trend.period == period,
        )
        .order_by(desc(Trend.popularity_score))
        .limit(10)
    )
    top_methods = [TrendResponse(**t.to_dict()) for t in method_result.scalars().all()]
    
    # Get top datasets
    dataset_result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == TrendType.DATASET,
            Trend.period == period,
        )
        .order_by(desc(Trend.popularity_score))
        .limit(10)
    )
    top_datasets = [TrendResponse(**t.to_dict()) for t in dataset_result.scalars().all()]
    
    # Get emerging keywords (high growth rate)
    keyword_result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == TrendType.KEYWORD,
            Trend.period == period,
        )
        .order_by(desc(Trend.growth_rate))
        .limit(10)
    )
    emerging_keywords = [TrendResponse(**t.to_dict()) for t in keyword_result.scalars().all()]
    
    return TrendStatistics(
        top_architectures=top_architectures,
        top_topics=top_topics,
        top_methods=top_methods,
        top_datasets=top_datasets,
        emerging_keywords=emerging_keywords,
        period=period,
    )


@router.get("/by-type/{trend_type}")
async def get_trends_by_type(
    trend_type: TrendType,
    period: TrendPeriod = TrendPeriod.WEEKLY,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get trends by type."""
    result = await db.execute(
        select(Trend)
        .where(
            Trend.trend_type == trend_type,
            Trend.period == period,
        )
        .order_by(desc(Trend.popularity_score))
        .limit(limit)
    )
    trends = result.scalars().all()
    
    return {
        "trend_type": trend_type.value,
        "period": period.value,
        "trends": [
            {
                "id": t.id,
                "name": t.name,
                "slug": t.slug,
                "frequency": t.frequency,
                "growth_rate": t.growth_rate,
                "popularity_score": t.popularity_score,
                "related_papers_count": t.related_papers_count,
                "related_models_count": t.related_models_count,
                "description": t.description,
            }
            for t in trends
        ],
    }
