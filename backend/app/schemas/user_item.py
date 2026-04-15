"""User item schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.user_item import UserItemStatus


class UserItemBase(BaseModel):
    """Base user item schema."""
    research_item_id: int
    status: UserItemStatus = UserItemStatus.UNREAD
    is_favorite: bool = False
    is_bookmarked: bool = False


class UserItemCreate(UserItemBase):
    """Schema for creating user items."""
    user_identifier: str
    notes: Optional[str] = None
    rating: Optional[int] = None


class UserItemUpdate(BaseModel):
    """Schema for updating user items."""
    status: Optional[UserItemStatus] = None
    is_favorite: Optional[bool] = None
    is_bookmarked: Optional[bool] = None
    notes: Optional[str] = None
    rating: Optional[int] = None


class UserItemResponse(UserItemBase):
    """User item response schema."""
    id: int
    user_identifier: str
    notes: Optional[str] = None
    rating: Optional[int] = None
    first_seen_at: datetime
    last_viewed_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Include research item details
    research_item_title: Optional[str] = None
    research_item_published_date: Optional[datetime] = None
    research_item_relevance_score: Optional[float] = None
    
    class Config:
        from_attributes = True
