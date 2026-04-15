"""Bootstrap service for default taxonomy and starter content."""
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
    ResearchItem,
    SourceType,
    StatusLabel,
)
from app.models.tag import Tag


DEFAULT_CATEGORIES = [
    {"name": "Classification", "slug": "classification", "description": "Image classification and recognition", "display_order": 1},
    {"name": "Object Detection", "slug": "detection", "description": "Object detection and localization", "display_order": 2},
    {"name": "Semantic Segmentation", "slug": "segmentation", "description": "Pixel-level image segmentation", "display_order": 3},
    {"name": "Instance Segmentation", "slug": "instance-segmentation", "description": "Instance-level segmentation and masks", "display_order": 4},
    {"name": "Image Generation", "slug": "generation", "description": "Image synthesis and generation", "display_order": 5},
    {"name": "Diffusion Models", "slug": "diffusion", "description": "Diffusion-based generative models", "display_order": 6},
    {"name": "Vision Transformers", "slug": "vision-transformers", "description": "Transformer architectures for vision", "display_order": 7},
    {"name": "Self-Supervised Learning", "slug": "self-supervised", "description": "Self-supervised and unsupervised methods", "display_order": 8},
    {"name": "Multimodal", "slug": "multimodal", "description": "Vision-language and multimodal models", "display_order": 9},
    {"name": "Medical Imaging", "slug": "medical", "description": "Medical and clinical imaging", "display_order": 10},
    {"name": "3D Vision", "slug": "3d-vision", "description": "3D vision and point clouds", "display_order": 11},
    {"name": "Video Understanding", "slug": "video", "description": "Video analysis and understanding", "display_order": 12},
    {"name": "Image Restoration", "slug": "restoration", "description": "Image denoising, deblurring, and restoration", "display_order": 13},
    {"name": "Super-Resolution", "slug": "super-resolution", "description": "Image upscaling and super-resolution", "display_order": 14},
    {"name": "Representation Learning", "slug": "representation", "description": "Feature learning and representations", "display_order": 15},
]


DEFAULT_TAGS = [
    {"name": "PyTorch", "slug": "pytorch", "color": "#EE4C2C"},
    {"name": "TensorFlow", "slug": "tensorflow", "color": "#FF6F00"},
    {"name": "JAX", "slug": "jax", "color": "#1A73E8"},
    {"name": "Self-Supervised", "slug": "self-supervised", "color": "#10B981"},
    {"name": "Supervised", "slug": "supervised", "color": "#3B82F6"},
    {"name": "Few-Shot", "slug": "few-shot", "color": "#8B5CF6"},
    {"name": "Zero-Shot", "slug": "zero-shot", "color": "#EC4899"},
    {"name": "Transfer Learning", "slug": "transfer-learning", "color": "#F59E0B"},
    {"name": "Real-Time", "slug": "real-time", "color": "#EF4444"},
    {"name": "Edge Computing", "slug": "edge", "color": "#6366F1"},
    {"name": "Open Source", "slug": "open-source", "color": "#22C55E"},
    {"name": "SOTA", "slug": "sota", "color": "#F97316"},
    {"name": "CNN", "slug": "cnn", "color": "#14B8A6"},
    {"name": "Transformer", "slug": "transformer", "color": "#8B5CF6"},
    {"name": "Diffusion", "slug": "diffusion", "color": "#06B6D4"},
    {"name": "GAN", "slug": "gan", "color": "#D946EF"},
]


