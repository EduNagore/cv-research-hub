"""Tag model for research items."""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.research_item import ResearchItem


class Tag(Base):
    """Tag model."""
    
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Statistics
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    research_items: Mapped[List["ResearchItem"]] = relationship(
        "ResearchItem",
        secondary="research_item_tags",
        back_populates="tags",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"
