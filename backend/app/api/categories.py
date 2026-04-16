"""Categories API routes."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse
from app.services.content_filters import gemini_discovered_filter
from app.models.research_item import ResearchItem

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> List[CategoryResponse]:
    """List all active categories."""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_order)
    )
    categories = result.scalars().all()
    responses = []
    for category in categories:
        count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .join(ResearchItem.categories)
            .where(Category.id == category.id, gemini_discovered_filter())
        )
        responses.append(
            CategoryResponse(
                **{
                    **category.to_dict(),
                    "item_count": count_result.scalar() or 0,
                }
            )
        )
    return responses


@router.get("/feed")
async def get_category_feed(
    limit_per_category: int = 6,
    db: AsyncSession = Depends(get_db),
):
    """Return a Gemini-prepared JSON feed grouped by category."""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_order)
    )
    categories = result.scalars().all()

    feed = []
    for category in categories:
        count_result = await db.execute(
            select(func.count(ResearchItem.id))
            .join(ResearchItem.categories)
            .where(Category.id == category.id, gemini_discovered_filter())
        )
        items_result = await db.execute(
            select(ResearchItem)
            .join(ResearchItem.categories)
            .where(Category.id == category.id, gemini_discovered_filter())
            .order_by(ResearchItem.published_date.desc(), ResearchItem.relevance_score.desc())
            .limit(limit_per_category)
        )
        items = items_result.scalars().all()

        feed.append(
            {
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                    "item_count": count_result.scalar() or 0,
                },
                "items": [
                    {
                        **item.to_dict(),
                        "categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in item.categories],
                        "tags": [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in item.tags],
                    }
                    for item in items
                ],
            }
        )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "categories": feed,
    }


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """Get a single category by slug."""
    result = await db.execute(
        select(Category).where(Category.slug == slug)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    count_result = await db.execute(
        select(func.count(ResearchItem.id))
        .join(ResearchItem.categories)
        .where(Category.id == category.id, gemini_discovered_filter())
    )
    return CategoryResponse(
        **{
            **category.to_dict(),
            "item_count": count_result.scalar() or 0,
        }
    )
