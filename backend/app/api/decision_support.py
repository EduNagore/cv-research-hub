"""Decision support API routes."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.decision_support import DecisionRequest, DecisionResponse, Recommendation

router = APIRouter()


@router.post("/recommend", response_model=DecisionResponse)
async def get_recommendations(
    request: DecisionRequest,
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """Get recommendations based on user requirements."""
    
    # Build task summary
    task_summary = f"{request.task_type} on {request.dataset_size} dataset of {request.image_type} images"
    
    # Initialize recommendations list
    primary_recommendations = []
    alternative_approaches = []
    
    # Task-specific logic
    if request.task_type.lower() in ["classification", "image classification"]:
        if request.accuracy_priority == "speed":
            primary_recommendations.append(Recommendation(
                approach_family="Efficient CNNs (MobileNet, EfficientNet-Lite)",
                description="Lightweight convolutional networks optimized for speed",
                recommended_models=["MobileNetV3", "EfficientNet-Lite0", "ShuffleNetV2"],
                relevant_papers=[],
                strengths=["Fast inference", "Low memory footprint", "Mobile-friendly"],
                limitations=["Lower accuracy than large models", "Limited transfer learning"],
                practical_notes="Best for real-time applications and edge deployment",
                suitability_score=0.9,
            ))
        elif request.accuracy_priority == "accuracy":
            primary_recommendations.append(Recommendation(
                approach_family="Vision Transformers & Large CNNs",
                description="High-capacity models for maximum accuracy",
                recommended_models=["ViT-Huge", "Swin Transformer", "ConvNeXt-XL", "EfficientNetV2-XL"],
                relevant_papers=[],
                strengths=["State-of-the-art accuracy", "Excellent transfer learning"],
                limitations=["High compute requirements", "Long training time", "Large memory needs"],
                practical_notes="Use with large datasets and sufficient compute resources",
                suitability_score=0.95,
            ))
        else:  # balanced
            primary_recommendations.append(Recommendation(
                approach_family="Modern Efficient Architectures",
                description="Balanced accuracy and efficiency",
                recommended_models=["EfficientNetV2-S/M", "ConvNeXt-T/S", "DeiT-Small"],
                relevant_papers=[],
                strengths=["Good accuracy-efficiency trade-off", "Well-supported"],
                limitations=["Not the fastest or most accurate"],
                practical_notes="Good default choice for most applications",
                suitability_score=0.85,
            ))
        
        # Alternative
        alternative_approaches.append(Recommendation(
            approach_family="Self-Supervised Learning",
            description="Leverage unlabeled data for better representations",
            recommended_models=["DINO", "MAE", "SimCLR"],
            relevant_papers=[],
            strengths=["Better with limited labels", "Improved generalization"],
            limitations=["Requires pre-training", "More complex pipeline"],
            practical_notes="Consider when annotation is expensive",
            suitability_score=0.7,
        ))
    
    elif request.task_type.lower() in ["detection", "object detection"]:
        if request.real_time_required:
            primary_recommendations.append(Recommendation(
                approach_family="Single-Stage Detectors",
                description="Fast one-pass detection architectures",
                recommended_models=["YOLOv8", "YOLO-NAS", "RT-DETR", "SSD"],
                relevant_papers=[],
                strengths=["Real-time performance", "Good accuracy-speed balance"],
                limitations=["Lower accuracy than two-stage on small objects"],
                practical_notes="Industry standard for real-time applications",
                suitability_score=0.92,
            ))
        else:
            primary_recommendations.append(Recommendation(
                approach_family="Transformer-Based Detectors",
                description="Attention-based detection with superior accuracy",
                recommended_models=["DETR", "Deformable DETR", "DINO-DETR"],
                relevant_papers=[],
                strengths=["Excellent accuracy", "Global context", "No NMS needed"],
                limitations=["Slower training", "Higher memory requirements"],
                practical_notes="Best for accuracy-critical applications",
                suitability_score=0.88,
            ))
    
    elif request.task_type.lower() in ["segmentation", "semantic segmentation"]:
        if request.dimensionality == "3d":
            primary_recommendations.append(Recommendation(
                approach_family="3D CNN Segmentation",
                description="Volumetric segmentation networks",
                recommended_models=["3D U-Net", "V-Net", "nnU-Net"],
                relevant_papers=[],
                strengths=["Proven for 3D medical imaging", "Good spatial coherence"],
                limitations=["High memory usage", "Slow inference"],
                practical_notes="Standard for medical 3D segmentation",
                suitability_score=0.9,
            ))
        else:
            primary_recommendations.append(Recommendation(
                approach_family="Modern Segmentation Architectures",
                description="State-of-the-art 2D segmentation",
                recommended_models=["Mask2Former", "OneFormer", "SegFormer", "U-Net++"],
                relevant_papers=[],
                strengths=["High accuracy", "Multiple scale handling"],
                limitations=["Can be computationally intensive"],
                practical_notes="Choose based on speed/accuracy needs",
                suitability_score=0.87,
            ))
    
    elif request.task_type.lower() in ["generation", "image generation"]:
        primary_recommendations.append(Recommendation(
            approach_family="Diffusion Models",
            description="State-of-the-art generative models",
            recommended_models=["Stable Diffusion", "DALL-E", "Imagen", "Midjourney-style models"],
            relevant_papers=[],
            strengths=["Highest quality generation", "Controllable generation"],
            limitations=["Slow sampling", "High compute for training"],
            practical_notes="Use pre-trained models when possible",
            suitability_score=0.93,
        ))
        
        alternative_approaches.append(Recommendation(
            approach_family="GANs",
            description="Generative Adversarial Networks",
            recommended_models=["StyleGAN3", "BigGAN", "CycleGAN"],
            relevant_papers=[],
            strengths=["Fast generation", "Good for specific domains"],
            limitations=["Training instability", "Mode collapse"],
            practical_notes="Consider for domain-specific generation",
            suitability_score=0.75,
        ))
    
    # Medical imaging specific
    if request.image_type in ["medical", "histopathology", "dermatology"]:
        primary_recommendations.insert(0, Recommendation(
            approach_family="Medical Imaging Specialized",
            description="Architectures designed for medical images",
            recommended_models=["nnU-Net", "TransUNet", "Swin-UNETR", "MedSAM"],
            relevant_papers=[],
            strengths=["Optimized for medical data", "Handles class imbalance", "Robust augmentation"],
            limitations=["May need domain adaptation", "Specialized preprocessing required"],
            practical_notes="Always validate with medical experts",
            suitability_score=0.95,
        ))
    
    # Data preparation tips
    data_preparation_tips = [
        f"Use appropriate augmentation for {request.image_type} images",
        "Normalize based on dataset statistics",
        "Consider class balancing techniques" if request.annotation_amount != "abundant" else "Leverage abundant annotations",
        "Use cross-validation for robust evaluation",
    ]
    
    if request.dataset_size == "small":
        data_preparation_tips.extend([
            "Use aggressive data augmentation",
            "Consider transfer learning from large pre-trained models",
            "Use techniques like mixup and cutmix",
        ])
    
    # Training considerations
    training_considerations = [
        "Use learning rate scheduling",
        "Monitor for overfitting with validation set",
        "Use mixed precision training for speed",
    ]
    
    if request.compute_budget == "limited":
        training_considerations.extend([
            "Use gradient accumulation",
            "Consider knowledge distillation",
            "Use smaller batch sizes",
        ])
    
    # Evaluation metrics
    evaluation_metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    
    if request.task_type.lower() in ["detection", "segmentation"]:
        evaluation_metrics.extend(["mAP", "IoU"])
    
    if request.image_type in ["medical", "histopathology"]:
        evaluation_metrics.extend(["Sensitivity", "Specificity", "AUC-ROC"])
    
    # Suggested reading
    suggested_reading = [
        {"title": "Recent advances in " + request.task_type, "url": "#"},
        {"title": "Best practices for " + request.image_type + " analysis", "url": "#"},
    ]
    
    # Trade-offs summary
    trade_offs_summary = f"""
    For {request.task_type} on {request.dataset_size} {request.image_type} dataset:
    - Primary focus: {'Speed' if request.real_time_required else 'Accuracy' if request.accuracy_priority == 'accuracy' else 'Balanced approach'}
    - Annotation needs: {request.annotation_amount}
    - Compute requirements: {request.compute_budget or 'moderate'}
    - Recommended to start with: {primary_recommendations[0].approach_family if primary_recommendations else 'Standard architectures'}
    """
    
    return DecisionResponse(
        task_summary=task_summary,
        primary_recommendations=primary_recommendations,
        alternative_approaches=alternative_approaches,
        data_preparation_tips=data_preparation_tips,
        training_considerations=training_considerations,
        evaluation_metrics=evaluation_metrics,
        suggested_reading=suggested_reading,
        useful_repositories=[],
        trade_offs_summary=trade_offs_summary,
    )


@router.get("/tasks")
async def get_supported_tasks():
    """Get list of supported tasks for decision support."""
    return {
        "tasks": [
            "classification",
            "detection",
            "segmentation",
            "instance segmentation",
            "generation",
            "super-resolution",
            "restoration",
            "3d reconstruction",
            "video understanding",
        ],
        "image_types": [
            "natural",
            "medical",
            "histopathology",
            "dermatology",
            "satellite",
            "industrial",
        ],
        "dataset_sizes": ["small", "medium", "large"],
        "annotation_amounts": ["none", "limited", "moderate", "abundant"],
    }
