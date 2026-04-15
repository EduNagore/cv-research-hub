"""User items API routes."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user_item import UserItem, UserItemStatus
from app.schemas.user_item import UserItemCreate, UserItemResponse, UserItemUpdate

router = APIRouter()


def get_user_identifier(request: Request) -> str:
    """Get user identifier from request."""
    import hashlib
    
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    identifier = hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()
    return identifier


@router.get("/favorites")
async def get_favorites(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get user's favorite items."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem)
        .where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.is_favorite == True,
            )
        )
        .order_by(desc(UserItem.created_at))
    )
    user_items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": ui.id,
                "research_item_id": ui.research_item_id,
                "research_item_title": ui.research_item.title,
                "research_item_published_date": ui.research_item.published_date.isoformat(),
                "research_item_relevance_score": ui.research_item.relevance_score,
                "is_favorite": ui.is_favorite,
                "is_bookmarked": ui.is_bookmarked,
                "status": ui.status.value,
                "notes": ui.notes,
                "rating": ui.rating,
                "created_at": ui.created_at.isoformat(),
            }
            for ui in user_items
        ]
    }


@router.get("/bookmarks")
async def get_bookmarks(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get user's bookmarked items."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem)
        .where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.is_bookmarked == True,
            )
        )
        .order_by(desc(UserItem.created_at))
    )
    user_items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": ui.id,
                "research_item_id": ui.research_item_id,
                "research_item_title": ui.research_item.title,
                "research_item_published_date": ui.research_item.published_date.isoformat(),
                "research_item_relevance_score": ui.research_item.relevance_score,
                "is_favorite": ui.is_favorite,
                "is_bookmarked": ui.is_bookmarked,
                "status": ui.status.value,
                "notes": ui.notes,
                "created_at": ui.created_at.isoformat(),
            }
            for ui in user_items
        ]
    }


@router.get("/review-later")
async def get_review_later(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get user's review later items."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem)
        .where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.status == UserItemStatus.REVIEW_LATER,
            )
        )
        .order_by(desc(UserItem.created_at))
    )
    user_items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": ui.id,
                "research_item_id": ui.research_item_id,
                "research_item_title": ui.research_item.title,
                "research_item_published_date": ui.research_item.published_date.isoformat(),
                "research_item_relevance_score": ui.research_item.relevance_score,
                "is_favorite": ui.is_favorite,
                "is_bookmarked": ui.is_bookmarked,
                "status": ui.status.value,
                "notes": ui.notes,
                "created_at": ui.created_at.isoformat(),
            }
            for ui in user_items
        ]
    }


@router.post("/{item_id}/favorite")
async def toggle_favorite(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status for an item."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem).where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id == item_id,
            )
        )
    )
    user_item = result.scalar_one_or_none()
    
    if user_item:
        user_item.is_favorite = not user_item.is_favorite
    else:
        user_item = UserItem(
            user_identifier=user_identifier,
            research_item_id=item_id,
            is_favorite=True,
        )
        db.add(user_item)
    
    await db.commit()
    
    return {
        "success": True,
        "is_favorite": user_item.is_favorite,
    }


@router.post("/{item_id}/bookmark")
async def toggle_bookmark(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Toggle bookmark status for an item."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem).where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id == item_id,
            )
        )
    )
    user_item = result.scalar_one_or_none()
    
    if user_item:
        user_item.is_bookmarked = not user_item.is_bookmarked
    else:
        user_item = UserItem(
            user_identifier=user_identifier,
            research_item_id=item_id,
            is_bookmarked=True,
        )
        db.add(user_item)
    
    await db.commit()
    
    return {
        "success": True,
        "is_bookmarked": user_item.is_bookmarked,
    }


@router.post("/{item_id}/status")
async def update_status(
    request: Request,
    item_id: int,
    status: UserItemStatus,
    db: AsyncSession = Depends(get_db),
):
    """Update status for an item."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem).where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id == item_id,
            )
        )
    )
    user_item = result.scalar_one_or_none()
    
    if user_item:
        user_item.status = status
        if status == UserItemStatus.READ:
            user_item.read_at = datetime.utcnow()
    else:
        user_item = UserItem(
            user_identifier=user_identifier,
            research_item_id=item_id,
            status=status,
        )
        if status == UserItemStatus.READ:
            user_item.read_at = datetime.utcnow()
        db.add(user_item)
    
    await db.commit()
    
    return {
        "success": True,
        "status": user_item.status.value,
    }


@router.post("/{item_id}/notes")
async def update_notes(
    request: Request,
    item_id: int,
    notes: str,
    db: AsyncSession = Depends(get_db),
):
    """Update notes for an item."""
    user_identifier = get_user_identifier(request)
    
    result = await db.execute(
        select(UserItem).where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id == item_id,
            )
        )
    )
    user_item = result.scalar_one_or_none()
    
    if user_item:
        user_item.notes = notes
    else:
        user_item = UserItem(
            user_identifier=user_identifier,
            research_item_id=item_id,
            notes=notes,
        )
        db.add(user_item)
    
    await db.commit()
    
    return {
        "success": True,
        "notes": user_item.notes,
    }
