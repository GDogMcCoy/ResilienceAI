"""
Statistical Anomaly Detection Methods

Implements classical statistical approaches for anomaly detection.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple, Union
from sklearn.preprocessing import StandardScaler
import warnings

from .architecture import BaseDetector, AnomalyScore, DetectionConfig, AnomalyType, AlertSeverity


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
    'StatisticalEnsembleDetector',
    'detect_univariate_outliers', 'detect_multivariate_outliers'
]
