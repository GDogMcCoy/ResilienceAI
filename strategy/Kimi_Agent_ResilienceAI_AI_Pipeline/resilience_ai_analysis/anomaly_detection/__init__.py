"""
ResilienceAI Anomaly Detection Module

Comprehensive anomaly detection framework including:
- Statistical methods (Z-Score, IQR, MAD)
- Machine learning (Isolation Forest, One-Class SVM)
- Deep learning (Autoencoders, VAE, LSTM)
- Clustering-based (K-Means, DBSCAN, LOF)
- Time series detection
- Real-time streaming
- Alert generation
- Visualization
"""

__version__ = "1.0.0"
__author__ = "ResilienceAI Engineering Team"

# Core components
from .architecture import (
    AnomalyType,
    AlertSeverity,
    AnomalyScore,
    DetectionConfig,
    BaseDetector,
    AnomalyDetectionPipeline
)

# Statistical detectors
from .statistical_detectors import (
    ZScoreDetector,
    ModifiedZScoreDetector,
    IQRDetector,
    GrubbsTestDetector,
    StatisticalEnsembleDetector,
    detect_univariate_outliers,
    detect_multivariate_outliers
)

# Isolation Forest
from .isolation_forest import (
    IsolationForestDetector,
    ExtendedIsolationForestDetector,
    IsolationForestOptimizer
)

# One-Class SVM
from .one_class_svm import (
    OneClassSVMDetector,
    NuOptimizedOneClassSVM,
    KernelAdaptiveOneClassSVM,
    IncrementalOneClassSVM
)

# Autoencoders
from .autoencoders import (
    AutoencoderDetector,
    VariationalAutoencoderDetector,
    LSTMAutoencoderDetector
)

# Clustering
from .clustering_detectors import (
    KMeansDistanceDetector,
    DBSCANDetector,
    LocalOutlierFactorDetector,
    HierarchicalClusteringDetector,
    ClusteringEnsembleDetector
)

# Time series
from .time_series import (
    TimeSeriesAnomalyDetector,
    StatisticalTimeSeriesDetector,
    ProphetStyleDetector,
    ChangePointDetector
)

# Real-time
from .realtime import (
    StreamingAnomalyDetector,
    AdaptiveThresholdDetector,
    EnsembleRealTimeDetector
)

# Scoring
from .scoring import (
    AnomalyScorer,
    MultiFactorScorer,
    TemporalScorer,
    ConfidenceEstimator,
    SeverityClassifier
)

# Alerts
from .alerts import (
    AlertChannel,
    Alert,
    AlertRule,
    AlertManager
)

# Visualization
from .visualization import (
    AnomalyVisualizer,
    RealTimeDashboard
)

# Integration
from .integration import (
    ResilienceAIIntegration,
    create_resilience_ai_anomaly_detection
)

# Performance
from .performance import (
    PerformanceMetrics,
    PerformanceOptimizer,
    ModelSelector
)

# Testing
from .testing import (
    AnomalyDetectionTester,
    UnitTestSuite,
    run_tests
)

__all__ = [
    # Version
    '__version__',
    '__author__',
    
    # Architecture
    'AnomalyType',
    'AlertSeverity',
    'AnomalyScore',
    'DetectionConfig',
    'BaseDetector',
    'AnomalyDetectionPipeline',
    
    # Statistical
    'ZScoreDetector',
    'ModifiedZScoreDetector',
    'IQRDetector',
    'GrubbsTestDetector',
    'StatisticalEnsembleDetector',
    'detect_univariate_outliers',
    'detect_multivariate_outliers',
    
    # Isolation Forest
    'IsolationForestDetector',
    'ExtendedIsolationForestDetector',
    'IsolationForestOptimizer',
    
    # One-Class SVM
    'OneClassSVMDetector',
    'NuOptimizedOneClassSVM',
    'KernelAdaptiveOneClassSVM',
    'IncrementalOneClassSVM',
    
    # Autoencoders
    'AutoencoderDetector',
    'VariationalAutoencoderDetector',
    'LSTMAutoencoderDetector',
    
    # Clustering
    'KMeansDistanceDetector',
    'DBSCANDetector',
    'LocalOutlierFactorDetector',
    'HierarchicalClusteringDetector',
    'ClusteringEnsembleDetector',
    
    # Time Series
    'TimeSeriesAnomalyDetector',
    'StatisticalTimeSeriesDetector',
    'ProphetStyleDetector',
    'ChangePointDetector',
    
    # Real-time
    'StreamingAnomalyDetector',
    'AdaptiveThresholdDetector',
    'EnsembleRealTimeDetector',
    
    # Scoring
    'AnomalyScorer',
    'MultiFactorScorer',
    'TemporalScorer',
    'ConfidenceEstimator',
    'SeverityClassifier',
    
    # Alerts
    'AlertChannel',
    'Alert',
    'AlertRule',
    'AlertManager',
    
    # Visualization
    'AnomalyVisualizer',
    'RealTimeDashboard',
    
    # Integration
    'ResilienceAIIntegration',
    'create_resilience_ai_anomaly_detection',
    
    # Performance
    'PerformanceMetrics',
    'PerformanceOptimizer',
    'ModelSelector',
    
    # Testing
    'AnomalyDetectionTester',
    'UnitTestSuite',
    'run_tests'
]
