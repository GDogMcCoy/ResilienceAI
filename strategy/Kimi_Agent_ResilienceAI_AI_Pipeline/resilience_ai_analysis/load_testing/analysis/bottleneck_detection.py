"""
Bottleneck identification framework for ResilienceAI
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import time
import statistics


class BottleneckType(Enum):
    """Types of performance bottlenecks"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    DATABASE = "database"
    ML_INFERENCE = "ml_inference"
    MODEL_LOADING = "model_loading"
    QUEUE_BACKLOG = "queue_backlog"
    EXTERNAL_API = "external_api"
    UNKNOWN = "unknown"


@dataclass
class Bottleneck:
    """Detected bottleneck information"""
    type: BottleneckType
    severity: str  # low, medium, high, critical
    component: str
    metric: str
    value: float
    threshold: float
    timestamp: float
    recommendation: str


class BottleneckDetector:
    """
    Detects performance bottlenecks in the system
    """
    
    def __init__(self):
        self.metrics_history: Dict[str, List[float]] = {}
        self.bottlenecks: List[Bottleneck] = []
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_io_wait": 20.0,
            "network_latency_ms": 100.0,
            "db_query_time_ms": 500.0,
            "ml_inference_ms": 100.0,
            "model_load_time_ms": 5000.0,
            "queue_depth": 1000,
            "error_rate_percent": 5.0,
            "p99_response_ms": 2000.0,
        }
    
    def record_metric(self, name: str, value: float):
        """Record a metric for analysis"""
        if name not in self.metrics_history:
            self.metrics_history[name] = []
        self.metrics_history[name].append(value)
        
        # Keep only last 1000 values
        self.metrics_history[name] = self.metrics_history[name][-1000:]
    
    def detect_cpu_bottleneck(self) -> Optional[Bottleneck]:
        """Detect CPU bottlenecks"""
        cpu_values = self.metrics_history.get("cpu_percent", [])
        if len(cpu_values) < 10:
            return None
        
        avg_cpu = statistics.mean(cpu_values[-10:])
        if avg_cpu > self.thresholds["cpu_percent"]:
            return Bottleneck(
                type=BottleneckType.CPU,
                severity=self._get_severity(avg_cpu, self.thresholds["cpu_percent"]),
                component="application_server",
                metric="cpu_percent",
                value=avg_cpu,
                threshold=self.thresholds["cpu_percent"],
                timestamp=time.time(),
                recommendation="Scale horizontally or optimize CPU-intensive operations"
            )
        return None
    
    def detect_memory_bottleneck(self) -> Optional[Bottleneck]:
        """Detect memory bottlenecks"""
        memory_values = self.metrics_history.get("memory_percent", [])
        if len(memory_values) < 10:
            return None
        
        avg_memory = statistics.mean(memory_values[-10:])
        if avg_memory > self.thresholds["memory_percent"]:
            return Bottleneck(
                type=BottleneckType.MEMORY,
                severity=self._get_severity(avg_memory, self.thresholds["memory_percent"]),
                component="application_server",
                metric="memory_percent",
                value=avg_memory,
                threshold=self.thresholds["memory_percent"],
                timestamp=time.time(),
                recommendation="Check for memory leaks, increase memory, or optimize model loading"
            )
        return None
    
    def detect_ml_inference_bottleneck(self) -> Optional[Bottleneck]:
        """Detect ML inference bottlenecks"""
        inference_values = self.metrics_history.get("ml_inference_ms", [])
        if len(inference_values) < 10:
            return None
        
        p95_inference = sorted(inference_values)[int(len(inference_values) * 0.95)]
        if p95_inference > self.thresholds["ml_inference_ms"]:
            return Bottleneck(
                type=BottleneckType.ML_INFERENCE,
                severity=self._get_severity(p95_inference, self.thresholds["ml_inference_ms"]),
                component="ml_service",
                metric="ml_inference_ms",
                value=p95_inference,
                threshold=self.thresholds["ml_inference_ms"],
                timestamp=time.time(),
                recommendation="Consider model optimization, batching, or GPU acceleration"
            )
        return None
    
    def detect_queue_bottleneck(self) -> Optional[Bottleneck]:
        """Detect queue backlog bottlenecks"""
        queue_values = self.metrics_history.get("queue_depth", [])
        if len(queue_values) < 5:
            return None
        
        current_depth = queue_values[-1]
        if current_depth > self.thresholds["queue_depth"]:
            return Bottleneck(
                type=BottleneckType.QUEUE_BACKLOG,
                severity=self._get_severity(current_depth, self.thresholds["queue_depth"]),
                component="task_queue",
                metric="queue_depth",
                value=current_depth,
                threshold=self.thresholds["queue_depth"],
                timestamp=time.time(),
                recommendation="Increase worker count or optimize processing time"
            )
        return None
    
    def detect_database_bottleneck(self) -> Optional[Bottleneck]:
        """Detect database bottlenecks"""
        db_values = self.metrics_history.get("db_query_time_ms", [])
        if len(db_values) < 10:
            return None
        
        p95_db = sorted(db_values)[int(len(db_values) * 0.95)]
        if p95_db > self.thresholds["db_query_time_ms"]:
            return Bottleneck(
                type=BottleneckType.DATABASE,
                severity=self._get_severity(p95_db, self.thresholds["db_query_time_ms"]),
                component="database",
                metric="db_query_time_ms",
                value=p95_db,
                threshold=self.thresholds["db_query_time_ms"],
                timestamp=time.time(),
                recommendation="Optimize queries, add indexes, or scale database"
            )
        return None
    
    def detect_network_bottleneck(self) -> Optional[Bottleneck]:
        """Detect network bottlenecks"""
        network_values = self.metrics_history.get("network_latency_ms", [])
        if len(network_values) < 10:
            return None
        
        avg_latency = statistics.mean(network_values[-10:])
        if avg_latency > self.thresholds["network_latency_ms"]:
            return Bottleneck(
                type=BottleneckType.NETWORK,
                severity=self._get_severity(avg_latency, self.thresholds["network_latency_ms"]),
                component="network",
                metric="network_latency_ms",
                value=avg_latency,
                threshold=self.thresholds["network_latency_ms"],
                timestamp=time.time(),
                recommendation="Check network configuration, consider CDN or connection pooling"
            )
        return None
    
    def _get_severity(self, value: float, threshold: float) -> str:
        """Determine severity based on how much threshold is exceeded"""
        ratio = value / threshold
        if ratio > 2.0:
            return "critical"
        elif ratio > 1.5:
            return "high"
        elif ratio > 1.2:
            return "medium"
        else:
            return "low"
    
    def run_detection(self) -> List[Bottleneck]:
        """Run all bottleneck detection methods"""
        detectors: List[Callable[[], Optional[Bottleneck]]] = [
            self.detect_cpu_bottleneck,
            self.detect_memory_bottleneck,
            self.detect_ml_inference_bottleneck,
            self.detect_queue_bottleneck,
            self.detect_database_bottleneck,
            self.detect_network_bottleneck,
        ]
        
        new_bottlenecks = []
        for detector in detectors:
            bottleneck = detector()
            if bottleneck:
                new_bottlenecks.append(bottleneck)
                self.bottlenecks.append(bottleneck)
        
        return new_bottlenecks
    
    def get_bottleneck_report(self) -> Dict:
        """Generate a comprehensive bottleneck report"""
        return {
            "total_bottlenecks_detected": len(self.bottlenecks),
            "bottlenecks_by_type": self._group_by_type(),
            "critical_bottlenecks": [
                b for b in self.bottlenecks if b.severity == "critical"
            ],
            "recommendations": self._generate_recommendations(),
        }
    
    def _group_by_type(self) -> Dict[str, int]:
        """Group bottlenecks by type"""
        counts = {}
        for b in self.bottlenecks:
            counts[b.type.value] = counts.get(b.type.value, 0) + 1
        return counts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations from detected bottlenecks"""
        recommendations = set()
        for b in self.bottlenecks:
            recommendations.add(b.recommendation)
        return list(recommendations)


# Bottleneck Test Scenarios
BOTTLENECK_TEST_SCENARIOS = {
    "cpu_intensive": {
        "description": "Test CPU-intensive model inference",
        "endpoint": "/api/v1/predict",
        "payload": {"model_type": "complex_nn", "features": "large_set"},
        "concurrent_users": 500,
        "duration": "10m",
        "expected_bottleneck": BottleneckType.CPU,
    },
    "memory_intensive": {
        "description": "Test memory-intensive operations",
        "endpoint": "/api/v1/models/{id}/deploy",
        "payload": {"preload": True, "cache_size": "large"},
        "concurrent_users": 100,
        "duration": "15m",
        "expected_bottleneck": BottleneckType.MEMORY,
    },
    "io_intensive": {
        "description": "Test I/O intensive batch processing",
        "endpoint": "/api/v1/batch-predict",
        "payload": {"batch_size": 10000, "output_format": "detailed"},
        "concurrent_users": 50,
        "duration": "10m",
        "expected_bottleneck": BottleneckType.DISK_IO,
    },
    "queue_buildup": {
        "description": "Test queue handling under load",
        "endpoint": "/api/v1/predict",
        "payload": {"async": True, "priority": "low"},
        "concurrent_users": 1000,
        "duration": "5m",
        "expected_bottleneck": BottleneckType.QUEUE_BACKLOG,
    },
}
