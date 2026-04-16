"""Research items API routes."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
    ResearchItem,
    SourceType,
    StatusLabel,
)
from app.schemas.research_item import (
    ResearchItemFilter,
    ResearchItemListResponse,
    ResearchItemResponse,
)
from app.services.content_filters import gemini_discovered_filter

router = APIRouter()


def get_user_identifier(request: Request) -> str:
    """Get user identifier from request."""
    # For MVP, use a combination of IP and user agent hash
    # In production, this would use proper authentication
    import hashlib
    
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    identifier = hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()
    return identifier


@router.get("", response_model=ResearchItemListResponse)
async def list_research_items(
    request: Request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    source: Optional[SourceType] = None,
    contribution_type: Optional[ContributionType] = None,
    status_label: Optional[StatusLabel] = None,
    modality: Optional[ModalityType] = None,
    architecture_family: Optional[ArchitectureFamily] = None,
    has_code: Optional[bool] = None,
    has_github: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    tags: Optional[str] = None,  # Comma-separated
    keywords: Optional[str] = None,  # Comma-separated
    sort_by: str = "published_date",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ResearchItemListResponse:
    """List research items with filtering."""
    query = select(ResearchItem).where(gemini_discovered_filter())
    
    # Apply filters
    if search:
        search_filter = or_(
            ResearchItem.title.ilike(f"%{search}%"),
            ResearchItem.abstract.ilike(f"%{search}%"),
            ResearchItem.short_summary.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
    
    if category:
        from app.models.category import Category
        query = query.join(ResearchItem.categories).where(Category.slug == category)
    
    if source:
        query = query.where(ResearchItem.source == source)
    
    if contribution_type:
        query = query.where(ResearchItem.contribution_type == contribution_type)
    
    if status_label:
        query = query.where(ResearchItem.status_label == status_label)
    
    if modality:
        query = query.where(ResearchItem.modality == modality)
    
    if architecture_family:
        query = query.where(ResearchItem.architecture_family == architecture_family)
    
    if has_code is not None:
        if has_code:
            query = query.where(ResearchItem.code_url.isnot(None))
        else:
            query = query.where(ResearchItem.code_url.is_(None))
    
    if has_github is not None:
        if has_github:
            query = query.where(ResearchItem.github_url.isnot(None))
        else:
            query = query.where(ResearchItem.github_url.is_(None))
    
    if date_from:
        query = query.where(ResearchItem.published_date >= date_from)
    
    if date_to:
        query = query.where(ResearchItem.published_date <= date_to)
    
    if min_score is not None:
        query = query.where(ResearchItem.relevance_score >= min_score)
    
    if max_score is not None:
        query = query.where(ResearchItem.relevance_score <= max_score)
    
    if tags:
        from app.models.tag import Tag
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.join(ResearchItem.tags).where(Tag.slug.in_(tag_list))
    
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
        keyword_filters = []
        for keyword in keyword_list:
            keyword_filters.append(ResearchItem.title.ilike(f"%{keyword}%"))
            keyword_filters.append(ResearchItem.abstract.ilike(f"%{keyword}%"))
        query = query.where(or_(*keyword_filters))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply sorting
    sort_column = getattr(ResearchItem, sort_by, ResearchItem.published_date)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get user interactions
    user_identifier = get_user_identifier(request)
    from app.models.user_item import UserItem
    
    user_items_result = await db.execute(
        select(UserItem)
        .where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id.in_([item.id for item in items]),
            )
        )
    )
    user_items_map = {
        ui.research_item_id: ui for ui in user_items_result.scalars().all()
    }
    
    # Build response
    item_responses = []
    for item in items:
        item_dict = {
            **item.to_dict(),
            "categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in item.categories],
            "tags": [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in item.tags],
        }
        
        # Add user interaction data
        user_item = user_items_map.get(item.id)
        if user_item:
            item_dict["is_favorite"] = user_item.is_favorite
            item_dict["is_bookmarked"] = user_item.is_bookmarked
            item_dict["user_status"] = user_item.status.value
        
        item_responses.append(ResearchItemResponse(**item_dict))
    
    total_pages = (total + page_size - 1) // page_size
    
    return ResearchItemListResponse(
        items=item_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/search")
async def search_research_items(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search research items."""
    # Use PostgreSQL full-text search
    from sqlalchemy import text
    
    search_query = f"""
    SELECT id, title, abstract, short_summary, relevance_score,
           ts_rank(to_tsvector('english', coalesce(title, '') || ' ' || 
                                        coalesce(abstract, '') || ' ' || 
                                        coalesce(short_summary, '')),
                   plainto_tsquery('english', :query)) as rank
    FROM research_items
    WHERE source_id LIKE 'gemini_%'
      AND to_tsvector('english', coalesce(title, '') || ' ' || 
                                  coalesce(abstract, '') || ' ' || 
                                  coalesce(short_summary, ''))
          @@ plainto_tsquery('english', :query)
    ORDER BY rank DESC, relevance_score DESC
    OFFSET :offset LIMIT :limit
    """
    
    offset = (page - 1) * page_size
    
    result = await db.execute(
        text(search_query),
        {
            "query": q,
            "offset": offset,
            "limit": page_size,
        },
    )
    
    rows = result.all()
    
    # Get full items
    item_ids = [row.id for row in rows]
    items_result = await db.execute(
        select(ResearchItem).where(ResearchItem.id.in_(item_ids))
    )
    items_map = {item.id: item for item in items_result.scalars().all()}
    
    # Maintain search order
    items = [items_map[item_id] for item_id in item_ids if item_id in items_map]
    
    # Get total count
    count_query = f"""
    SELECT COUNT(*)
    FROM research_items
    WHERE source_id LIKE 'gemini_%'
      AND to_tsvector('english', coalesce(title, '') || ' ' || 
                                  coalesce(abstract, '') || ' ' || 
                                  coalesce(short_summary, ''))
          @@ plainto_tsquery('english', :query)
    """
    count_result = await db.execute(text(count_query), {"query": q})
    total = count_result.scalar() or 0
    
    return {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "source": item.source.value,
                "published_date": item.published_date.isoformat(),
                "relevance_score": item.relevance_score,
                "short_summary": item.short_summary,
                "github_stars": item.github_stars,
                "categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in item.categories],
                "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in item.tags],
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{slug}", response_model=ResearchItemResponse)
async def get_research_item(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ResearchItemResponse:
    """Get a single research item by slug."""
    result = await db.execute(
        select(ResearchItem).where(
            ResearchItem.slug == slug,
            gemini_discovered_filter(),
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Research item not found")
    
    # Update last viewed
    user_identifier = get_user_identifier(request)
    from app.models.user_item import UserItem
    
    user_item_result = await db.execute(
        select(UserItem).where(
            and_(
                UserItem.user_identifier == user_identifier,
                UserItem.research_item_id == item.id,
            )
        )
    )
    user_item = user_item_result.scalar_one_or_none()
    
    if user_item:
        user_item.last_viewed_at = datetime.utcnow()
    else:
        user_item = UserItem(
            user_identifier=user_identifier,
            research_item_id=item.id,
            last_viewed_at=datetime.utcnow(),
        )
        db.add(user_item)
    
    await db.commit()
    
    # Build response
    item_dict = {
        **item.to_dict(),
        "categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in item.categories],
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in item.tags],
        "is_favorite": user_item.is_favorite if user_item else False,
        "is_bookmarked": user_item.is_bookmarked if user_item else False,
        "user_status": user_item.status.value if user_item else "unread",
    }
    
    return ResearchItemResponse(**item_dict)


@router.get("/by-category/{category_slug}")
async def get_items_by_category(
    category_slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get research items by category."""
    from app.models.category import Category
    
    # Get category
    category_result = await db.execute(
        select(Category).where(Category.slug == category_slug)
    )
    category_obj = category_result.scalar_one_or_none()
    
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get items
    query = (
        select(ResearchItem)
        .join(ResearchItem.categories)
        .where(Category.id == category_obj.id, gemini_discovered_filter())
        .order_by(desc(ResearchItem.published_date))
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "category": {
            "id": category_obj.id,
            "name": category_obj.name,
            "slug": category_obj.slug,
            "description": category_obj.description,
        },
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "source": item.source.value,
                "published_date": item.published_date.isoformat(),
                "relevance_score": item.relevance_score,
                "short_summary": item.short_summary,
                "github_stars": item.github_stars,
                "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in item.tags],
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
