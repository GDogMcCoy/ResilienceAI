"""
Core Architecture for Anomaly Detection System

Provides base classes and abstractions for all anomaly detection components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    POINT = "point"                    # Single data point anomaly
    CONTEXTUAL = "contextual"          # Context-dependent anomaly
    COLLECTIVE = "collective"          # Sequence of anomalous points
    TEMPORAL = "temporal"              # Time-based pattern anomaly
    SPATIAL = "spatial"                # Spatial pattern anomaly


class AlertSeverity(Enum):
    """Severity levels for anomaly alerts."""
    CRITICAL = "critical"              # Immediate action required
    HIGH = "high"                      # Urgent attention needed
    MEDIUM = "medium"                  # Monitor closely
    LOW = "low"                        # Informational


@dataclass
class AnomalyScore:
    """Represents an anomaly detection result."""
    score: float                       # Anomaly score (0-1, higher = more anomalous)
    is_anomaly: bool                   # Whether this is classified as anomaly
    confidence: float                  # Confidence in the detection (0-1)
    anomaly_type: AnomalyType          # Type of anomaly detected
    severity: AlertSeverity            # Severity level
    timestamp: datetime                # When detected
    feature_contributions: Dict[str, float]  # Feature importance
    metadata: Dict[str, Any]           # Additional context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'is_anomaly': self.is_anomaly,
            'confidence': self.confidence,
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'feature_contributions': self.feature_contributions,
            'metadata': self.metadata
        }


@dataclass
class DetectionConfig:
    """Configuration for anomaly detection."""
    threshold: float = 0.5             # Anomaly threshold
    sensitivity: float = 0.8           # Detection sensitivity
    window_size: int = 100             # Sliding window size
    min_samples: int = 30              # Minimum samples for detection
    update_frequency: str = '1min'     # How often to update models
    enable_ensemble: bool = True       # Use ensemble scoring


class BaseDetector(ABC):
    """Abstract base class for all anomaly detectors."""
    
    def __init__(self, name: str, config: DetectionConfig):
        self.name = name
        self.config = config
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.training_stats: Dict[str, Any] = {}
        
    @abstractmethod
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'BaseDetector':
        """Fit the detector to training data."""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels (-1 for anomaly, 1 for normal)."""
        pass
    
    @abstractmethod
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores for samples."""
        pass
    
    def detect(self, X: np.ndarray, 
               feature_names: Optional[List[str]] = None) -> List[AnomalyScore]:
        """Full detection pipeline with detailed results."""
        if not self.is_fitted:
            raise RuntimeError(f"Detector {self.name} must be fitted before detection")
        
        scores = self.score_samples(X)
        predictions = self.predict(X)
        
        if feature_names:
            self.feature_names = feature_names
        
        results = []
        for i, (score, pred) in enumerate(zip(scores, predictions)):
            # Calculate feature contributions if possible
            feature_contribs = self._get_feature_contributions(X[i:i+1]) if hasattr(X, '__len__') else {}
            
            anomaly_score = AnomalyScore(
                score=float(score),
                is_anomaly=pred == -1,
                confidence=self._calculate_confidence(score),
                anomaly_type=self._determine_anomaly_type(X[i:i+1]),
                severity=self._determine_severity(score),
                timestamp=datetime.now(),
                feature_contributions=feature_contribs,
                metadata={'detector': self.name, 'index': i}
            )
            results.append(anomaly_score)
        
        return results
    
    def _calculate_confidence(self, score: float) -> float:
        """Calculate confidence based on distance from threshold."""
        threshold = self.config.threshold
        distance = abs(score - threshold)
        return min(1.0, distance * 2 + 0.5)
    
    def _determine_anomaly_type(self, X: np.ndarray) -> AnomalyType:
        """Determine the type of anomaly."""
        return AnomalyType.POINT
    
    def _determine_severity(self, score: float) -> AlertSeverity:
        """Determine alert severity based on score."""
        if score > 0.9:
            return AlertSeverity.CRITICAL
        elif score > 0.75:
            return AlertSeverity.HIGH
        elif score > 0.6:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Get feature contributions to anomaly score."""
        return {}


