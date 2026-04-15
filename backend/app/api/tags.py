"""Tags API routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse

router = APIRouter()


@router.get("", response_model=List[TagResponse])
async def list_tags(
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> List[TagResponse]:
    """List all tags."""
    query = select(Tag).where(Tag.is_active == True)
    
    if search:
        query = query.where(Tag.name.ilike(f"%{search}%"))
    
    query = query.order_by(Tag.item_count.desc()).limit(limit)
    
    result = await db.execute(query)
    tags = result.scalars().all()
    return [TagResponse(**t.to_dict()) for t in tags]


@router.get("/popular")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get most popular tags."""
    result = await db.execute(
        select(Tag)
        .where(Tag.is_active == True)
        .order_by(Tag.item_count.desc())
        .limit(limit)
    )
    tags = result.scalars().all()
    
    return {
        "tags": [
            {
                "id": t.id,
                "name": t.name,
                "slug": t.slug,
                "color": t.color,
                "item_count": t.item_count,
            }
            for t in tags
        ]
    }
