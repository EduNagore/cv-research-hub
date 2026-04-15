"""Research Item model - the core entity of the platform."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.user_item import UserItem


class ContributionType(str, PyEnum):
    """Types of contributions."""
    PAPER = "paper"
    MODEL = "model"
    BENCHMARK = "benchmark"
    DATASET = "dataset"
    REPOSITORY = "repository"
    LIBRARY = "library"
    SURVEY = "survey"


class StatusLabel(str, PyEnum):
    """Status labels for items."""
    NEW = "new"
    TRENDING = "trending"
    UPDATED = "updated"
    USEFUL_FOR_RESEARCH = "useful_for_research"
    USEFUL_FOR_PRODUCTION = "useful_for_production"


class ModalityType(str, PyEnum):
    """Types of modalities."""
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"
    THREE_D = "3d"
    MEDICAL = "medical"
    HISTOPATHOLOGY = "histopathology"
    DERMATOLOGY = "dermatology"
    NATURAL_IMAGES = "natural_images"


class ArchitectureFamily(str, PyEnum):
    """Architecture families."""
    CNN = "cnn"
    TRANSFORMER = "transformer"
    DIFFUSION = "diffusion"
    GAN = "gan"
    AUTOENCODER = "autoencoder"
    RNN = "rnn"
    MLP = "mlp"
    HYBRID = "hybrid"
    OTHER = "other"


class SourceType(str, PyEnum):
    """Source types."""
    ARXIV = "arxiv"
    PAPERS_WITH_CODE = "papers_with_code"
    GITHUB = "github"
    HUGGINGFACE = "huggingface"
    OPENREVIEW = "openreview"
    JOURNAL = "journal"
    CONFERENCE = "conference"
    OTHER = "other"


# Association table for research items and categories
research_item_categories = Table(
    "research_item_categories",
    Base.metadata,
    Column("research_item_id", Integer, ForeignKey("research_items.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)

# Association table for research items and tags
research_item_tags = Table(
    "research_item_tags",
    Base.metadata,
    Column("research_item_id", Integer, ForeignKey("research_items.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class ResearchItem(Base):
    """Research item model."""
    
    __tablename__ = "research_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Core identification
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(600), unique=True, index=True)
    
    # Source information
    source: Mapped[SourceType] = mapped_column(SQLEnum(SourceType), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Publication info
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    authors: Mapped[Optional[List[str]]] = mapped_column(JSON)
    author_affiliations: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Content
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    short_summary: Mapped[Optional[str]] = mapped_column(Text)
    full_summary: Mapped[Optional[str]] = mapped_column(Text)
    why_it_matters: Mapped[Optional[str]] = mapped_column(Text)
    problem_solved: Mapped[Optional[str]] = mapped_column(Text)
    contribution_description: Mapped[Optional[str]] = mapped_column(Text)
    use_cases: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Links
    paper_url: Mapped[Optional[str]] = mapped_column(String(1000))
    abstract_url: Mapped[Optional[str]] = mapped_column(String(1000))
    code_url: Mapped[Optional[str]] = mapped_column(String(1000))
    github_url: Mapped[Optional[str]] = mapped_column(String(1000))
    project_page_url: Mapped[Optional[str]] = mapped_column(String(1000))
    demo_url: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Classification
    contribution_type: Mapped[ContributionType] = mapped_column(
        SQLEnum(ContributionType), nullable=False, index=True
    )
    modality: Mapped[Optional[ModalityType]] = mapped_column(SQLEnum(ModalityType), index=True)
    architecture_family: Mapped[Optional[ArchitectureFamily]] = mapped_column(SQLEnum(ArchitectureFamily))
    model_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    
    # Status
    status_label: Mapped[StatusLabel] = mapped_column(
        SQLEnum(StatusLabel), default=StatusLabel.NEW, index=True
    )
    is_official_code: Mapped[bool] = mapped_column(Boolean, default=False)
    is_unofficial_reimplementation: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # GitHub metadata
    github_stars: Mapped[Optional[int]] = mapped_column(Integer)
    github_forks: Mapped[Optional[int]] = mapped_column(Integer)
    github_last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    github_language: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Scoring
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    recency_score: Mapped[float] = mapped_column(Float, default=0.0)
    code_availability_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    clarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Conference/Journal info
    venue: Mapped[Optional[str]] = mapped_column(String(255))
    venue_type: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Deduplication
    canonical_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("research_items.id"))
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True)
    duplicate_ids: Mapped[Optional[List[int]]] = mapped_column(JSON)
    
    # Ingestion metadata
    ingestion_batch_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    last_ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    metadata_version: Mapped[int] = mapped_column(Integer, default=1)
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Relationships
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=research_item_categories,
        back_populates="research_items",
        lazy="selectin",
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=research_item_tags,
        back_populates="research_items",
        lazy="selectin",
    )
    user_items: Mapped[List["UserItem"]] = relationship(
        "UserItem",
        back_populates="research_item",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<ResearchItem(id={self.id}, title='{self.title[:50]}...')>"
