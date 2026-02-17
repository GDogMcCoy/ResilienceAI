"""
Performance Metrics Tracking System for ResilienceAI

Comprehensive tracking of system performance and model effectiveness.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import threading
import json
import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


@dataclass
class ModelPerformanceMetrics:
    """Metrics for model performance tracking."""
    model_name: str
    model_version: str
    timestamp: datetime
    
    # Prediction metrics
    prediction_count: int = 0
    prediction_latency_ms: float = 0.0
    prediction_latency_p95_ms: float = 0.0
    prediction_latency_p99_ms: float = 0.0
    
    # Accuracy metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None  # Mean Absolute Error
    rmse: Optional[float] = None  # Root Mean Square Error
    r2_score: Optional[float] = None
    
    # Drift metrics
    data_drift_score: Optional[float] = None
    concept_drift_score: Optional[float] = None
    feature_drift_scores: Dict[str, float] = field(default_factory=dict)
    
    # Resource metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
            "prediction_count": self.prediction_count,
            "prediction_latency_ms": self.prediction_latency_ms,
            "prediction_latency_p95_ms": self.prediction_latency_p95_ms,
            "prediction_latency_p99_ms": self.prediction_latency_p99_ms,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "mae": self.mae,
            "rmse": self.rmse,
            "r2_score": self.r2_score,
            "data_drift_score": self.data_drift_score,
            "concept_drift_score": self.concept_drift_score,
            "feature_drift_scores": self.feature_drift_scores,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent
        }


@dataclass
class SystemHealthMetrics:
    """System-level health metrics."""
    timestamp: datetime
    
    # Availability
    uptime_seconds: float = 0.0
    availability_percent: float = 100.0
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    
    # Latency metrics
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    
    # Resource utilization
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "availability_percent": self.availability_percent,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate": self.error_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "p50_response_time_ms": self.p50_response_time_ms,
            "p95_response_time_ms": self.p95_response_time_ms,
            "p99_response_time_ms": self.p99_response_time_ms,
            "requests_per_second": self.requests_per_second,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_usage_percent": self.disk_usage_percent
        }


@dataclass
class UserExperienceMetrics:
    """User experience and satisfaction metrics."""
    timestamp: datetime
    period: str  # "hourly", "daily", "weekly", "monthly"
    
    # Engagement
    active_users: int = 0
    total_sessions: int = 0
    avg_session_duration_seconds: float = 0.0
    
    # Satisfaction
    explicit_feedback_count: int = 0
    avg_satisfaction_score: float = 0.0
    nps_score: Optional[float] = None  # Net Promoter Score
    
    # Quality
    avg_response_quality: float = 0.0
    high_quality_response_percent: float = 0.0
    
    # Retention
    return_user_percent: float = 0.0
    churn_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "period": self.period,
            "active_users": self.active_users,
            "total_sessions": self.total_sessions,
            "avg_session_duration_seconds": self.avg_session_duration_seconds,
            "explicit_feedback_count": self.explicit_feedback_count,
            "avg_satisfaction_score": self.avg_satisfaction_score,
            "nps_score": self.nps_score,
            "avg_response_quality": self.avg_response_quality,
            "high_quality_response_percent": self.high_quality_response_percent,
            "return_user_percent": self.return_user_percent,
            "churn_rate": self.churn_rate
        }


class MetricsTracker:
    """
    Comprehensive metrics tracking and aggregation system.
    
    Tracks:
    - Model performance over time
    - System health and availability
    - User experience metrics
    - Custom business metrics
    
    Features:
    - Real-time metric collection
    - Automatic aggregation (hourly, daily, weekly)
    - Anomaly detection
    - Trend analysis
    - Efficient storage (JSONL/Parquet)
    """
    
    def __init__(
        self,
        storage_path: str = "data/metrics",
        buffer_size: int = 1000,
        auto_flush: bool = True
    ):
        """
        Initialize the metrics tracker.
        
        Args:
            storage_path: Directory for metric storage
            buffer_size: Number of metrics to buffer before flushing
            auto_flush: Whether to auto-flush when buffer is full
        """
        self.storage_path = Path(storage_path)
        self.buffer_size = buffer_size
        self.auto_flush = auto_flush
        
        self.metrics_buffer: Dict[str, List[Dict]] = defaultdict(list)
        self.buffer_lock = threading.Lock()
        
        # Aggregation windows
        self.aggregation_windows = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }
        
        # Metric history for anomaly detection
        self.metric_history: Dict[str, List[float]] = defaultdict(list)
        self.history_max_size = 1000
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def record_model_prediction(
        self,
        model_name: str,
        model_version: str,
        latency_ms: float,
        prediction: Any,
        actual: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a single model prediction.
        
        Args:
            model_name: Name of the model
            model_version: Model version
            latency_ms: Prediction latency in milliseconds
            prediction: Model prediction
            actual: Ground truth (if available)
            metadata: Additional metadata
        """
        metric = {
            "type": "model_prediction",
            "model_name": model_name,
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency_ms,
            "prediction": str(prediction)[:100],  # Truncate for storage
            "actual": str(actual)[:100] if actual is not None else None,
            "metadata": metadata or {}
        }
        self._buffer_metric(metric)
        
        # Update history for anomaly detection
        self._update_history(f"{model_name}_latency", latency_ms)
    
    def record_model_performance(
        self,
        metrics: ModelPerformanceMetrics
    ):
        """Record comprehensive model performance metrics."""
        metric = {
            "type": "model_performance",
            **metrics.to_dict()
        }
        self._buffer_metric(metric)
    
    def record_system_health(
        self,
        metrics: SystemHealthMetrics
    ):
        """Record system health metrics."""
        metric = {
            "type": "system_health",
            **metrics.to_dict()
        }
        self._buffer_metric(metric)
        
        # Update history
        self._update_history("error_rate", metrics.error_rate)
        self._update_history("response_time", metrics.avg_response_time_ms)
    
    def record_user_experience(
        self,
        metrics: UserExperienceMetrics
    ):
        """Record user experience metrics."""
        metric = {
            "type": "user_experience",
            **metrics.to_dict()
        }
        self._buffer_metric(metric)
    
    def record_custom_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a custom metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
            timestamp: Optional timestamp (defaults to now)
        """
        metric = {
            "type": "custom",
            "metric_name": metric_name,
            "value": value,
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "tags": tags or {}
        }
        self._buffer_metric(metric)
        
        # Update history
        self._update_history(metric_name, value)
    
    def record_query_metrics(
        self,
        query_id: str,
        query: str,
        latency_ms: float,
        tools_used: List[str],
        quality_score: Optional[float] = None,
        success: bool = True
    ):
        """
        Record metrics for a single query.
        
        Args:
            query_id: Query identifier
            query: Query text
            latency_ms: Response latency
            tools_used: List of tools invoked
            quality_score: Optional quality score
            success: Whether query was successful
        """
        metric = {
            "type": "query",
            "query_id": query_id,
            "query_length": len(query.split()),
            "latency_ms": latency_ms,
            "tools_count": len(tools_used),
            "tools_used": tools_used,
            "quality_score": quality_score,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self._buffer_metric(metric)
        
        # Update history
        self._update_history("query_latency", latency_ms)
        if quality_score is not None:
            self._update_history("query_quality", quality_score)
    
    def _buffer_metric(self, metric: Dict[str, Any]):
        """Add metric to buffer and flush if needed."""
        with self.buffer_lock:
            metric_type = metric["type"]
            self.metrics_buffer[metric_type].append(metric)
            
            if len(self.metrics_buffer[metric_type]) >= self.buffer_size and self.auto_flush:
                self._flush_buffer(metric_type)
    
    def _flush_buffer(self, metric_type: str):
        """Persist buffered metrics to storage."""
        if metric_type not in self.metrics_buffer:
            return
        
        metrics = self.metrics_buffer[metric_type]
        if not metrics:
            return
        
        # Use JSONL for simple storage
        filename = self.storage_path / f"{metric_type}_{datetime.now():%Y%m%d}.jsonl"
        
        with open(filename, "a") as f:
            for metric in metrics:
                f.write(json.dumps(metric) + "\n")
        
        # Clear buffer
        self.metrics_buffer[metric_type] = []
    
    def _update_history(self, metric_name: str, value: float):
        """Update metric history for anomaly detection."""
        self.metric_history[metric_name].append(value)
        
        # Keep history bounded
        if len(self.metric_history[metric_name]) > self.history_max_size:
            self.metric_history[metric_name] = self.metric_history[metric_name][-self.history_max_size:]
    
    def flush(self):
        """Manually flush all buffers."""
        with self.buffer_lock:
            for metric_type in list(self.metrics_buffer.keys()):
                self._flush_buffer(metric_type)
    
    def get_metrics_summary(
        self,
        metric_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a metric type.
        
        Args:
            metric_type: Type of metrics to summarize
            start_date: Filter by start date
            end_date: Filter by end date
            metric_name: Filter by specific metric name (for custom metrics)
            
        Returns:
            Summary dictionary with statistics
        """
        # Load relevant files
        all_metrics = []
        
        for file_path in self.storage_path.glob(f"{metric_type}_*.jsonl"):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            timestamp = datetime.fromisoformat(data["timestamp"])
                            
                            # Apply filters
                            if start_date and timestamp < start_date:
                                continue
                            if end_date and timestamp > end_date:
                                continue
                            if metric_name and data.get("metric_name") != metric_name:
                                continue
                            
                            all_metrics.append(data)
            except Exception as e:
                continue
        
        if not all_metrics:
            return {"error": "No metrics found", "total_records": 0}
        
        # Compute summary
        summary = {
            "total_records": len(all_metrics),
            "date_range": {
                "start": min(m["timestamp"] for m in all_metrics),
                "end": max(m["timestamp"] for m in all_metrics)
            }
        }
        
        # Extract numeric values
        numeric_values = []
        for m in all_metrics:
            if "value" in m and isinstance(m["value"], (int, float)):
                numeric_values.append(m["value"])
            elif "latency_ms" in m:
                numeric_values.append(m["latency_ms"])
            elif "quality_score" in m and m["quality_score"] is not None:
                numeric_values.append(m["quality_score"])
        
        if numeric_values:
            summary["statistics"] = {
                "count": len(numeric_values),
                "mean": round(np.mean(numeric_values), 3),
                "median": round(np.median(numeric_values), 3),
                "std": round(np.std(numeric_values), 3),
                "min": round(min(numeric_values), 3),
                "max": round(max(numeric_values), 3),
                "p95": round(np.percentile(numeric_values, 95), 3),
                "p99": round(np.percentile(numeric_values, 99), 3)
            }
        
        return summary
    
    def detect_anomalies(
        self,
        metric_name: str,
        window_size: int = 100,
        threshold_std: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metric values.
        
        Args:
            metric_name: Name of metric to check
            window_size: Number of recent values to consider
            threshold_std: Standard deviation threshold for anomaly
            
        Returns:
            List of detected anomalies
        """
        if metric_name not in self.metric_history:
            return []
        
        values = self.metric_history[metric_name][-window_size:]
        
        if len(values) < 10:
            return []
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        threshold = threshold_std * std
        anomalies = []
        
        # Check most recent value
        recent_value = values[-1]
        z_score = (recent_value - mean) / std
        
        if abs(z_score) > threshold_std:
            anomalies.append({
                "metric_name": metric_name,
                "value": recent_value,
                "expected_range": [mean - threshold, mean + threshold],
                "z_score": round(z_score, 3),
                "severity": "critical" if abs(z_score) > 4 else "warning",
                "timestamp": datetime.now().isoformat()
            })
        
        return anomalies
    
    def get_model_performance_summary(
        self,
        model_name: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get performance summary for models.
        
        Args:
            model_name: Optional model name filter
            days: Number of days to include
            
        Returns:
            Performance summary
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Load model performance metrics
        all_metrics = []
        
        for file_path in self.storage_path.glob("model_performance_*.jsonl"):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            timestamp = datetime.fromisoformat(data["timestamp"])
                            
                            if timestamp >= start_date:
                                if model_name is None or data.get("model_name") == model_name:
                                    all_metrics.append(data)
            except Exception:
                continue
        
        if not all_metrics:
            return {"error": "No model performance data found"}
        
        # Group by model
        by_model = defaultdict(list)
        for m in all_metrics:
            by_model[m["model_name"]].append(m)
        
        summary = {}
        for model, metrics in by_model.items():
            summary[model] = {
                "record_count": len(metrics),
                "avg_accuracy": np.mean([m["accuracy"] for m in metrics if m.get("accuracy")]),
                "avg_latency_ms": np.mean([m["prediction_latency_ms"] for m in metrics]),
                "latest_version": max(metrics, key=lambda x: x["timestamp"]).get("model_version")
            }
        
        return summary
    
    def get_system_health_summary(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get system health summary.
        
        Args:
            hours: Number of hours to include
            
        Returns:
            Health summary
        """
        start_date = datetime.now() - timedelta(hours=hours)
        
        # Load system health metrics
        all_metrics = []
        
        for file_path in self.storage_path.glob("system_health_*.jsonl"):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            timestamp = datetime.fromisoformat(data["timestamp"])
                            
                            if timestamp >= start_date:
                                all_metrics.append(data)
            except Exception:
                continue
        
        if not all_metrics:
            return {"error": "No system health data found"}
        
        # Compute summary
        error_rates = [m["error_rate"] for m in all_metrics]
        response_times = [m["avg_response_time_ms"] for m in all_metrics]
        
        return {
            "period_hours": hours,
            "record_count": len(all_metrics),
            "avg_error_rate": round(np.mean(error_rates), 4),
            "max_error_rate": round(max(error_rates), 4),
            "avg_response_time_ms": round(np.mean(response_times), 2),
            "p95_response_time_ms": round(np.percentile(response_times, 95), 2),
            "latest_availability": all_metrics[-1].get("availability_percent", 100.0)
        }


# Convenience functions
def record_latency(
    operation: str,
    latency_ms: float,
    tracker: Optional[MetricsTracker] = None
):
    """Quick latency recording."""
    if tracker is None:
        tracker = MetricsTracker()
    
    tracker.record_custom_metric(
        metric_name=f"{operation}_latency_ms",
        value=latency_ms
    )


def record_error(
    error_type: str,
    tracker: Optional[MetricsTracker] = None
):
    """Quick error recording."""
    if tracker is None:
        tracker = MetricsTracker()
    
    tracker.record_custom_metric(
        metric_name=f"error_{error_type}",
        value=1.0
    )