class AnomalyDetectionPipeline:
    """Main pipeline orchestrating multiple detectors."""
    
    def __init__(self, config: DetectionConfig = None):
        self.config = config or DetectionConfig()
        self.detectors: Dict[str, BaseDetector] = {}
        self.ensemble_weights: Dict[str, float] = {}
        self.alert_handlers: List[Callable] = []
        self.detection_history: List[AnomalyScore] = []
        
    def add_detector(self, detector: BaseDetector, weight: float = 1.0):
        """Add a detector to the pipeline."""
        self.detectors[detector.name] = detector
        self.ensemble_weights[detector.name] = weight
        logger.info(f"Added detector: {detector.name} with weight {weight}")
        
    def remove_detector(self, name: str):
        """Remove a detector from the pipeline."""
        if name in self.detectors:
            del self.detectors[name]
            del self.ensemble_weights[name]
            logger.info(f"Removed detector: {name}")
    
    def fit_all(self, X: np.ndarray, y: Optional[np.ndarray] = None):
        """Fit all detectors in the pipeline."""
        for name, detector in self.detectors.items():
            logger.info(f"Fitting detector: {name}")
            detector.fit(X, y)
    
    def detect(self, X: np.ndarray, 
               feature_names: Optional[List[str]] = None,
               use_ensemble: bool = True) -> Dict[str, List[AnomalyScore]]:
        """Run detection with all detectors."""
        results = {}
        
        for name, detector in self.detectors.items():
            try:
                detector_results = detector.detect(X, feature_names)
                results[name] = detector_results
            except Exception as e:
                logger.error(f"Detector {name} failed: {e}")
                results[name] = []
        
        if use_ensemble and self.config.enable_ensemble:
            results['ensemble'] = self._ensemble_score(results)
        
        # Store in history
        for detector_results in results.values():
            self.detection_history.extend(detector_results)
        
        return results
    
    def _ensemble_score(self, results: Dict[str, List[AnomalyScore]]) -> List[AnomalyScore]:
        """Combine scores from multiple detectors using weighted average."""
        if not results:
            return []
        
        # Get number of samples from first detector
        n_samples = len(list(results.values())[0])
        ensemble_results = []
        
        for i in range(n_samples):
            weighted_score = 0.0
            total_weight = 0.0
            all_confidences = []
            any_anomaly = False
            max_severity = AlertSeverity.LOW
            combined_contributions: Dict[str, List[float]] = {}
            
            for detector_name, detector_results in results.items():
                if i < len(detector_results):
                    result = detector_results[i]
                    weight = self.ensemble_weights.get(detector_name, 1.0)
                    weighted_score += result.score * weight
                    total_weight += weight
                    all_confidences.append(result.confidence)
                    any_anomaly = any_anomaly or result.is_anomaly
                    
                    # Track highest severity
                    severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, 
                                     AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                    if severity_order.index(result.severity) > severity_order.index(max_severity):
                        max_severity = result.severity
                    
                    # Aggregate feature contributions
                    for feature, contrib in result.feature_contributions.items():
                        if feature not in combined_contributions:
                            combined_contributions[feature] = []
                        combined_contributions[feature].append(contrib)
            
            # Calculate final ensemble score
            final_score = weighted_score / total_weight if total_weight > 0 else 0.5
            avg_confidence = np.mean(all_confidences) if all_confidences else 0.5
            
            # Average feature contributions
            avg_contributions = {
                f: np.mean(v) for f, v in combined_contributions.items()
            }
            
            ensemble_result = AnomalyScore(
                score=final_score,
                is_anomaly=final_score > self.config.threshold or any_anomaly,
                confidence=avg_confidence,
                anomaly_type=AnomalyType.POINT,
                severity=max_severity,
                timestamp=datetime.now(),
                feature_contributions=avg_contributions,
                metadata={'detector': 'ensemble', 'index': i, 
                         'contributing_detectors': list(results.keys())}
            )
            ensemble_results.append(ensemble_result)
        
        return ensemble_results
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler callback."""
        self.alert_handlers.append(handler)
    
    def process_alerts(self, results: Dict[str, List[AnomalyScore]]):
        """Process and send alerts for detected anomalies."""
        for detector_name, detector_results in results.items():
            for result in detector_results:
                if result.is_anomaly:
                    for handler in self.alert_handlers:
                        try:
                            handler(result)
                        except Exception as e:
                            logger.error(f"Alert handler failed: {e}")


# Export main classes
__all__ = [
    'AnomalyType', 'AlertSeverity', 'AnomalyScore', 'DetectionConfig',
    'BaseDetector', 'AnomalyDetectionPipeline'
]
