"""
ResilienceAI Continuous Monitoring
===================================
Continuous monitoring for ethical AI.
"""

import numpy as np
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
from sklearn.metrics import confusion_matrix
import json


@dataclass
class MonitoringAlert:
    alert_id: str
    timestamp: str
    alert_type: str
    severity: str
    metric_name: str
    metric_value: float
    threshold: float
    description: str
    recommended_action: str
    status: str


class ContinuousMonitor:
    """Continuous monitoring system for ethical AI."""
    
    def __init__(self, model_id: str, window_size: int = 1000):
        self.model_id = model_id
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.labels = deque(maxlen=window_size)
        self.protected_attrs = {}
        self.timestamps = deque(maxlen=window_size)
        self.thresholds = {
            'demographic_parity': 0.05,
            'equalized_odds': 0.05,
            'prediction_drift': 0.1,
            'performance_degradation': 0.05
        }
        self.alerts: List[MonitoringAlert] = []
        self.alert_handlers: List[Callable] = []
    
    def log_prediction(self, prediction: int, probability: float,
                       protected_attrs: Dict[str, Any], timestamp: Optional[str] = None):
        self.predictions.append({'prediction': prediction, 'probability': probability})
        for attr_name, attr_value in protected_attrs.items():
            if attr_name not in self.protected_attrs:
                self.protected_attrs[attr_name] = deque(maxlen=self.window_size)
            self.protected_attrs[attr_name].append(attr_value)
        self.timestamps.append(timestamp or datetime.now().isoformat())
    
    def log_label(self, label: int, timestamp: Optional[str] = None):
        self.labels.append(label)
    
    def check_fairness(self) -> List[MonitoringAlert]:
        alerts = []
        if len(self.labels) < 100:
            return alerts
        
        y_true = np.array(list(self.labels))
        y_pred = np.array([p['prediction'] for p in self.predictions])
        
        for attr_name, attr_values in self.protected_attrs.items():
            attr_array = np.array(list(attr_values))
            
            dp_violation = self._check_demographic_parity(y_pred, attr_array)
            if dp_violation['violated']:
                alerts.append(MonitoringAlert(
                    alert_id=f"DP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now().isoformat(),
                    alert_type="fairness_violation",
                    severity=dp_violation['severity'],
                    metric_name="demographic_parity",
                    metric_value=dp_violation['value'],
                    threshold=self.thresholds['demographic_parity'],
                    description=f"Demographic parity violation for {attr_name}",
                    recommended_action="Review thresholds and retrain",
                    status="open"
                ))
        
        self.alerts.extend(alerts)
        for handler in self.alert_handlers:
            for alert in alerts:
                handler(alert)
        return alerts
    
    def _check_demographic_parity(self, y_pred: np.ndarray, attr: np.ndarray) -> Dict:
        groups = np.unique(attr)
        rates = [y_pred[attr == g].mean() for g in groups]
        disparity = max(rates) - min(rates)
        severity = 'low' if disparity < 0.08 else 'medium' if disparity < 0.12 else 'high'
        return {
            'violated': disparity > self.thresholds['demographic_parity'],
            'value': disparity,
            'severity': severity
        }
    
    def get_monitoring_dashboard(self) -> Dict:
        return {
            "model_id": self.model_id,
            "samples_logged": len(self.predictions),
            "open_alerts": len([a for a in self.alerts if a.status == 'open']),
            "current_metrics": self._calculate_current_metrics()
        }
    
    def _calculate_current_metrics(self) -> Dict:
        if len(self.predictions) == 0:
            return {}
        y_pred = np.array([p['prediction'] for p in self.predictions])
        y_prob = np.array([p['probability'] for p in self.predictions])
        metrics = {
            "positive_rate": y_pred.mean(),
            "avg_confidence": y_prob.mean(),
            "distribution": {"positive": int(y_pred.sum()), "negative": int(len(y_pred) - y_pred.sum())}
        }
        if len(self.labels) > 0:
            y_true = np.array(list(self.labels))
            min_len = min(len(y_true), len(y_pred))
            metrics["accuracy"] = (y_true[:min_len] == y_pred[:min_len]).mean()
        return metrics
    
    def register_alert_handler(self, handler: Callable):
        self.alert_handlers.append(handler)
    
    def generate_monitoring_report(self) -> str:
        report = {
            "model_id": self.model_id,
            "report_time": datetime.now().isoformat(),
            "summary": {
                "total_samples": len(self.predictions),
                "total_alerts": len(self.alerts),
                "open_alerts": len([a for a in self.alerts if a.status == 'open'])
            },
            "current_metrics": self._calculate_current_metrics()
        }
        return json.dumps(report, indent=2)


if __name__ == "__main__":
    monitor = ContinuousMonitor("risk-predictor-v1", window_size=500)
    
    np.random.seed(42)
    for i in range(200):
        pred = np.random.randint(0, 2)
        prob = np.random.rand()
        protected = {'gender': np.random.choice(['M', 'F'])}
        monitor.log_prediction(pred, prob, protected)
        monitor.log_label(np.random.randint(0, 2))
    
    alerts = monitor.check_fairness()
    print(f"Generated {len(alerts)} alerts")
    print(json.dumps(monitor.get_monitoring_dashboard(), indent=2))
