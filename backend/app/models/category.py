"""Category model for research items."""
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.research_item import ResearchItem


class Category(Base):
    """Category model."""
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Statistics
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    research_items: Mapped[List["ResearchItem"]] = relationship(
        "ResearchItem",
        secondary="research_item_categories",
        back_populates="categories",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"