SAMPLE_ITEMS = [
    {
        "title": "Vision Transformer: An Image is Worth 16x16 Words",
        "slug": "vision-transformer-image-worth-16x16-words-abc123",
        "source": SourceType.ARXIV,
        "source_id": "2010.11929",
        "published_date": datetime.utcnow() - timedelta(days=5),
        "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov"],
        "abstract": "Pure transformers applied to sequences of image patches can achieve strong image classification performance when pre-trained at scale.",
        "short_summary": "Introduces ViT, a transformer-first architecture that changed the direction of modern vision backbones.",
        "full_summary": "Vision Transformer showed that patch-based transformers could compete with and often surpass CNNs when pre-trained on large datasets.",
        "why_it_matters": "A foundational image-AI architecture that still shapes modern research.",
        "paper_url": "https://arxiv.org/pdf/2010.11929.pdf",
        "abstract_url": "https://arxiv.org/abs/2010.11929",
        "github_url": "https://github.com/google-research/vision_transformer",
        "contribution_type": ContributionType.PAPER,
        "modality": ModalityType.IMAGE,
        "architecture_family": ArchitectureFamily.TRANSFORMER,
        "model_name": "ViT",
        "status_label": StatusLabel.TRENDING,
        "is_official_code": True,
        "github_stars": 28450,
        "relevance_score": 95.0,
        "recency_score": 0.7,
        "code_availability_score": 0.8,
        "source_quality_score": 0.8,
        "impact_score": 0.95,
        "clarity_score": 0.9,
        "venue": "ICLR",
        "raw_metadata": {"bootstrap": True},
    },
    {
        "title": "Stable Diffusion: High-Resolution Image Synthesis with Latent Diffusion Models",
        "slug": "stable-diffusion-latent-diffusion-models-def456",
        "source": SourceType.ARXIV,
        "source_id": "2112.10752",
        "published_date": datetime.utcnow() - timedelta(days=3),
        "authors": ["Robin Rombach", "Andreas Blattmann", "Dominik Lorenz"],
        "abstract": "Latent diffusion models achieve strong image synthesis quality while remaining much more practical to run than pixel-space diffusion.",
        "short_summary": "A key generative image model that made high-quality synthesis broadly usable.",
        "full_summary": "Latent diffusion pushed image generation into mainstream developer workflows by reducing the compute cost of high-resolution synthesis.",
        "why_it_matters": "A landmark model for modern image generation workflows.",
        "paper_url": "https://arxiv.org/pdf/2112.10752.pdf",
        "abstract_url": "https://arxiv.org/abs/2112.10752",
        "github_url": "https://github.com/CompVis/stable-diffusion",
        "contribution_type": ContributionType.MODEL,
        "modality": ModalityType.IMAGE,
        "architecture_family": ArchitectureFamily.DIFFUSION,
        "model_name": "Stable Diffusion",
        "status_label": StatusLabel.TRENDING,
        "is_official_code": True,
        "github_stars": 75320,
        "relevance_score": 98.0,
        "recency_score": 0.9,
        "code_availability_score": 1.0,
        "source_quality_score": 0.8,
        "impact_score": 1.0,
        "clarity_score": 0.95,
        "venue": "CVPR",
        "raw_metadata": {"bootstrap": True},
    },
    {
        "title": "YOLOv8: Real-Time Object Detection",
        "slug": "yolov8-real-time-object-detection-ghi789",
        "source": SourceType.GITHUB,
        "source_id": "gh_yolov8",
        "published_date": datetime.utcnow() - timedelta(days=1),
        "authors": ["Ultralytics"],
        "abstract": "A fast and practical object detection stack with strong accuracy and deployment support.",
        "short_summary": "A production-friendly detector for daily computer vision work.",
        "full_summary": "YOLOv8 is a strong baseline for real-time detection, segmentation, and classification in applied image AI projects.",
        "why_it_matters": "A practical reference point for production image pipelines.",
        "github_url": "https://github.com/ultralytics/ultralytics",
        "contribution_type": ContributionType.MODEL,
        "modality": ModalityType.IMAGE,
        "architecture_family": ArchitectureFamily.CNN,
        "model_name": "YOLOv8",
        "status_label": StatusLabel.USEFUL_FOR_PRODUCTION,
        "is_official_code": True,
        "github_stars": 31200,
        "relevance_score": 92.0,
        "recency_score": 0.9,
        "code_availability_score": 1.0,
        "source_quality_score": 0.7,
        "impact_score": 0.92,
        "clarity_score": 0.9,
        "raw_metadata": {"bootstrap": True},
    },
    {
        "title": "Segment Anything Model (SAM)",
        "slug": "segment-anything-model-sam-jkl012",
        "source": SourceType.ARXIV,
        "source_id": "2304.02643",
        "published_date": datetime.utcnow() - timedelta(days=7),
        "authors": ["Alexander Kirillov", "Eric Mintun", "Nikhila Ravi"],
        "abstract": "A promptable segmentation foundation model trained with a large-scale data engine.",
        "short_summary": "A foundation model for promptable image segmentation.",
        "full_summary": "SAM popularized promptable zero-shot segmentation and became a building block for many image processing workflows.",
        "why_it_matters": "A major model for segmentation-first image tooling.",
        "paper_url": "https://arxiv.org/pdf/2304.02643.pdf",
        "abstract_url": "https://arxiv.org/abs/2304.02643",
        "github_url": "https://github.com/facebookresearch/segment-anything",
        "contribution_type": ContributionType.MODEL,
        "modality": ModalityType.IMAGE,
        "architecture_family": ArchitectureFamily.TRANSFORMER,
        "model_name": "SAM",
        "status_label": StatusLabel.TRENDING,
        "is_official_code": True,
        "github_stars": 45600,
        "relevance_score": 96.0,
        "recency_score": 0.7,
        "code_availability_score": 1.0,
        "source_quality_score": 0.8,
        "impact_score": 0.97,
        "clarity_score": 0.92,
        "venue": "ICCV",
        "raw_metadata": {"bootstrap": True},
    },
]


