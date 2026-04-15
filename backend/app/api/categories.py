"""Categories API routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

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
    return [CategoryResponse(**c.to_dict()) for c in categories]


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
    
    return CategoryResponse(**category.to_dict())
