"""
ResilienceAI Self-Improvement System

A comprehensive self-improving platform for continuous learning and optimization.

Components:
- Feedback Collection: Explicit and implicit user feedback
- Quality Evaluation: ML-powered response quality assessment
- Metrics Tracking: Comprehensive performance monitoring
- A/B Testing: Controlled experimentation framework
- Model Retraining: Automated model improvement pipeline
- Hyperparameter Optimization: Automated tuning
- Feature Importance: Model explainability
- Satisfaction Tracking: User experience measurement
- Learning Pipeline: Continuous improvement workflow
- Adaptation Engine: Dynamic system behavior
"""

from .feedback_collector import (
    ExplicitFeedbackCollector,
    ImplicitFeedbackCollector,
    FeedbackType,
    FeedbackCategory,
    ExplicitFeedback,
    InteractionSignals
)

from .quality_evaluator import (
    MLQualityEvaluator,
    QualityDimensions,
    QualityEvaluation
)

from .metrics_tracker import (
    MetricsTracker,
    ModelPerformanceMetrics,
    SystemHealthMetrics,
    UserExperienceMetrics
)

from .ab_testing import (
    ABTestingFramework,
    Experiment,
    Variant,
    ExperimentStatus,
    ExperimentType
)

from .model_retrainer import (
    AutomatedModelRetrainer,
    ModelVersion,
    RetrainTrigger
)

__version__ = "1.0.0"
__all__ = [
    # Feedback Collection
    "ExplicitFeedbackCollector",
    "ImplicitFeedbackCollector",
    "FeedbackType",
    "FeedbackCategory",
    "ExplicitFeedback",
    "InteractionSignals",
    
    # Quality Evaluation
    "MLQualityEvaluator",
    "QualityDimensions",
    "QualityEvaluation",
    
    # Metrics Tracking
    "MetricsTracker",
    "ModelPerformanceMetrics",
    "SystemHealthMetrics",
    "UserExperienceMetrics",
    
    # A/B Testing
    "ABTestingFramework",
    "Experiment",
    "Variant",
    "ExperimentStatus",
    "ExperimentType",
    
    # Model Retraining
    "AutomatedModelRetrainer",
    "ModelVersion",
    "RetrainTrigger",
]
