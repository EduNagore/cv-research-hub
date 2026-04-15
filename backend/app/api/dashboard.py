"""Dashboard API routes."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.research_item import ResearchItem, ContributionType, StatusLabel
from app.schemas.dashboard import DashboardStats, DailySummary, CategoryCount, TopItemBrief

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Get dashboard statistics."""
    if date is None:
        date = datetime.utcnow()
    
    # Calculate date ranges
    today_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_ago = today_start - timedelta(days=7)
    month_ago = today_start - timedelta(days=30)
    
    # Get total counts
    total_result = await db.execute(select(func.count(ResearchItem.id)))
    total_items = total_result.scalar() or 0
    latest_ingestion_result = await db.execute(select(func.max(ResearchItem.last_ingested_at)))
    latest_ingestion_at = latest_ingestion_result.scalar_one_or_none()
    
    # Get counts by contribution type
    papers_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.contribution_type == ContributionType.PAPER)
    )
    total_papers = papers_result.scalar() or 0
    
    models_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.contribution_type == ContributionType.MODEL)
    )
    total_models = models_result.scalar() or 0
    
    datasets_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.contribution_type == ContributionType.DATASET)
    )
    total_datasets = datasets_result.scalar() or 0
    
    repos_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.contribution_type == ContributionType.REPOSITORY)
    )
    total_repositories = repos_result.scalar() or 0
    
    # Get today's new items
    today_items_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
            )
        )
    )
    total_new_items = today_items_result.scalar() or 0
    
    # Get items from last 7 and 30 days
    items_7d_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.published_date >= week_ago)
    )
    items_last_7_days = items_7d_result.scalar() or 0
    
    items_30d_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(ResearchItem.published_date >= month_ago)
    )
    items_last_30_days = items_30d_result.scalar() or 0
    
    # Get category breakdown
    from app.models.category import Category
    category_result = await db.execute(
        select(Category.name, Category.slug, Category.item_count)
        .where(Category.is_active == True)
        .order_by(Category.display_order)
    )
    categories = category_result.all()
    category_breakdown = [
        CategoryCount(name=c.name, slug=c.slug, count=c.item_count)
        for c in categories
    ]
    
    # Get today's counts by type
    today_papers_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
                ResearchItem.contribution_type == ContributionType.PAPER,
            )
        )
    )
    top_papers_count = today_papers_result.scalar() or 0
    
    today_models_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
                ResearchItem.contribution_type == ContributionType.MODEL,
            )
        )
    )
    new_models_count = today_models_result.scalar() or 0
    
    today_datasets_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
                ResearchItem.contribution_type == ContributionType.DATASET,
            )
        )
    )
    new_datasets_count = today_datasets_result.scalar() or 0
    
    today_benchmarks_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
                ResearchItem.contribution_type == ContributionType.BENCHMARK,
            )
        )
    )
    new_benchmarks_count = today_benchmarks_result.scalar() or 0
    
    # Create daily summary
    daily_summary = DailySummary(
        date=today_start,
        total_new_items=total_new_items,
        top_papers_count=top_papers_count,
        new_models_count=new_models_count,
        new_datasets_count=new_datasets_count,
        new_benchmarks_count=new_benchmarks_count,
        category_breakdown=category_breakdown,
    )
    
    # Get top 10 today
    top_10_result = await db.execute(
        select(ResearchItem)
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
            )
        )
        .order_by(ResearchItem.relevance_score.desc())
        .limit(10)
    )
    top_10_today = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in top_10_result.scalars().all()
    ]
    
    # Get most promising papers (high relevance, recent)
    promising_result = await db.execute(
        select(ResearchItem)
        .where(ResearchItem.contribution_type == ContributionType.PAPER)
        .order_by(ResearchItem.relevance_score.desc())
        .limit(10)
    )
    most_promising_papers = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in promising_result.scalars().all()
    ]
    
    # Get useful repositories (has GitHub, good stars)
    repos_query_result = await db.execute(
        select(ResearchItem)
        .where(ResearchItem.github_url.isnot(None))
        .order_by(ResearchItem.github_stars.desc().nullslast())
        .limit(10)
    )
    useful_repositories = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in repos_query_result.scalars().all()
    ]
    
    # Get new architectures/models
    arch_result = await db.execute(
        select(ResearchItem)
        .where(ResearchItem.contribution_type == ContributionType.MODEL)
        .order_by(ResearchItem.published_date.desc())
        .limit(10)
    )
    new_architectures = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in arch_result.scalars().all()
    ]
    
    # Get new benchmarks/datasets
    bench_result = await db.execute(
        select(ResearchItem)
        .where(
            ResearchItem.contribution_type.in_([
                ContributionType.BENCHMARK,
                ContributionType.DATASET,
            ])
        )
        .order_by(ResearchItem.published_date.desc())
        .limit(10)
    )
    new_benchmarks_datasets = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in bench_result.scalars().all()
    ]
    
    # Get "worth looking at" - trending or high relevance
    worth_result = await db.execute(
        select(ResearchItem)
        .where(
            ResearchItem.status_label.in_([
                StatusLabel.TRENDING,
                StatusLabel.USEFUL_FOR_RESEARCH,
            ])
        )
        .order_by(ResearchItem.relevance_score.desc())
        .limit(10)
    )
    worth_looking_at = [
        TopItemBrief(
            id=item.id,
            title=item.title,
            slug=item.slug,
            source=item.source.value,
            published_date=item.published_date,
            relevance_score=item.relevance_score,
            short_summary=item.short_summary,
            github_stars=item.github_stars,
            categories=[c.name for c in item.categories],
            tags=[t.name for t in item.tags],
        )
        for item in worth_result.scalars().all()
    ]
    
    # Get source breakdown
    from app.models.research_item import SourceType
    source_breakdown = {}
    for source in SourceType:
        count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .where(ResearchItem.source == source)
        )
        source_breakdown[source.value] = count_result.scalar() or 0
    
    return DashboardStats(
        daily_summary=daily_summary,
        top_10_today=top_10_today,
        most_promising_papers=most_promising_papers,
        useful_repositories=useful_repositories,
        new_architectures=new_architectures,
        new_benchmarks_datasets=new_benchmarks_datasets,
        worth_looking_at=worth_looking_at,
        total_items=total_items,
        total_papers=total_papers,
        total_models=total_models,
        total_datasets=total_datasets,
        total_repositories=total_repositories,
        items_last_7_days=items_last_7_days,
        items_last_30_days=items_last_30_days,
        latest_ingestion_at=latest_ingestion_at,
        sources_breakdown=source_breakdown,
    )


