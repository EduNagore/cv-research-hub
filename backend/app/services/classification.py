"""Classification service for categorizing research items."""
import re
from typing import Dict, List, Optional

from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
)


class ClassificationService:
    """Service for classifying research items."""

    CATEGORY_SLUG_MAP = {
        "classification": "classification",
        "detection": "detection",
        "segmentation": "segmentation",
        "generation": "generation",
        "super_resolution": "super-resolution",
        "restoration": "restoration",
        "3d_vision": "3d-vision",
        "video": "video",
        "multimodal": "multimodal",
        "medical": "medical",
        "histopathology": "medical",
        "dermatology": "medical",
    }
    
    # Keywords for classification
    TASK_KEYWORDS = {
        "classification": ["classification", "classifier", "categorization", "recognition"],
        "detection": ["detection", "detect", "object detection", "yolo", "rcnn", "faster r-cnn"],
        "segmentation": ["segmentation", "segment", "semantic segmentation", "instance segmentation"],
        "generation": ["generation", "generative", "synthesis", "synthesizing", "diffusion", "gan"],
        "super_resolution": ["super-resolution", "super resolution", "upsampling", "upscaling"],
        "restoration": ["restoration", "denoising", "deblurring", "inpainting"],
        "3d_vision": ["3d", "point cloud", "depth estimation", "nerf", "volumetric"],
        "video": ["video", "temporal", "frame", "action recognition"],
        "multimodal": ["multimodal", "vision-language", "clip", "vlm", "text-image"],
        "medical": ["medical", "clinical", "healthcare", "diagnosis", "radiology"],
        "histopathology": ["histopathology", "pathology", "histology", "wsi"],
        "dermatology": ["dermatology", "skin", "dermoscopy"],
    }
    
    ARCHITECTURE_KEYWORDS = {
        "transformer": ["transformer", "vit", "swin", "detr", "bert", "attention"],
        "cnn": ["cnn", "convolutional", "resnet", "efficientnet", "mobilenet", "vgg"],
        "diffusion": ["diffusion", "ddpm", "stable diffusion", "score-based"],
        "gan": ["gan", "generative adversarial", "stylegan", "discriminator"],
        "autoencoder": ["autoencoder", "vae", "variational", "encoder-decoder"],
        "mlp": ["mlp", "multilayer perceptron", "feedforward"],
    }
    
    CONTRIBUTION_KEYWORDS = {
        "model": ["model", "architecture", "network", "backbone", "framework"],
        "benchmark": ["benchmark", "evaluation", "comparison", "leaderboard"],
        "dataset": ["dataset", "corpus", "collection", "benchmark dataset"],
        "survey": ["survey", "review", "overview", "taxonomy"],
        "library": ["library", "toolkit", "framework", "package", "toolbox"],
    }
    
    def __init__(self):
        pass
    
    async def classify(
        self,
        title: str,
        abstract: str,
    ) -> Dict:
        """Classify a research item based on title and abstract."""
        text = f"{title} {abstract}".lower()
        
        # Determine categories
        categories = self._determine_categories(text)
        
        # Determine modality
        modality = self._determine_modality(text)
        
        # Determine architecture family
        architecture = self._determine_architecture(text)
        
        # Determine contribution type
        contribution_type = self._determine_contribution_type(text)
        
        # Extract model name
        model_name = self._extract_model_name(title, text)
        
        # Generate summaries
        short_summary = self._generate_short_summary(title, abstract)
        full_summary = self._generate_full_summary(title, abstract)
        why_it_matters = self._generate_why_it_matters(text, categories)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        return {
            "categories": categories,
            "tags": tags,
            "modality": modality,
            "architecture_family": architecture,
            "contribution_type": contribution_type,
            "model_name": model_name,
            "short_summary": short_summary,
            "full_summary": full_summary,
            "why_it_matters": why_it_matters,
        }
    
    def _determine_categories(self, text: str) -> List[str]:
        """Determine categories based on keywords."""
        categories = []
        
        for category, keywords in self.TASK_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                category_slug = self.CATEGORY_SLUG_MAP.get(category)
                if category_slug and category_slug not in categories:
                    categories.append(category_slug)

        if "transformer" in text or "vit" in text or "swin" in text:
            categories.append("vision-transformers")
        if "diffusion" in text:
            categories.append("diffusion")
        if "self-supervised" in text or "unsupervised" in text:
            categories.append("self-supervised")
        if "representation learning" in text:
            categories.append("representation")
        
        # Default to general if no match
        if not categories:
            categories.append("classification")
        
        # preserve insertion order and uniqueness
        return list(dict.fromkeys(categories))
    
    def _determine_modality(self, text: str) -> Optional[ModalityType]:
        """Determine modality type."""
        if any(kw in text for kw in ["histopathology", "pathology", "histology"]):
            return ModalityType.HISTOPATHOLOGY
        elif any(kw in text for kw in ["dermatology", "skin", "dermoscopy"]):
            return ModalityType.DERMATOLOGY
        elif any(kw in text for kw in ["medical", "clinical", "radiology", "mri", "ct scan"]):
            return ModalityType.MEDICAL
        elif any(kw in text for kw in ["3d", "point cloud", "volumetric", "nerf"]):
            return ModalityType.THREE_D
        elif any(kw in text for kw in ["video", "temporal", "frame sequence"]):
            return ModalityType.VIDEO
        elif any(kw in text for kw in ["multimodal", "vision-language", "text-image", "clip"]):
            return ModalityType.MULTIMODAL
        else:
            return ModalityType.IMAGE
    
    def _determine_architecture(self, text: str) -> Optional[ArchitectureFamily]:
        """Determine architecture family."""
        scores = {}
        
        for arch, keywords in self.ARCHITECTURE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[arch] = score
        
        if scores:
            return ArchitectureFamily(max(scores, key=scores.get))
        
        return ArchitectureFamily.OTHER
    
    def _determine_contribution_type(self, text: str) -> ContributionType:
        """Determine contribution type."""
        scores = {}
        
        for contrib_type, keywords in self.CONTRIBUTION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[contrib_type] = score
        
        if scores:
            return ContributionType(max(scores, key=scores.get))
        
        return ContributionType.PAPER
    
    def _extract_model_name(self, title: str, text: str) -> Optional[str]:
        """Extract model name from title."""
        # Common patterns for model names
        patterns = [
            r'([A-Z][a-zA-Z]*(?:Net|Former|ViT|DETR|YOLO|GAN|Diffusion|CLIP))\s*:',
            r'([A-Z][a-zA-Z]*(?:Net|Former|ViT|DETR|YOLO|GAN|Diffusion|CLIP))\s+',
            r'^(\w+(?:Net|Former|ViT|DETR|YOLO))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_short_summary(self, title: str, abstract: str) -> str:
        """Generate a short summary (2-4 lines)."""
        if not abstract:
            return title
        
        # Take first 2-3 sentences
        sentences = abstract.split(".")
        summary_sentences = []
        char_count = 0
        
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence:
                summary_sentences.append(sentence)
                char_count += len(sentence)
                if char_count > 300:
                    break
        
        return ". ".join(summary_sentences) + "." if summary_sentences else abstract[:300]
    
    def _generate_full_summary(self, title: str, abstract: str) -> str:
        """Generate a full summary."""
        if not abstract:
            return title
        
        # Use the full abstract but clean it up
        summary = abstract.strip()
        
        # Ensure it ends with a period
        if not summary.endswith("."):
            summary += "."
        
        return summary
    
    def _generate_why_it_matters(self, text: str, categories: List[str]) -> str:
        """Generate 'why it matters' explanation."""
        reasons = []
        
        if "transformer" in text:
            reasons.append("Leverages attention mechanisms for better performance")
        
        if "diffusion" in text or "gan" in text:
            reasons.append("Advances generative modeling capabilities")
        
        if any(c in ["detection", "segmentation"] for c in categories):
            reasons.append("Improves visual understanding and scene parsing")
        
        if "medical" in text or "clinical" in text:
            reasons.append("Has potential healthcare applications")
        
        if "efficient" in text or "lightweight" in text:
            reasons.append("Enables deployment on resource-constrained devices")
        
        if "self-supervised" in text or "unsupervised" in text:
            reasons.append("Reduces dependency on labeled data")
        
        if not reasons:
            reasons.append("Contributes to advancing computer vision research")
        
        return " ".join(reasons)
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        tags = set()
        
        # Common CV/ML tags
        common_tags = {
            "pytorch": "PyTorch",
            "tensorflow": "TensorFlow",
            "jax": "JAX",
            "self-supervised": "Self-Supervised",
            "supervised": "Supervised",
            "unsupervised": "Unsupervised",
            "few-shot": "Few-Shot",
            "zero-shot": "Zero-Shot",
            "transfer learning": "Transfer Learning",
            "fine-tuning": "Fine-Tuning",
            "real-time": "Real-Time",
            "edge": "Edge Computing",
            "open source": "Open Source",
            "state-of-the-art": "SOTA",
        }
        
        for keyword, tag in common_tags.items():
            if keyword in text:
                tags.add(tag)
        
        return list(tags)
