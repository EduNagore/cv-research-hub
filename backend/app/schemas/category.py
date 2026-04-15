"""Category schemas."""
from typing import List, Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str
    slug: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating categories."""
    display_order: int = 0
    is_active: bool = True
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    """Schema for updating categories."""
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryInDB(CategoryBase):
    """Category from database."""
    id: int
    display_order: int
    is_active: bool
    item_count: int
    
    class Config:
        from_attributes = True


class CategoryResponse(CategoryInDB):
    """Full category response."""
    pass
