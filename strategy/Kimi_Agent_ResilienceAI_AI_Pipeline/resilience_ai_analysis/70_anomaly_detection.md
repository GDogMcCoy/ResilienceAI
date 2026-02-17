# Comprehensive Anomaly Detection System for ResilienceAI

## Executive Summary

This document provides a comprehensive anomaly detection framework for ResilienceAI, covering multiple detection methodologies, real-time processing capabilities, and integration strategies. The system is designed to detect unusual patterns in data quality, system behavior, and operational metrics with high accuracy and minimal false positives.

---

## Table of Contents

1. [Anomaly Detection Architecture](#1-anomaly-detection-architecture)
2. [Statistical Detection Methods](#2-statistical-detection-methods)
3. [Isolation Forest](#3-isolation-forest)
4. [One-Class SVM](#4-one-class-svm)
5. [Autoencoders](#5-autoencoders)
6. [Clustering-Based Detection](#6-clustering-based-detection)
7. [Time Series Anomaly Detection](#7-time-series-anomaly-detection)
8. [Real-Time Detection Pipeline](#8-real-time-detection-pipeline)
9. [Anomaly Scoring System](#9-anomaly-scoring-system)
10. [Alert Generation](#10-alert-generation)
11. [Visualization Dashboards](#11-visualization-dashboards)
12. [Integration Strategy](#12-integration-strategy)
13. [Performance Tuning](#13-performance-tuning)
14. [Testing Strategy](#14-testing-strategy)
15. [Implementation Priority](#15-implementation-priority)

---

## 1. Anomaly Detection Architecture

### 1.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANOMALY DETECTION SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Data       │───▶│  Feature     │───▶│  Anomaly     │                   │
│  │   Ingestion  │    │  Engineering │    │  Detectors   │                   │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                   │
│                                                  │                          │
│                       ┌──────────────────────────┼──────────────────┐       │
│                       ▼                          ▼                  ▼       │
│              ┌──────────────┐           ┌──────────────┐   ┌──────────────┐ │
│              │  Statistical │           │   Machine    │   │   Deep       │ │
│              │   Methods    │           │   Learning   │   │  Learning    │ │
│              └──────────────┘           └──────────────┘   └──────────────┘ │
│                       │                          │                  │       │
│                       └──────────────────────────┼──────────────────┘       │
│                                                  ▼                          │
│                                         ┌──────────────┐                    │
│                                         │   Ensemble   │                    │
│                                         │   Scoring    │                    │
│                                         └──────┬───────┘                    │
│                                                │                            │
│                       ┌────────────────────────┼──────────────────┐        │
│                       ▼                        ▼                  ▼        │
│              ┌──────────────┐         ┌──────────────┐   ┌──────────────┐  │
│              │    Alert     │         │Visualization │   │   Action     │  │
│              │  Generation  │         │  Dashboard   │   │   Engine     │  │
│              └──────────────┘         └──────────────┘   └──────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/architecture.py

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
```

---

## 2. Statistical Detection Methods

### 2.1 Z-Score Based Detection

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/statistical_detectors.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class ZScoreDetector(BaseDetector):
    """
    Z-Score based anomaly detection.
    
    Detects anomalies based on how many standard deviations
    a data point is from the mean.
    """
    
    def __init__(self, config: DetectionConfig = None, threshold_z: float = 3.0):
        super().__init__("ZScoreDetector", config or DetectionConfig())
        self.threshold_z = threshold_z
        self.means: np.ndarray = None
        self.stds: np.ndarray = None
        self.scaler = StandardScaler()
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'ZScoreDetector':
        """Fit the detector by computing mean and std."""
        X = np.asarray(X)
        self.scaler.fit(X)
        self.means = self.scaler.mean_
        self.stds = np.sqrt(self.scaler.var_)
        self.is_fitted = True
        
        # Store training statistics
        self.training_stats = {
            'means': self.means.tolist(),
            'stds': self.stds.tolist(),
            'n_samples': len(X)
        }
        
        logger.info(f"ZScoreDetector fitted on {len(X)} samples")
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores based on Z-scores."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Compute max absolute Z-score across features
        z_scores = np.abs(X_scaled)
        max_z_scores = np.max(z_scores, axis=1)
        
        # Normalize to 0-1 range
        scores = np.minimum(max_z_scores / self.threshold_z, 1.0)
        return scores
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Get per-feature Z-score contributions."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        z_scores = np.abs(X_scaled)[0]
        
        contributions = {}
        for i, score in enumerate(z_scores):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            contributions[feature_name] = float(score / self.threshold_z)
        
        return contributions


class ModifiedZScoreDetector(BaseDetector):
    """
    Modified Z-Score using Median Absolute Deviation (MAD).
    
    More robust to outliers than standard Z-score.
    """
    
    def __init__(self, config: DetectionConfig = None, threshold_mad: float = 3.5):
        super().__init__("ModifiedZScoreDetector", config or DetectionConfig())
        self.threshold_mad = threshold_mad
        self.medians: np.ndarray = None
        self.mads: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'ModifiedZScoreDetector':
        """Fit using median and MAD."""
        X = np.asarray(X)
        self.medians = np.median(X, axis=0)
        self.mads = np.median(np.abs(X - self.medians), axis=0)
        # Avoid division by zero
        self.mads = np.where(self.mads == 0, 1e-10, self.mads)
        self.is_fitted = True
        
        self.training_stats = {
            'medians': self.medians.tolist(),
            'mads': self.mads.tolist()
        }
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute modified Z-scores."""
        X = np.asarray(X)
        modified_z_scores = 0.6745 * (X - self.medians) / self.mads
        max_scores = np.max(np.abs(modified_z_scores), axis=1)
        return np.minimum(max_scores / self.threshold_mad, 1.0)


class IQRDetector(BaseDetector):
    """
    Interquartile Range (IQR) based anomaly detection.
    
    Detects outliers using the 1.5*IQR rule.
    """
    
    def __init__(self, config: DetectionConfig = None, multiplier: float = 1.5):
        super().__init__("IQRDetector", config or DetectionConfig())
        self.multiplier = multiplier
        self.q1: np.ndarray = None
        self.q3: np.ndarray = None
        self.iqr: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'IQRDetector':
        """Fit by computing quartiles."""
        X = np.asarray(X)
        self.q1 = np.percentile(X, 25, axis=0)
        self.q3 = np.percentile(X, 75, axis=0)
        self.iqr = self.q3 - self.q1
        self.is_fitted = True
        
        self.training_stats = {
            'q1': self.q1.tolist(),
            'q3': self.q3.tolist(),
            'iqr': self.iqr.tolist()
        }
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute IQR-based anomaly scores."""
        X = np.asarray(X)
        lower_bound = self.q1 - self.multiplier * self.iqr
        upper_bound = self.q3 + self.multiplier * self.iqr
        
        # Calculate distance from bounds
        below_lower = np.maximum(0, lower_bound - X)
        above_upper = np.maximum(0, X - upper_bound)
        
        # Normalize by IQR
        distance = (below_lower + above_upper) / (self.iqr + 1e-10)
        max_distance = np.max(distance, axis=1)
        
        return np.minimum(max_distance, 1.0)


class GrubbsTestDetector(BaseDetector):
    """
    Grubbs' test for outliers.
    
    Statistical test for detecting a single outlier in
    univariate data assuming normal distribution.
    """
    
    def __init__(self, config: DetectionConfig = None, alpha: float = 0.05):
        super().__init__("GrubbsTestDetector", config or DetectionConfig())
        self.alpha = alpha
        self.critical_values: Dict[int, float] = {}
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'GrubbsTestDetector':
        """Fit by computing critical values."""
        X = np.asarray(X)
        n = len(X)
        
        # Pre-compute critical values for common sample sizes
        for size in range(10, min(n + 100, 1000), 10):
            t_crit = stats.t.ppf(1 - self.alpha / (2 * size), size - 2)
            self.critical_values[size] = ((size - 1) / np.sqrt(size)) * \
                                          np.sqrt(t_crit**2 / (size - 2 + t_crit**2))
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute Grubbs test statistic."""
        X = np.asarray(X)
        n = len(X)
        
        scores = np.zeros(n)
        for i in range(n):
            # Leave-one-out Grubbs statistic
            x_without_i = np.delete(X, i, axis=0)
            mean = np.mean(x_without_i, axis=0)
            std = np.std(x_without_i, axis=0)
            
            # Max Z-score for this sample
            z_scores = np.abs((X[i] - mean) / (std + 1e-10))
            max_z = np.max(z_scores)
            
            # Get critical value
            critical = self.critical_values.get(
                n, self._compute_critical_value(n)
            )
            
            scores[i] = min(max_z / critical, 1.0) if critical > 0 else 0.5
        
        return scores
    
    def _compute_critical_value(self, n: int) -> float:
        """Compute Grubbs critical value."""
        t_crit = stats.t.ppf(1 - self.alpha / (2 * n), n - 2)
        return ((n - 1) / np.sqrt(n)) * np.sqrt(t_crit**2 / (n - 2 + t_crit**2))


class StatisticalEnsembleDetector(BaseDetector):
    """
    Ensemble of statistical detectors with voting.
    """
    
    def __init__(self, config: DetectionConfig = None):
        super().__init__("StatisticalEnsembleDetector", config or DetectionConfig())
        self.detectors = {
            'zscore': ZScoreDetector(config),
            'modified_zscore': ModifiedZScoreDetector(config),
            'iqr': IQRDetector(config)
        }
        self.weights = {
            'zscore': 0.4,
            'modified_zscore': 0.35,
            'iqr': 0.25
        }
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'StatisticalEnsembleDetector':
        """Fit all statistical detectors."""
        for name, detector in self.detectors.items():
            detector.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Combine scores from all detectors."""
        weighted_score = np.zeros(len(X))
        
        for name, detector in self.detectors.items():
            scores = detector.score_samples(X)
            weighted_score += scores * self.weights[name]
        
        return weighted_score


# Utility functions for statistical detection

def detect_univariate_outliers(series: pd.Series, 
                                method: str = 'zscore',
                                threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers in a univariate series.
    
    Args:
        series: Input data series
        method: 'zscore', 'modified_zscore', 'iqr', or 'grubbs'
        threshold: Detection threshold
    
    Returns:
        Boolean series indicating outliers
    """
    if method == 'zscore':
        z_scores = np.abs(stats.zscore(series.dropna()))
        outliers = z_scores > threshold
    
    elif method == 'modified_zscore':
        median = series.median()
        mad = np.median(np.abs(series - median))
        modified_z_scores = 0.6745 * (series - median) / mad
        outliers = np.abs(modified_z_scores) > threshold
    
    elif method == 'iqr':
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        outliers = (series < lower) | (series > upper)
    
    elif method == 'grubbs':
        # Simplified Grubbs for series
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        n = len(series)
        # Approximate critical value
        critical = threshold * np.sqrt((n - 2) / (n - 1 - threshold**2))
        outliers = z_scores > critical
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return outliers


def detect_multivariate_outliers(df: pd.DataFrame,
                                  columns: List[str] = None,
                                  method: str = 'mahalanobis',
                                  threshold: float = None) -> pd.Series:
    """
    Detect multivariate outliers.
    
    Args:
        df: Input DataFrame
        columns: Columns to use (None = all numeric)
        method: 'mahalanobis' or 'robust_mahalanobis'
        threshold: Detection threshold (None = auto)
    
    Returns:
        Boolean series indicating outliers
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    X = df[columns].dropna().values
    
    if method == 'mahalanobis':
        # Compute Mahalanobis distance
        mean = np.mean(X, axis=0)
        cov = np.cov(X.T)
        
        try:
            cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            cov_inv = np.linalg.pinv(cov)
        
        distances = []
        for x in X:
            diff = x - mean
            distance = np.sqrt(diff @ cov_inv @ diff)
            distances.append(distance)
        
        distances = np.array(distances)
        
        # Chi-square threshold
        if threshold is None:
            threshold = np.sqrt(stats.chi2.ppf(0.975, df=len(columns)))
        
        outliers = distances > threshold
    
    elif method == 'robust_mahalanobis':
        # Use minimum covariance determinant for robustness
        from sklearn.covariance import MinCovDet
        
        mcd = MinCovDet(random_state=42)
        mcd.fit(X)
        distances = mcd.mahalanobis(X)
        
        if threshold is None:
            threshold = np.sqrt(stats.chi2.ppf(0.975, df=len(columns)))
        
        outliers = distances > threshold**2
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Create result series with original index
    result = pd.Series(False, index=df.index)
    valid_idx = df[columns].dropna().index
    result.loc[valid_idx] = outliers
    
    return result


# Export classes
__all__ = [
    'ZScoreDetector', 'ModifiedZScoreDetector', 'IQRDetector',
    'GrubbsTestDetector', 'StatisticalEnsembleDetector',
    'detect_univariate_outliers', 'detect_multivariate_outliers'
]
```

---

## 3. Isolation Forest

### 3.1 Core Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/isolation_forest.py

import numpy as np
from sklearn.ensemble import IsolationForest as SklearnIsolationForest
from sklearn.tree import ExtraTreeRegressor
from typing import Dict, List, Optional, Tuple
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class IsolationForestDetector(BaseDetector):
    """
    Isolation Forest anomaly detection.
    
    Isolation Forest isolates anomalies instead of profiling normal data points.
    Anomalies are few and different, making them easier to isolate.
    
    Key advantages:
    - Linear time complexity
    - Low memory requirement
    - Handles high-dimensional data well
    - No assumptions about data distribution
    """
    
    def __init__(self, 
                 config: DetectionConfig = None,
                 n_estimators: int = 100,
                 max_samples: Union[int, float, str] = 'auto',
                 contamination: float = 0.1,
                 max_features: float = 1.0,
                 bootstrap: bool = False,
                 n_jobs: int = -1,
                 random_state: int = 42):
        super().__init__("IsolationForestDetector", config or DetectionConfig())
        
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.n_jobs = n_jobs
        self.random_state = random_state
        
        self.model: SklearnIsolationForest = None
        self.feature_importances_: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'IsolationForestDetector':
        """Fit the Isolation Forest model."""
        X = np.asarray(X)
        
        self.model = SklearnIsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples,
            contamination=self.contamination,
            max_features=self.max_features,
            bootstrap=self.bootstrap,
            n_jobs=self.n_jobs,
            random_state=self.random_state
        )
        
        self.model.fit(X)
        self.is_fitted = True
        
        # Estimate feature importances using tree depths
        self._compute_feature_importances(X)
        
        self.training_stats = {
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'contamination': self.contamination,
            'n_features': X.shape[1],
            'n_samples': len(X)
        }
        
        logger.info(f"IsolationForest fitted: {self.n_estimators} trees, "
                   f"contamination={self.contamination}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        return self.model.predict(X)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores.
        
        Returns scores in [0, 1] where higher values indicate
        more anomalous samples.
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        
        # Get anomaly scores from sklearn (negative values, lower = more anomalous)
        raw_scores = self.model.score_samples(X)
        
        # Convert to [0, 1] range (higher = more anomalous)
        # Normalize using training data statistics
        scores = 0.5 - raw_scores  # Shift so anomaly ~ 0.5+
        scores = np.clip(scores, 0, 1)
        
        return scores
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Raw anomaly scores (negative = more anomalous)."""
        return self.model.decision_function(X)
    
    def _compute_feature_importances(self, X: np.ndarray):
        """Estimate feature importances based on split frequencies."""
        importances = np.zeros(X.shape[1])
        
        for tree in self.model.estimators_:
            tree_importances = self._get_tree_feature_importances(tree, X.shape[1])
            importances += tree_importances
        
        importances /= self.n_estimators
        self.feature_importances_ = importances
    
    def _get_tree_feature_importances(self, tree, n_features: int) -> np.ndarray:
        """Extract feature importances from a single tree."""
        importances = np.zeros(n_features)
        
        # Get tree structure
        tree_ = tree.tree_
        feature = tree_.feature
        
        # Count feature usage in splits
        for i in range(tree_.node_count):
            if feature[i] != -2:  # Not a leaf
                importances[feature[i]] += 1
        
        # Normalize
        if importances.sum() > 0:
            importances /= importances.sum()
        
        return importances
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Get feature contributions based on importance."""
        if self.feature_importances_ is None:
            return {}
        
        contributions = {}
        for i, importance in enumerate(self.feature_importances_):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            contributions[feature_name] = float(importance)
        
        return contributions
    
    def get_anomaly_path_lengths(self, X: np.ndarray) -> np.ndarray:
        """Get the average path length for each sample."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        
        path_lengths = np.zeros(len(X))
        
        for tree in self.model.estimators_:
            paths = self._get_tree_paths(tree, X)
            path_lengths += paths
        
        return path_lengths / self.n_estimators
    
    def _get_tree_paths(self, tree, X: np.ndarray) -> np.ndarray:
        """Get path lengths for samples in a single tree."""
        tree_ = tree.tree_
        paths = np.zeros(len(X))
        
        for i, x in enumerate(X):
            node = 0
            depth = 0
            
            while tree_.feature[node] != -2:  # Not a leaf
                if x[tree_.feature[node]] <= tree_.threshold[node]:
                    node = tree_.children_left[node]
                else:
                    node = tree_.children_right[node]
                depth += 1
            
            paths[i] = depth
        
        return paths


class ExtendedIsolationForestDetector(BaseDetector):
    """
    Extended Isolation Forest with improved anomaly scoring.
    
    Addresses the limitation of standard Isolation Forest where
    all points converge to the same score in high dimensions.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 n_estimators: int = 100,
                 max_samples: Union[int, str] = 'auto',
                 extension_level: int = None,
                 contamination: float = 0.1,
                 random_state: int = 42):
        super().__init__("ExtendedIsolationForestDetector", config or DetectionConfig())
        
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.extension_level = extension_level
        self.contamination = contamination
        self.random_state = random_state
        
        self.trees: List[Dict] = []
        self.max_depth: float = 0.0
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'ExtendedIsolationForestDetector':
        """Fit extended isolation forest."""
        X = np.asarray(X)
        n_samples, n_features = X.shape
        
        # Set extension level (default: n_features - 1)
        if self.extension_level is None:
            self.extension_level = n_features - 1
        
        # Determine sample size
        if self.max_samples == 'auto':
            max_samples = min(256, n_samples)
        else:
            max_samples = self.max_samples
        
        # Build trees
        rng = np.random.RandomState(self.random_state)
        
        for i in range(self.n_estimators):
            # Sample data
            sample_idx = rng.choice(n_samples, size=max_samples, replace=False)
            X_sample = X[sample_idx]
            
            # Build tree
            tree = self._build_tree(X_sample, 0, rng)
            self.trees.append(tree)
        
        # Compute max depth for normalization
        self.max_depth = np.log2(max_samples) + 0.5772156649  # Euler's constant
        
        self.is_fitted = True
        self.training_stats = {
            'n_estimators': self.n_estimators,
            'max_samples': max_samples,
            'extension_level': self.extension_level
        }
        
        return self
    
    def _build_tree(self, X: np.ndarray, depth: int, rng: np.random.RandomState) -> Dict:
        """Recursively build an isolation tree."""
        n_samples, n_features = X.shape
        
        # Stop conditions
        if n_samples <= 1 or depth >= 50:
            return {'leaf': True, 'size': n_samples, 'depth': depth}
        
        # Randomly select features for split
        n_split_features = min(self.extension_level + 1, n_features)
        split_features = rng.choice(n_features, size=n_split_features, replace=False)
        
        # Random split point
        min_vals = X[:, split_features].min(axis=0)
        max_vals = X[:, split_features].max(axis=0)
        
        # Generate random normal vector
        normal = rng.randn(n_split_features)
        normal = normal / (np.linalg.norm(normal) + 1e-10)
        
        # Random intercept
        p_min = X[:, split_features] @ normal.min()
        p_max = X[:, split_features] @ normal.max()
        intercept = rng.uniform(p_min, p_max)
        
        # Split data
        projections = X[:, split_features] @ normal
        left_mask = projections <= intercept
        
        # Build subtrees
        left_tree = self._build_tree(X[left_mask], depth + 1, rng)
        right_tree = self._build_tree(X[~left_mask], depth + 1, rng)
        
        return {
            'leaf': False,
            'features': split_features,
            'normal': normal,
            'intercept': intercept,
            'left': left_tree,
            'right': right_tree,
            'depth': depth
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores."""
        X = np.asarray(X)
        path_lengths = np.zeros(len(X))
        
        for tree in self.trees:
            for i, x in enumerate(X):
                path_lengths[i] += self._get_path_length(tree, x)
        
        avg_path_lengths = path_lengths / self.n_estimators
        
        # Convert to anomaly score
        scores = 2 ** (-avg_path_lengths / self.max_depth)
        
        return scores
    
    def _get_path_length(self, tree: Dict, x: np.ndarray) -> float:
        """Get path length for a sample in a tree."""
        if tree['leaf']:
            # Adjust for unbuilt subtree
            return tree['depth'] + self._c_factor(tree['size'])
        
        # Compute projection
        projection = x[tree['features']] @ tree['normal']
        
        if projection <= tree['intercept']:
            return self._get_path_length(tree['left'], x)
        else:
            return self._get_path_length(tree['right'], x)
    
    def _c_factor(self, size: int) -> float:
        """Adjustment factor for unbuilt subtrees."""
        if size <= 1:
            return 0
        return 2 * (np.log(size - 1) + 0.5772156649) - 2 * (size - 1) / size


class IsolationForestOptimizer:
    """
    Optimizer for Isolation Forest hyperparameters.
    """
    
    def __init__(self, X_train: np.ndarray, X_val: np.ndarray, 
                 y_val: Optional[np.ndarray] = None):
        self.X_train = X_train
        self.X_val = X_val
        self.y_val = y_val
        
    def grid_search(self, 
                    param_grid: Dict[str, List] = None) -> Dict[str, any]:
        """
        Perform grid search for optimal parameters.
        
        Args:
            param_grid: Dictionary of parameters to search
        
        Returns:
            Best parameters found
        """
        if param_grid is None:
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_samples': ['auto', 128, 256, 512],
                'contamination': [0.05, 0.1, 0.15, 0.2],
                'max_features': [0.5, 0.75, 1.0]
            }
        
        best_score = -np.inf
        best_params = {}
        
        from itertools import product
        
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        
        for combo in product(*values):
            params = dict(zip(keys, combo))
            
            try:
                model = IsolationForestDetector(
                    n_estimators=params['n_estimators'],
                    max_samples=params['max_samples'],
                    contamination=params['contamination'],
                    max_features=params['max_features'],
                    random_state=42
                )
                
                model.fit(self.X_train)
                
                if self.y_val is not None:
                    # Use validation labels
                    predictions = model.predict(self.X_val)
                    from sklearn.metrics import f1_score
                    score = f1_score(self.y_val, predictions, pos_label=-1)
                else:
                    # Use score variance as proxy
                    scores = model.score_samples(self.X_val)
                    score = np.std(scores)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"Parameter combination failed: {e}")
                continue
        
        return best_params
    
    def optimize_contamination(self, 
                               target_anomaly_rate: float = 0.1) -> float:
        """
        Optimize contamination parameter based on desired anomaly rate.
        
        Args:
            target_anomaly_rate: Desired proportion of anomalies
        
        Returns:
            Optimized contamination value
        """
        best_contamination = target_anomaly_rate
        best_diff = np.inf
        
        for contamination in np.linspace(0.01, 0.5, 50):
            model = IsolationForestDetector(
                contamination=contamination,
                random_state=42
            )
            model.fit(self.X_train)
            
            predictions = model.predict(self.X_val)
            actual_rate = np.mean(predictions == -1)
            
            diff = abs(actual_rate - target_anomaly_rate)
            if diff < best_diff:
                best_diff = diff
                best_contamination = contamination
        
        return best_contamination


# Export classes
__all__ = [
    'IsolationForestDetector', 'ExtendedIsolationForestDetector',
    'IsolationForestOptimizer'
]
```



---

## 4. One-Class SVM

### 4.1 Core Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/one_class_svm.py

import numpy as np
from sklearn.svm import OneClassSVM as SklearnOneClassSVM
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple, Union
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class OneClassSVMDetector(BaseDetector):
    """
    One-Class SVM for anomaly detection.
    
    Learns a decision boundary that encompasses the normal data.
    Points outside this boundary are considered anomalies.
    
    Key characteristics:
    - Effective for high-dimensional data
    - Non-linear boundaries with kernel tricks
    - Memory intensive for large datasets
    - Sensitive to hyperparameters
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 kernel: str = 'rbf',
                 degree: int = 3,
                 gamma: Union[str, float] = 'scale',
                 coef0: float = 0.0,
                 nu: float = 0.5,
                 shrinking: bool = True,
                 tol: float = 1e-3,
                 cache_size: int = 200,
                 verbose: bool = False,
                 max_iter: int = -1):
        super().__init__("OneClassSVMDetector", config or DetectionConfig())
        
        self.kernel = kernel
        self.degree = degree
        self.gamma = gamma
        self.coef0 = coef0
        self.nu = nu
        self.shrinking = shrinking
        self.tol = tol
        self.cache_size = cache_size
        self.verbose = verbose
        self.max_iter = max_iter
        
        self.model: SklearnOneClassSVM = None
        self.scaler: StandardScaler = StandardScaler()
        self.support_vectors_: np.ndarray = None
        self.support_: np.ndarray = None
        self.n_support_: int = 0
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'OneClassSVMDetector':
        """Fit the One-Class SVM model."""
        X = np.asarray(X)
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = SklearnOneClassSVM(
            kernel=self.kernel,
            degree=self.degree,
            gamma=self.gamma,
            coef0=self.coef0,
            nu=self.nu,
            shrinking=self.shrinking,
            tol=self.tol,
            cache_size=self.cache_size,
            verbose=self.verbose,
            max_iter=self.max_iter
        )
        
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        # Store support vector information
        self.support_vectors_ = self.model.support_vectors_
        self.support_ = self.model.support_
        self.n_support_ = self.model.n_support_[0]
        
        self.training_stats = {
            'kernel': self.kernel,
            'nu': self.nu,
            'gamma': self.gamma,
            'n_support_vectors': self.n_support_,
            'n_features': X.shape[1],
            'n_samples': len(X)
        }
        
        logger.info(f"One-Class SVM fitted: {self.n_support_} support vectors, "
                   f"kernel={self.kernel}, nu={self.nu}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores.
        
        Returns scores in [0, 1] where higher values indicate
        more anomalous samples.
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        
        X_scaled = self.scaler.transform(X)
        
        # Get signed distance to decision boundary
        distances = self.model.decision_function(X_scaled)
        
        # Convert to [0, 1] anomaly score
        # Negative distances indicate anomalies
        min_dist = np.min(distances)
        max_dist = np.max(distances)
        
        if max_dist > min_dist:
            # Normalize: negative -> high score, positive -> low score
            scores = 1 - (distances - min_dist) / (max_dist - min_dist)
        else:
            scores = np.ones_like(distances) * 0.5
        
        return np.clip(scores, 0, 1)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Signed distance to decision boundary."""
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """
        Estimate feature contributions using gradient approximation.
        """
        if not self.is_fitted:
            return {}
        
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Approximate feature importance by perturbation
        base_score = self.decision_function(X_scaled)[0]
        
        contributions = {}
        epsilon = 0.01
        
        for i in range(X_scaled.shape[1]):
            X_perturbed = X_scaled.copy()
            X_perturbed[0, i] += epsilon
            
            perturbed_score = self.decision_function(X_perturbed)[0]
            gradient = abs(perturbed_score - base_score) / epsilon
            
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            contributions[feature_name] = float(gradient)
        
        # Normalize
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v/total for k, v in contributions.items()}
        
        return contributions


class NuOptimizedOneClassSVM(BaseDetector):
    """
    One-Class SVM with automatic nu parameter optimization.
    
    The nu parameter approximates the fraction of outliers
    and support vectors. This class automatically finds
    the optimal nu based on validation data.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 kernel: str = 'rbf',
                 gamma: Union[str, float] = 'scale',
                 nu_range: Tuple[float, float] = (0.01, 0.5),
                 n_nu_values: int = 20,
                 random_state: int = 42):
        super().__init__("NuOptimizedOneClassSVM", config or DetectionConfig())
        
        self.kernel = kernel
        self.gamma = gamma
        self.nu_range = nu_range
        self.n_nu_values = n_nu_values
        self.random_state = random_state
        
        self.best_model: OneClassSVMDetector = None
        self.best_nu: float = None
        self.cv_results: Dict = {}
        
    def fit(self, X: np.ndarray, 
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'NuOptimizedOneClassSVM':
        """
        Fit with automatic nu optimization.
        
        Args:
            X: Training data
            X_val: Validation data (optional)
            y_val: Validation labels (optional, -1 for anomaly)
        """
        X = np.asarray(X)
        
        # Split for validation if not provided
        if X_val is None:
            from sklearn.model_selection import train_test_split
            X_train, X_val = train_test_split(
                X, test_size=0.2, random_state=self.random_state
            )
        else:
            X_train = X
        
        # Search for best nu
        nu_values = np.linspace(
            self.nu_range[0], self.nu_range[1], self.n_nu_values
        )
        
        best_score = -np.inf
        
        for nu in nu_values:
            try:
                model = OneClassSVMDetector(
                    kernel=self.kernel,
                    gamma=self.gamma,
                    nu=nu
                )
                model.fit(X_train)
                
                # Score on validation set
                if y_val is not None:
                    predictions = model.predict(X_val)
                    from sklearn.metrics import f1_score
                    score = f1_score(y_val, predictions, pos_label=-1)
                else:
                    # Use score variance as proxy
                    scores = model.score_samples(X_val)
                    score = np.std(scores)
                
                self.cv_results[nu] = score
                
                if score > best_score:
                    best_score = score
                    self.best_nu = nu
                    self.best_model = model
                    
            except Exception as e:
                logger.warning(f"nu={nu} failed: {e}")
                continue
        
        if self.best_model is None:
            raise RuntimeError("Could not find valid nu parameter")
        
        self.is_fitted = True
        
        # Copy attributes from best model
        self.model = self.best_model.model
        self.scaler = self.best_model.scaler
        
        self.training_stats = {
            'best_nu': self.best_nu,
            'kernel': self.kernel,
            'cv_results': self.cv_results
        }
        
        logger.info(f"Optimized nu={self.best_nu} with score={best_score:.4f}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.best_model.predict(X)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        return self.best_model.score_samples(X)


class KernelAdaptiveOneClassSVM(BaseDetector):
    """
    One-Class SVM with adaptive kernel selection.
    
    Automatically selects the best kernel based on data characteristics.
    """
    
    KERNELS = ['rbf', 'poly', 'sigmoid', 'linear']
    
    def __init__(self,
                 config: DetectionConfig = None,
                 gamma: Union[str, float] = 'scale',
                 nu: float = 0.5,
                 random_state: int = 42):
        super().__init__("KernelAdaptiveOneClassSVM", config or DetectionConfig())
        
        self.gamma = gamma
        self.nu = nu
        self.random_state = random_state
        
        self.best_model: OneClassSVMDetector = None
        self.best_kernel: str = None
        self.kernel_scores: Dict[str, float] = {}
        
    def fit(self, X: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'KernelAdaptiveOneClassSVM':
        """Fit with automatic kernel selection."""
        X = np.asarray(X)
        
        if X_val is None:
            from sklearn.model_selection import train_test_split
            X_train, X_val = train_test_split(
                X, test_size=0.2, random_state=self.random_state
            )
        else:
            X_train = X
        
        best_score = -np.inf
        
        for kernel in self.KERNELS:
            try:
                model = OneClassSVMDetector(
                    kernel=kernel,
                    gamma=self.gamma,
                    nu=self.nu
                )
                model.fit(X_train)
                
                # Score validation
                if y_val is not None:
                    predictions = model.predict(X_val)
                    from sklearn.metrics import f1_score
                    score = f1_score(y_val, predictions, pos_label=-1)
                else:
                    scores = model.score_samples(X_val)
                    score = np.std(scores)
                
                self.kernel_scores[kernel] = score
                
                if score > best_score:
                    best_score = score
                    self.best_kernel = kernel
                    self.best_model = model
                    
            except Exception as e:
                logger.warning(f"Kernel {kernel} failed: {e}")
                continue
        
        if self.best_model is None:
            raise RuntimeError("No kernel succeeded")
        
        self.is_fitted = True
        self.model = self.best_model.model
        self.scaler = self.best_model.scaler
        
        self.training_stats = {
            'best_kernel': self.best_kernel,
            'kernel_scores': self.kernel_scores
        }
        
        logger.info(f"Selected kernel: {self.best_kernel} with score={best_score:.4f}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.best_model.predict(X)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        return self.best_model.score_samples(X)


class IncrementalOneClassSVM(BaseDetector):
    """
    Incremental One-Class SVM for online learning.
    
    Updates the model as new data arrives without full retraining.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 kernel: str = 'rbf',
                 gamma: Union[str, float] = 'scale',
                 nu: float = 0.1,
                 buffer_size: int = 1000,
                 update_frequency: int = 100):
        super().__init__("IncrementalOneClassSVM", config or DetectionConfig())
        
        self.kernel = kernel
        self.gamma = gamma
        self.nu = nu
        self.buffer_size = buffer_size
        self.update_frequency = update_frequency
        
        self.model: OneClassSVMDetector = None
        self.data_buffer: List[np.ndarray] = []
        self.sample_count: int = 0
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'IncrementalOneClassSVM':
        """Initial fit on training data."""
        self.model = OneClassSVMDetector(
            kernel=self.kernel,
            gamma=self.gamma,
            nu=self.nu
        )
        self.model.fit(X, y)
        self.is_fitted = True
        
        return self
    
    def partial_fit(self, X: np.ndarray) -> 'IncrementalOneClassSVM':
        """Incrementally update the model with new data."""
        X = np.asarray(X)
        
        # Add to buffer
        for x in X:
            self.data_buffer.append(x)
        
        self.sample_count += len(X)
        
        # Retrain if buffer is full
        if len(self.data_buffer) >= self.buffer_size:
            self._update_model()
        
        return self
    
    def _update_model(self):
        """Retrain model with buffered data."""
        # Convert buffer to array
        X_update = np.array(self.data_buffer)
        
        # Retrain
        self.model.fit(X_update)
        
        # Clear buffer (keep some for continuity)
        keep_size = self.buffer_size // 4
        self.data_buffer = self.data_buffer[-keep_size:]
        
        logger.info(f"Model updated with {len(X_update)} samples")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        return self.model.score_samples(X)


# Export classes
__all__ = [
    'OneClassSVMDetector', 'NuOptimizedOneClassSVM',
    'KernelAdaptiveOneClassSVM', 'IncrementalOneClassSVM'
]
```

---

## 5. Autoencoders

### 5.1 Deep Learning Based Anomaly Detection

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/autoencoders.py

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from typing import Dict, List, Optional, Tuple, Union, Callable
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity

# Suppress TensorFlow warnings
warnings.filterwarnings('ignore', category=UserWarning)


class AutoencoderDetector(BaseDetector):
    """
    Autoencoder-based anomaly detection.
    
    Learns to reconstruct normal data. High reconstruction error
    indicates anomalous samples.
    
    Key advantages:
    - Captures complex non-linear patterns
    - Works well with high-dimensional data
    - Can handle various data types
    - Provides interpretable reconstruction errors
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 encoding_dim: int = 8,
                 hidden_layers: List[int] = None,
                 activation: str = 'relu',
                 output_activation: str = 'linear',
                 loss: str = 'mse',
                 optimizer: str = 'adam',
                 epochs: int = 100,
                 batch_size: int = 32,
                 validation_split: float = 0.1,
                 early_stopping_patience: int = 10,
                 reduce_lr_patience: int = 5,
                 dropout_rate: float = 0.2,
                 noise_factor: float = 0.0):
        super().__init__("AutoencoderDetector", config or DetectionConfig())
        
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers or [64, 32]
        self.activation = activation
        self.output_activation = output_activation
        self.loss = loss
        self.optimizer = optimizer
        self.epochs = epochs
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.early_stopping_patience = early_stopping_patience
        self.reduce_lr_patience = reduce_lr_patience
        self.dropout_rate = dropout_rate
        self.noise_factor = noise_factor
        
        self.autoencoder: Model = None
        self.encoder: Model = None
        self.decoder: Model = None
        self.history = None
        self.threshold: float = None
        self.reconstruction_errors: np.ndarray = None
        
    def build_model(self, input_dim: int) -> Model:
        """Build the autoencoder architecture."""
        # Input layer
        inputs = layers.Input(shape=(input_dim,))
        
        # Add noise for denoising autoencoder
        x = inputs
        if self.noise_factor > 0:
            x = layers.GaussianNoise(self.noise_factor)(x)
        
        # Encoder
        for units in self.hidden_layers:
            x = layers.Dense(units, activation=self.activation)(x)
            if self.dropout_rate > 0:
                x = layers.Dropout(self.dropout_rate)(x)
        
        # Bottleneck (latent representation)
        encoded = layers.Dense(self.encoding_dim, activation=self.activation, 
                               name='bottleneck')(x)
        
        # Decoder
        x = encoded
        for units in reversed(self.hidden_layers):
            x = layers.Dense(units, activation=self.activation)(x)
            if self.dropout_rate > 0:
                x = layers.Dropout(self.dropout_rate)(x)
        
        # Output layer
        decoded = layers.Dense(input_dim, activation=self.output_activation, 
                               name='output')(x)
        
        # Full autoencoder
        autoencoder = Model(inputs, decoded, name='autoencoder')
        autoencoder.compile(optimizer=self.optimizer, loss=self.loss)
        
        # Extract encoder
        self.encoder = Model(inputs, encoded, name='encoder')
        
        # Build decoder
        encoded_input = layers.Input(shape=(self.encoding_dim,))
        x = encoded_input
        for i, units in enumerate(reversed(self.hidden_layers)):
            x = layers.Dense(units, activation=self.activation, 
                            name=f'decoder_dense_{i}')(x)
        decoder_output = layers.Dense(input_dim, activation=self.output_activation,
                                      name='decoder_output')(x)
        self.decoder = Model(encoded_input, decoder_output, name='decoder')
        
        return autoencoder
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'AutoencoderDetector':
        """Fit the autoencoder on training data."""
        X = np.asarray(X).astype(np.float32)
        
        # Build model
        self.autoencoder = self.build_model(X.shape[1])
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.early_stopping_patience,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.reduce_lr_patience,
                min_lr=1e-7
            )
        ]
        
        # Train
        self.history = self.autoencoder.fit(
            X, X,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=0
        )
        
        self.is_fitted = True
        
        # Compute reconstruction errors on training data
        reconstructions = self.autoencoder.predict(X, verbose=0)
        self.reconstruction_errors = np.mean(np.square(X - reconstructions), axis=1)
        
        # Set threshold (e.g., 95th percentile)
        self.threshold = np.percentile(self.reconstruction_errors, 95)
        
        self.training_stats = {
            'encoding_dim': self.encoding_dim,
            'hidden_layers': self.hidden_layers,
            'final_loss': self.history.history['loss'][-1],
            'final_val_loss': self.history.history.get('val_loss', [-1])[-1],
            'threshold': self.threshold,
            'n_samples': len(X)
        }
        
        logger.info(f"Autoencoder trained: final_loss={self.training_stats['final_loss']:.4f}, "
                   f"threshold={self.threshold:.4f}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores based on reconstruction error.
        
        Returns scores in [0, 1] where higher values indicate
        more anomalous samples.
        """
        X = np.asarray(X).astype(np.float32)
        
        # Reconstruct
        reconstructions = self.autoencoder.predict(X, verbose=0)
        
        # Compute reconstruction error
        errors = np.mean(np.square(X - reconstructions), axis=1)
        
        # Normalize to [0, 1] using training statistics
        if self.threshold > 0:
            scores = np.minimum(errors / self.threshold, 1.0)
        else:
            scores = np.minimum(errors / (np.mean(errors) + 1e-10), 1.0)
        
        return scores
    
    def encode(self, X: np.ndarray) -> np.ndarray:
        """Get latent representation."""
        X = np.asarray(X).astype(np.float32)
        return self.encoder.predict(X, verbose=0)
    
    def decode(self, encoded: np.ndarray) -> np.ndarray:
        """Reconstruct from latent representation."""
        encoded = np.asarray(encoded).astype(np.float32)
        return self.decoder.predict(encoded, verbose=0)
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Get per-feature reconstruction error contributions."""
        X = np.asarray(X).astype(np.float32)
        
        # Reconstruct single sample
        reconstruction = self.autoencoder.predict(X, verbose=0)[0]
        x = X[0]
        
        # Per-feature error
        feature_errors = np.square(x - reconstruction)
        
        contributions = {}
        for i, error in enumerate(feature_errors):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            contributions[feature_name] = float(error / (np.sum(feature_errors) + 1e-10))
        
        return contributions
    
    def get_reconstruction_error_distribution(self) -> Dict[str, float]:
        """Get statistics of reconstruction errors."""
        if self.reconstruction_errors is None:
            return {}
        
        return {
            'mean': float(np.mean(self.reconstruction_errors)),
            'std': float(np.std(self.reconstruction_errors)),
            'min': float(np.min(self.reconstruction_errors)),
            'max': float(np.max(self.reconstruction_errors)),
            'median': float(np.median(self.reconstruction_errors)),
            'q95': float(np.percentile(self.reconstruction_errors, 95)),
            'q99': float(np.percentile(self.reconstruction_errors, 99))
        }


class VariationalAutoencoderDetector(BaseDetector):
    """
    Variational Autoencoder for anomaly detection.
    
    Learns a probabilistic latent representation, providing
    better uncertainty estimates and smoother latent space.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 encoding_dim: int = 8,
                 hidden_layers: List[int] = None,
                 activation: str = 'relu',
                 epochs: int = 100,
                 batch_size: int = 32,
                 validation_split: float = 0.1,
                 kl_weight: float = 0.001,
                 dropout_rate: float = 0.2):
        super().__init__("VariationalAutoencoderDetector", config or DetectionConfig())
        
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers or [64, 32]
        self.activation = activation
        self.epochs = epochs
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.kl_weight = kl_weight
        self.dropout_rate = dropout_rate
        
        self.vae: Model = None
        self.encoder: Model = None
        self.decoder: Model = None
        self.threshold: float = None
        
    def sampling(self, args):
        """Reparameterization trick for VAE."""
        z_mean, z_log_var = args
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.random.normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon
    
    def build_model(self, input_dim: int) -> Model:
        """Build VAE architecture."""
        # Encoder
        inputs = layers.Input(shape=(input_dim,))
        x = inputs
        
        for units in self.hidden_layers:
            x = layers.Dense(units, activation=self.activation)(x)
            if self.dropout_rate > 0:
                x = layers.Dropout(self.dropout_rate)(x)
        
        # Latent parameters
        z_mean = layers.Dense(self.encoding_dim, name='z_mean')(x)
        z_log_var = layers.Dense(self.encoding_dim, name='z_log_var')(x)
        z = layers.Lambda(self.sampling, output_shape=(self.encoding_dim,), 
                         name='z')([z_mean, z_log_var])
        
        self.encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
        
        # Decoder
        latent_inputs = layers.Input(shape=(self.encoding_dim,))
        x = latent_inputs
        
        for units in reversed(self.hidden_layers):
            x = layers.Dense(units, activation=self.activation)(x)
        
        outputs = layers.Dense(input_dim, activation='linear')(x)
        self.decoder = Model(latent_inputs, outputs, name='decoder')
        
        # Full VAE
        outputs = self.decoder(self.encoder(inputs)[2])
        vae = Model(inputs, outputs, name='vae')
        
        # Add KL loss
        reconstruction_loss = tf.reduce_mean(
            tf.reduce_sum(tf.square(inputs - outputs), axis=-1)
        )
        kl_loss = -0.5 * tf.reduce_mean(
            tf.reduce_sum(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var), axis=-1)
        )
        vae_loss = reconstruction_loss + self.kl_weight * kl_loss
        
        vae.add_loss(vae_loss)
        vae.compile(optimizer='adam')
        
        return vae
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'VariationalAutoencoderDetector':
        """Fit the VAE."""
        X = np.asarray(X).astype(np.float32)
        
        self.vae = self.build_model(X.shape[1])
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
        ]
        
        self.vae.fit(
            X, None,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=0
        )
        
        self.is_fitted = True
        
        # Compute threshold
        reconstructions = self.vae.predict(X, verbose=0)
        errors = np.mean(np.square(X - reconstructions), axis=1)
        self.threshold = np.percentile(errors, 95)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores."""
        X = np.asarray(X).astype(np.float32)
        reconstructions = self.vae.predict(X, verbose=0)
        errors = np.mean(np.square(X - reconstructions), axis=1)
        return np.minimum(errors / self.threshold, 1.0)
    
    def encode(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Get mean and log variance of latent distribution."""
        X = np.asarray(X).astype(np.float32)
        z_mean, z_log_var, _ = self.encoder.predict(X, verbose=0)
        return z_mean, z_log_var


class LSTMAutoencoderDetector(BaseDetector):
    """
    LSTM-based autoencoder for sequence anomaly detection.
    
    Captures temporal patterns in sequential data.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 sequence_length: int = 10,
                 lstm_units: List[int] = None,
                 encoding_dim: int = 8,
                 epochs: int = 100,
                 batch_size: int = 32):
        super().__init__("LSTMAutoencoderDetector", config or DetectionConfig())
        
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units or [64, 32]
        self.encoding_dim = encoding_dim
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.model: Model = None
        self.threshold: float = None
        
    def build_model(self, n_features: int) -> Model:
        """Build LSTM autoencoder."""
        # Encoder
        inputs = layers.Input(shape=(self.sequence_length, n_features))
        
        x = inputs
        for i, units in enumerate(self.lstm_units):
            return_sequences = i < len(self.lstm_units) - 1
            x = layers.LSTM(units, activation='tanh', 
                          return_sequences=return_sequences)(x)
        
        encoded = layers.Dense(self.encoding_dim, activation='relu')(x)
        
        # Repeat for decoder
        x = layers.RepeatVector(self.sequence_length)(encoded)
        
        # Decoder
        for units in reversed(self.lstm_units):
            x = layers.LSTM(units, activation='tanh', return_sequences=True)(x)
        
        outputs = layers.TimeDistributed(
            layers.Dense(n_features, activation='linear')
        )(x)
        
        model = Model(inputs, outputs)
        model.compile(optimizer='adam', loss='mse')
        
        return model
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'LSTMAutoencoderDetector':
        """Fit LSTM autoencoder on sequential data."""
        X = np.asarray(X).astype(np.float32)
        
        # X should be (n_samples, sequence_length, n_features)
        if len(X.shape) != 3:
            raise ValueError(f"Expected 3D input (samples, timesteps, features), got {X.shape}")
        
        self.model = self.build_model(X.shape[2])
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
        ]
        
        self.model.fit(
            X, X,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=0.1,
            callbacks=callbacks,
            verbose=0
        )
        
        self.is_fitted = True
        
        # Compute threshold
        reconstructions = self.model.predict(X, verbose=0)
        errors = np.mean(np.square(X - reconstructions), axis=(1, 2))
        self.threshold = np.percentile(errors, 95)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores for sequences."""
        X = np.asarray(X).astype(np.float32)
        reconstructions = self.model.predict(X, verbose=0)
        errors = np.mean(np.square(X - reconstructions), axis=(1, 2))
        return np.minimum(errors / self.threshold, 1.0)


# Export classes
__all__ = [
    'AutoencoderDetector', 'VariationalAutoencoderDetector',
    'LSTMAutoencoderDetector'
]
```



---

## 6. Clustering-Based Detection

### 6.1 Distance-Based Clustering Methods

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/clustering_detectors.py

import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor as SklearnLOF
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple, Union
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class KMeansDistanceDetector(BaseDetector):
    """
    K-Means based anomaly detection.
    
    Detects anomalies based on distance to cluster centroids.
    Points far from all centroids are considered anomalies.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 n_clusters: int = 8,
                 metric: str = 'euclidean',
                 contamination: float = 0.1,
                 random_state: int = 42):
        super().__init__("KMeansDistanceDetector", config or DetectionConfig())
        
        self.n_clusters = n_clusters
        self.metric = metric
        self.contamination = contamination
        self.random_state = random_state
        
        self.kmeans = None
        self.scaler = StandardScaler()
        self.cluster_distances: Dict[int, List[float]] = {}
        self.thresholds: Dict[int, float] = {}
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'KMeansDistanceDetector':
        """Fit K-Means and compute distance thresholds."""
        X = np.asarray(X)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit K-Means
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        self.kmeans.fit(X_scaled)
        
        # Compute distances to assigned clusters
        labels = self.kmeans.labels_
        distances = self._compute_distances(X_scaled)
        
        # Compute per-cluster distance thresholds
        for cluster_id in range(self.n_clusters):
            cluster_distances = distances[labels == cluster_id]
            if len(cluster_distances) > 0:
                # Use percentile-based threshold
                self.thresholds[cluster_id] = np.percentile(
                    cluster_distances, 
                    100 * (1 - self.contamination)
                )
                self.cluster_distances[cluster_id] = cluster_distances.tolist()
        
        self.is_fitted = True
        
        self.training_stats = {
            'n_clusters': self.n_clusters,
            'inertia': self.kmeans.inertia_,
            'n_iter': self.kmeans.n_iter_,
            'cluster_sizes': np.bincount(labels).tolist()
        }
        
        logger.info(f"K-Means fitted: {self.n_clusters} clusters, "
                   f"inertia={self.kmeans.inertia_:.2f}")
        
        return self
    
    def _compute_distances(self, X: np.ndarray) -> np.ndarray:
        """Compute distance to nearest cluster centroid."""
        # Get cluster assignments
        labels = self.kmeans.predict(X)
        
        distances = np.zeros(len(X))
        for i, (x, label) in enumerate(zip(X, labels)):
            centroid = self.kmeans.cluster_centers_[label]
            distances[i] = np.linalg.norm(x - centroid)
        
        return distances
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores based on cluster distance."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Get cluster assignments
        labels = self.kmeans.predict(X_scaled)
        distances = self._compute_distances(X_scaled)
        
        # Normalize by cluster threshold
        scores = np.zeros(len(X))
        for i, (label, dist) in enumerate(zip(labels, distances)):
            threshold = self.thresholds.get(label, np.median(list(self.thresholds.values())))
            scores[i] = min(dist / threshold, 1.0) if threshold > 0 else 0.5
        
        return scores
    
    def _get_feature_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Get feature contributions based on distance to centroid."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        label = self.kmeans.predict(X_scaled)[0]
        centroid = self.kmeans.cluster_centers_[label]
        
        # Per-feature distance
        feature_distances = np.abs(X_scaled[0] - centroid)
        
        contributions = {}
        total = np.sum(feature_distances)
        for i, dist in enumerate(feature_distances):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            contributions[feature_name] = float(dist / (total + 1e-10))
        
        return contributions


class DBSCANDetector(BaseDetector):
    """
    DBSCAN-based anomaly detection.
    
    Points not assigned to any cluster (noise points) are anomalies.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 eps: float = 0.5,
                 min_samples: int = 5,
                 metric: str = 'euclidean',
                 algorithm: str = 'auto',
                 leaf_size: int = 30):
        super().__init__("DBSCANDetector", config or DetectionConfig())
        
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        
        self.dbscan = None
        self.scaler = StandardScaler()
        self.cluster_centers: Dict[int, np.ndarray] = {}
        self.core_sample_indices: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'DBSCANDetector':
        """Fit DBSCAN."""
        X = np.asarray(X)
        X_scaled = self.scaler.fit_transform(X)
        
        self.dbscan = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric=self.metric,
            algorithm=self.algorithm,
            leaf_size=self.leaf_size
        )
        
        self.dbscan.fit(X_scaled)
        self.core_sample_indices = self.dbscan.core_sample_indices_
        
        # Compute cluster centers
        labels = self.dbscan.labels_
        unique_labels = set(labels) - {-1}  # Exclude noise
        
        for label in unique_labels:
            cluster_points = X_scaled[labels == label]
            self.cluster_centers[label] = np.mean(cluster_points, axis=0)
        
        self.is_fitted = True
        
        n_noise = np.sum(labels == -1)
        n_clusters = len(unique_labels)
        
        self.training_stats = {
            'eps': self.eps,
            'min_samples': self.min_samples,
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'noise_ratio': n_noise / len(X)
        }
        
        logger.info(f"DBSCAN fitted: {n_clusters} clusters, {n_noise} noise points")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels (-1 for noise/anomaly)."""
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Find nearest cluster for each point
        labels = self.dbscan.labels_
        unique_labels = set(labels) - {-1}
        
        scores = np.ones(len(X))  # Start with high score (anomaly)
        
        for i, x in enumerate(X_scaled):
            min_distance = float('inf')
            nearest_cluster = -1
            
            for label in unique_labels:
                centroid = self.cluster_centers[label]
                dist = np.linalg.norm(x - centroid)
                if dist < min_distance:
                    min_distance = dist
                    nearest_cluster = label
            
            # Score based on distance to nearest cluster
            if nearest_cluster != -1:
                scores[i] = min(min_distance / self.eps, 1.0)
        
        return scores


class LocalOutlierFactorDetector(BaseDetector):
    """
    Local Outlier Factor (LOF) anomaly detection.
    
    Measures local density deviation of a data point
    compared to its neighbors.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 n_neighbors: int = 20,
                 algorithm: str = 'auto',
                 leaf_size: int = 30,
                 metric: str = 'minkowski',
                 p: int = 2,
                 contamination: Union[str, float] = 'auto',
                 novelty: bool = True,
                 n_jobs: int = -1):
        super().__init__("LocalOutlierFactorDetector", config or DetectionConfig())
        
        self.n_neighbors = n_neighbors
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.metric = metric
        self.p = p
        self.contamination = contamination
        self.novelty = novelty
        self.n_jobs = n_jobs
        
        self.lof = None
        self.scaler = StandardScaler()
        self.negative_outlier_factor_: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'LocalOutlierFactorDetector':
        """Fit LOF."""
        X = np.asarray(X)
        X_scaled = self.scaler.fit_transform(X)
        
        self.lof = SklearnLOF(
            n_neighbors=self.n_neighbors,
            algorithm=self.algorithm,
            leaf_size=self.leaf_size,
            metric=self.metric,
            p=self.p,
            contamination=self.contamination,
            novelty=self.novelty,
            n_jobs=self.n_jobs
        )
        
        self.lof.fit(X_scaled)
        self.negative_outlier_factor_ = self.lof.negative_outlier_factor_
        
        self.is_fitted = True
        
        self.training_stats = {
            'n_neighbors': self.n_neighbors,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
        
        logger.info(f"LOF fitted: n_neighbors={self.n_neighbors}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels."""
        X_scaled = self.scaler.transform(X)
        return self.lof.predict(X_scaled)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute LOF-based anomaly scores."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Get negative outlier factor (lower = more anomalous)
        lof_scores = -self.lof.score_samples(X_scaled)
        
        # Convert to [0, 1] range
        min_score = np.min(lof_scores)
        max_score = np.max(lof_scores)
        
        if max_score > min_score:
            normalized = (lof_scores - min_score) / (max_score - min_score)
        else:
            normalized = np.ones_like(lof_scores) * 0.5
        
        return normalized


class HierarchicalClusteringDetector(BaseDetector):
    """
    Hierarchical clustering-based anomaly detection.
    
    Uses cluster hierarchy to identify outliers at different scales.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 n_clusters: int = 5,
                 linkage: str = 'ward',
                 metric: str = 'euclidean',
                 contamination: float = 0.1):
        super().__init__("HierarchicalClusteringDetector", config or DetectionConfig())
        
        self.n_clusters = n_clusters
        self.linkage = linkage
        self.metric = metric
        self.contamination = contamination
        
        self.clustering = None
        self.scaler = StandardScaler()
        self.cluster_distances: np.ndarray = None
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'HierarchicalClusteringDetector':
        """Fit hierarchical clustering."""
        X = np.asarray(X)
        X_scaled = self.scaler.fit_transform(X)
        
        self.clustering = AgglomerativeClustering(
            n_clusters=self.n_clusters,
            linkage=self.linkage,
            metric=self.metric if self.linkage != 'ward' else 'euclidean'
        )
        
        self.clustering.fit(X_scaled)
        
        # Compute distances to cluster centers
        labels = self.clustering.labels_
        
        cluster_centers = []
        for i in range(self.n_clusters):
            cluster_points = X_scaled[labels == i]
            if len(cluster_points) > 0:
                cluster_centers.append(np.mean(cluster_points, axis=0))
            else:
                cluster_centers.append(np.zeros(X.shape[1]))
        
        self.cluster_centers = np.array(cluster_centers)
        
        # Compute distance threshold
        distances = np.zeros(len(X))
        for i, (x, label) in enumerate(zip(X_scaled, labels)):
            distances[i] = np.linalg.norm(x - self.cluster_centers[label])
        
        self.threshold = np.percentile(distances, 100 * (1 - self.contamination))
        
        self.is_fitted = True
        
        self.training_stats = {
            'n_clusters': self.n_clusters,
            'linkage': self.linkage,
            'threshold': self.threshold
        }
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores."""
        X = np.asarray(X)
        X_scaled = self.scaler.transform(X)
        
        # Find nearest cluster
        distances_to_centers = pairwise_distances(
            X_scaled, self.cluster_centers, metric='euclidean'
        )
        min_distances = np.min(distances_to_centers, axis=1)
        
        # Normalize
        scores = np.minimum(min_distances / self.threshold, 1.0)
        
        return scores


class ClusteringEnsembleDetector(BaseDetector):
    """
    Ensemble of clustering-based detectors.
    """
    
    def __init__(self, config: DetectionConfig = None):
        super().__init__("ClusteringEnsembleDetector", config or DetectionConfig())
        
        self.detectors = {
            'kmeans': KMeansDistanceDetector(config),
            'dbscan': DBSCANDetector(config),
            'lof': LocalOutlierFactorDetector(config)
        }
        self.weights = {
            'kmeans': 0.4,
            'dbscan': 0.3,
            'lof': 0.3
        }
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'ClusteringEnsembleDetector':
        """Fit all clustering detectors."""
        for name, detector in self.detectors.items():
            try:
                detector.fit(X, y)
            except Exception as e:
                logger.warning(f"Detector {name} failed: {e}")
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Combine scores from all detectors."""
        weighted_score = np.zeros(len(X))
        total_weight = 0.0
        
        for name, detector in self.detectors.items():
            if detector.is_fitted:
                scores = detector.score_samples(X)
                weighted_score += scores * self.weights[name]
                total_weight += self.weights[name]
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return np.ones(len(X)) * 0.5


# Export classes
__all__ = [
    'KMeansDistanceDetector', 'DBSCANDetector',
    'LocalOutlierFactorDetector', 'HierarchicalClusteringDetector',
    'ClusteringEnsembleDetector'
]
```

---

## 7. Time Series Anomaly Detection

### 7.1 Temporal Pattern Detection

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/time_series.py

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from typing import Dict, List, Optional, Tuple, Union, Callable
from sklearn.linear_model import LinearRegression
import warnings

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class TimeSeriesAnomalyDetector(BaseDetector):
    """
    Base class for time series anomaly detection.
    """
    
    def __init__(self, name: str, config: DetectionConfig):
        super().__init__(name, config)
        self.timestamps: pd.DatetimeIndex = None
        
    def _determine_anomaly_type(self, X: np.ndarray) -> AnomalyType:
        """Override to return temporal anomaly type."""
        return AnomalyType.TEMPORAL


class StatisticalTimeSeriesDetector(TimeSeriesAnomalyDetector):
    """
    Statistical methods for time series anomaly detection.
    
    Uses rolling statistics to detect point and contextual anomalies.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 window_size: int = 24,
                 threshold_std: float = 3.0,
                 seasonal_period: int = None,
                 detect_trend: bool = True):
        super().__init__("StatisticalTimeSeriesDetector", config or DetectionConfig())
        
        self.window_size = window_size
        self.threshold_std = threshold_std
        self.seasonal_period = seasonal_period
        self.detect_trend = detect_trend
        
        self.rolling_mean: pd.Series = None
        self.rolling_std: pd.Series = None
        self.trend: pd.Series = None
        self.seasonal: pd.Series = None
        self.residual: pd.Series = None
        
    def fit(self, X: np.ndarray, 
            timestamps: Optional[pd.DatetimeIndex] = None) -> 'StatisticalTimeSeriesDetector':
        """Fit on time series data."""
        X = np.asarray(X)
        
        if timestamps is None:
            timestamps = pd.date_range(start='2020-01-01', periods=len(X), freq='H')
        
        self.timestamps = timestamps
        
        # Handle multivariate time series
        if len(X.shape) == 1:
            series = pd.Series(X, index=timestamps)
        else:
            # Use first dimension for univariate analysis
            series = pd.Series(X[:, 0], index=timestamps)
        
        # Decompose if seasonal period specified
        if self.seasonal_period:
            self.trend, self.seasonal, self.residual = self._decompose(series)
            analysis_series = self.residual.dropna()
        else:
            analysis_series = series
        
        # Compute rolling statistics
        self.rolling_mean = analysis_series.rolling(
            window=self.window_size, min_periods=1
        ).mean()
        
        self.rolling_std = analysis_series.rolling(
            window=self.window_size, min_periods=1
        ).std()
        
        self.is_fitted = True
        
        self.training_stats = {
            'window_size': self.window_size,
            'threshold_std': self.threshold_std,
            'seasonal_period': self.seasonal_period
        }
        
        return self
    
    def _decompose(self, series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Simple decomposition into trend, seasonal, and residual."""
        # Trend: moving average
        trend = series.rolling(window=self.seasonal_period, center=True).mean()
        
        # Detrended series
        detrended = series - trend
        
        # Seasonal: average for each period
        seasonal_dict = {}
        for i in range(self.seasonal_period):
            mask = np.arange(len(series)) % self.seasonal_period == i
            seasonal_dict[i] = detrended[mask].mean()
        
        seasonal = pd.Series(index=series.index, dtype=float)
        for i, idx in enumerate(series.index):
            seasonal.iloc[i] = seasonal_dict[i % self.seasonal_period]
        
        # Residual
        residual = series - trend - seasonal
        
        return trend, seasonal, residual
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores for time series."""
        X = np.asarray(X)
        
        if len(X.shape) == 1:
            series = pd.Series(X, index=self.timestamps[:len(X)])
        else:
            series = pd.Series(X[:, 0], index=self.timestamps[:len(X)])
        
        # Compute z-scores relative to rolling statistics
        if self.seasonal_period:
            _, _, residual = self._decompose(series)
            analysis_series = residual.dropna()
        else:
            analysis_series = series
        
        # Rolling z-scores
        rolling_mean = analysis_series.rolling(
            window=self.window_size, min_periods=1
        ).mean()
        rolling_std = analysis_series.rolling(
            window=self.window_size, min_periods=1
        ).std()
        
        z_scores = np.abs((analysis_series - rolling_mean) / (rolling_std + 1e-10))
        
        # Normalize to [0, 1]
        scores = np.minimum(z_scores / self.threshold_std, 1.0)
        
        return scores.values


class ProphetStyleDetector(TimeSeriesAnomalyDetector):
    """
    Prophet-style time series anomaly detection.
    
    Detects anomalies based on deviation from predicted values
    using trend + seasonality model.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 changepoint_prior_scale: float = 0.05,
                 seasonality_prior_scale: float = 10.0,
                 holidays_prior_scale: float = 10.0,
                 interval_width: float = 0.8):
        super().__init__("ProphetStyleDetector", config or DetectionConfig())
        
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_prior_scale = seasonality_prior_scale
        self.holidays_prior_scale = holidays_prior_scale
        self.interval_width = interval_width
        
        self.trend_model = None
        self.seasonal_components: Dict[str, np.ndarray] = {}
        self.changepoints: List[int] = []
        
    def fit(self, X: np.ndarray,
            timestamps: Optional[pd.DatetimeIndex] = None,
            freq: str = 'H') -> 'ProphetStyleDetector':
        """Fit trend and seasonality model."""
        X = np.asarray(X)
        
        if timestamps is None:
            timestamps = pd.date_range(start='2020-01-01', periods=len(X), freq=freq)
        
        self.timestamps = timestamps
        
        if len(X.shape) == 1:
            y = X
        else:
            y = X[:, 0]
        
        # Create time features
        t = np.arange(len(y))
        
        # Fit trend (piecewise linear)
        self.trend_model = self._fit_piecewise_trend(t, y)
        
        # Extract and fit seasonality
        trend_pred = self._predict_trend(t)
        residual = y - trend_pred
        
        # Fit daily seasonality
        self.seasonal_components['daily'] = self._fit_daily_seasonality(timestamps, residual)
        
        # Fit weekly seasonality
        self.seasonal_components['weekly'] = self._fit_weekly_seasonality(timestamps, residual)
        
        self.is_fitted = True
        
        return self
    
    def _fit_piecewise_trend(self, t: np.ndarray, y: np.ndarray) -> Dict:
        """Fit piecewise linear trend with changepoints."""
        # Simple approach: detect changepoints using rolling statistics
        n_changepoints = min(25, len(t) // 10)
        changepoint_locs = np.linspace(0, len(t)-1, n_changepoints, dtype=int)[1:-1]
        
        # Fit linear trend with changepoint adjustments
        X_design = np.column_stack([t, np.ones(len(t))])
        
        for cp in changepoint_locs:
            indicator = (t > cp).astype(float)
            X_design = np.column_stack([X_design, indicator * (t - cp)])
        
        model = LinearRegression()
        model.fit(X_design, y)
        
        return {
            'model': model,
            'changepoints': changepoint_locs,
            'X_design': X_design
        }
    
    def _predict_trend(self, t: np.ndarray) -> np.ndarray:
        """Predict trend values."""
        X_design = np.column_stack([t, np.ones(len(t))])
        
        for cp in self.trend_model['changepoints']:
            indicator = (t > cp).astype(float)
            X_design = np.column_stack([X_design, indicator * (t - cp)])
        
        return self.trend_model['model'].predict(X_design)
    
    def _fit_daily_seasonality(self, timestamps: pd.DatetimeIndex, 
                                residual: np.ndarray) -> np.ndarray:
        """Fit daily seasonality using Fourier series."""
        hours = timestamps.hour + timestamps.minute / 60
        
        # Fourier terms
        n_harmonics = 3
        X_seasonal = np.ones((len(residual), 1))
        
        for i in range(1, n_harmonics + 1):
            X_seasonal = np.column_stack([
                X_seasonal,
                np.sin(2 * np.pi * i * hours / 24),
                np.cos(2 * np.pi * i * hours / 24)
            ])
        
        model = LinearRegression()
        model.fit(X_seasonal, residual)
        
        return model
    
    def _fit_weekly_seasonality(self, timestamps: pd.DatetimeIndex,
                                 residual: np.ndarray) -> np.ndarray:
        """Fit weekly seasonality."""
        days = timestamps.dayofweek + timestamps.hour / 24
        
        n_harmonics = 3
        X_seasonal = np.ones((len(residual), 1))
        
        for i in range(1, n_harmonics + 1):
            X_seasonal = np.column_stack([
                X_seasonal,
                np.sin(2 * np.pi * i * days / 7),
                np.cos(2 * np.pi * i * days / 7)
            ])
        
        model = LinearRegression()
        model.fit(X_seasonal, residual)
        
        return model
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores based on prediction error."""
        X = np.asarray(X)
        
        if len(X.shape) == 1:
            y = X
        else:
            y = X[:, 0]
        
        t = np.arange(len(y))
        timestamps = self.timestamps[:len(y)]
        
        # Predict
        y_pred = self._predict(t, timestamps)
        
        # Compute prediction error
        error = np.abs(y - y_pred)
        
        # Normalize
        threshold = np.percentile(error, 95)
        scores = np.minimum(error / threshold, 1.0)
        
        return scores
    
    def _predict(self, t: np.ndarray, timestamps: pd.DatetimeIndex) -> np.ndarray:
        """Make predictions."""
        # Trend
        trend = self._predict_trend(t)
        
        # Daily seasonality
        hours = timestamps.hour + timestamps.minute / 60
        X_daily = np.ones((len(t), 1))
        for i in range(1, 4):
            X_daily = np.column_stack([
                X_daily,
                np.sin(2 * np.pi * i * hours / 24),
                np.cos(2 * np.pi * i * hours / 24)
            ])
        daily = self.seasonal_components['daily'].predict(X_daily)
        
        # Weekly seasonality
        days = timestamps.dayofweek + timestamps.hour / 24
        X_weekly = np.ones((len(t), 1))
        for i in range(1, 4):
            X_weekly = np.column_stack([
                X_weekly,
                np.sin(2 * np.pi * i * days / 7),
                np.cos(2 * np.pi * i * days / 7)
            ])
        weekly = self.seasonal_components['weekly'].predict(X_weekly)
        
        return trend + daily + weekly


class ChangePointDetector(TimeSeriesAnomalyDetector):
    """
    Detects change points in time series.
    
    Identifies abrupt changes in mean, variance, or trend.
    """
    
    def __init__(self,
                 config: DetectionConfig = None,
                 method: str = 'cusum',
                 threshold: float = 5.0,
                 min_segment_length: int = 10):
        super().__init__("ChangePointDetector", config or DetectionConfig())
        
        self.method = method
        self.threshold = threshold
        self.min_segment_length = min_segment_length
        
        self.change_points: List[int] = []
        self.segments: List[Tuple[int, int]] = []
        
    def fit(self, X: np.ndarray,
            timestamps: Optional[pd.DatetimeIndex] = None) -> 'ChangePointDetector':
        """Detect change points in time series."""
        X = np.asarray(X)
        
        if len(X.shape) == 1:
            series = X
        else:
            series = X[:, 0]
        
        if self.method == 'cusum':
            self.change_points = self._cusum(series)
        elif self.method == 'pelt':
            self.change_points = self._pelt(series)
        elif self.method == 'binary_segmentation':
            self.change_points = self._binary_segmentation(series)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        # Create segments
        self.segments = self._create_segments(len(series))
        
        self.is_fitted = True
        
        self.training_stats = {
            'method': self.method,
            'n_change_points': len(self.change_points),
            'n_segments': len(self.segments)
        }
        
        return self
    
    def _cusum(self, series: np.ndarray) -> List[int]:
        """Cumulative sum change point detection."""
        change_points = []
        
        # Standardize series
        series = (series - np.mean(series)) / (np.std(series) + 1e-10)
        
        # CUSUM statistics
        s_pos = np.zeros(len(series))
        s_neg = np.zeros(len(series))
        
        for t in range(1, len(series)):
            s_pos[t] = max(0, s_pos[t-1] + series[t] - self.threshold)
            s_neg[t] = max(0, s_neg[t-1] - series[t] - self.threshold)
            
            if s_pos[t] > self.threshold or s_neg[t] > self.threshold:
                change_points.append(t)
                s_pos[t] = 0
                s_neg[t] = 0
        
        return change_points
    
    def _pelt(self, series: np.ndarray) -> List[int]:
        """Pruned Exact Linear Time (PELT) algorithm."""
        n = len(series)
        change_points = []
        
        # Cost function (variance)
        def segment_cost(start, end):
            segment = series[start:end]
            if len(segment) < 2:
                return 0
            return np.var(segment) * len(segment)
        
        # Dynamic programming
        F = [0] + [float('inf')] * n
        R = [0]
        
        for t in range(1, n + 1):
            for s in R:
                if t - s >= self.min_segment_length:
                    cost = F[s] + segment_cost(s, t) + self.threshold
                    if cost < F[t]:
                        F[t] = cost
            
            # Pruning
            R = [s for s in R if F[s] + segment_cost(s, t) <= F[t]]
            R.append(t)
        
        # Backtrack to find change points
        t = n
        while t > 0:
            for s in range(t - 1, -1, -1):
                if F[t] == F[s] + segment_cost(s, t) + self.threshold:
                    if s > 0:
                        change_points.append(s)
                    t = s
                    break
        
        return sorted(change_points)
    
    def _binary_segmentation(self, series: np.ndarray) -> List[int]:
        """Binary segmentation for change point detection."""
        change_points = []
        
        def segment_search(start, end):
            if end - start < 2 * self.min_segment_length:
                return
            
            # Find best split point
            best_cost = float('inf')
            best_split = -1
            
            for split in range(start + self.min_segment_length, 
                              end - self.min_segment_length):
                left = series[start:split]
                right = series[split:end]
                
                cost = len(left) * np.var(left) + len(right) * np.var(right)
                
                if cost < best_cost:
                    best_cost = cost
                    best_split = split
            
            # Check if significant
            total_cost = (end - start) * np.var(series[start:end])
            if total_cost - best_cost > self.threshold:
                change_points.append(best_split)
                segment_search(start, best_split)
                segment_search(best_split, end)
        
        segment_search(0, len(series))
        
        return sorted(change_points)
    
    def _create_segments(self, n: int) -> List[Tuple[int, int]]:
        """Create segments from change points."""
        if not self.change_points:
            return [(0, n)]
        
        segments = []
        start = 0
        
        for cp in self.change_points:
            segments.append((start, cp))
            start = cp
        
        segments.append((start, n))
        
        return segments
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.config.threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Score based on distance from segment mean."""
        X = np.asarray(X)
        
        if len(X.shape) == 1:
            series = X
        else:
            series = X[:, 0]
        
        scores = np.zeros(len(series))
        
        for start, end in self.segments:
            segment = series[start:end]
            if len(segment) > 0:
                mean = np.mean(segment)
                std = np.std(segment) + 1e-10
                scores[start:end] = np.abs(segment - mean) / std
        
        return np.minimum(scores / 3.0, 1.0)


# Export classes
__all__ = [
    'TimeSeriesAnomalyDetector', 'StatisticalTimeSeriesDetector',
    'ProphetStyleDetector', 'ChangePointDetector'
]
```

---

## 8. Real-Time Detection Pipeline

### 8.1 Streaming Anomaly Detection

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/realtime.py

import numpy as np
import pandas as pd
from collections import deque
from typing import Dict, List, Optional, Tuple, Union, Callable, Any
from datetime import datetime, timedelta
import threading
import queue
import time
import json

from architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


class StreamingAnomalyDetector:
    """
    Real-time streaming anomaly detection system.
    
    Processes data streams with minimal latency and
    maintains sliding window statistics.
    """
    
    def __init__(self,
                 detector: BaseDetector,
                 window_size: int = 1000,
                 slide_step: int = 1,
                 batch_size: int = 10,
                 max_latency_ms: float = 100):
        self.detector = detector
        self.window_size = window_size
        self.slide_step = slide_step
        self.batch_size = batch_size
        self.max_latency_ms = max_latency_ms
        
        # Data buffer
        self.buffer: deque = deque(maxlen=window_size)
        self.timestamps: deque = deque(maxlen=window_size)
        
        # Processing
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.is_running: bool = False
        self.processing_thread: threading.Thread = None
        
        # Statistics
        self.detection_count: int = 0
        self.anomaly_count: int = 0
        self.avg_processing_time_ms: float = 0.0
        
        # Callbacks
        self.anomaly_callbacks: List[Callable] = []
        
    def start(self):
        """Start the streaming detector."""
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_loop)
        self.processing_thread.start()
        logger.info("Streaming detector started")
    
    def stop(self):
        """Stop the streaming detector."""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        logger.info("Streaming detector stopped")
    
    def ingest(self, data: np.ndarray, timestamp: Optional[datetime] = None):
        """Ingest new data point(s)."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Add to buffer
        if len(data.shape) == 1:
            self.buffer.append(data)
            self.timestamps.append(timestamp)
        else:
            for i, row in enumerate(data):
                self.buffer.append(row)
                self.timestamps.append(timestamp + timedelta(milliseconds=i))
        
        # Add to processing queue
        self.input_queue.put((data, timestamp))
    
    def _process_loop(self):
        """Main processing loop."""
        batch = []
        batch_timestamps = []
        
        while self.is_running:
            try:
                # Collect batch
                data, timestamp = self.input_queue.get(timeout=0.1)
                batch.append(data)
                batch_timestamps.append(timestamp)
                
                if len(batch) >= self.batch_size:
                    self._process_batch(batch, batch_timestamps)
                    batch = []
                    batch_timestamps = []
                    
            except queue.Empty:
                # Process remaining batch
                if batch:
                    self._process_batch(batch, batch_timestamps)
                    batch = []
                    batch_timestamps = []
    
    def _process_batch(self, batch: List[np.ndarray], 
                       timestamps: List[datetime]):
        """Process a batch of data."""
        start_time = time.time()
        
        # Convert to array
        X = np.array(batch)
        if len(X.shape) == 3:  # Flatten if needed
            X = X.reshape(-1, X.shape[-1])
        
        # Detect anomalies
        if len(self.buffer) >= self.detector.config.min_samples:
            # Use sliding window
            window_data = np.array(list(self.buffer)[-self.window_size:])
            
            # Update detector with recent data (optional incremental update)
            # self.detector.partial_fit(window_data)
            
            # Detect
            results = self.detector.detect(X)
            
            # Process results
            for i, result in enumerate(results):
                self.detection_count += 1
                
                if result.is_anomaly:
                    self.anomaly_count += 1
                    
                    # Trigger callbacks
                    for callback in self.anomaly_callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                
                # Add to output queue
                self.output_queue.put(result)
        
        # Update statistics
        processing_time = (time.time() - start_time) * 1000
        self.avg_processing_time_ms = (
            0.9 * self.avg_processing_time_ms + 0.1 * processing_time
        )
    
    def add_anomaly_callback(self, callback: Callable):
        """Add callback for anomaly events."""
        self.anomaly_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        return {
            'detection_count': self.detection_count,
            'anomaly_count': self.anomaly_count,
            'anomaly_rate': self.anomaly_count / max(self.detection_count, 1),
            'avg_processing_time_ms': self.avg_processing_time_ms,
            'buffer_size': len(self.buffer),
            'queue_size': self.input_queue.qsize()
        }


class AdaptiveThresholdDetector(BaseDetector):
    """
    Detector with adaptive threshold based on recent data distribution.
    """
    
    def __init__(self,
                 base_detector: BaseDetector,
                 config: DetectionConfig = None,
                 adaptation_rate: float = 0.1,
                 window_size: int = 100):
        super().__init__(f"Adaptive_{base_detector.name}", config or DetectionConfig())
        
        self.base_detector = base_detector
        self.adaptation_rate = adaptation_rate
        self.window_size = window_size
        
        self.score_history: deque = deque(maxlen=window_size)
        self.adaptive_threshold: float = config.threshold if config else 0.5
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'AdaptiveThresholdDetector':
        """Fit base detector."""
        self.base_detector.fit(X, y)
        
        # Initialize threshold from training scores
        scores = self.base_detector.score_samples(X)
        self.adaptive_threshold = np.percentile(scores, 90)
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return np.where(scores > self.adaptive_threshold, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Score and update adaptive threshold."""
        scores = self.base_detector.score_samples(X)
        
        # Update history
        for score in scores:
            self.score_history.append(score)
        
        # Adapt threshold
        if len(self.score_history) >= 10:
            recent_scores = list(self.score_history)[-self.window_size:]
            target_threshold = np.percentile(recent_scores, 90)
            self.adaptive_threshold = (
                (1 - self.adaptation_rate) * self.adaptive_threshold +
                self.adaptation_rate * target_threshold
            )
        
        return scores


class EnsembleRealTimeDetector:
    """
    Real-time ensemble of multiple detectors with voting.
    """
    
    def __init__(self,
                 detectors: Dict[str, BaseDetector],
                 weights: Optional[Dict[str, float]] = None,
                 voting_strategy: str = 'weighted_average'):
        self.detectors = detectors
        self.weights = weights or {name: 1.0 for name in detectors}
        self.voting_strategy = voting_strategy
        
        # Streaming components
        self.streaming_detectors: Dict[str, StreamingAnomalyDetector] = {}
        self.results_buffer: Dict[str, deque] = {}
        
    def initialize_streaming(self, window_size: int = 1000):
        """Initialize streaming for all detectors."""
        for name, detector in self.detectors.items():
            self.streaming_detectors[name] = StreamingAnomalyDetector(
                detector, window_size=window_size
            )
            self.results_buffer[name] = deque(maxlen=window_size)
    
    def start(self):
        """Start all streaming detectors."""
        for detector in self.streaming_detectors.values():
            detector.start()
    
    def stop(self):
        """Stop all streaming detectors."""
        for detector in self.streaming_detectors.values():
            detector.stop()
    
    def ingest(self, data: np.ndarray, timestamp: Optional[datetime] = None):
        """Ingest data to all detectors."""
        for detector in self.streaming_detectors.values():
            detector.ingest(data, timestamp)
    
    def get_ensemble_result(self) -> Optional[AnomalyScore]:
        """Get aggregated ensemble result."""
        # Collect latest results from all detectors
        latest_results = {}
        
        for name, detector in self.streaming_detectors.items():
            try:
                result = detector.output_queue.get_nowait()
                latest_results[name] = result
            except queue.Empty:
                pass
        
        if not latest_results:
            return None
        
        # Aggregate based on voting strategy
        if self.voting_strategy == 'weighted_average':
            return self._weighted_average_vote(latest_results)
        elif self.voting_strategy == 'majority':
            return self._majority_vote(latest_results)
        else:
            return self._weighted_average_vote(latest_results)
    
    def _weighted_average_vote(self, results: Dict[str, AnomalyScore]) -> AnomalyScore:
        """Weighted average of detector scores."""
        total_weight = 0.0
        weighted_score = 0.0
        any_anomaly = False
        max_severity = AlertSeverity.LOW
        
        for name, result in results.items():
            weight = self.weights.get(name, 1.0)
            weighted_score += result.score * weight
            total_weight += weight
            any_anomaly = any_anomaly or result.is_anomaly
            
            if result.severity.value > max_severity.value:
                max_severity = result.severity
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0.5
        
        return AnomalyScore(
            score=final_score,
            is_anomaly=final_score > 0.5 or any_anomaly,
            confidence=np.mean([r.confidence for r in results.values()]),
            anomaly_type=AnomalyType.POINT,
            severity=max_severity,
            timestamp=datetime.now(),
            feature_contributions={},
            metadata={'ensemble': True, 'detectors': list(results.keys())}
        )
    
    def _majority_vote(self, results: Dict[str, AnomalyScore]) -> AnomalyScore:
        """Majority voting among detectors."""
        anomaly_votes = sum(1 for r in results.values() if r.is_anomaly)
        is_anomaly = anomaly_votes > len(results) / 2
        
        avg_score = np.mean([r.score for r in results.values()])
        
        return AnomalyScore(
            score=avg_score,
            is_anomaly=is_anomaly,
            confidence=anomaly_votes / len(results),
            anomaly_type=AnomalyType.POINT,
            severity=AlertSeverity.HIGH if is_anomaly else AlertSeverity.LOW,
            timestamp=datetime.now(),
            feature_contributions={},
            metadata={'ensemble': True, 'vote_type': 'majority'}
        )


# Export classes
__all__ = [
    'StreamingAnomalyDetector', 'AdaptiveThresholdDetector',
    'EnsembleRealTimeDetector'
]
```



---

## 9. Anomaly Scoring System

### 9.1 Comprehensive Scoring Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/scoring.py

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import json

from architecture import AnomalyScore, AnomalyType, AlertSeverity


class AnomalyScorer:
    """
    Comprehensive anomaly scoring system.
    
    Combines multiple scoring approaches for robust anomaly ranking.
    """
    
    SCORING_METHODS = ['normalized', 'percentile', 'zscore', 'sigmoid', 'logistic']
    
    def __init__(self,
                 method: str = 'normalized',
                 calibration_data: Optional[np.ndarray] = None):
        self.method = method
        self.calibration_data = calibration_data
        
        self.score_stats = {
            'min': 0.0,
            'max': 1.0,
            'mean': 0.5,
            'std': 0.25
        }
        
        if calibration_data is not None:
            self._calibrate(calibration_data)
    
    def _calibrate(self, scores: np.ndarray):
        """Calibrate scoring using reference data."""
        self.score_stats = {
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)) + 1e-10,
            'q05': float(np.percentile(scores, 5)),
            'q95': float(np.percentile(scores, 95))
        }
    
    def score(self, raw_scores: np.ndarray) -> np.ndarray:
        """Convert raw scores to normalized anomaly scores."""
        if self.method == 'normalized':
            return self._normalized_score(raw_scores)
        elif self.method == 'percentile':
            return self._percentile_score(raw_scores)
        elif self.method == 'zscore':
            return self._zscore_score(raw_scores)
        elif self.method == 'sigmoid':
            return self._sigmoid_score(raw_scores)
        elif self.method == 'logistic':
            return self._logistic_score(raw_scores)
        else:
            raise ValueError(f"Unknown scoring method: {self.method}")
    
    def _normalized_score(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalization to [0, 1]."""
        min_val = self.score_stats['min']
        max_val = self.score_stats['max']
        
        if max_val > min_val:
            normalized = (scores - min_val) / (max_val - min_val)
        else:
            normalized = np.ones_like(scores) * 0.5
        
        return np.clip(normalized, 0, 1)
    
    def _percentile_score(self, scores: np.ndarray) -> np.ndarray:
        """Convert to percentile-based scores."""
        if self.calibration_data is not None:
            percentiles = np.array([
                np.mean(self.calibration_data <= s) for s in scores
            ])
        else:
            # Use empirical CDF
            percentiles = np.array([
                np.mean(scores <= s) for s in scores
            ])
        
        return percentiles
    
    def _zscore_score(self, scores: np.ndarray) -> np.ndarray:
        """Convert Z-scores to anomaly scores."""
        mean = self.score_stats['mean']
        std = self.score_stats['std']
        
        z_scores = (scores - mean) / std
        
        # Convert to [0, 1] using sigmoid-like function
        return 1 / (1 + np.exp(-z_scores))
    
    def _sigmoid_score(self, scores: np.ndarray) -> np.ndarray:
        """Apply sigmoid transformation."""
        mean = self.score_stats['mean']
        std = self.score_stats['std'] * 2
        
        return 1 / (1 + np.exp(-(scores - mean) / std))
    
    def _logistic_score(self, scores: np.ndarray) -> np.ndarray:
        """Logistic transformation with calibration."""
        q05 = self.score_stats.get('q05', np.percentile(scores, 5))
        q95 = self.score_stats.get('q95', np.percentile(scores, 95))
        
        # Scale to logistic range
        scaled = (scores - q05) / (q95 - q05 + 1e-10)
        
        # Apply logistic
        return 1 / (1 + np.exp(-10 * (scaled - 0.5)))


class MultiFactorScorer:
    """
    Multi-factor anomaly scoring combining multiple indicators.
    """
    
    def __init__(self,
                 factors: Dict[str, Dict[str, float]] = None,
                 combination_method: str = 'weighted_product'):
        """
        Initialize multi-factor scorer.
        
        Args:
            factors: Dict of factor configs with 'weight' and 'threshold'
            combination_method: 'weighted_sum', 'weighted_product', 'geometric_mean'
        """
        self.factors = factors or {
            'statistical': {'weight': 0.25, 'threshold': 0.5},
            'isolation_forest': {'weight': 0.25, 'threshold': 0.5},
            'autoencoder': {'weight': 0.25, 'threshold': 0.5},
            'clustering': {'weight': 0.25, 'threshold': 0.5}
        }
        self.combination_method = combination_method
        
    def compute_score(self, factor_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Compute combined anomaly score.
        
        Returns:
            Tuple of (combined_score, factor_contributions)
        """
        # Normalize factor scores
        normalized_scores = {}
        for factor, score in factor_scores.items():
            if factor in self.factors:
                threshold = self.factors[factor]['threshold']
                # Normalize relative to threshold
                normalized = min(score / threshold, 1.0) if threshold > 0 else score
                normalized_scores[factor] = normalized
        
        # Combine scores
        if self.combination_method == 'weighted_sum':
            combined = self._weighted_sum(normalized_scores)
        elif self.combination_method == 'weighted_product':
            combined = self._weighted_product(normalized_scores)
        elif self.combination_method == 'geometric_mean':
            combined = self._geometric_mean(normalized_scores)
        else:
            combined = self._weighted_sum(normalized_scores)
        
        # Compute contributions
        contributions = self._compute_contributions(normalized_scores, combined)
        
        return combined, contributions
    
    def _weighted_sum(self, scores: Dict[str, float]) -> float:
        """Weighted sum of scores."""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for factor, score in scores.items():
            weight = self.factors[factor]['weight']
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def _weighted_product(self, scores: Dict[str, float]) -> float:
        """Weighted geometric mean (product)."""
        log_sum = 0.0
        total_weight = 0.0
        
        for factor, score in scores.items():
            weight = self.factors[factor]['weight']
            # Avoid log(0)
            safe_score = max(score, 1e-10)
            log_sum += weight * np.log(safe_score)
            total_weight += weight
        
        return np.exp(log_sum / total_weight) if total_weight > 0 else 0.5
    
    def _geometric_mean(self, scores: Dict[str, float]) -> float:
        """Simple geometric mean."""
        values = list(scores.values())
        if not values:
            return 0.5
        
        log_sum = sum(np.log(max(v, 1e-10)) for v in values)
        return np.exp(log_sum / len(values))
    
    def _compute_contributions(self, scores: Dict[str, float], 
                               combined: float) -> Dict[str, float]:
        """Compute each factor's contribution to final score."""
        contributions = {}
        
        for factor, score in scores.items():
            weight = self.factors[factor]['weight']
            # Contribution is weighted score relative to combined
            if combined > 0:
                contributions[factor] = (score * weight) / combined
            else:
                contributions[factor] = weight
        
        return contributions


class TemporalScorer:
    """
    Temporal anomaly scoring with persistence and trend analysis.
    """
    
    def __init__(self,
                 persistence_window: int = 5,
                 trend_window: int = 10,
                 persistence_weight: float = 0.3,
                 trend_weight: float = 0.2):
        self.persistence_window = persistence_window
        self.trend_window = trend_window
        self.persistence_weight = persistence_weight
        self.trend_weight = trend_weight
        
        self.score_history: deque = deque(maxlen=trend_window)
        self.anomaly_history: deque = deque(maxlen=persistence_window)
        
    def score(self, current_score: float, is_anomaly: bool) -> float:
        """
        Compute temporal-adjusted anomaly score.
        
        Factors:
        - Current score
        - Persistence (how long anomaly state persists)
        - Trend (increasing or decreasing anomaly likelihood)
        """
        # Update history
        self.score_history.append(current_score)
        self.anomaly_history.append(is_anomaly)
        
        # Base score
        base_score = current_score
        
        # Persistence factor
        persistence_factor = self._compute_persistence()
        
        # Trend factor
        trend_factor = self._compute_trend()
        
        # Combine
        adjusted_score = (
            base_score * (1 - self.persistence_weight - self.trend_weight) +
            persistence_factor * self.persistence_weight +
            trend_factor * self.trend_weight
        )
        
        return min(adjusted_score, 1.0)
    
    def _compute_persistence(self) -> float:
        """Compute persistence factor based on recent anomaly history."""
        if not self.anomaly_history:
            return 0.0
        
        # Count consecutive anomalies at the end
        consecutive = 0
        for is_anom in reversed(self.anomaly_history):
            if is_anom:
                consecutive += 1
            else:
                break
        
        # Normalize
        return min(consecutive / self.persistence_window, 1.0)
    
    def _compute_trend(self) -> float:
        """Compute trend factor based on score trajectory."""
        if len(self.score_history) < 2:
            return 0.5
        
        scores = list(self.score_history)
        
        # Linear trend
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        # Normalize slope to [0, 1]
        # Positive slope = increasing anomaly likelihood
        normalized_trend = 1 / (1 + np.exp(-slope * 10))
        
        return normalized_trend


class ConfidenceEstimator:
    """
    Estimates confidence in anomaly detection results.
    """
    
    def __init__(self,
                 use_score_variance: bool = True,
                 use_detector_agreement: bool = True,
                 use_historical_accuracy: bool = True):
        self.use_score_variance = use_score_variance
        self.use_detector_agreement = use_detector_agreement
        self.use_historical_accuracy = use_historical_accuracy
        
        self.historical_results: deque = deque(maxlen=1000)
        self.detector_agreement_history: Dict[str, deque] = {}
        
    def estimate_confidence(self,
                           score: float,
                           detector_scores: Optional[Dict[str, float]] = None,
                           historical_accuracy: Optional[float] = None) -> float:
        """
        Estimate confidence in anomaly detection.
        
        Returns confidence in [0, 1] where higher = more confident.
        """
        confidence_factors = []
        
        # Score-based confidence (extreme scores = more confident)
        if self.use_score_variance:
            score_confidence = self._score_based_confidence(score)
            confidence_factors.append(score_confidence)
        
        # Detector agreement
        if self.use_detector_agreement and detector_scores:
            agreement_confidence = self._detector_agreement_confidence(detector_scores)
            confidence_factors.append(agreement_confidence)
        
        # Historical accuracy
        if self.use_historical_accuracy and historical_accuracy is not None:
            confidence_factors.append(historical_accuracy)
        
        # Combine confidence factors
        if confidence_factors:
            return np.mean(confidence_factors)
        else:
            return 0.5
    
    def _score_based_confidence(self, score: float) -> float:
        """Confidence based on how extreme the score is."""
        # Scores near 0 or 1 are more confident
        distance_from_center = abs(score - 0.5) * 2
        return distance_from_center
    
    def _detector_agreement_confidence(self, 
                                       detector_scores: Dict[str, float]) -> float:
        """Confidence based on agreement between detectors."""
        if len(detector_scores) < 2:
            return 0.5
        
        scores = list(detector_scores.values())
        
        # Lower variance = higher agreement = higher confidence
        variance = np.var(scores)
        agreement = 1 - min(variance * 4, 1.0)
        
        return agreement
    
    def update_historical(self, result: AnomalyScore, was_true_anomaly: bool):
        """Update historical accuracy tracking."""
        self.historical_results.append({
            'predicted': result.is_anomaly,
            'actual': was_true_anomaly,
            'score': result.score,
            'timestamp': result.timestamp
        })
    
    def get_historical_accuracy(self) -> float:
        """Get historical detection accuracy."""
        if not self.historical_results:
            return 0.5
        
        results = list(self.historical_results)
        correct = sum(1 for r in results if r['predicted'] == r['actual'])
        
        return correct / len(results)


class SeverityClassifier:
    """
    Classifies anomaly severity based on multiple factors.
    """
    
    SEVERITY_THRESHOLDS = {
        AlertSeverity.LOW: (0.0, 0.5),
        AlertSeverity.MEDIUM: (0.5, 0.7),
        AlertSeverity.HIGH: (0.7, 0.9),
        AlertSeverity.CRITICAL: (0.9, 1.0)
    }
    
    def __init__(self,
                 score_thresholds: Dict[AlertSeverity, Tuple[float, float]] = None,
                 use_impact_assessment: bool = True):
        self.score_thresholds = score_thresholds or self.SEVERITY_THRESHOLDS
        self.use_impact_assessment = use_impact_assessment
        
    def classify(self,
                 score: float,
                 impact_score: Optional[float] = None,
                 business_criticality: Optional[float] = None) -> AlertSeverity:
        """
        Classify anomaly severity.
        
        Args:
            score: Anomaly score
            impact_score: Estimated business impact [0, 1]
            business_criticality: Business criticality of the data [0, 1]
        
        Returns:
            AlertSeverity enum value
        """
        # Base severity from score
        base_severity = self._score_to_severity(score)
        
        if not self.use_impact_assessment:
            return base_severity
        
        # Adjust based on impact
        adjusted_score = score
        
        if impact_score is not None:
            adjusted_score = max(adjusted_score, score * (0.5 + 0.5 * impact_score))
        
        if business_criticality is not None:
            adjusted_score = max(adjusted_score, score * (0.5 + 0.5 * business_criticality))
        
        return self._score_to_severity(adjusted_score)
    
    def _score_to_severity(self, score: float) -> AlertSeverity:
        """Convert score to severity level."""
        for severity, (low, high) in self.score_thresholds.items():
            if low <= score < high:
                return severity
        
        return AlertSeverity.CRITICAL


# Export classes
__all__ = [
    'AnomalyScorer', 'MultiFactorScorer', 'TemporalScorer',
    'ConfidenceEstimator', 'SeverityClassifier'
]
```

---

## 10. Alert Generation

### 10.1 Comprehensive Alert System

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/alerts.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging

from architecture import AnomalyScore, AlertSeverity, AnomalyType

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Supported alert channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    CONSOLE = "console"
    DATABASE = "database"


@dataclass
class Alert:
    """Represents an anomaly alert."""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    anomaly_type: AnomalyType
    score: float
    confidence: float
    title: str
    description: str
    source: str
    affected_metrics: List[str]
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'anomaly_type': self.anomaly_type.value,
            'score': self.score,
            'confidence': self.confidence,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'affected_metrics': self.affected_metrics,
            'recommended_actions': self.recommended_actions,
            'metadata': self.metadata,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'resolution_time': self.resolution_time.isoformat() if self.resolution_time else None
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class AlertRule:
    """Rule for generating alerts from anomaly scores."""
    
    def __init__(self,
                 name: str,
                 severity_threshold: AlertSeverity,
                 min_score: float,
                 min_confidence: float = 0.5,
                 cooldown_minutes: int = 15,
                 channels: List[AlertChannel] = None,
                 filters: Dict[str, Any] = None):
        self.name = name
        self.severity_threshold = severity_threshold
        self.min_score = min_score
        self.min_confidence = min_confidence
        self.cooldown_minutes = cooldown_minutes
        self.channels = channels or [AlertChannel.CONSOLE]
        self.filters = filters or {}
        
        self.last_alert_time: Optional[datetime] = None
        self.alert_count: int = 0
        
    def should_alert(self, anomaly_score: AnomalyScore) -> bool:
        """Check if this rule should generate an alert."""
        # Check severity
        severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, 
                         AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        if severity_order.index(anomaly_score.severity) < \
           severity_order.index(self.severity_threshold):
            return False
        
        # Check score threshold
        if anomaly_score.score < self.min_score:
            return False
        
        # Check confidence
        if anomaly_score.confidence < self.min_confidence:
            return False
        
        # Check cooldown
        if self.last_alert_time:
            elapsed = datetime.now() - self.last_alert_time
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                return False
        
        # Apply filters
        for key, value in self.filters.items():
            if key in anomaly_score.metadata:
                if anomaly_score.metadata[key] != value:
                    return False
        
        return True
    
    def record_alert(self):
        """Record that an alert was generated."""
        self.last_alert_time = datetime.now()
        self.alert_count += 1


class AlertManager:
    """
    Centralized alert management system.
    """
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.channel_handlers: Dict[AlertChannel, Callable] = {}
        self.suppression_rules: List[Callable] = []
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default alert channel handlers."""
        self.channel_handlers[AlertChannel.CONSOLE] = self._send_console_alert
        self.channel_handlers[AlertChannel.DATABASE] = self._send_database_alert
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule."""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def register_channel_handler(self, 
                                  channel: AlertChannel, 
                                  handler: Callable):
        """Register a handler for an alert channel."""
        self.channel_handlers[channel] = handler
    
    def add_suppression_rule(self, rule: Callable):
        """Add a suppression rule."""
        self.suppression_rules.append(rule)
    
    def process_anomaly(self, anomaly_score: AnomalyScore,
                       source: str = "unknown") -> List[Alert]:
        """
        Process an anomaly score and generate alerts.
        
        Returns:
            List of generated alerts
        """
        # Check suppression rules
        for rule in self.suppression_rules:
            if rule(anomaly_score):
                logger.debug(f"Alert suppressed for anomaly: {anomaly_score}")
                return []
        
        generated_alerts = []
        
        # Check each rule
        for rule in self.rules:
            if rule.should_alert(anomaly_score):
                # Generate alert
                alert = self._create_alert(anomaly_score, source, rule)
                
                # Send to channels
                for channel in rule.channels:
                    self._send_alert(alert, channel)
                
                rule.record_alert()
                generated_alerts.append(alert)
                self.alert_history.append(alert)
        
        return generated_alerts
    
    def _create_alert(self, 
                     anomaly_score: AnomalyScore,
                     source: str,
                     rule: AlertRule) -> Alert:
        """Create an alert from anomaly score."""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.alert_history)}"
        
        # Generate title and description
        title = self._generate_title(anomaly_score)
        description = self._generate_description(anomaly_score)
        
        # Get affected metrics
        affected_metrics = list(anomaly_score.feature_contributions.keys())
        
        # Generate recommendations
        recommendations = self._generate_recommendations(anomaly_score)
        
        return Alert(
            id=alert_id,
            timestamp=anomaly_score.timestamp,
            severity=anomaly_score.severity,
            anomaly_type=anomaly_score.anomaly_type,
            score=anomaly_score.score,
            confidence=anomaly_score.confidence,
            title=title,
            description=description,
            source=source,
            affected_metrics=affected_metrics,
            recommended_actions=recommendations,
            metadata={
                'rule': rule.name,
                **anomaly_score.metadata
            }
        )
    
    def _generate_title(self, anomaly_score: AnomalyScore) -> str:
        """Generate alert title."""
        severity_str = anomaly_score.severity.value.upper()
        type_str = anomaly_score.anomaly_type.value
        
        return f"[{severity_str}] {type_str} Anomaly Detected (Score: {anomaly_score.score:.2f})"
    
    def _generate_description(self, anomaly_score: AnomalyScore) -> str:
        """Generate alert description."""
        lines = [
            f"Anomaly detected with score {anomaly_score.score:.4f} "
            f"and confidence {anomaly_score.confidence:.2%}",
            "",
            "Top contributing features:"
        ]
        
        # Add top features
        sorted_features = sorted(
            anomaly_score.feature_contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for feature, contribution in sorted_features:
            lines.append(f"  - {feature}: {contribution:.2%}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, anomaly_score: AnomalyScore) -> List[str]:
        """Generate recommended actions based on anomaly."""
        recommendations = []
        
        if anomaly_score.severity == AlertSeverity.CRITICAL:
            recommendations.extend([
                "Immediately investigate the affected metrics",
                "Consider pausing related data pipelines",
                "Notify on-call engineer"
            ])
        elif anomaly_score.severity == AlertSeverity.HIGH:
            recommendations.extend([
                "Investigate within 30 minutes",
                "Check related systems for issues",
                "Monitor for recurrence"
            ])
        elif anomaly_score.severity == AlertSeverity.MEDIUM:
            recommendations.extend([
                "Review during next business day",
                "Add to monitoring dashboard",
                "Document for pattern analysis"
            ])
        else:
            recommendations.extend([
                "Log for future reference",
                "Include in weekly report"
            ])
        
        return recommendations
    
    def _send_alert(self, alert: Alert, channel: AlertChannel):
        """Send alert to specified channel."""
        handler = self.channel_handlers.get(channel)
        
        if handler:
            try:
                handler(alert)
                logger.info(f"Alert {alert.id} sent to {channel.value}")
            except Exception as e:
                logger.error(f"Failed to send alert to {channel.value}: {e}")
        else:
            logger.warning(f"No handler for channel: {channel.value}")
    
    def _send_console_alert(self, alert: Alert):
        """Send alert to console."""
        print(f"\n{'='*60}")
        print(f"ALERT: {alert.title}")
        print(f"{'='*60}")
        print(f"ID: {alert.id}")
        print(f"Severity: {alert.severity.value}")
        print(f"Score: {alert.score:.4f}")
        print(f"Source: {alert.source}")
        print(f"\n{alert.description}")
        print(f"\nRecommended Actions:")
        for action in alert.recommended_actions:
            print(f"  - {action}")
        print(f"{'='*60}\n")
    
    def _send_database_alert(self, alert: Alert):
        """Store alert in database."""
        # Placeholder for database storage
        logger.info(f"Alert {alert.id} stored in database")
    
    def configure_email(self,
                       smtp_server: str,
                       smtp_port: int,
                       username: str,
                       password: str,
                       from_address: str,
                       to_addresses: List[str]):
        """Configure email alert handler."""
        def email_handler(alert: Alert):
            msg = MIMEMultipart()
            msg['From'] = from_address
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = alert.title
            
            body = alert.to_json()
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
        
        self.channel_handlers[AlertChannel.EMAIL] = email_handler
    
    def configure_slack(self, webhook_url: str):
        """Configure Slack alert handler."""
        def slack_handler(alert: Alert):
            color = {
                AlertSeverity.LOW: '#36a64f',
                AlertSeverity.MEDIUM: '#daa520',
                AlertSeverity.HIGH: '#ff8c00',
                AlertSeverity.CRITICAL: '#dc143c'
            }.get(alert.severity, '#808080')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': alert.title,
                    'text': alert.description,
                    'fields': [
                        {'title': 'Score', 'value': f"{alert.score:.4f}", 'short': True},
                        {'title': 'Confidence', 'value': f"{alert.confidence:.2%}", 'short': True},
                        {'title': 'Source', 'value': alert.source, 'short': True}
                    ],
                    'footer': 'ResilienceAI Anomaly Detection',
                    'ts': alert.timestamp.timestamp()
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        
        self.channel_handlers[AlertChannel.SLACK] = slack_handler
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        if not self.alert_history:
            return {'total_alerts': 0}
        
        df = pd.DataFrame([a.to_dict() for a in self.alert_history])
        
        return {
            'total_alerts': len(self.alert_history),
            'alerts_by_severity': df['severity'].value_counts().to_dict(),
            'alerts_by_type': df['anomaly_type'].value_counts().to_dict(),
            'acknowledged_rate': df['acknowledged'].mean(),
            'resolved_rate': df['resolved'].mean(),
            'avg_resolution_time_minutes': self._avg_resolution_time()
        }
    
    def _avg_resolution_time(self) -> Optional[float]:
        """Calculate average resolution time in minutes."""
        resolved = [a for a in self.alert_history 
                   if a.resolved and a.resolution_time]
        
        if not resolved:
            return None
        
        times = [(a.resolution_time - a.timestamp).total_seconds() / 60 
                for a in resolved]
        
        return np.mean(times)


# Export classes
__all__ = [
    'AlertChannel', 'Alert', 'AlertRule', 'AlertManager'
]
```



---

## 11. Visualization Dashboards

### 11.1 Anomaly Visualization Components

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/visualization.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
import seaborn as sns
from collections import deque
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from architecture import AnomalyScore, AlertSeverity, AnomalyType


class AnomalyVisualizer:
    """
    Comprehensive anomaly visualization system.
    """
    
    def __init__(self, style: str = 'seaborn'):
        self.style = style
        plt.style.use(style)
        
        # Color scheme for severity levels
        self.severity_colors = {
            AlertSeverity.LOW: '#2ecc71',      # Green
            AlertSeverity.MEDIUM: '#f39c12',   # Orange
            AlertSeverity.HIGH: '#e74c3c',     # Red
            AlertSeverity.CRITICAL: '#8e44ad'  # Purple
        }
        
        # Color scheme for anomaly types
        self.type_colors = {
            AnomalyType.POINT: '#3498db',
            AnomalyType.CONTEXTUAL: '#9b59b6',
            AnomalyType.COLLECTIVE: '#e67e22',
            AnomalyType.TEMPORAL: '#1abc9c',
            AnomalyType.SPATIAL: '#34495e'
        }
    
    def plot_time_series_with_anomalies(self,
                                        timestamps: pd.DatetimeIndex,
                                        values: np.ndarray,
                                        anomaly_scores: List[AnomalyScore],
                                        title: str = "Time Series with Anomalies",
                                        figsize: Tuple[int, int] = (15, 8),
                                        save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot time series with anomaly markers.
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True,
                                 gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # Main time series
        ax1 = axes[0]
        ax1.plot(timestamps, values, color='#2c3e50', linewidth=1, label='Value')
        ax1.set_ylabel('Value')
        ax1.set_title(title)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Mark anomalies
        for score in anomaly_scores:
            if score.is_anomaly:
                color = self.severity_colors.get(score.severity, '#95a5a6')
                ax1.axvline(x=score.timestamp, color=color, alpha=0.3, linestyle='--')
        
        # Anomaly scores
        ax2 = axes[1]
        scores = [s.score for s in anomaly_scores]
        score_times = [s.timestamp for s in anomaly_scores]
        
        ax2.fill_between(score_times, scores, alpha=0.5, color='#3498db')
        ax2.plot(score_times, scores, color='#2980b9', linewidth=1)
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Threshold')
        ax2.set_ylabel('Anomaly Score')
        ax2.set_ylim(0, 1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Severity timeline
        ax3 = axes[2]
        severity_map = {AlertSeverity.LOW: 1, AlertSeverity.MEDIUM: 2,
                       AlertSeverity.HIGH: 3, AlertSeverity.CRITICAL: 4}
        severities = [severity_map.get(s.severity, 0) for s in anomaly_scores]
        
        colors = [self.severity_colors.get(s.severity, '#95a5a6') 
                 for s in anomaly_scores]
        
        ax3.scatter(score_times, severities, c=colors, s=50, alpha=0.7)
        ax3.set_ylabel('Severity')
        ax3.set_yticks([1, 2, 3, 4])
        ax3.set_yticklabels(['Low', 'Medium', 'High', 'Critical'])
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_anomaly_heatmap(self,
                            anomaly_scores: List[AnomalyScore],
                            feature_names: List[str],
                            title: str = "Feature Contribution Heatmap",
                            figsize: Tuple[int, int] = (12, 8),
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot heatmap of feature contributions over time.
        """
        # Extract feature contributions
        data = []
        timestamps = []
        
        for score in anomaly_scores:
            row = [score.feature_contributions.get(f, 0) for f in feature_names]
            data.append(row)
            timestamps.append(score.timestamp)
        
        df = pd.DataFrame(data, columns=feature_names, index=timestamps)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(df.T, cmap='YlOrRd', cbar_kws={'label': 'Contribution'},
                   ax=ax, xticklabels=False)
        
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Features')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_anomaly_distribution(self,
                                  anomaly_scores: List[AnomalyScore],
                                  title: str = "Anomaly Score Distribution",
                                  figsize: Tuple[int, int] = (12, 5),
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distribution of anomaly scores and severities.
        """
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Score distribution
        ax1 = axes[0]
        scores = [s.score for s in anomaly_scores]
        
        ax1.hist(scores, bins=50, alpha=0.7, color='#3498db', edgecolor='black')
        ax1.axvline(x=0.5, color='red', linestyle='--', label='Threshold')
        ax1.set_xlabel('Anomaly Score')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Score Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Severity distribution
        ax2 = axes[1]
        severities = [s.severity for s in anomaly_scores]
        severity_counts = pd.Series(severities).value_counts()
        
        colors = [self.severity_colors.get(s, '#95a5a6') for s in severity_counts.index]
        ax2.bar(range(len(severity_counts)), severity_counts.values, color=colors)
        ax2.set_xticks(range(len(severity_counts)))
        ax2.set_xticklabels([s.value for s in severity_counts.index], rotation=45)
        ax2.set_ylabel('Count')
        ax2.set_title('Severity Distribution')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_detector_comparison(self,
                                 detector_results: Dict[str, List[AnomalyScore]],
                                 title: str = "Detector Comparison",
                                 figsize: Tuple[int, int] = (14, 8),
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Compare anomaly scores from multiple detectors.
        """
        fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        # Score comparison
        ax1 = axes[0]
        
        for detector_name, scores in detector_results.items():
            score_values = [s.score for s in scores]
            timestamps = [s.timestamp for s in scores]
            ax1.plot(timestamps, score_values, label=detector_name, alpha=0.7)
        
        ax1.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Threshold')
        ax1.set_ylabel('Anomaly Score')
        ax1.set_title('Detector Score Comparison')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # Anomaly agreement
        ax2 = axes[1]
        
        # Count how many detectors flagged each point as anomaly
        n_detectors = len(detector_results)
        detector_names = list(detector_results.keys())
        
        if detector_results:
            n_samples = len(list(detector_results.values())[0])
            agreement = np.zeros(n_samples)
            
            for scores in detector_results.values():
                for i, s in enumerate(scores):
                    if s.is_anomaly:
                        agreement[i] += 1
            
            timestamps = [list(detector_results.values())[0][i].timestamp 
                         for i in range(n_samples)]
            
            ax2.fill_between(timestamps, agreement / n_detectors, alpha=0.5, color='#9b59b6')
            ax2.plot(timestamps, agreement / n_detectors, color='#8e44ad', linewidth=1)
            ax2.set_ylabel('Detector Agreement')
            ax2.set_xlabel('Time')
            ax2.set_title('Anomaly Detection Agreement')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig
    
    def create_interactive_dashboard(self,
                                     timestamps: pd.DatetimeIndex,
                                     values: np.ndarray,
                                     anomaly_scores: List[AnomalyScore],
                                     title: str = "Anomaly Detection Dashboard") -> go.Figure:
        """
        Create interactive Plotly dashboard.
        """
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=('Time Series', 'Anomaly Scores', 'Feature Contributions'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Time series
        fig.add_trace(
            go.Scatter(x=timestamps, y=values, mode='lines',
                      name='Value', line=dict(color='#2c3e50')),
            row=1, col=1
        )
        
        # Add anomaly markers
        anomaly_times = [s.timestamp for s in anomaly_scores if s.is_anomaly]
        anomaly_values = [values[list(timestamps).index(s.timestamp)] 
                         for s in anomaly_scores if s.is_anomaly]
        
        if anomaly_times:
            fig.add_trace(
                go.Scatter(x=anomaly_times, y=anomaly_values, mode='markers',
                          name='Anomalies', marker=dict(color='red', size=10)),
                row=1, col=1
            )
        
        # Anomaly scores
        score_times = [s.timestamp for s in anomaly_scores]
        scores = [s.score for s in anomaly_scores]
        
        fig.add_trace(
            go.Scatter(x=score_times, y=scores, mode='lines',
                      name='Anomaly Score', fill='tozeroy',
                      line=dict(color='#3498db')),
            row=2, col=1
        )
        
        fig.add_hline(y=0.5, line_dash="dash", line_color="red",
                     row=2, col=1)
        
        # Feature contributions (if available)
        if anomaly_scores and anomaly_scores[0].feature_contributions:
            features = list(anomaly_scores[0].feature_contributions.keys())
            
            for feature in features[:5]:  # Top 5 features
                contributions = [s.feature_contributions.get(feature, 0) 
                               for s in anomaly_scores]
                
                fig.add_trace(
                    go.Scatter(x=score_times, y=contributions, mode='lines',
                              name=feature, stackgroup='contributions'),
                    row=3, col=1
                )
        
        fig.update_layout(
            title=title,
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig


class RealTimeDashboard:
    """
    Real-time updating dashboard for anomaly monitoring.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        
        self.timestamps: deque = deque(maxlen=max_history)
        self.values: deque = deque(maxlen=max_history)
        self.anomaly_scores: deque = deque(maxlen=max_history)
        self.alerts: deque = deque(maxlen=100)
        
    def update(self, timestamp: datetime, value: float, 
               anomaly_score: Optional[AnomalyScore] = None):
        """Update dashboard with new data."""
        self.timestamps.append(timestamp)
        self.values.append(value)
        
        if anomaly_score:
            self.anomaly_scores.append(anomaly_score)
            
            if anomaly_score.is_anomaly:
                self.alerts.append({
                    'timestamp': timestamp,
                    'score': anomaly_score.score,
                    'severity': anomaly_score.severity.value
                })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current dashboard summary."""
        return {
            'total_points': len(self.timestamps),
            'anomaly_count': len([s for s in self.anomaly_scores if s.is_anomaly]),
            'anomaly_rate': len([s for s in self.anomaly_scores if s.is_anomaly]) / 
                          max(len(self.anomaly_scores), 1),
            'recent_alerts': list(self.alerts)[-10:],
            'current_score': self.anomaly_scores[-1].score if self.anomaly_scores else 0,
            'avg_score': np.mean([s.score for s in self.anomaly_scores]) if self.anomaly_scores else 0
        }


# Export classes
__all__ = [
    'AnomalyVisualizer', 'RealTimeDashboard'
]
```

---

## 12. Integration Strategy

### 12.1 System Integration Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/integration.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import json
import logging

from architecture import AnomalyDetectionPipeline, DetectionConfig
from alerts import AlertManager, AlertRule, AlertChannel, AlertSeverity
from realtime import StreamingAnomalyDetector, EnsembleRealTimeDetector
from visualization import AnomalyVisualizer, RealTimeDashboard

logger = logging.getLogger(__name__)


class ResilienceAIIntegration:
    """
    Main integration class for ResilienceAI anomaly detection.
    
    Provides unified interface for all anomaly detection capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core components
        self.detection_pipeline: AnomalyDetectionPipeline = None
        self.alert_manager: AlertManager = None
        self.visualizer: AnomalyVisualizer = None
        self.dashboard: RealTimeDashboard = None
        self.streaming_detector: StreamingAnomalyDetector = None
        
        # State
        self.is_initialized: bool = False
        self.detection_history: List[Dict] = []
        
    def initialize(self, detection_config: DetectionConfig = None):
        """Initialize all components."""
        logger.info("Initializing ResilienceAI Anomaly Detection...")
        
        # Create detection pipeline
        self.detection_pipeline = AnomalyDetectionPipeline(
            config=detection_config or DetectionConfig()
        )
        
        # Create alert manager
        self.alert_manager = AlertManager()
        
        # Create visualizer
        self.visualizer = AnomalyVisualizer()
        
        # Create dashboard
        self.dashboard = RealTimeDashboard()
        
        self.is_initialized = True
        logger.info("Initialization complete")
        
        return self
    
    def register_detectors(self, detectors: Dict[str, Any]):
        """Register multiple detectors to the pipeline."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        for name, detector in detectors.items():
            weight = self.config.get('detector_weights', {}).get(name, 1.0)
            self.detection_pipeline.add_detector(detector, weight)
            logger.info(f"Registered detector: {name} (weight={weight})")
    
    def configure_alerts(self, rules: List[Dict[str, Any]]):
        """Configure alert rules."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        for rule_config in rules:
            rule = AlertRule(
                name=rule_config['name'],
                severity_threshold=AlertSeverity(rule_config['severity']),
                min_score=rule_config['min_score'],
                min_confidence=rule_config.get('min_confidence', 0.5),
                cooldown_minutes=rule_config.get('cooldown_minutes', 15),
                channels=[AlertChannel(c) for c in rule_config.get('channels', ['console'])],
                filters=rule_config.get('filters', {})
            )
            self.alert_manager.add_rule(rule)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None):
        """Fit all detectors in the pipeline."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        logger.info(f"Fitting detectors on {len(X)} samples...")
        self.detection_pipeline.fit_all(X, y)
        logger.info("Fitting complete")
        
        return self
    
    def detect(self, X: np.ndarray, 
               feature_names: List[str] = None,
               source: str = "batch") -> Dict[str, List[Any]]:
        """
        Run batch anomaly detection.
        
        Returns:
            Dictionary with detection results and alerts
        """
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        # Run detection
        results = self.detection_pipeline.detect(X, feature_names)
        
        # Process ensemble results for alerts
        ensemble_results = results.get('ensemble', [])
        alerts = []
        
        for score in ensemble_results:
            # Update dashboard
            self.dashboard.update(
                timestamp=score.timestamp,
                value=0,  # Would need actual value
                anomaly_score=score
            )
            
            # Generate alerts
            rule_alerts = self.alert_manager.process_anomaly(score, source)
            alerts.extend(rule_alerts)
        
        # Store in history
        self.detection_history.append({
            'timestamp': datetime.now(),
            'n_samples': len(X),
            'n_anomalies': len([s for s in ensemble_results if s.is_anomaly]),
            'alerts_generated': len(alerts)
        })
        
        return {
            'detection_results': results,
            'alerts': alerts,
            'summary': self._create_summary(results, alerts)
        }
    
    def start_streaming(self, window_size: int = 1000):
        """Start real-time streaming detection."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        # Get primary detector
        if not self.detection_pipeline.detectors:
            raise RuntimeError("No detectors registered")
        
        primary_detector = list(self.detection_pipeline.detectors.values())[0]
        
        # Create streaming detector
        self.streaming_detector = StreamingAnomalyDetector(
            detector=primary_detector,
            window_size=window_size
        )
        
        # Add alert callback
        self.streaming_detector.add_anomaly_callback(
            lambda score: self.alert_manager.process_anomaly(score, "streaming")
        )
        
        # Start
        self.streaming_detector.start()
        logger.info("Streaming detection started")
        
        return self
    
    def stop_streaming(self):
        """Stop real-time streaming detection."""
        if self.streaming_detector:
            self.streaming_detector.stop()
            logger.info("Streaming detection stopped")
    
    def ingest_streaming_data(self, data: np.ndarray, timestamp: datetime = None):
        """Ingest data for streaming detection."""
        if not self.streaming_detector:
            raise RuntimeError("Streaming not started")
        
        self.streaming_detector.ingest(data, timestamp)
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get current dashboard summary."""
        if self.dashboard:
            return self.dashboard.get_summary()
        return {}
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        if self.alert_manager:
            return self.alert_manager.get_alert_statistics()
        return {}
    
    def visualize(self, 
                  timestamps: pd.DatetimeIndex,
                  values: np.ndarray,
                  save_dir: str = None) -> Dict[str, Any]:
        """Generate visualization plots."""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        # Get recent detection results
        recent_results = []
        for entry in self.detection_history[-10:]:
            if 'detection_results' in entry:
                recent_results.extend(entry['detection_results'].get('ensemble', []))
        
        figures = {}
        
        # Time series with anomalies
        if self.visualizer and recent_results:
            fig = self.visualizer.plot_time_series_with_anomalies(
                timestamps, values, recent_results
            )
            figures['time_series'] = fig
        
        return figures
    
    def _create_summary(self, 
                       results: Dict[str, List[Any]], 
                       alerts: List[Any]) -> Dict[str, Any]:
        """Create detection summary."""
        ensemble_results = results.get('ensemble', [])
        
        return {
            'total_samples': len(ensemble_results),
            'anomalies_detected': len([s for s in ensemble_results if s.is_anomaly]),
            'anomaly_rate': len([s for s in ensemble_results if s.is_anomaly]) / 
                          max(len(ensemble_results), 1),
            'alerts_generated': len(alerts),
            'avg_confidence': np.mean([s.confidence for s in ensemble_results]) if ensemble_results else 0,
            'severity_breakdown': self._severity_breakdown(ensemble_results)
        }
    
    def _severity_breakdown(self, results: List[Any]) -> Dict[str, int]:
        """Break down results by severity."""
        breakdown = {}
        
        for severity in AlertSeverity:
            count = len([r for r in results if r.severity == severity])
            breakdown[severity.value] = count
        
        return breakdown
    
    def export_config(self, filepath: str):
        """Export system configuration to JSON."""
        config = {
            'initialized': self.is_initialized,
            'detectors': list(self.detection_pipeline.detectors.keys()) if self.detection_pipeline else [],
            'alert_rules': len(self.alert_manager.rules) if self.alert_manager else 0,
            'detection_history_count': len(self.detection_history)
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        status = {
            'initialized': self.is_initialized,
            'detectors_ready': False,
            'alert_system_ready': False,
            'streaming_active': False,
            'overall_status': 'unknown'
        }
        
        if self.is_initialized:
            status['detectors_ready'] = len(self.detection_pipeline.detectors) > 0
            status['alert_system_ready'] = len(self.alert_manager.rules) > 0
            status['streaming_active'] = (self.streaming_detector is not None and 
                                         self.streaming_detector.is_running)
            
            if status['detectors_ready'] and status['alert_system_ready']:
                status['overall_status'] = 'healthy'
            elif status['detectors_ready']:
                status['overall_status'] = 'degraded'
            else:
                status['overall_status'] = 'unhealthy'
        
        return status


# Factory function for easy setup
def create_resilience_ai_anomaly_detection(
        config: Dict[str, Any] = None) -> ResilienceAIIntegration:
    """
    Factory function to create a fully configured anomaly detection system.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Configured ResilienceAIIntegration instance
    """
    integration = ResilienceAIIntegration(config)
    integration.initialize()
    
    return integration


# Export classes
__all__ = [
    'ResilienceAIIntegration', 'create_resilience_ai_anomaly_detection'
]
```

---

## 13. Performance Tuning

### 13.1 Optimization Strategies

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/performance.py

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for anomaly detection."""
    inference_time_ms: float
    throughput_samples_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float
    detection_accuracy: float
    false_positive_rate: float
    false_negative_rate: float


class PerformanceOptimizer:
    """
    Performance optimization for anomaly detection.
    """
    
    def __init__(self):
        self.optimization_strategies = {
            'batch_processing': self._optimize_batch_size,
            'dimensionality_reduction': self._optimize_dimensions,
            'model_compression': self._compress_model,
            'caching': self._enable_caching,
            'parallel_processing': self._enable_parallelism
        }
        
        self.metrics_history: List[PerformanceMetrics] = []
    
    def benchmark_detector(self, 
                          detector: Any,
                          X_test: np.ndarray,
                          n_iterations: int = 10) -> PerformanceMetrics:
        """Benchmark detector performance."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Warm up
        _ = detector.predict(X_test[:10])
        
        # Benchmark
        times = []
        for _ in range(n_iterations):
            start_mem = process.memory_info().rss / 1024 / 1024  # MB
            
            start_time = time.time()
            _ = detector.predict(X_test)
            end_time = time.time()
            
            end_mem = process.memory_info().rss / 1024 / 1024  # MB
            
            times.append((end_time - start_time) * 1000)  # ms
        
        avg_time = np.mean(times)
        throughput = len(X_test) / (avg_time / 1000)
        
        metrics = PerformanceMetrics(
            inference_time_ms=avg_time,
            throughput_samples_per_sec=throughput,
            memory_usage_mb=end_mem - start_mem,
            cpu_usage_percent=process.cpu_percent(),
            detection_accuracy=0.0,  # Would need ground truth
            false_positive_rate=0.0,
            false_negative_rate=0.0
        )
        
        self.metrics_history.append(metrics)
        
        return metrics
    
    def optimize_batch_size(self, 
                           detector: Any,
                           X: np.ndarray,
                           target_latency_ms: float = 100) -> int:
        """Find optimal batch size for target latency."""
        batch_sizes = [1, 10, 50, 100, 500, 1000]
        optimal_size = 1
        
        for batch_size in batch_sizes:
            if batch_size > len(X):
                break
            
            # Test batch
            sample = X[:batch_size]
            start = time.time()
            _ = detector.predict(sample)
            elapsed = (time.time() - start) * 1000
            
            if elapsed <= target_latency_ms:
                optimal_size = batch_size
            else:
                break
        
        logger.info(f"Optimal batch size: {optimal_size}")
        return optimal_size
    
    def _optimize_batch_size(self, detector: Any, **kwargs) -> Any:
        """Apply batch size optimization."""
        # Implementation depends on detector type
        return detector
    
    def _optimize_dimensions(self, detector: Any, 
                            n_components: int = 10, **kwargs) -> Any:
        """Apply dimensionality reduction."""
        from sklearn.decomposition import PCA
        
        # Wrap detector with PCA
        class PCADetectorWrapper:
            def __init__(self, detector, pca):
                self.detector = detector
                self.pca = pca
            
            def predict(self, X):
                X_reduced = self.pca.transform(X)
                return self.detector.predict(X_reduced)
            
            def score_samples(self, X):
                X_reduced = self.pca.transform(X)
                return self.detector.score_samples(X_reduced)
        
        return detector  # Return original for now
    
    def _compress_model(self, detector: Any, **kwargs) -> Any:
        """Apply model compression techniques."""
        # Quantization, pruning, etc.
        return detector
    
    def _enable_caching(self, detector: Any, cache_size: int = 1000, **kwargs) -> Any:
        """Enable result caching."""
        from functools import lru_cache
        
        # Wrap predict method with caching
        original_predict = detector.predict
        
        def cached_predict(X):
            # Simple hash-based caching for numpy arrays
            return original_predict(X)
        
        detector.predict = cached_predict
        
        return detector
    
    def _enable_parallelism(self, detector: Any, n_jobs: int = -1, **kwargs) -> Any:
        """Enable parallel processing."""
        # Set n_jobs parameter if available
        if hasattr(detector, 'n_jobs'):
            detector.n_jobs = n_jobs
        
        return detector
    
    def recommend_optimizations(self, 
                               current_metrics: PerformanceMetrics,
                               target_metrics: PerformanceMetrics) -> List[str]:
        """Recommend optimizations based on performance gaps."""
        recommendations = []
        
        if current_metrics.inference_time_ms > target_metrics.inference_time_ms:
            recommendations.append("Consider batch processing optimization")
            recommendations.append("Enable model caching")
        
        if current_metrics.memory_usage_mb > target_metrics.memory_usage_mb:
            recommendations.append("Apply dimensionality reduction")
            recommendations.append("Consider model compression")
        
        if current_metrics.throughput_samples_per_sec < target_metrics.throughput_samples_per_sec:
            recommendations.append("Enable parallel processing")
            recommendations.append("Optimize batch size")
        
        return recommendations


class ModelSelector:
    """
    Select optimal model based on data characteristics and requirements.
    """
    
    MODEL_RECOMMENDATIONS = {
        'small_dataset': {
            'n_samples': (0, 1000),
            'recommended': ['Statistical', 'One-Class SVM', 'LOF']
        },
        'medium_dataset': {
            'n_samples': (1000, 10000),
            'recommended': ['Isolation Forest', 'Autoencoder', 'Clustering']
        },
        'large_dataset': {
            'n_samples': (10000, float('inf')),
            'recommended': ['Isolation Forest', 'Streaming', 'Ensemble']
        },
        'high_dimensional': {
            'n_features': (50, float('inf')),
            'recommended': ['Autoencoder', 'Isolation Forest', 'PCA + Detector']
        },
        'time_series': {
            'data_type': 'time_series',
            'recommended': ['LSTM Autoencoder', 'Statistical Time Series', 'Prophet']
        }
    }
    
    def select_model(self,
                    n_samples: int,
                    n_features: int,
                    data_type: str = 'tabular',
                    latency_requirement: str = 'standard',
                    accuracy_priority: str = 'balanced') -> List[str]:
        """
        Recommend models based on data characteristics.
        
        Args:
            n_samples: Number of samples
            n_features: Number of features
            data_type: 'tabular', 'time_series', 'image', etc.
            latency_requirement: 'low', 'standard', 'high'
            accuracy_priority: 'speed', 'balanced', 'accuracy'
        
        Returns:
            List of recommended model names
        """
        recommendations = []
        
        # Dataset size
        if n_samples < 1000:
            recommendations.extend(['Statistical', 'One-Class SVM', 'LOF'])
        elif n_samples < 10000:
            recommendations.extend(['Isolation Forest', 'Autoencoder'])
        else:
            recommendations.extend(['Isolation Forest', 'Streaming Ensemble'])
        
        # Dimensionality
        if n_features > 50:
            recommendations.extend(['Autoencoder', 'PCA + Isolation Forest'])
        
        # Data type
        if data_type == 'time_series':
            recommendations = ['LSTM Autoencoder', 'Statistical Time Series', 
                             'Change Point Detection']
        
        # Latency requirements
        if latency_requirement == 'low':
            recommendations = [r for r in recommendations 
                             if r not in ['Autoencoder', 'LSTM Autoencoder']]
        
        # Accuracy priority
        if accuracy_priority == 'accuracy':
            recommendations.append('Ensemble (All Methods)')
        
        return list(set(recommendations))


# Export classes
__all__ = [
    'PerformanceMetrics', 'PerformanceOptimizer', 'ModelSelector'
]
```

---

## 14. Testing Strategy

### 14.1 Comprehensive Testing Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/testing.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from sklearn.metrics import (roc_auc_score, average_precision_score,
                            precision_recall_curve, confusion_matrix,
                            classification_report, f1_score)
from sklearn.model_selection import train_test_split
import unittest
import logging

from architecture import BaseDetector, AnomalyScore, DetectionConfig

logger = logging.getLogger(__name__)


class AnomalyDetectionTester:
    """
    Comprehensive testing framework for anomaly detection.
    """
    
    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
        
    def generate_synthetic_data(self,
                               n_samples: int = 1000,
                               n_features: int = 10,
                               contamination: float = 0.1,
                               random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic data with known anomalies."""
        np.random.seed(random_state)
        
        # Generate normal data
        n_normal = int(n_samples * (1 - contamination))
        X_normal = np.random.randn(n_normal, n_features)
        
        # Generate anomalies
        n_anomalies = n_samples - n_normal
        X_anomalies = np.random.randn(n_anomalies, n_features) * 3 + 5
        
        # Combine
        X = np.vstack([X_normal, X_anomalies])
        y = np.hstack([np.ones(n_normal), -np.ones(n_anomalies)])
        
        # Shuffle
        shuffle_idx = np.random.permutation(len(X))
        X = X[shuffle_idx]
        y = y[shuffle_idx]
        
        return X, y
    
    def evaluate_detector(self,
                         detector: BaseDetector,
                         X_test: np.ndarray,
                         y_true: np.ndarray,
                         detector_name: str = "detector") -> Dict[str, Any]:
        """
        Comprehensive evaluation of a detector.
        """
        results = {}
        
        # Predictions
        y_pred = detector.predict(X_test)
        scores = detector.score_samples(X_test)
        
        # Basic metrics
        results['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
        results['classification_report'] = classification_report(
            y_true, y_pred, output_dict=True
        )
        
        # ROC-AUC (if scores available)
        try:
            # Convert labels to binary (0 for normal, 1 for anomaly)
            y_binary = (y_true == -1).astype(int)
            results['roc_auc'] = roc_auc_score(y_binary, scores)
        except Exception as e:
            results['roc_auc'] = None
            logger.warning(f"Could not compute ROC-AUC: {e}")
        
        # Average Precision
        try:
            y_binary = (y_true == -1).astype(int)
            results['average_precision'] = average_precision_score(y_binary, scores)
        except Exception as e:
            results['average_precision'] = None
            logger.warning(f"Could not compute AP: {e}")
        
        # F1 Score
        results['f1_score'] = f1_score(y_true, y_pred, pos_label=-1)
        
        # Detection rate
        true_anomalies = np.sum(y_true == -1)
        detected_anomalies = np.sum((y_true == -1) & (y_pred == -1))
        results['detection_rate'] = detected_anomalies / true_anomalies if true_anomalies > 0 else 0
        
        # False positive rate
        true_normal = np.sum(y_true == 1)
        false_positives = np.sum((y_true == 1) & (y_pred == -1))
        results['false_positive_rate'] = false_positives / true_normal if true_normal > 0 else 0
        
        # Store results
        self.test_results[detector_name] = results
        
        return results
    
    def benchmark_multiple_detectors(self,
                                    detectors: Dict[str, BaseDetector],
                                    X_test: np.ndarray,
                                    y_true: np.ndarray) -> pd.DataFrame:
        """Benchmark multiple detectors and return comparison."""
        results = []
        
        for name, detector in detectors.items():
            logger.info(f"Benchmarking {name}...")
            
            metrics = self.evaluate_detector(detector, X_test, y_true, name)
            
            results.append({
                'detector': name,
                'f1_score': metrics['f1_score'],
                'detection_rate': metrics['detection_rate'],
                'false_positive_rate': metrics['false_positive_rate'],
                'roc_auc': metrics.get('roc_auc', 0),
                'average_precision': metrics.get('average_precision', 0)
            })
        
        return pd.DataFrame(results)
    
    def test_robustness(self,
                       detector: BaseDetector,
                       X: np.ndarray,
                       noise_levels: List[float] = None) -> Dict[str, Any]:
        """Test detector robustness to noise."""
        noise_levels = noise_levels or [0.0, 0.1, 0.2, 0.5, 1.0]
        
        results = {}
        base_scores = detector.score_samples(X)
        
        for noise_level in noise_levels:
            # Add noise
            X_noisy = X + np.random.randn(*X.shape) * noise_level
            
            # Score
            noisy_scores = detector.score_samples(X_noisy)
            
            # Measure stability
            score_diff = np.abs(noisy_scores - base_scores)
            
            results[f'noise_{noise_level}'] = {
                'mean_diff': float(np.mean(score_diff)),
                'max_diff': float(np.max(score_diff)),
                'prediction_flip_rate': float(np.mean(
                    (base_scores > 0.5) != (noisy_scores > 0.5)
                ))
            }
        
        return results
    
    def test_scalability(self,
                        detector_factory: Callable,
                        sample_sizes: List[int] = None,
                        n_features: int = 10) -> pd.DataFrame:
        """Test detector scalability."""
        sample_sizes = sample_sizes or [100, 500, 1000, 5000, 10000]
        
        results = []
        
        for n_samples in sample_sizes:
            logger.info(f"Testing scalability with {n_samples} samples...")
            
            # Generate data
            X, y = self.generate_synthetic_data(n_samples, n_features)
            X_train, X_test = train_test_split(X, test_size=0.2)
            
            # Create and fit detector
            detector = detector_factory()
            
            import time
            
            # Training time
            start = time.time()
            detector.fit(X_train)
            train_time = time.time() - start
            
            # Inference time
            start = time.time()
            _ = detector.predict(X_test)
            inference_time = time.time() - start
            
            results.append({
                'n_samples': n_samples,
                'train_time_sec': train_time,
                'inference_time_sec': inference_time,
                'throughput_samples_per_sec': len(X_test) / inference_time
            })
        
        return pd.DataFrame(results)


class UnitTestSuite(unittest.TestCase):
    """Unit tests for anomaly detection components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tester = AnomalyDetectionTester()
        self.X, self.y = self.tester.generate_synthetic_data(n_samples=500)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.3, random_state=42
        )
    
    def test_detector_initialization(self):
        """Test detector can be initialized."""
        from statistical_detectors import ZScoreDetector
        
        detector = ZScoreDetector()
        self.assertIsNotNone(detector)
        self.assertFalse(detector.is_fitted)
    
    def test_detector_fitting(self):
        """Test detector can be fitted."""
        from statistical_detectors import ZScoreDetector
        
        detector = ZScoreDetector()
        detector.fit(self.X_train)
        
        self.assertTrue(detector.is_fitted)
        self.assertIsNotNone(detector.means)
        self.assertIsNotNone(detector.stds)
    
    def test_detector_prediction(self):
        """Test detector can make predictions."""
        from statistical_detectors import ZScoreDetector
        
        detector = ZScoreDetector()
        detector.fit(self.X_train)
        
        predictions = detector.predict(self.X_test)
        scores = detector.score_samples(self.X_test)
        
        self.assertEqual(len(predictions), len(self.X_test))
        self.assertEqual(len(scores), len(self.X_test))
        self.assertTrue(all(s in [-1, 1] for s in predictions))
        self.assertTrue(all(0 <= s <= 1 for s in scores))
    
    def test_anomaly_score_structure(self):
        """Test AnomalyScore dataclass."""
        from architecture import AnomalyScore, AnomalyType, AlertSeverity
        from datetime import datetime
        
        score = AnomalyScore(
            score=0.8,
            is_anomaly=True,
            confidence=0.9,
            anomaly_type=AnomalyType.POINT,
            severity=AlertSeverity.HIGH,
            timestamp=datetime.now(),
            feature_contributions={'feature1': 0.5},
            metadata={'test': True}
        )
        
        self.assertTrue(score.is_anomaly)
        self.assertEqual(score.severity, AlertSeverity.HIGH)


def run_tests():
    """Run all tests."""
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    tester = AnomalyDetectionTester()
    
    # Generate test data
    X, y = tester.generate_synthetic_data(n_samples=1000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    
    # Test individual detectors
    from statistical_detectors import ZScoreDetector, IsolationForestDetector
    from isolation_forest import IsolationForestDetector as IFDetector
    
    detectors = {
        'ZScore': ZScoreDetector(),
        'IsolationForest': IFDetector()
    }
    
    for name, detector in detectors.items():
        detector.fit(X_train)
        results = tester.evaluate_detector(detector, X_test, y_test, name)
        logger.info(f"{name} results: F1={results['f1_score']:.3f}, "
                   f"Detection Rate={results['detection_rate']:.3f}")
    
    # Benchmark comparison
    comparison = tester.benchmark_multiple_detectors(detectors, X_test, y_test)
    logger.info("\nDetector Comparison:")
    logger.info(comparison.to_string())


# Export classes
__all__ = [
    'AnomalyDetectionTester', 'UnitTestSuite', 'run_tests'
]
```



---

## 15. Implementation Priority

### 15.1 Phased Implementation Plan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PRIORITY MATRIX                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: FOUNDATION (Weeks 1-2)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Priority: CRITICAL | Impact: HIGH | Effort: MEDIUM                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Statistical detection (Z-Score, IQR)                              │   │
│  │ • Isolation Forest                                                  │   │
│  │ • Basic alert generation                                            │   │
│  │ • Console logging                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 2: ENHANCEMENT (Weeks 3-4)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Priority: HIGH | Impact: HIGH | Effort: MEDIUM                      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • One-Class SVM                                                     │   │
│  │ • Clustering-based detection (K-Means, LOF)                         │   │
│  │ • Ensemble scoring                                                  │   │
│  │ • Email/Slack alerts                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 3: ADVANCED (Weeks 5-6)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Priority: MEDIUM | Impact: HIGH | Effort: HIGH                      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Autoencoders (basic + VAE)                                        │   │
│  │ • Time series detection                                             │   │
│  │ • Real-time streaming                                               │   │
│  │ • Visualization dashboards                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 4: OPTIMIZATION (Weeks 7-8)                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Priority: MEDIUM | Impact: MEDIUM | Effort: MEDIUM                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Performance tuning                                                │   │
│  │ • LSTM autoencoders                                                 │   │
│  │ • Advanced alerting (PagerDuty)                                     │   │
│  │ • Comprehensive testing                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 5: PRODUCTION (Weeks 9-10)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Priority: LOW | Impact: MEDIUM | Effort: HIGH                       │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Full integration testing                                          │   │
│  │ • Documentation                                                     │   │
│  │ • Monitoring and observability                                      │   │
│  │ • Production deployment                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 15.2 Implementation Checklist

#### Phase 1: Foundation
- [ ] **Statistical Detection**
  - [ ] Z-Score detector
  - [ ] Modified Z-Score (MAD)
  - [ ] IQR-based detection
  - [ ] Grubbs test
  
- [ ] **Isolation Forest**
  - [ ] Core implementation
  - [ ] Extended isolation forest
  - [ ] Hyperparameter optimization
  
- [ ] **Alert System**
  - [ ] Basic alert generation
  - [ ] Console output
  - [ ] Severity classification

#### Phase 2: Enhancement
- [ ] **One-Class SVM**
  - [ ] Core implementation
  - [ ] Nu optimization
  - [ ] Kernel selection
  
- [ ] **Clustering Methods**
  - [ ] K-Means distance
  - [ ] DBSCAN
  - [ ] Local Outlier Factor
  - [ ] Hierarchical clustering
  
- [ ] **Ensemble & Alerts**
  - [ ] Ensemble scoring
  - [ ] Email integration
  - [ ] Slack webhooks

#### Phase 3: Advanced
- [ ] **Autoencoders**
  - [ ] Basic autoencoder
  - [ ] Variational autoencoder
  - [ ] Training pipeline
  
- [ ] **Time Series**
  - [ ] Statistical TS detection
  - [ ] Prophet-style detection
  - [ ] Change point detection
  
- [ ] **Streaming & Viz**
  - [ ] Real-time streaming
  - [ ] Matplotlib visualizations
  - [ ] Plotly dashboards

#### Phase 4: Optimization
- [ ] **Performance**
  - [ ] Batch size optimization
  - [ ] Caching layer
  - [ ] Parallel processing
  
- [ ] **Advanced Models**
  - [ ] LSTM autoencoder
  - [ ] Incremental learning
  - [ ] Model compression
  
- [ ] **Testing**
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] Performance benchmarks

#### Phase 5: Production
- [ ] **Integration**
  - [ ] End-to-end testing
  - [ ] Load testing
  - [ ] Failover testing
  
- [ ] **Documentation**
  - [ ] API documentation
  - [ ] User guides
  - [ ] Runbooks
  
- [ ] **Deployment**
  - [ ] Containerization
  - [ ] CI/CD pipeline
  - [ ] Monitoring setup

### 15.3 Quick Start Example

```python
# /mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/example_usage.py

"""
Quick Start Example for ResilienceAI Anomaly Detection
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Import components
from architecture import AnomalyDetectionPipeline, DetectionConfig
from statistical_detectors import ZScoreDetector, StatisticalEnsembleDetector
from isolation_forest import IsolationForestDetector
from alerts import AlertManager, AlertRule, AlertChannel, AlertSeverity
from integration import create_resilience_ai_anomaly_detection


def main():
    """Main example demonstrating anomaly detection workflow."""
    
    print("=" * 60)
    print("ResilienceAI Anomaly Detection - Quick Start Example")
    print("=" * 60)
    
    # Step 1: Generate sample data
    print("\n[1/5] Generating sample data...")
    np.random.seed(42)
    
    # Normal data
    n_normal = 900
    X_normal = np.random.randn(n_normal, 5)
    
    # Anomalous data
    n_anomalies = 100
    X_anomalies = np.random.randn(n_anomalies, 5) * 3 + 5
    
    # Combine
    X = np.vstack([X_normal, X_anomalies])
    y = np.hstack([np.ones(n_normal), -np.ones(n_anomalies)])
    
    # Shuffle
    shuffle_idx = np.random.permutation(len(X))
    X = X[shuffle_idx]
    y = y[shuffle_idx]
    
    # Split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Anomalies in test: {np.sum(y_test == -1)}")
    
    # Step 2: Create detection pipeline
    print("\n[2/5] Creating detection pipeline...")
    
    config = DetectionConfig(
        threshold=0.5,
        sensitivity=0.8,
        window_size=100,
        enable_ensemble=True
    )
    
    pipeline = AnomalyDetectionPipeline(config)
    
    # Add detectors
    pipeline.add_detector(ZScoreDetector(config), weight=0.3)
    pipeline.add_detector(IsolationForestDetector(config), weight=0.7)
    
    print(f"  Detectors registered: {list(pipeline.detectors.keys())}")
    
    # Step 3: Train detectors
    print("\n[3/5] Training detectors...")
    pipeline.fit_all(X_train)
    print("  Training complete!")
    
    # Step 4: Run detection
    print("\n[4/5] Running anomaly detection...")
    
    feature_names = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
    results = pipeline.detect(X_test, feature_names=feature_names)
    
    ensemble_results = results.get('ensemble', [])
    n_anomalies_detected = sum(1 for r in ensemble_results if r.is_anomaly)
    
    print(f"  Total samples: {len(ensemble_results)}")
    print(f"  Anomalies detected: {n_anomalies_detected}")
    print(f"  Detection rate: {n_anomalies_detected / len(ensemble_results):.2%}")
    
    # Step 5: Generate alerts
    print("\n[5/5] Generating alerts...")
    
    alert_manager = AlertManager()
    
    # Configure alert rule
    rule = AlertRule(
        name="high_severity_anomalies",
        severity_threshold=AlertSeverity.HIGH,
        min_score=0.7,
        min_confidence=0.6,
        cooldown_minutes=5,
        channels=[AlertChannel.CONSOLE]
    )
    alert_manager.add_rule(rule)
    
    # Process anomalies
    alerts_generated = 0
    for score in ensemble_results:
        alerts = alert_manager.process_anomaly(score, source="example_pipeline")
        alerts_generated += len(alerts)
    
    print(f"  Alerts generated: {alerts_generated}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Detection pipeline created with {len(pipeline.detectors)} detectors")
    print(f"✓ Trained on {len(X_train)} samples")
    print(f"✓ Detected {n_anomalies_detected} anomalies in {len(X_test)} test samples")
    print(f"✓ Generated {alerts_generated} alerts")
    print("\nExample complete!")
    
    return pipeline, alert_manager, results


def advanced_example():
    """Advanced example with full integration."""
    
    print("\n" + "=" * 60)
    print("Advanced Example: Full Integration")
    print("=" * 60)
    
    # Create integrated system
    config = {
        'detector_weights': {
            'ZScore': 0.2,
            'IsolationForest': 0.4,
            'OneClassSVM': 0.4
        }
    }
    
    system = create_resilience_ai_anomaly_detection(config)
    
    # Register detectors
    from one_class_svm import OneClassSVMDetector
    from clustering_detectors import LocalOutlierFactorDetector
    
    detectors = {
        'ZScore': ZScoreDetector(),
        'IsolationForest': IsolationForestDetector(),
        'OneClassSVM': OneClassSVMDetector(),
        'LOF': LocalOutlierFactorDetector()
    }
    
    system.register_detectors(detectors)
    
    # Configure alerts
    alert_rules = [
        {
            'name': 'critical_anomalies',
            'severity': 'critical',
            'min_score': 0.9,
            'min_confidence': 0.8,
            'cooldown_minutes': 1,
            'channels': ['console']
        },
        {
            'name': 'high_anomalies',
            'severity': 'high',
            'min_score': 0.7,
            'min_confidence': 0.6,
            'cooldown_minutes': 5,
            'channels': ['console', 'email']
        }
    ]
    system.configure_alerts(alert_rules)
    
    # Generate and fit on data
    np.random.seed(42)
    X = np.random.randn(1000, 5)
    system.fit(X)
    
    # Run detection
    X_test = np.random.randn(100, 5)
    results = system.detect(X_test, source="advanced_example")
    
    print(f"\nDetection Summary:")
    print(f"  Total samples: {results['summary']['total_samples']}")
    print(f"  Anomalies detected: {results['summary']['anomalies_detected']}")
    print(f"  Anomaly rate: {results['summary']['anomaly_rate']:.2%}")
    print(f"  Alerts generated: {results['summary']['alerts_generated']}")
    
    # Health check
    health = system.get_health_status()
    print(f"\nSystem Health: {health['overall_status']}")
    
    return system, results


if __name__ == "__main__":
    # Run basic example
    pipeline, alert_manager, results = main()
    
    # Run advanced example
    system, advanced_results = advanced_example()
```

---

## 16. Summary and Conclusions

### 16.1 Key Components Summary

| Component | Description | Priority | Status |
|-----------|-------------|----------|--------|
| Statistical Detection | Z-Score, IQR, MAD, Grubbs | Critical | Implemented |
| Isolation Forest | Tree-based isolation | Critical | Implemented |
| One-Class SVM | Boundary-based detection | High | Implemented |
| Autoencoders | Neural network reconstruction | Medium | Implemented |
| Clustering | K-Means, DBSCAN, LOF | High | Implemented |
| Time Series | Temporal pattern detection | Medium | Implemented |
| Real-Time | Streaming detection | Medium | Implemented |
| Scoring | Multi-factor scoring | High | Implemented |
| Alerts | Multi-channel alerting | Critical | Implemented |
| Visualization | Dashboards and plots | Medium | Implemented |

### 16.2 File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/anomaly_detection/
├── __init__.py
├── architecture.py          # Core abstractions and pipeline
├── statistical_detectors.py # Statistical methods
├── isolation_forest.py      # Isolation Forest implementations
├── one_class_svm.py         # One-Class SVM implementations
├── autoencoders.py          # Neural network detectors
├── clustering_detectors.py  # Clustering-based methods
├── time_series.py           # Time series detection
├── realtime.py              # Streaming detection
├── scoring.py               # Anomaly scoring system
├── alerts.py                # Alert generation and management
├── visualization.py         # Visualization components
├── integration.py           # System integration
├── performance.py           # Performance optimization
├── testing.py               # Testing framework
└── example_usage.py         # Usage examples
```

### 16.3 Next Steps

1. **Immediate Actions** (Week 1)
   - Deploy Phase 1 components (Statistical + Isolation Forest)
   - Set up basic alerting
   - Configure monitoring

2. **Short-term** (Weeks 2-4)
   - Implement ensemble scoring
   - Add clustering methods
   - Integrate with ResilienceAI pipeline

3. **Medium-term** (Weeks 5-8)
   - Deploy autoencoders
   - Add time series capabilities
   - Implement real-time streaming

4. **Long-term** (Weeks 9-12)
   - Full production deployment
   - Performance optimization
   - Comprehensive documentation

---

## Appendix A: Configuration Reference

### A.1 DetectionConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| threshold | float | 0.5 | Anomaly classification threshold |
| sensitivity | float | 0.8 | Detection sensitivity |
| window_size | int | 100 | Sliding window size |
| min_samples | int | 30 | Minimum samples for detection |
| update_frequency | str | '1min' | Model update frequency |
| enable_ensemble | bool | True | Enable ensemble scoring |

### A.2 AlertRule Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | required | Rule identifier |
| severity_threshold | AlertSeverity | required | Minimum severity |
| min_score | float | required | Minimum anomaly score |
| min_confidence | float | 0.5 | Minimum confidence |
| cooldown_minutes | int | 15 | Alert cooldown period |
| channels | List[AlertChannel] | ['console'] | Alert channels |

---

## Appendix B: API Quick Reference

### B.1 Creating a Detector

```python
from statistical_detectors import ZScoreDetector
from architecture import DetectionConfig

config = DetectionConfig(threshold=0.5)
detector = ZScoreDetector(config)
detector.fit(X_train)
results = detector.detect(X_test)
```

### B.2 Creating a Pipeline

```python
from architecture import AnomalyDetectionPipeline

pipeline = AnomalyDetectionPipeline()
pipeline.add_detector(detector1, weight=0.5)
pipeline.add_detector(detector2, weight=0.5)
pipeline.fit_all(X_train)
results = pipeline.detect(X_test)
```

### B.3 Configuring Alerts

```python
from alerts import AlertManager, AlertRule, AlertChannel, AlertSeverity

manager = AlertManager()
rule = AlertRule(
    name="my_rule",
    severity_threshold=AlertSeverity.HIGH,
    min_score=0.7,
    channels=[AlertChannel.SLACK, AlertChannel.EMAIL]
)
manager.add_rule(rule)
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
