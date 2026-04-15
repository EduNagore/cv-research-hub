"""User Item model for favorites, read status, and read-later."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.research_item import ResearchItem


class UserItemStatus(str, PyEnum):
    """Status of user item interaction."""
    UNREAD = "unread"
    READING = "reading"
    READ = "read"
    REVIEW_LATER = "review_later"
    ARCHIVED = "archived"


class UserItem(Base):
    """User item interaction model."""
    
    __tablename__ = "user_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # User identification (using session/device ID for MVP)
    user_identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Research item reference
    research_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("research_items.id"), nullable=False, index=True
    )
    
    # Status
    status: Mapped[UserItemStatus] = mapped_column(
        SQLEnum(UserItemStatus), default=UserItemStatus.UNREAD, index=True
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # User notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 rating
    
    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    research_item: Mapped["ResearchItem"] = relationship(
        "ResearchItem",
        back_populates="user_items",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<UserItem(id={self.id}, user='{self.user_identifier}', item_id={self.research_item_id})>"
