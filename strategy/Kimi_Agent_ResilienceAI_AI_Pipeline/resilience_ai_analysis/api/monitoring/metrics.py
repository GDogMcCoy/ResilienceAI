"""
API Monitoring and Analytics for ResilienceAI
Prometheus metrics, structured logging, and health checks

File: src/api/monitoring/metrics.py
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
import functools
from contextlib import contextmanager

# Optional Prometheus support
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Optional structured logging
try:
    import structlog
    logger = structlog.get_logger()
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False


# Prometheus Metrics (only if available)
if PROMETHEUS_AVAILABLE:
    # API Request Metrics
    API_REQUESTS_TOTAL = Counter(
        'resilienceai_api_requests_total',
        'Total API requests',
        ['service', 'endpoint', 'method', 'status']
    )
    
    API_REQUEST_DURATION = Histogram(
        'resilienceai_api_request_duration_seconds',
        'API request duration in seconds',
        ['service', 'endpoint'],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
    )
    
    API_ACTIVE_REQUESTS = Gauge(
        'resilienceai_api_active_requests',
        'Number of active API requests',
        ['service']
    )
    
    # Cache Metrics
    API_CACHE_HITS = Counter(
        'resilienceai_api_cache_hits_total',
        'Total cache hits',
        ['service', 'cache_type']
    )
    
    API_CACHE_MISSES = Counter(
        'resilienceai_api_cache_misses_total',
        'Total cache misses',
        ['service', 'cache_type']
    )
    
    API_CACHE_SIZE = Gauge(
        'resilienceai_api_cache_size',
        'Current cache size',
        ['service', 'cache_type']
    )
    
    # Circuit Breaker Metrics
    CIRCUIT_BREAKER_STATE = Gauge(
        'resilienceai_circuit_breaker_state',
        'Circuit breaker state (0=closed, 1=open, 2=half-open)',
        ['service']
    )
    
    CIRCUIT_BREAKER_FAILURES = Counter(
        'resilienceai_circuit_breaker_failures_total',
        'Total circuit breaker failures',
        ['service']
    )
    
    CIRCUIT_BREAKER_TRANSITIONS = Counter(
        'resilienceai_circuit_breaker_transitions_total',
        'Circuit breaker state transitions',
        ['service', 'from_state', 'to_state']
    )
    
    # Rate Limit Metrics
    RATE_LIMIT_HITS = Counter(
        'resilienceai_rate_limit_hits_total',
        'Total rate limit hits',
        ['service', 'key']
    )
    
    RATE_LIMIT_TOKENS = Gauge(
        'resilienceai_rate_limit_tokens',
        'Current rate limit tokens',
        ['service', 'key']
    )
    
    # External API Metrics
    EXTERNAL_API_LATENCY = Histogram(
        'resilienceai_external_api_latency_seconds',
        'External API latency',
        ['service', 'api_name'],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    )
    
    EXTERNAL_API_ERRORS = Counter(
        'resilienceai_external_api_errors_total',
        'External API errors',
        ['service', 'api_name', 'error_type']
    )
    
    EXTERNAL_API_REQUESTS = Counter(
        'resilienceai_external_api_requests_total',
        'External API requests',
        ['service', 'api_name', 'status']
    )
    
    # Data Freshness Metrics
    DATA_FRESHNESS_SECONDS = Gauge(
        'resilienceai_data_freshness_seconds',
        'Data freshness in seconds since last update',
        ['data_source']
    )
    
    DATA_UPDATE_TIMESTAMP = Gauge(
        'resilienceai_data_update_timestamp',
        'Unix timestamp of last data update',
        ['data_source']
    )
    
    # Webhook Metrics
    WEBHOOK_DELIVERIES = Counter(
        'resilienceai_webhook_deliveries_total',
        'Total webhook deliveries',
        ['subscription_id', 'status']
    )
    
    WEBHOOK_DELIVERY_DURATION = Histogram(
        'resilienceai_webhook_delivery_duration_seconds',
        'Webhook delivery duration',
        ['subscription_id']
    )
    
    # Application Info
    APP_INFO = Info(
        'resilienceai_app_info',
        'Application information'
    )


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    service: str
    endpoint: str
    method: str
    start_time: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    cache_hit: bool = False
    
    def duration(self) -> float:
        """Get request duration"""
        return time.time() - self.start_time


class APIMetricsCollector:
    """
    Collects and exposes API metrics
    
    Usage:
        collector = APIMetricsCollector()
        
        @collector.track_request("noaa", "/alerts")
        async def fetch_alerts():
            return await client.get_alerts()
    """
    
    def __init__(self):
        self.request_start_times: Dict[str, float] = {}
        self.health_checks: Dict[str, Callable] = {}
        
        # Set app info if Prometheus available
        if PROMETHEUS_AVAILABLE:
            APP_INFO.info({
                'version': '2.0.0',
                'name': 'ResilienceAI API',
                'environment': 'production'
            })
    
    def record_request_start(self, request_id: str, service: str):
        """Record request start time"""
        self.request_start_times[request_id] = time.time()
        
        if PROMETHEUS_AVAILABLE:
            API_ACTIVE_REQUESTS.labels(service=service).inc()
    
    def record_request_end(
        self,
        request_id: str,
        service: str,
        endpoint: str,
        method: str,
        status_code: int
    ):
        """Record request completion"""
        start_time = self.request_start_times.pop(request_id, None)
        
        if start_time and PROMETHEUS_AVAILABLE:
            duration = time.time() - start_time
            
            API_REQUEST_DURATION.labels(
                service=service,
                endpoint=endpoint
            ).observe(duration)
            
            API_REQUESTS_TOTAL.labels(
                service=service,
                endpoint=endpoint,
                method=method,
                status=status_code
            ).inc()
        
        if PROMETHEUS_AVAILABLE:
            API_ACTIVE_REQUESTS.labels(service=service).dec()
    
    def record_cache_hit(self, service: str, cache_type: str = "memory"):
        """Record cache hit"""
        if PROMETHEUS_AVAILABLE:
            API_CACHE_HITS.labels(service=service, cache_type=cache_type).inc()
    
    def record_cache_miss(self, service: str, cache_type: str = "memory"):
        """Record cache miss"""
        if PROMETHEUS_AVAILABLE:
            API_CACHE_MISSES.labels(service=service, cache_type=cache_type).inc()
    
    def update_cache_size(self, service: str, cache_type: str, size: int):
        """Update cache size metric"""
        if PROMETHEUS_AVAILABLE:
            API_CACHE_SIZE.labels(service=service, cache_type=cache_type).set(size)
    
    def record_external_api_call(
        self,
        service: str,
        api_name: str,
        latency: float,
        status_code: int = 200,
        error: Optional[str] = None
    ):
        """Record external API call metrics"""
        if PROMETHEUS_AVAILABLE:
            EXTERNAL_API_LATENCY.labels(
                service=service,
                api_name=api_name
            ).observe(latency)
            
            EXTERNAL_API_REQUESTS.labels(
                service=service,
                api_name=api_name,
                status=status_code
            ).inc()
            
            if error:
                EXTERNAL_API_ERRORS.labels(
                    service=service,
                    api_name=api_name,
                    error_type=error
                ).inc()
    
    def update_data_freshness(self, data_source: str, last_update: datetime):
        """Update data freshness metric"""
        if PROMETHEUS_AVAILABLE:
            freshness = (datetime.utcnow() - last_update).total_seconds()
            DATA_FRESHNESS_SECONDS.labels(data_source=data_source).set(freshness)
            DATA_UPDATE_TIMESTAMP.labels(data_source=data_source).set(
                last_update.timestamp()
            )
    
    def record_circuit_state_change(
        self,
        service: str,
        from_state: str,
        to_state: str
    ):
        """Record circuit breaker state change"""
        if PROMETHEUS_AVAILABLE:
            state_map = {"closed": 0, "open": 1, "half_open": 2}
            CIRCUIT_BREAKER_STATE.labels(service=service).set(state_map.get(to_state, 0))
            CIRCUIT_BREAKER_TRANSITIONS.labels(
                service=service,
                from_state=from_state,
                to_state=to_state
            ).inc()
    
    def record_rate_limit_hit(self, service: str, key: str):
        """Record rate limit hit"""
        if PROMETHEUS_AVAILABLE:
            RATE_LIMIT_HITS.labels(service=service, key=key).inc()
    
    def record_webhook_delivery(
        self,
        subscription_id: str,
        success: bool,
        duration: float
    ):
        """Record webhook delivery metric"""
        if PROMETHEUS_AVAILABLE:
            status = "success" if success else "failure"
            WEBHOOK_DELIVERIES.labels(
                subscription_id=subscription_id,
                status=status
            ).inc()
            WEBHOOK_DELIVERY_DURATION.labels(
                subscription_id=subscription_id
            ).observe(duration)
    
    def track_request(self, service: str, endpoint: str, method: str = "GET"):
        """Decorator for tracking API calls"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                request_id = f"{service}:{endpoint}:{time.time()}"
                
                self.record_request_start(request_id, service)
                
                try:
                    result = await func(*args, **kwargs)
                    self.record_request_end(
                        request_id, service, endpoint, method, 200
                    )
                    return result
                except Exception as e:
                    self.record_request_end(
                        request_id, service, endpoint, method, 500
                    )
                    raise
            
            return wrapper
        return decorator
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        import asyncio
        
        results = {}
        
        for name, check in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check):
                    result = await check()
                else:
                    result = check()
                
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "healthy": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return results
    
    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus-formatted metrics"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        return b"# Prometheus not available\n"
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint"""
        if PROMETHEUS_AVAILABLE:
            return CONTENT_TYPE_LATEST
        return "text/plain"


@contextmanager
def timed_execution(metric: Histogram, labels: Dict[str, str]):
    """Context manager for timing code execution"""
    start = time.time()
    try:
        yield
    finally:
        if PROMETHEUS_AVAILABLE:
            metric.labels(**labels).observe(time.time() - start)


class HealthCheckManager:
    """
    Manages health checks for all API dependencies
    
    Usage:
        health = HealthCheckManager()
        
        @health.add_check("noaa")
        async def check_noaa():
            return await test_noaa_connection()
        
        status = await health.run_all_checks()
    """
    
    def __init__(self):
        self.checks: Dict[str, Dict] = {}
    
    def add_check(
        self,
        name: str,
        check_func: Callable,
        interval: int = 60,
        timeout: int = 10,
        description: str = ""
    ):
        """Add a health check"""
        self.checks[name] = {
            "func": check_func,
            "interval": interval,
            "timeout": timeout,
            "description": description,
            "last_check": None,
            "last_result": None,
            "consecutive_failures": 0,
            "consecutive_successes": 0
        }
    
    async def run_check(self, name: str) -> Dict:
        """Run a single health check"""
        import asyncio
        
        check = self.checks.get(name)
        if not check:
            return {
                "status": "unknown",
                "error": "Check not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            check_func = check["func"]
            
            if asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(
                    check_func(),
                    timeout=check["timeout"]
                )
            else:
                result = check_func()
            
            check["last_check"] = datetime.utcnow()
            check["last_result"] = result
            
            if result:
                check["consecutive_successes"] += 1
                check["consecutive_failures"] = 0
            else:
                check["consecutive_failures"] += 1
                check["consecutive_successes"] = 0
            
            return {
                "status": "healthy" if result else "unhealthy",
                "description": check["description"],
                "last_check": check["last_check"].isoformat(),
                "consecutive_failures": check["consecutive_failures"],
                "consecutive_successes": check["consecutive_successes"]
            }
            
        except asyncio.TimeoutError:
            check["consecutive_failures"] += 1
            return {
                "status": "timeout",
                "description": check["description"],
                "consecutive_failures": check["consecutive_failures"],
                "timeout_seconds": check["timeout"]
            }
        except Exception as e:
            check["consecutive_failures"] += 1
            return {
                "status": "error",
                "description": check["description"],
                "error": str(e),
                "consecutive_failures": check["consecutive_failures"]
            }
    
    async def run_all_checks(self) -> Dict[str, Dict]:
        """Run all health checks"""
        results = {}
        for name in self.checks:
            results[name] = await self.run_check(name)
        return results
    
    def get_overall_status(self, results: Dict[str, Dict]) -> str:
        """Determine overall health status"""
        statuses = [r["status"] for r in results.values()]
        
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s in ["error", "timeout"] for s in statuses):
            return "degraded"
        return "unhealthy"
    
    def get_status_summary(self, results: Dict[str, Dict]) -> Dict:
        """Get status summary"""
        total = len(results)
        healthy = sum(1 for r in results.values() if r["status"] == "healthy")
        unhealthy = sum(1 for r in results.values() if r["status"] == "unhealthy")
        errors = sum(1 for r in results.values() if r["status"] in ["error", "timeout"])
        
        return {
            "total_checks": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "errors": errors,
            "overall_status": self.get_overall_status(results)
        }


class PerformanceProfiler:
    """
    Performance profiling for API calls
    """
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = {}
    
    def record(self, operation: str, duration: float):
        """Record operation duration"""
        if operation not in self.profiles:
            self.profiles[operation] = []
        self.profiles[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict:
        """Get statistics for operation"""
        durations = self.profiles.get(operation, [])
        
        if not durations:
            return {"count": 0}
        
        durations.sort()
        
        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "mean": sum(durations) / len(durations),
            "p50": durations[len(durations) // 2],
            "p95": durations[int(len(durations) * 0.95)],
            "p99": durations[int(len(durations) * 0.99)] if len(durations) >= 100 else max(durations)
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all operations"""
        return {op: self.get_stats(op) for op in self.profiles}


# Global instances
collector = APIMetricsCollector()
health = HealthCheckManager()
profiler = PerformanceProfiler()


if __name__ == "__main__":
    import asyncio
    
    async def test_metrics():
        # Test metrics collection
        collector.record_request_start("test-1", "noaa")
        await asyncio.sleep(0.1)
        collector.record_request_end("test-1", "noaa", "/alerts", "GET", 200)
        
        collector.record_cache_hit("noaa", "memory")
        collector.record_cache_miss("census", "redis")
        
        # Test health checks
        health.add_check("test", lambda: True, description="Test check")
        
        results = await health.run_all_checks()
        print(f"Health check results: {results}")
        
        summary = health.get_status_summary(results)
        print(f"Status summary: {summary}")
        
        # Test profiling
        profiler.record("test_op", 0.1)
        profiler.record("test_op", 0.2)
        profiler.record("test_op", 0.15)
        
        stats = profiler.get_stats("test_op")
        print(f"Profiler stats: {stats}")
        
        # Get Prometheus metrics
        metrics = collector.get_prometheus_metrics()
        print(f"\nPrometheus metrics:\n{metrics.decode()[:500]}...")
    
    asyncio.run(test_metrics())
