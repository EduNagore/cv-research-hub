"""Seed data script for initial database population."""
import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.category import Category
from app.models.tag import Tag
from app.models.research_item import ResearchItem, ContributionType, SourceType, StatusLabel, ModalityType, ArchitectureFamily


async def seed_categories(db: AsyncSession):
    """Seed categories."""
    categories = [
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
    
    for cat_data in categories:
        # Check if category exists
        from sqlalchemy import select
        result = await db.execute(select(Category).where(Category.slug == cat_data["slug"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    await db.commit()
    print(f"Seeded {len(categories)} categories")


async def seed_tags(db: AsyncSession):
    """Seed tags."""
    tags = [
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
    
    for tag_data in tags:
        from sqlalchemy import select
        result = await db.execute(select(Tag).where(Tag.slug == tag_data["slug"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            tag = Tag(**tag_data)
            db.add(tag)
    
    await db.commit()
    print(f"Seeded {len(tags)} tags")


async def seed_sample_items(db: AsyncSession):
    """Seed sample research items."""
    from sqlalchemy import select
    
    # Check if items already exist
    result = await db.execute(select(ResearchItem).limit(1))
    if result.scalar_one_or_none():
        print("Research items already exist, skipping")
        return
    
    sample_items = [
        {
            "title": "Vision Transformer: An Image is Worth 16x16 Words",
            "slug": "vision-transformer-image-worth-16x16-words-abc123",
            "source": SourceType.ARXIV,
            "source_id": "2010.11929",
            "published_date": datetime.utcnow() - timedelta(days=5),
            "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov"],
            "abstract": "While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. In vision, attention is either applied in conjunction with convolutional networks, or used to replace certain components of convolutional networks while keeping their overall structure in place. We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.",
            "short_summary": "Introduces Vision Transformer (ViT), a pure transformer architecture for image classification that achieves excellent results when pre-trained on large datasets.",
            "why_it_matters": "Demonstrates that transformers can work directly on images without CNNs, opening new research directions for vision architectures.",
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
            "venue": "ICLR",
        },
        {
            "title": "Stable Diffusion: High-Resolution Image Synthesis with Latent Diffusion Models",
            "slug": "stable-diffusion-latent-diffusion-models-def456",
            "source": SourceType.ARXIV,
            "source_id": "2112.10752",
            "published_date": datetime.utcnow() - timedelta(days=3),
            "authors": ["Robin Rombach", "Andreas Blattmann", "Dominik Lorenz"],
            "abstract": "High-resolution image synthesis with latent diffusion models. By decomposing the image formation process into a sequential application of denoising autoencoders, diffusion models (DMs) achieve state-of-the-art synthesis results on image data and beyond.",
            "short_summary": "Introduces latent diffusion models that achieve high-quality image generation while being computationally efficient by operating in latent space.",
            "why_it_matters": "Enables high-quality image generation on consumer hardware, democratizing access to generative AI.",
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
            "venue": "CVPR",
        },
        {
            "title": "YOLOv8: Real-Time Object Detection",
            "slug": "yolov8-real-time-object-detection-ghi789",
            "source": SourceType.GITHUB,
            "source_id": "gh_yolov8",
            "published_date": datetime.utcnow() - timedelta(days=1),
            "authors": ["Ultralytics"],
            "abstract": "YOLOv8 is the latest version of the YOLO (You Only Look Once) AI models developed by Ultralytics. It offers state-of-the-art performance in object detection, image classification, and instance segmentation tasks.",
            "short_summary": "A state-of-the-art, real-time object detection model with improved accuracy and speed over previous versions.",
            "why_it_matters": "Industry-standard for real-time object detection with excellent speed-accuracy trade-off.",
            "github_url": "https://github.com/ultralytics/ultralytics",
            "contribution_type": ContributionType.MODEL,
            "modality": ModalityType.IMAGE,
            "architecture_family": ArchitectureFamily.CNN,
            "model_name": "YOLOv8",
            "status_label": StatusLabel.USEFUL_FOR_PRODUCTION,
            "is_official_code": True,
            "github_stars": 31200,
            "relevance_score": 92.0,
        },
        {
            "title": "Segment Anything Model (SAM)",
            "slug": "segment-anything-model-sam-jkl012",
            "source": SourceType.ARXIV,
            "source_id": "2304.02643",
            "published_date": datetime.utcnow() - timedelta(days=7),
            "authors": ["Alexander Kirillov", "Eric Mintun", "Nikhila Ravi"],
            "abstract": "We introduce the Segment Anything (SA) project: a new task, model, and dataset for image segmentation. Using our efficient model in a data collection loop, we built the largest segmentation dataset to date.",
            "short_summary": "Introduces a foundation model for image segmentation that can segment any object in an image given various types of prompts.",
            "why_it_matters": "First foundation model for segmentation with zero-shot capabilities, enabling new interactive segmentation applications.",
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
            "venue": "ICCV",
        },
        {
            "title": "ImageNet Large Scale Visual Recognition Challenge",
            "slug": "imagenet-large-scale-visual-recognition-mno345",
            "source": SourceType.ARXIV,
            "source_id": "1409.0575",
            "published_date": datetime.utcnow() - timedelta(days=10),
            "authors": ["Olga Russakovsky", "Jia Deng", "Hao Su"],
            "abstract": "The ImageNet Large Scale Visual Recognition Challenge is a benchmark in object category classification and detection on hundreds of object categories and millions of images.",
            "short_summary": "The definitive benchmark dataset for large-scale image classification and object detection.",
            "why_it_matters": "The most influential dataset in computer vision history, driving progress in deep learning.",
            "paper_url": "https://arxiv.org/pdf/1409.0575.pdf",
            "abstract_url": "https://arxiv.org/abs/1409.0575",
            "contribution_type": ContributionType.DATASET,
            "modality": ModalityType.IMAGE,
            "status_label": StatusLabel.USEFUL_FOR_RESEARCH,
            "relevance_score": 88.0,
            "venue": "IJCV",
        },
    ]
    
    # Get categories and tags for association
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    
    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    
    for item_data in sample_items:
        item = ResearchItem(**item_data)
        
        # Associate categories based on content
        if "transformer" in item.title.lower():
            vit_cat = next((c for c in categories if c.slug == "vision-transformers"), None)
            if vit_cat:
                item.categories.append(vit_cat)
        
        if "diffusion" in item.title.lower() or "stable" in item.title.lower():
            diff_cat = next((c for c in categories if c.slug == "diffusion"), None)
            gen_cat = next((c for c in categories if c.slug == "generation"), None)
            if diff_cat:
                item.categories.append(diff_cat)
            if gen_cat:
                item.categories.append(gen_cat)
        
        if "detection" in item.title.lower() or "yolo" in item.title.lower():
            det_cat = next((c for c in categories if c.slug == "detection"), None)
            if det_cat:
                item.categories.append(det_cat)
        
        if "segment" in item.title.lower():
            seg_cat = next((c for c in categories if c.slug == "segmentation"), None)
            if seg_cat:
                item.categories.append(seg_cat)
        
        # Associate tags
        if "transformer" in item.title.lower():
            trans_tag = next((t for t in tags if t.slug == "transformer"), None)
            if trans_tag:
                item.tags.append(trans_tag)
        
        if item.github_url:
            oss_tag = next((t for t in tags if t.slug == "open-source"), None)
            if oss_tag:
                item.tags.append(oss_tag)
        
        db.add(item)
    
    await db.commit()
    print(f"Seeded {len(sample_items)} research items")


async def main():
    """Main seed function."""
    async with AsyncSessionLocal() as db:
        print("Seeding database...")
        await seed_categories(db)
        await seed_tags(db)
        await seed_sample_items(db)
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
