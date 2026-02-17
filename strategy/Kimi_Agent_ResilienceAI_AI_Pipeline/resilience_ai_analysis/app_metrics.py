"""
Application-level metrics for capacity planning
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class RequestMetrics:
    """Request-level metrics"""
    timestamp: datetime
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    payload_size_bytes: int
    user_id: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Service-level aggregated metrics"""
    service_name: str
    timestamp: datetime
    
    # Request metrics
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    
    # Latency metrics (ms)
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float
    
    # Throughput
    requests_per_second: float
    
    # Queue metrics
    queue_depth: int
    queue_wait_time_ms: float
    
    # Resource usage
    cpu_percent: float
    memory_mb: float
    active_connections: int


class ApplicationMetricsCollector:
    """Collect application-level metrics"""
    
    def __init__(self):
        self.request_history: List[RequestMetrics] = []
        self.service_metrics: Dict[str, List[ServiceMetrics]] = defaultdict(list)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_latency': 0,
            'errors': 0
        })
        
    def record_request(self, metric: RequestMetrics):
        """Record a single request metric"""
        self.request_history.append(metric)
        
        # Update endpoint stats
        key = f"{metric.method}:{metric.endpoint}"
        self.endpoint_stats[key]['count'] += 1
        self.endpoint_stats[key]['total_latency'] += metric.response_time_ms
        if metric.status_code >= 400:
            self.endpoint_stats[key]['errors'] += 1
    
    def calculate_service_metrics(
        self,
        service_name: str,
        window_seconds: int = 60
    ) -> ServiceMetrics:
        """Calculate aggregated service metrics"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        recent_requests = [
            r for r in self.request_history
            if r.timestamp >= cutoff
        ]
        
        if not recent_requests:
            return ServiceMetrics(
                service_name=service_name,
                timestamp=datetime.now(),
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                error_rate=0,
                avg_latency=0,
                p50_latency=0,
                p95_latency=0,
                p99_latency=0,
                max_latency=0,
                requests_per_second=0,
                queue_depth=0,
                queue_wait_time_ms=0,
                cpu_percent=0,
                memory_mb=0,
                active_connections=0
            )
        
        latencies = [r.response_time_ms for r in recent_requests]
        sorted_latencies = sorted(latencies)
        total = len(recent_requests)
        errors = sum(1 for r in recent_requests if r.status_code >= 400)
        
        return ServiceMetrics(
            service_name=service_name,
            timestamp=datetime.now(),
            total_requests=total,
            successful_requests=total - errors,
            failed_requests=errors,
            error_rate=errors / total if total > 0 else 0,
            avg_latency=sum(latencies) / total,
            p50_latency=sorted_latencies[int(total * 0.5)],
            p95_latency=sorted_latencies[int(total * 0.95)] if total > 1 else sorted_latencies[0],
            p99_latency=sorted_latencies[int(total * 0.99)] if total > 1 else sorted_latencies[0],
            max_latency=max(latencies),
            requests_per_second=total / window_seconds,
            queue_depth=0,
            queue_wait_time_ms=0,
            cpu_percent=0,
            memory_mb=0,
            active_connections=0
        )
    
    def get_endpoint_breakdown(self) -> Dict[str, Dict]:
        """Get performance breakdown by endpoint"""
        breakdown = {}
        for endpoint, stats in self.endpoint_stats.items():
            if stats['count'] > 0:
                breakdown[endpoint] = {
                    'request_count': stats['count'],
                    'avg_latency_ms': stats['total_latency'] / stats['count'],
                    'error_count': stats['errors'],
                    'error_rate': stats['errors'] / stats['count']
                }
        return breakdown
