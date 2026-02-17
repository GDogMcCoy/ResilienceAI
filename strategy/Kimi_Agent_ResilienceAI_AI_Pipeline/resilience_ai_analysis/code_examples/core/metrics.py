"""
ResilienceAI - Metrics Collection
Prometheus metrics for monitoring and observability.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricValue:
    """Single metric value."""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: float


class MetricsCollector:
    """
    Collects and exposes metrics for the agent system.
    
    Features:
    - Prometheus integration
    - Custom metrics
    - Performance tracking
    - Health monitoring
    """
    
    def __init__(self, enable_prometheus: bool = True, port: int = 9090):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.port = port
        self._metrics: Dict[str, Any] = {}
        self._custom_metrics: Dict[str, List[MetricValue]] = {}
        
        if self.enable_prometheus:
            self._init_prometheus_metrics()
            self._start_server()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Request metrics
        self._agent_requests_total = Counter(
            'agent_requests_total',
            'Total agent requests',
            ['agent_name', 'status']
        )
        
        self._agent_request_duration = Histogram(
            'agent_request_duration_seconds',
            'Agent request duration',
            ['agent_name'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Tool metrics
        self._tool_executions_total = Counter(
            'tool_executions_total',
            'Total tool executions',
            ['tool_name', 'status']
        )
        
        self._tool_execution_duration = Histogram(
            'tool_execution_duration_seconds',
            'Tool execution duration',
            ['tool_name'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        )
        
        # LLM metrics
        self._llm_requests_total = Counter(
            'llm_requests_total',
            'Total LLM requests',
            ['provider', 'model', 'status']
        )
        
        self._llm_tokens_used = Counter(
            'llm_tokens_used_total',
            'Total LLM tokens used',
            ['provider', 'token_type']  # prompt, completion
        )
        
        self._llm_latency = Histogram(
            'llm_latency_seconds',
            'LLM request latency',
            ['provider', 'model'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # System metrics
        self._active_agents = Gauge(
            'active_agents',
            'Number of active agents',
            ['agent_name']
        )
        
        self._memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['memory_type']
        )
        
        self._cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )
        
        self._cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )
        
        # Workflow metrics
        self._workflow_executions_total = Counter(
            'workflow_executions_total',
            'Total workflow executions',
            ['workflow_name', 'status']
        )
        
        self._workflow_duration = Histogram(
            'workflow_duration_seconds',
            'Workflow execution duration',
            ['workflow_name'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
        )
    
    def _start_server(self):
        """Start Prometheus HTTP server."""
        try:
            start_http_server(self.port)
            print(f"Prometheus metrics server started on port {self.port}")
        except Exception as e:
            print(f"Failed to start Prometheus server: {e}")
    
    def record_agent_request(
        self,
        agent_name: str,
        status: str,
        duration_ms: float
    ):
        """Record agent request metrics."""
        if self.enable_prometheus:
            self._agent_requests_total.labels(
                agent_name=agent_name,
                status=status
            ).inc()
            
            self._agent_request_duration.labels(
                agent_name=agent_name
            ).observe(duration_ms / 1000)
        
        # Also store custom metric
        self._store_custom_metric("agent_request", {
            "agent_name": agent_name,
            "status": status,
            "duration_ms": duration_ms
        })
    
    def record_tool_execution(
        self,
        tool_name: str,
        success: bool,
        duration_ms: float
    ):
        """Record tool execution metrics."""
        status = "success" if success else "failure"
        
        if self.enable_prometheus:
            self._tool_executions_total.labels(
                tool_name=tool_name,
                status=status
            ).inc()
            
            self._tool_execution_duration.labels(
                tool_name=tool_name
            ).observe(duration_ms / 1000)
        
        self._store_custom_metric("tool_execution", {
            "tool_name": tool_name,
            "status": status,
            "duration_ms": duration_ms
        })
    
    def record_llm_request(
        self,
        provider: str,
        model: str,
        success: bool,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float
    ):
        """Record LLM request metrics."""
        status = "success" if success else "failure"
        
        if self.enable_prometheus:
            self._llm_requests_total.labels(
                provider=provider,
                model=model,
                status=status
            ).inc()
            
            self._llm_tokens_used.labels(
                provider=provider,
                token_type="prompt"
            ).inc(prompt_tokens)
            
            self._llm_tokens_used.labels(
                provider=provider,
                token_type="completion"
            ).inc(completion_tokens)
            
            self._llm_latency.labels(
                provider=provider,
                model=model
            ).observe(latency_ms / 1000)
        
        self._store_custom_metric("llm_request", {
            "provider": provider,
            "model": model,
            "status": status,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": latency_ms
        })
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        if self.enable_prometheus:
            self._cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        if self.enable_prometheus:
            self._cache_misses.labels(cache_type=cache_type).inc()
    
    def set_active_agents(self, agent_name: str, count: int):
        """Set active agent count."""
        if self.enable_prometheus:
            self._active_agents.labels(agent_name=agent_name).set(count)
    
    def set_memory_usage(self, memory_type: str, bytes_used: int):
        """Set memory usage."""
        if self.enable_prometheus:
            self._memory_usage.labels(memory_type=memory_type).set(bytes_used)
    
    def record_workflow_execution(
        self,
        workflow_name: str,
        success: bool,
        duration_ms: float
    ):
        """Record workflow execution metrics."""
        status = "success" if success else "failure"
        
        if self.enable_prometheus:
            self._workflow_executions_total.labels(
                workflow_name=workflow_name,
                status=status
            ).inc()
            
            self._workflow_duration.labels(
                workflow_name=workflow_name
            ).observe(duration_ms / 1000)
    
    def _store_custom_metric(self, metric_type: str, data: Dict[str, Any]):
        """Store custom metric for non-Prometheus usage."""
        if metric_type not in self._custom_metrics:
            self._custom_metrics[metric_type] = []
        
        metric = MetricValue(
            name=metric_type,
            value=data.get("duration_ms", 0),
            labels={k: str(v) for k, v in data.items()},
            timestamp=time.time()
        )
        
        self._custom_metrics[metric_type].append(metric)
        
        # Limit stored metrics
        if len(self._custom_metrics[metric_type]) > 10000:
            self._custom_metrics[metric_type] = self._custom_metrics[metric_type][-5000:]
    
    def get_custom_metrics(
        self,
        metric_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get custom metrics."""
        if metric_type:
            metrics = self._custom_metrics.get(metric_type, [])
            return {
                metric_type: [
                    {
                        "name": m.name,
                        "value": m.value,
                        "labels": m.labels,
                        "timestamp": m.timestamp
                    }
                    for m in metrics[-limit:]
                ]
            }
        
        return {
            k: [
                {
                    "name": m.name,
                    "value": m.value,
                    "labels": m.labels,
                    "timestamp": m.timestamp
                }
                for m in v[-limit:]
            ]
            for k, v in self._custom_metrics.items()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        summary = {
            "prometheus_enabled": self.enable_prometheus,
            "custom_metrics": {
                k: len(v) for k, v in self._custom_metrics.items()
            }
        }
        
        if self.enable_prometheus:
            # Add Prometheus-specific summary
            summary["prometheus_port"] = self.port
        
        return summary