@router.get("/daily-summary", response_model=DailySummary)
async def get_daily_summary(
    date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> DailySummary:
    """Get daily summary."""
    if date is None:
        date = datetime.utcnow()
    
    today_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Get today's new items count
    today_items_result = await db.execute(
        select(func.count(ResearchItem.id))
        .where(
            and_(
                ResearchItem.published_date >= today_start,
                ResearchItem.published_date < today_end,
            )
        )
    )
    total_new_items = today_items_result.scalar() or 0
    
    # Get counts by type
    type_counts = {}
    for contrib_type in ContributionType:
        count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .where(
                and_(
                    ResearchItem.published_date >= today_start,
                    ResearchItem.published_date < today_end,
                    ResearchItem.contribution_type == contrib_type,
                )
            )
        )
        type_counts[contrib_type.value] = count_result.scalar() or 0
    
    # Get category breakdown
    from app.models.category import Category
    category_result = await db.execute(
        select(Category.name, Category.slug, Category.item_count)
        .where(Category.is_active == True)
        .order_by(Category.display_order)
    )
    categories = category_result.all()
    category_breakdown = [
        CategoryCount(name=c.name, slug=c.slug, count=c.item_count)
        for c in categories
    ]
    
    return DailySummary(
        date=today_start,
        total_new_items=total_new_items,
        top_papers_count=type_counts.get("paper", 0),
        new_models_count=type_counts.get("model", 0),
        new_datasets_count=type_counts.get("dataset", 0),
        new_benchmarks_count=type_counts.get("benchmark", 0),
        category_breakdown=category_breakdown,
    )
