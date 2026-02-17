"""
Prometheus metrics for load testing
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server, Info
from typing import Optional
import time


class LoadTestMetrics:
    """Prometheus metrics for load testing"""
    
    def __init__(self, namespace: str = "loadtest"):
        self.namespace = namespace
        
        # Info metric
        self.test_info = Info(
            f'{namespace}_test',
            'Load test information'
        )
        
        # Counters
        self.requests_total = Counter(
            f'{namespace}_requests_total',
            'Total requests',
            ['endpoint', 'method', 'status']
        )
        
        self.errors_total = Counter(
            f'{namespace}_errors_total',
            'Total errors',
            ['endpoint', 'error_type']
        )
        
        # Histograms
        self.request_duration = Histogram(
            f'{namespace}_request_duration_seconds',
            'Request duration in seconds',
            ['endpoint', 'method'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        )
        
        self.response_size = Histogram(
            f'{namespace}_response_size_bytes',
            'Response size in bytes',
            ['endpoint'],
            buckets=[100, 1000, 10000, 100000, 1000000]
        )
        
        # Gauges
        self.active_users = Gauge(
            f'{namespace}_active_users',
            'Number of active users'
        )
        
        self.current_rps = Gauge(
            f'{namespace}_current_rps',
            'Current requests per second'
        )
        
        self.response_time_p50 = Gauge(
            f'{namespace}_response_time_p50_seconds',
            '50th percentile response time'
        )
        
        self.response_time_p95 = Gauge(
            f'{namespace}_response_time_p95_seconds',
            '95th percentile response time'
        )
        
        self.response_time_p99 = Gauge(
            f'{namespace}_response_time_p99_seconds',
            '99th percentile response time'
        )
        
        self.error_rate = Gauge(
            f'{namespace}_error_rate_percent',
            'Error rate percentage'
        )
    
    def record_request(self, endpoint: str, method: str, status: int, 
                       duration: float, response_size: int = 0):
        """Record a request metric"""
        status_class = f"{status // 100}xx"
        
        self.requests_total.labels(
            endpoint=endpoint,
            method=method,
            status=status_class
        ).inc()
        
        self.request_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
        
        if response_size > 0:
            self.response_size.labels(endpoint=endpoint).observe(response_size)
    
    def record_error(self, endpoint: str, error_type: str):
        """Record an error metric"""
        self.errors_total.labels(
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    def update_active_users(self, count: int):
        """Update active users gauge"""
        self.active_users.set(count)
    
    def update_rps(self, rps: float):
        """Update RPS gauge"""
        self.current_rps.set(rps)
    
    def update_percentiles(self, p50: float, p95: float, p99: float):
        """Update response time percentiles"""
        self.response_time_p50.set(p50)
        self.response_time_p95.set(p95)
        self.response_time_p99.set(p99)
    
    def update_error_rate(self, rate: float):
        """Update error rate gauge"""
        self.error_rate.set(rate)
    
    def set_test_info(self, test_id: str, test_type: str, target_host: str):
        """Set test information"""
        self.test_info.info({
            'test_id': test_id,
            'test_type': test_type,
            'target_host': target_host,
        })


def setup_metrics_server(port: int = 9090) -> None:
    """Start Prometheus metrics server"""
    start_http_server(port)
    print(f"Metrics server started on port {port}")


class MetricsCollector:
    """Collect and aggregate metrics during load test"""
    
    def __init__(self):
        self.response_times: list = []
        self.error_count: int = 0
        self.request_count: int = 0
        self.start_time: Optional[float] = None
    
    def start(self):
        """Start collecting metrics"""
        self.start_time = time.time()
    
    def record(self, response_time: float, is_error: bool = False):
        """Record a metric sample"""
        self.response_times.append(response_time)
        self.request_count += 1
        if is_error:
            self.error_count += 1
    
    def get_statistics(self) -> dict:
        """Get collected statistics"""
        if not self.response_times:
            return {}
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': (self.error_count / max(self.request_count, 1)) * 100,
            'duration_seconds': duration,
            'rps': self.request_count / max(duration, 1),
            'response_time': {
                'min': min(sorted_times),
                'max': max(sorted_times),
                'mean': sum(sorted_times) / n,
                'p50': sorted_times[int(n * 0.50)],
                'p90': sorted_times[int(n * 0.90)],
                'p95': sorted_times[int(n * 0.95)],
                'p99': sorted_times[int(n * 0.99)],
            }
        }
    
    def reset(self):
        """Reset all metrics"""
        self.response_times = []
        self.error_count = 0
        self.request_count = 0
        self.start_time = None