class BootstrapService:
    """Ensure the app has usable starter data on a fresh install."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> dict:
        """Create default categories/tags and starter items when needed."""
        categories_created = await self._ensure_categories()
        tags_created = await self._ensure_tags()
        items_created = await self._ensure_sample_items()
        await self.db.commit()
        return {
            "categories_created": categories_created,
            "tags_created": tags_created,
            "items_created": items_created,
        }

    async def _ensure_categories(self) -> int:
        created = 0
        for category_data in DEFAULT_CATEGORIES:
            existing = await self.db.execute(
                select(Category).where(Category.slug == category_data["slug"])
            )
            if existing.scalar_one_or_none():
                continue
            self.db.add(Category(**category_data))
            created += 1
        await self.db.flush()
        return created

    async def _ensure_tags(self) -> int:
        created = 0
        for tag_data in DEFAULT_TAGS:
            existing = await self.db.execute(
                select(Tag).where(Tag.slug == tag_data["slug"])
            )
            if existing.scalar_one_or_none():
                continue
            self.db.add(Tag(**tag_data))
            created += 1
        await self.db.flush()
        return created

    async def _ensure_sample_items(self) -> int:
        existing_items = await self.db.execute(select(ResearchItem.id).limit(1))
        if existing_items.scalar_one_or_none():
            return 0

        categories = {
            category.slug: category
            for category in (await self.db.execute(select(Category))).scalars().all()
        }
        tags = {
            tag.slug: tag
            for tag in (await self.db.execute(select(Tag))).scalars().all()
        }

        starter_links = {
            "vision-transformer-image-worth-16x16-words-abc123": {
                "categories": ["vision-transformers", "classification"],
                "tags": ["transformer", "open-source", "sota"],
            },
            "stable-diffusion-latent-diffusion-models-def456": {
                "categories": ["generation", "diffusion"],
                "tags": ["diffusion", "open-source", "pytorch"],
            },
            "yolov8-real-time-object-detection-ghi789": {
                "categories": ["detection"],
                "tags": ["cnn", "real-time", "open-source"],
            },
            "segment-anything-model-sam-jkl012": {
                "categories": ["segmentation", "vision-transformers"],
                "tags": ["transformer", "open-source", "sota"],
            },
        }

        created = 0
        for item_data in SAMPLE_ITEMS:
            item = ResearchItem(**item_data)
            links = starter_links.get(item.slug, {"categories": [], "tags": []})
            for category_slug in links["categories"]:
                category = categories.get(category_slug)
                if category:
                    item.categories.append(category)
                    category.item_count += 1
            for tag_slug in links["tags"]:
                tag = tags.get(tag_slug)
                if tag:
                    item.tags.append(tag)
                    tag.item_count += 1
            self.db.add(item)
            created += 1

        await self.db.flush()
        return created
