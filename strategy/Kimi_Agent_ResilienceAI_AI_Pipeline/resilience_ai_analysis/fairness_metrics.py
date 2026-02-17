"""
ResilienceAI Fairness Metrics
==============================
Comprehensive fairness metrics for AI systems.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score


@dataclass
class FairnessMetricResult:
    """Result of a fairness metric calculation."""
    metric_name: str
    value: float
    threshold: float
    is_fair: bool
    group_values: Dict[str, float]
    disparity: float
    interpretation: str


class FairnessMetrics:
    """Comprehensive fairness metrics calculator."""
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
    
    def calculate_all_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                              y_prob: Optional[np.ndarray],
                              protected_attr: np.ndarray) -> Dict[str, FairnessMetricResult]:
        """Calculate all fairness metrics."""
        metrics = {}
        metrics['demographic_parity'] = self.demographic_parity(y_pred, protected_attr)
        metrics['equalized_odds'] = self.equalized_odds(y_true, y_pred, protected_attr)
        metrics['equal_opportunity'] = self.equal_opportunity(y_true, y_pred, protected_attr)
        metrics['predictive_parity'] = self.predictive_parity(y_true, y_pred, protected_attr)
        metrics['accuracy_parity'] = self.accuracy_parity(y_true, y_pred, protected_attr)
        
        if y_prob is not None:
            metrics['calibration'] = self.calibration(y_true, y_prob, protected_attr)
            metrics['auc_parity'] = self.auc_parity(y_true, y_prob, protected_attr)
        
        return metrics
    
    def demographic_parity(self, y_pred: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate demographic parity difference."""
        groups = np.unique(protected_attr)
        selection_rates = {group: y_pred[protected_attr == group].mean() for group in groups}
        disparity = max(selection_rates.values()) - min(selection_rates.values())
        return FairnessMetricResult(
            metric_name="Demographic Parity",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=selection_rates,
            disparity=disparity,
            interpretation=f"Selection rate disparity: {disparity:.4f}"
        )
    
    def equalized_odds(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate equalized odds difference."""
        groups = np.unique(protected_attr)
        tprs, fprs = {}, {}
        for group in groups:
            mask = protected_attr == group
            cm = confusion_matrix(y_true[mask], y_pred[mask])
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                tprs[group] = tp / (tp + fn) if (tp + fn) > 0 else 0
                fprs[group] = fp / (fp + tn) if (fp + tn) > 0 else 0
        tpr_diff = max(tprs.values()) - min(tprs.values()) if tprs else 0
        fpr_diff = max(fprs.values()) - min(fprs.values()) if fprs else 0
        max_diff = max(tpr_diff, fpr_diff)
        return FairnessMetricResult(
            metric_name="Equalized Odds",
            value=max_diff,
            threshold=self.threshold,
            is_fair=max_diff <= self.threshold,
            group_values={"TPR": tprs, "FPR": fprs},
            disparity=max_diff,
            interpretation=f"Max(TPR: {tpr_diff:.4f}, FPR: {fpr_diff:.4f})"
        )
    
    def equal_opportunity(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate equal opportunity difference (TPR equality)."""
        groups = np.unique(protected_attr)
        tprs = {}
        for group in groups:
            mask = (protected_attr == group) & (y_true == 1)
            if mask.sum() > 0:
                tprs[group] = y_pred[mask].mean()
        disparity = max(tprs.values()) - min(tprs.values()) if tprs else 0
        return FairnessMetricResult(
            metric_name="Equal Opportunity",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=tprs,
            disparity=disparity,
            interpretation=f"TPR disparity: {disparity:.4f}"
        )
    
    def predictive_parity(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate predictive parity (PPV equality)."""
        groups = np.unique(protected_attr)
        ppvs = {}
        for group in groups:
            mask = (protected_attr == group) & (y_pred == 1)
            if mask.sum() > 0:
                ppvs[group] = y_true[mask].mean()
        disparity = max(ppvs.values()) - min(ppvs.values()) if ppvs else 0
        return FairnessMetricResult(
            metric_name="Predictive Parity",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=ppvs,
            disparity=disparity,
            interpretation=f"PPV disparity: {disparity:.4f}"
        )
    
    def calibration(self, y_true: np.ndarray, y_prob: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate calibration error across groups."""
        groups = np.unique(protected_attr)
        errors = {}
        for group in groups:
            mask = protected_attr == group
            pred_rate = y_prob[mask].mean()
            actual_rate = y_true[mask].mean()
            errors[group] = abs(pred_rate - actual_rate)
        disparity = max(errors.values()) - min(errors.values())
        return FairnessMetricResult(
            metric_name="Calibration",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=errors,
            disparity=disparity,
            interpretation=f"Calibration disparity: {disparity:.4f}"
        )
    
    def auc_parity(self, y_true: np.ndarray, y_prob: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate AUC parity across groups."""
        groups = np.unique(protected_attr)
        aucs = {}
        for group in groups:
            mask = protected_attr == group
            if len(np.unique(y_true[mask])) > 1:
                aucs[group] = roc_auc_score(y_true[mask], y_prob[mask])
            else:
                aucs[group] = 0.5
        disparity = max(aucs.values()) - min(aucs.values()) if aucs else 0
        return FairnessMetricResult(
            metric_name="AUC Parity",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=aucs,
            disparity=disparity,
            interpretation=f"AUC disparity: {disparity:.4f}"
        )
    
    def accuracy_parity(self, y_true: np.ndarray, y_pred: np.ndarray, protected_attr: np.ndarray) -> FairnessMetricResult:
        """Calculate accuracy parity."""
        groups = np.unique(protected_attr)
        accuracies = {group: accuracy_score(y_true[protected_attr == group], y_pred[protected_attr == group]) for group in groups}
        disparity = max(accuracies.values()) - min(accuracies.values())
        return FairnessMetricResult(
            metric_name="Accuracy Parity",
            value=disparity,
            threshold=self.threshold,
            is_fair=disparity <= self.threshold,
            group_values=accuracies,
            disparity=disparity,
            interpretation=f"Accuracy disparity: {disparity:.4f}"
        )
    
    def generate_fairness_report(self, metrics: Dict[str, FairnessMetricResult]) -> str:
        """Generate comprehensive fairness report."""
        fair_count = sum(1 for m in metrics.values() if m.is_fair)
        report = ["=" * 60, "FAIRNESS METRICS REPORT", "=" * 60]
        report.append(f"\nOverall Fairness: {fair_count}/{len(metrics)} metrics passed")
        report.append(f"Threshold: {self.threshold}\n")
        
        for name, result in metrics.items():
            status = "PASS" if result.is_fair else "FAIL"
            report.append(f"{name}: {status} (Value: {result.value:.4f})")
        
        return "\n".join(report)


if __name__ == "__main__":
    np.random.seed(42)
    n = 1000
    y_true = np.random.randint(0, 2, n)
    y_pred = np.random.randint(0, 2, n)
    y_prob = np.random.rand(n)
    protected = np.random.choice(['A', 'B', 'C'], n)
    
    metrics = FairnessMetrics(threshold=0.05)
    results = metrics.calculate_all_metrics(y_true, y_pred, y_prob, protected)
    print(metrics.generate_fairness_report(results))
