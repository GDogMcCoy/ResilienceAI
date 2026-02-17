"""
ResilienceAI Bias Detection Framework
======================================
Comprehensive bias detection for AI systems.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from sklearn.metrics import confusion_matrix
import json


class BiasType(Enum):
    """Types of bias that can be detected."""
    DEMOGRAPHIC = "demographic"
    HISTORICAL = "historical"
    MEASUREMENT = "measurement"
    AGGREGATION = "aggregation"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    REPRESENTATIONAL = "representational"
    SYSTEMIC = "systemic"


@dataclass
class BiasReport:
    """Comprehensive bias detection report."""
    bias_type: BiasType
    severity: str
    affected_groups: List[str]
    metric_name: str
    metric_value: float
    threshold: float
    description: str
    recommendations: List[str]
    timestamp: str


class BiasDetector:
    """Main bias detection class."""
    
    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes
        self.bias_reports: List[BiasReport] = []
        self.thresholds = {
            'demographic_parity': 0.05,
            'equalized_odds': 0.05,
            'equal_opportunity': 0.05,
            'predictive_parity': 0.05,
            'calibration': 0.03,
            'statistical_parity': 0.05
        }
    
    def detect_data_bias(self, df: pd.DataFrame, target_col: str) -> Dict[str, BiasReport]:
        """Detect bias in training data."""
        reports = {}
        
        for attr in self.protected_attributes:
            if attr not in df.columns:
                continue
                
            representation = self._check_representation(df, attr)
            if representation['is_biased']:
                reports[f"{attr}_representation"] = BiasReport(
                    bias_type=BiasType.REPRESENTATIONAL,
                    severity=representation['severity'],
                    affected_groups=representation['underrepresented'],
                    metric_name="representation_ratio",
                    metric_value=representation['min_ratio'],
                    threshold=0.2,
                    description=f"Underrepresentation in {attr}",
                    recommendations=["Collect more data", "Apply rebalancing"],
                    timestamp=pd.Timestamp.now().isoformat()
                )
            
            label_bias = self._check_label_bias(df, attr, target_col)
            if label_bias['is_biased']:
                reports[f"{attr}_label"] = BiasReport(
                    bias_type=BiasType.HISTORICAL,
                    severity=label_bias['severity'],
                    affected_groups=label_bias['affected_groups'],
                    metric_name="label_disparity",
                    metric_value=label_bias['max_disparity'],
                    threshold=0.1,
                    description=f"Label bias in {attr}",
                    recommendations=["Review labeling", "Apply correction"],
                    timestamp=pd.Timestamp.now().isoformat()
                )
        
        return reports
    
    def _check_representation(self, df: pd.DataFrame, attr: str) -> Dict:
        counts = df[attr].value_counts(normalize=True)
        min_ratio = counts.min()
        underrepresented = counts[counts < 0.2].index.tolist()
        severity = 'low' if min_ratio > 0.15 else 'medium' if min_ratio > 0.1 else 'high'
        return {
            'is_biased': min_ratio < 0.2,
            'severity': severity,
            'min_ratio': min_ratio,
            'underrepresented': underrepresented
        }
    
    def _check_label_bias(self, df: pd.DataFrame, attr: str, target_col: str) -> Dict:
        label_rates = df.groupby(attr)[target_col].mean()
        max_disparity = label_rates.max() - label_rates.min()
        severity = 'low' if max_disparity < 0.15 else 'medium' if max_disparity < 0.25 else 'high'
        return {
            'is_biased': max_disparity > 0.1,
            'severity': severity,
            'max_disparity': max_disparity,
            'affected_groups': []
        }
    
    def detect_model_bias(self, y_true: np.ndarray, y_pred: np.ndarray,
                          protected_attrs: Dict[str, np.ndarray]) -> Dict[str, BiasReport]:
        """Detect bias in model predictions."""
        reports = {}
        
        for attr_name, attr_values in protected_attrs.items():
            dp_result = self._calculate_demographic_parity(y_pred, attr_values)
            if dp_result['violation']:
                reports[f"{attr_name}_demographic_parity"] = BiasReport(
                    bias_type=BiasType.DEMOGRAPHIC,
                    severity=dp_result['severity'],
                    affected_groups=dp_result['affected_groups'],
                    metric_name="demographic_parity_difference",
                    metric_value=dp_result['max_difference'],
                    threshold=self.thresholds['demographic_parity'],
                    description=f"Demographic parity violation for {attr_name}",
                    recommendations=["Apply post-processing", "Use fairness constraints"],
                    timestamp=pd.Timestamp.now().isoformat()
                )
            
            eo_result = self._calculate_equalized_odds(y_true, y_pred, attr_values)
            if eo_result['violation']:
                reports[f"{attr_name}_equalized_odds"] = BiasReport(
                    bias_type=BiasType.EVALUATION,
                    severity=eo_result['severity'],
                    affected_groups=[],
                    metric_name="equalized_odds_difference",
                    metric_value=eo_result['max_difference'],
                    threshold=self.thresholds['equalized_odds'],
                    description=f"Equalized odds violation for {attr_name}",
                    recommendations=["Apply calibration", "Threshold tuning"],
                    timestamp=pd.Timestamp.now().isoformat()
                )
        
        return reports
    
    def _calculate_demographic_parity(self, y_pred: np.ndarray, attr: np.ndarray) -> Dict:
        groups = np.unique(attr)
        rates = {group: y_pred[attr == group].mean() for group in groups}
        max_diff = max(rates.values()) - min(rates.values())
        affected = [g for g, r in rates.items() if r == min(rates.values())]
        severity = 'low' if max_diff < 0.08 else 'medium' if max_diff < 0.12 else 'high'
        return {
            'violation': max_diff > self.thresholds['demographic_parity'],
            'severity': severity,
            'max_difference': max_diff,
            'affected_groups': affected,
            'rates': rates
        }
    
    def _calculate_equalized_odds(self, y_true: np.ndarray, y_pred: np.ndarray, attr: np.ndarray) -> Dict:
        groups = np.unique(attr)
        tprs, fprs = [], []
        for group in groups:
            mask = attr == group
            cm = confusion_matrix(y_true[mask], y_pred[mask])
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                tprs.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
                fprs.append(fp / (fp + tn) if (fp + tn) > 0 else 0)
        max_diff = max(max(tprs) - min(tprs), max(fprs) - min(fprs)) if tprs else 0
        severity = 'low' if max_diff < 0.08 else 'medium' if max_diff < 0.12 else 'high'
        return {
            'violation': max_diff > self.thresholds['equalized_odds'],
            'severity': severity,
            'max_difference': max_diff
        }


if __name__ == "__main__":
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'gender': np.random.choice(['M', 'F'], n, p=[0.6, 0.4]),
        'target': np.random.randint(0, 2, n)
    })
    
    detector = BiasDetector(['gender'])
    data_bias = detector.detect_data_bias(df, 'target')
    print(f"Detected {len(data_bias)} bias issues")
