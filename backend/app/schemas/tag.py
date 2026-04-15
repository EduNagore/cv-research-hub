"""Tag schemas."""
from typing import Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    """Base tag schema."""
    name: str
    slug: str


class TagCreate(TagBase):
    """Schema for creating tags."""
    color: Optional[str] = None
    is_active: bool = True


class TagResponse(TagBase):
    """Tag response schema."""
    id: int
    color: Optional[str] = None
    item_count: int
    
    class Config:
        from_attributes = True
