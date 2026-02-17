# ResilienceAI Monitoring & Observability Design

## Executive Summary

This document provides a comprehensive monitoring and observability architecture for ResilienceAI, covering metrics collection, distributed tracing, logging, alerting, and performance monitoring across all system components.

---

## Table of Contents

1. [Monitoring Architecture Overview](#1-monitoring-architecture-overview)
2. [Prometheus Metrics Collection](#2-prometheus-metrics-collection)
3. [Grafana Dashboards](#3-grafana-dashboards)
4. [Distributed Tracing](#4-distributed-tracing)
5. [Centralized Logging](#5-centralized-logging)
6. [Alertmanager Configuration](#6-alertmanager-configuration)
7. [SLO/SLI Definitions](#7-slosli-definitions)
8. [Error Tracking](#8-error-tracking)
9. [Performance Monitoring](#9-performance-monitoring)
10. [Uptime Monitoring](#10-uptime-monitoring)
11. [Cost Monitoring](#11-cost-monitoring)
12. [Deployment Guide](#12-deployment-guide)
13. [Implementation Priority](#13-implementation-priority)

---

## 1. Monitoring Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Monitoring Stack                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Frontend   │  │    API       │  │   Worker     │  │   Database   │     │
│  │   (React)    │  │   (FastAPI)  │  │  (Celery)    │  │  (PostgreSQL)│     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Prometheus Metrics Collection                     │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │App      │ │Node     │ │Redis    │ │PostgreSQL│ │Custom   │       │   │
│  │  │Metrics  │ │Exporter │ │Exporter│ │ Exporter │ │Metrics  │       │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘ └────┬───┘       │   │
│  │       └───────────┴───────────┴───────────┴────────────┘            │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │                    ┌─────────────────┐                               │   │
│  │                    │   Prometheus    │                               │   │
│  │                    │    Server       │                               │   │
│  │                    └────────┬────────┘                               │   │
│  └─────────────────────────────┼───────────────────────────────────────┘   │
│                                │                                            │
│         ┌──────────────────────┼──────────────────────┐                     │
│         ▼                      ▼                      ▼                     │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │   Grafana   │      │ Alertmanager│      │   Thanos    │                 │
│  │  Dashboards │      │   (Alerts)  │      │ (Long-term) │                 │
│  └─────────────┘      └──────┬──────┘      └─────────────┘                 │
│                              │                                             │
│                              ▼                                             │
│                    ┌─────────────────┐                                     │
│                    │  Notification   │                                     │
│                    │   Channels      │                                     │
│                    │ (Slack, PagerDuty, Email)                           │
│                    └─────────────────┘                                     │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Distributed Tracing (Jaeger)                      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │  │
│  │  │ OpenTelemetry │ │ Jaeger Agent │ │ Jaeger Collector │ │ Storage │  │
│  │  │   SDKs        │ │              │ │                  │ │ (ES/Cassandra)│
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Centralized Logging (ELK Stack)                   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │  │
│  │  │ Filebeat│ │ Logstash│ │Elasticsearch│ │  Kibana  │               │  │
│  │  │         │ │         │ │             │ │          │               │  │
│  │  └─────────┘ └─────────┘ └─────────────┘ └──────────┘               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Error Tracking (Sentry)                           │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                               │  │
│  │  │ Sentry  │ │ Sentry  │ │ Sentry  │                               │  │
│  │  │  SDK    │ │ Server  │ │  Relay  │                               │  │
│  │  └─────────┘ └─────────┘ └─────────┘                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Mapping

| Component | Monitoring Tool | Metrics | Logs | Traces | Alerts |
|-----------|----------------|---------|------|--------|--------|
| Frontend (React) | Prometheus + Sentry | RUM metrics | Browser logs | OpenTelemetry | Error rate |
| API (FastAPI) | Prometheus | Request metrics | Application logs | OpenTelemetry | Latency, Errors |
| Workers (Celery) | Prometheus | Task metrics | Worker logs | OpenTelemetry | Queue depth, Failures |
| Database (PostgreSQL) | postgres_exporter | DB metrics | Slow query logs | - | Connection pool |
| Cache (Redis) | redis_exporter | Cache metrics | - | - | Memory usage |
| Message Queue (Redis/RabbitMQ) | rabbitmq_exporter | Queue metrics | - | - | Queue depth |
| Infrastructure | Node Exporter | System metrics | System logs | - | Resource usage |
| Kubernetes | kube-state-metrics | K8s metrics | Pod logs | - | Pod health |

### 1.3 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Collection Flow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Sources → Collectors → Storage → Visualization → Alerting      │
│                                                                  │
│  Metrics:                                                            │
│  Apps → Prometheus → TSDB → Grafana → Alertmanager              │
│                                                                  │
│  Logs:                                                               │
│  Apps → Filebeat → Logstash → Elasticsearch → Kibana            │
│                                                                  │
│  Traces:                                                             │
│  Apps → OpenTelemetry → Jaeger Collector → Storage → Jaeger UI  │
│                                                                  │
│  Errors:                                                             │
│  Apps → Sentry SDK → Sentry Relay → PostgreSQL → Sentry UI      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Prometheus Metrics Collection

### 2.1 Prometheus Server Configuration

**File: `/opt/monitoring/prometheus/prometheus.yml`**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'resilienceai-production'
    replica: '{{.ExternalURL}}'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      timeout: 10s
      api_version: v2

# Load rules once and periodically evaluate them
rule_files:
  - /etc/prometheus/rules/*.yml
  - /etc/prometheus/alerts/*.yml

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics

  # API Service
  - job_name: 'resilienceai-api'
    static_configs:
      - targets:
        - 'api-1:8000'
        - 'api-2:8000'
        - 'api-3:8000'
    metrics_path: /metrics
    scrape_interval: 10s
    scrape_timeout: 5s
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [__address__]
        regex: '([^:]+):\d+'
        target_label: host

  # Frontend Service
  - job_name: 'resilienceai-frontend'
    static_configs:
      - targets:
        - 'frontend-1:3000'
        - 'frontend-2:3000'
    metrics_path: /metrics
    scrape_interval: 15s

  # Celery Workers
  - job_name: 'resilienceai-workers'
    static_configs:
      - targets:
        - 'worker-1:5555'
        - 'worker-2:5555'
        - 'worker-3:5555'
    metrics_path: /metrics
    scrape_interval: 10s

  # PostgreSQL Exporter
  - job_name: 'postgresql'
    static_configs:
      - targets:
        - 'postgres-exporter:9187'
    scrape_interval: 15s

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets:
        - 'redis-exporter:9121'
    scrape_interval: 15s

  # Node Exporter (Infrastructure)
  - job_name: 'node'
    static_configs:
      - targets:
        - 'node-exporter-1:9100'
        - 'node-exporter-2:9100'
        - 'node-exporter-3:9100'
    scrape_interval: 15s

  # Kubernetes API Server
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - default
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  # Kubernetes Nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics

  # Kubernetes Pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  # Blackbox Exporter (Uptime Monitoring)
  - job_name: 'blackbox-http'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://api.resilienceai.io/health
        - https://app.resilienceai.io/health
        - https://resilienceai.io
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

# Remote write for long-term storage (Thanos/Grafana Cloud)
remote_write:
  - url: "http://thanos-receive:19291/api/v1/receive"
    queue_config:
      max_samples_per_send: 1000
      max_shards: 200
      capacity: 2500
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'go_.*'
        action: drop
```

### 2.2 Custom Application Metrics (FastAPI)

**File: `/app/resilienceai/monitoring/metrics.py`**

```python
"""
ResilienceAI Custom Prometheus Metrics
"""
from prometheus_client import Counter, Histogram, Gauge, Info, Enum
from prometheus_client.openmetrics.exposition import generate_latest
from functools import wraps
import time
from typing import Callable, Any

# Application Info
APP_INFO = Info('resilienceai_app', 'ResilienceAI Application Information')
APP_INFO.info({
    'version': '1.0.0',
    'environment': 'production',
    'service': 'resilienceai-api'
})

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    'resilienceai_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

HTTP_REQUEST_DURATION = Histogram(
    'resilienceai_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

HTTP_REQUEST_SIZE = Histogram(
    'resilienceai_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

HTTP_RESPONSE_SIZE = Histogram(
    'resilienceai_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

# Business Metrics
PREDICTION_REQUESTS_TOTAL = Counter(
    'resilienceai_prediction_requests_total',
    'Total prediction requests',
    ['model_type', 'status', 'client_id']
)

PREDICTION_DURATION = Histogram(
    'resilienceai_prediction_duration_seconds',
    'Prediction request duration',
    ['model_type'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

PREDICTION_CONFIDENCE = Histogram(
    'resilienceai_prediction_confidence',
    'Prediction confidence scores',
    ['model_type'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Risk Assessment Metrics
RISK_ASSESSMENTS_TOTAL = Counter(
    'resilienceai_risk_assessments_total',
    'Total risk assessments performed',
    ['risk_level', 'assessment_type', 'client_id']
)

RISK_SCORE_DISTRIBUTION = Histogram(
    'resilienceai_risk_score_distribution',
    'Distribution of risk scores',
    ['assessment_type'],
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# User Metrics
ACTIVE_USERS = Gauge(
    'resilienceai_active_users',
    'Number of active users',
    ['user_type']
)

USER_SESSIONS_TOTAL = Counter(
    'resilienceai_user_sessions_total',
    'Total user sessions',
    ['user_type', 'auth_method']
)

USER_ACTIONS_TOTAL = Counter(
    'resilienceai_user_actions_total',
    'Total user actions',
    ['action_type', 'user_type']
)

# Database Metrics
DB_CONNECTIONS = Gauge(
    'resilienceai_db_connections',
    'Database connection pool status',
    ['state', 'database']
)

DB_QUERY_DURATION = Histogram(
    'resilienceai_db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

DB_QUERY_ERRORS_TOTAL = Counter(
    'resilienceai_db_query_errors_total',
    'Total database query errors',
    ['query_type', 'error_type']
)

# Cache Metrics
CACHE_OPERATIONS_TOTAL = Counter(
    'resilienceai_cache_operations_total',
    'Total cache operations',
    ['operation', 'result', 'cache_name']
)

CACHE_HIT_RATIO = Gauge(
    'resilienceai_cache_hit_ratio',
    'Cache hit ratio',
    ['cache_name']
)

# Celery Task Metrics
CELERY_TASKS_TOTAL = Counter(
    'resilienceai_celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status', 'queue']
)

CELERY_TASK_DURATION = Histogram(
    'resilienceai_celery_task_duration_seconds',
    'Celery task duration',
    ['task_name'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

CELERY_QUEUE_SIZE = Gauge(
    'resilienceai_celery_queue_size',
    'Celery queue size',
    ['queue_name']
)

CELERY_WORKERS_ACTIVE = Gauge(
    'resilienceai_celery_workers_active',
    'Number of active Celery workers',
    ['queue_name']
)

# External API Metrics
EXTERNAL_API_CALLS_TOTAL = Counter(
    'resilienceai_external_api_calls_total',
    'Total external API calls',
    ['api_name', 'endpoint', 'status_code']
)

EXTERNAL_API_DURATION = Histogram(
    'resilienceai_external_api_duration_seconds',
    'External API call duration',
    ['api_name', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Error Metrics
ERRORS_TOTAL = Counter(
    'resilienceai_errors_total',
    'Total errors',
    ['error_type', 'error_code', 'endpoint']
)

EXCEPTIONS_TOTAL = Counter(
    'resilienceai_exceptions_total',
    'Total exceptions',
    ['exception_type', 'module']
)

# Feature Flags
FEATURE_FLAG_STATE = Enum(
    'resilienceai_feature_flag_state',
    'Feature flag state',
    ['flag_name'],
    states=['enabled', 'disabled', 'partial']
)

# System Health
SYSTEM_HEALTH = Gauge(
    'resilienceai_system_health',
    'System health status (1 = healthy, 0 = unhealthy)',
    ['component']
)

# Cost Metrics (for cost monitoring)
RESOURCE_USAGE = Gauge(
    'resilienceai_resource_usage',
    'Resource usage for cost tracking',
    ['resource_type', 'service']
)

API_CALLS_BY_TIER = Counter(
    'resilienceai_api_calls_by_tier',
    'API calls by pricing tier',
    ['tier', 'endpoint']
)


def track_request_duration(endpoint: str, method: str = 'GET'):
    """Decorator to track HTTP request duration"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise e
            finally:
                duration = time.time() - start_time
                HTTP_REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint,
                    service='api'
                ).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise e
            finally:
                duration = time.time() - start_time
                HTTP_REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint,
                    service='api'
                ).observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def track_prediction(model_type: str):
    """Decorator to track prediction metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            client_id = kwargs.get('client_id', 'anonymous')
            try:
                result = await func(*args, **kwargs)
                PREDICTION_REQUESTS_TOTAL.labels(
                    model_type=model_type,
                    status='success',
                    client_id=client_id
                ).inc()
                
                # Track confidence if available
                if hasattr(result, 'confidence'):
                    PREDICTION_CONFIDENCE.labels(
                        model_type=model_type
                    ).observe(result.confidence)
                
                return result
            except Exception as e:
                PREDICTION_REQUESTS_TOTAL.labels(
                    model_type=model_type,
                    status='error',
                    client_id=client_id
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                PREDICTION_DURATION.labels(
                    model_type=model_type
                ).observe(duration)
        return wrapper
    return decorator


class MetricsMiddleware:
    """FastAPI middleware for collecting metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            method = scope.get("method", "GET")
            path = scope.get("path", "/")
            
            # Track request
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=path,
                status_code='unknown',
                service='api'
            ).inc()
            
            await self.app(scope, receive, send)
            
            # Track duration
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION.labels(
                method=method,
                endpoint=path,
                service='api'
            ).observe(duration)
        else:
            await self.app(scope, receive, send)
```

### 2.3 Prometheus Recording Rules

**File: `/opt/monitoring/prometheus/rules/recording_rules.yml`**

```yaml
groups:
  - name: resilienceai_api_rules
    interval: 30s
    rules:
      # Request rate per endpoint
      - record: resilienceai:api_request_rate_5m
        expr: |
          sum by (endpoint, method) (
            rate(resilienceai_http_requests_total[5m])
          )
      
      # Error rate per endpoint
      - record: resilienceai:api_error_rate_5m
        expr: |
          sum by (endpoint) (
            rate(resilienceai_http_requests_total{status_code=~"5.."}[5m])
          ) /
          sum by (endpoint) (
            rate(resilienceai_http_requests_total[5m])
          )
      
      # Average latency per endpoint
      - record: resilienceai:api_latency_avg_5m
        expr: |
          sum by (endpoint) (
            rate(resilienceai_http_request_duration_seconds_sum[5m])
          ) /
          sum by (endpoint) (
            rate(resilienceai_http_request_duration_seconds_count[5m])
          )
      
      # 95th percentile latency
      - record: resilienceai:api_latency_p95_5m
        expr: |
          histogram_quantile(0.95,
            sum by (endpoint, le) (
              rate(resilienceai_http_request_duration_seconds_bucket[5m])
            )
          )
      
      # 99th percentile latency
      - record: resilienceai:api_latency_p99_5m
        expr: |
          histogram_quantile(0.99,
            sum by (endpoint, le) (
              rate(resilienceai_http_request_duration_seconds_bucket[5m])
            )
          )

  - name: resilienceai_prediction_rules
    interval: 30s
    rules:
      # Prediction rate by model
      - record: resilienceai:prediction_rate_5m
        expr: |
          sum by (model_type) (
            rate(resilienceai_prediction_requests_total[5m])
          )
      
      # Prediction error rate
      - record: resilienceai:prediction_error_rate_5m
        expr: |
          sum by (model_type) (
            rate(resilienceai_prediction_requests_total{status="error"}[5m])
          ) /
          sum by (model_type) (
            rate(resilienceai_prediction_requests_total[5m])
          )
      
      # Average prediction duration
      - record: resilienceai:prediction_duration_avg_5m
        expr: |
          sum by (model_type) (
            rate(resilienceai_prediction_duration_seconds_sum[5m])
          ) /
          sum by (model_type) (
            rate(resilienceai_prediction_duration_seconds_count[5m])
          )

  - name: resilienceai_business_rules
    interval: 1m
    rules:
      # Active users (5-minute window)
      - record: resilienceai:active_users_5m
        expr: |
          sum by (user_type) (
            resilienceai_active_users
          )
      
      # Risk assessment rate
      - record: resilienceai:risk_assessment_rate_5m
        expr: |
          sum by (risk_level) (
            rate(resilienceai_risk_assessments_total[5m])
          )

  - name: resilienceai_infrastructure_rules
    interval: 30s
    rules:
      # CPU utilization
      - record: resilienceai:cpu_utilization
        expr: |
          100 - (avg by (instance) (
            irate(node_cpu_seconds_total{mode="idle"}[5m])
          ) * 100)
      
      # Memory utilization
      - record: resilienceai:memory_utilization
        expr: |
          (1 - (
            node_memory_MemAvailable_bytes /
            node_memory_MemTotal_bytes
          )) * 100
      
      # Disk utilization
      - record: resilienceai:disk_utilization
        expr: |
          (1 - (
            node_filesystem_avail_bytes /
            node_filesystem_size_bytes
          )) * 100
      
      # Network throughput
      - record: resilienceai:network_throughput_mbps
        expr: |
          sum by (instance) (
            rate(node_network_receive_bytes_total[5m]) +
            rate(node_network_transmit_bytes_total[5m])
          ) / 1024 / 1024

  - name: resilienceai_slo_rules
    interval: 1m
    rules:
      # API availability (success rate)
      - record: resilienceai:slo_api_availability_1h
        expr: |
          1 - (
            sum(rate(resilienceai_http_requests_total{status_code=~"5.."}[1h])) /
            sum(rate(resilienceai_http_requests_total[1h]))
          )
      
      # API latency SLO
      - record: resilienceai:slo_api_latency_1h
        expr: |
          sum(rate(resilienceai_http_request_duration_seconds_bucket{le="0.5"}[1h])) /
          sum(rate(resilienceai_http_request_duration_seconds_count[1h]))
```



### 2.4 Prometheus Alerting Rules

**File: `/opt/monitoring/prometheus/alerts/alerting_rules.yml`**

```yaml
groups:
  - name: resilienceai_critical_alerts
    rules:
      # Critical: API Down
      - alert: ResilienceAIAPIDown
        expr: up{job="resilienceai-api"} == 0
        for: 1m
        labels:
          severity: critical
          team: platform
          service: api
        annotations:
          summary: "ResilienceAI API is down"
          description: "API instance {{ $labels.instance }} has been down for more than 1 minute"
          runbook_url: "https://wiki.resilienceai.io/runbooks/api-down"
          dashboard_url: "https://grafana.resilienceai.io/d/api-health"
      
      # Critical: High Error Rate
      - alert: ResilienceAIHighErrorRate
        expr: |
          sum by (endpoint) (
            rate(resilienceai_http_requests_total{status_code=~"5.."}[5m])
          ) /
          sum by (endpoint) (
            rate(resilienceai_http_requests_total[5m])
          ) > 0.05
        for: 2m
        labels:
          severity: critical
          team: platform
          service: api
        annotations:
          summary: "High error rate detected"
          description: "Error rate for {{ $labels.endpoint }} is {{ $value | humanizePercentage }}"
          dashboard_url: "https://grafana.resilienceai.io/d/error-rate"
      
      # Critical: High Latency
      - alert: ResilienceAIHighLatency
        expr: |
          histogram_quantile(0.99,
            sum by (le) (
              rate(resilienceai_http_request_duration_seconds_bucket[5m])
            )
          ) > 2.0
        for: 3m
        labels:
          severity: critical
          team: platform
          service: api
        annotations:
          summary: "High latency detected"
          description: "P99 latency is {{ $value }}s, exceeding 2s threshold"
      
      # Critical: Database Connection Issues
      - alert: ResilienceAIDatabaseDown
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
          team: data
          service: database
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL exporter is not responding"
      
      # Critical: Database Connection Pool Exhausted
      - alert: ResilienceAIDBConnectionPoolExhausted
        expr: |
          resilienceai_db_connections{state="active"} /
          resilienceai_db_connections{state="max"} > 0.9
        for: 2m
        labels:
          severity: critical
          team: data
          service: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool utilization is {{ $value | humanizePercentage }}"

  - name: resilienceai_warning_alerts
    rules:
      # Warning: Elevated Error Rate
      - alert: ResilienceAIElevatedErrorRate
        expr: |
          sum by (endpoint) (
            rate(resilienceai_http_requests_total{status_code=~"5.."}[5m])
          ) /
          sum by (endpoint) (
            rate(resilienceai_http_requests_total[5m])
          ) > 0.01
        for: 5m
        labels:
          severity: warning
          team: platform
          service: api
        annotations:
          summary: "Elevated error rate detected"
          description: "Error rate for {{ $labels.endpoint }} is {{ $value | humanizePercentage }}"
      
      # Warning: Elevated Latency
      - alert: ResilienceAIElevatedLatency
        expr: |
          histogram_quantile(0.95,
            sum by (le) (
              rate(resilienceai_http_request_duration_seconds_bucket[5m])
            )
          ) > 1.0
        for: 5m
        labels:
          severity: warning
          team: platform
          service: api
        annotations:
          summary: "Elevated latency detected"
          description: "P95 latency is {{ $value }}s"
      
      # Warning: High CPU Usage
      - alert: ResilienceAIHighCPU
        expr: |
          100 - (avg by (instance) (
            irate(node_cpu_seconds_total{mode="idle"}[5m])
          ) * 100) > 80
        for: 5m
        labels:
          severity: warning
          team: platform
          service: infrastructure
        annotations:
          summary: "High CPU usage"
          description: "CPU usage on {{ $labels.instance }} is {{ $value }}%"
      
      # Warning: High Memory Usage
      - alert: ResilienceAIHighMemory
        expr: |
          (1 - (
            node_memory_MemAvailable_bytes /
            node_memory_MemTotal_bytes
          )) * 100 > 85
        for: 5m
        labels:
          severity: warning
          team: platform
          service: infrastructure
        annotations:
          summary: "High memory usage"
          description: "Memory usage on {{ $labels.instance }} is {{ $value }}%"
      
      # Warning: Disk Space Low
      - alert: ResilienceAILowDiskSpace
        expr: |
          (1 - (
            node_filesystem_avail_bytes /
            node_filesystem_size_bytes
          )) * 100 > 80
        for: 5m
        labels:
          severity: warning
          team: platform
          service: infrastructure
        annotations:
          summary: "Low disk space"
          description: "Disk usage on {{ $labels.instance }} is {{ $value }}%"
      
      # Warning: Celery Queue Backlog
      - alert: ResilienceAICeleryQueueBacklog
        expr: resilienceai_celery_queue_size > 1000
        for: 5m
        labels:
          severity: warning
          team: platform
          service: workers
        annotations:
          summary: "Celery queue backlog detected"
          description: "Queue {{ $labels.queue_name }} has {{ $value }} pending tasks"
      
      # Warning: Celery Worker Down
      - alert: ResilienceAICeleryWorkerDown
        expr: resilienceai_celery_workers_active == 0
        for: 2m
        labels:
          severity: warning
          team: platform
          service: workers
        annotations:
          summary: "Celery workers are down"
          description: "No active workers for queue {{ $labels.queue_name }}"
      
      # Warning: Cache Hit Ratio Low
      - alert: ResilienceAILowCacheHitRatio
        expr: resilienceai_cache_hit_ratio < 0.7
        for: 10m
        labels:
          severity: warning
          team: platform
          service: cache
        annotations:
          summary: "Low cache hit ratio"
          description: "Cache {{ $labels.cache_name }} hit ratio is {{ $value | humanizePercentage }}"
      
      # Warning: Redis Memory High
      - alert: ResilienceAIRedisMemoryHigh
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
          team: platform
          service: cache
        annotations:
          summary: "Redis memory usage high"
          description: "Redis memory usage is {{ $value | humanizePercentage }}"

  - name: resilienceai_prediction_alerts
    rules:
      # Warning: Prediction Error Rate High
      - alert: ResilienceAIPredictionErrorRate
        expr: |
          sum by (model_type) (
            rate(resilienceai_prediction_requests_total{status="error"}[5m])
          ) /
          sum by (model_type) (
            rate(resilienceai_prediction_requests_total[5m])
          ) > 0.05
        for: 3m
        labels:
          severity: warning
          team: ml
          service: prediction
        annotations:
          summary: "High prediction error rate"
          description: "Prediction error rate for {{ $labels.model_type }} is {{ $value | humanizePercentage }}"
      
      # Warning: Prediction Latency High
      - alert: ResilienceAIPredictionLatency
        expr: |
          histogram_quantile(0.95,
            sum by (model_type, le) (
              rate(resilienceai_prediction_duration_seconds_bucket[5m])
            )
          ) > 5.0
        for: 5m
        labels:
          severity: warning
          team: ml
          service: prediction
        annotations:
          summary: "High prediction latency"
          description: "P95 prediction latency for {{ $labels.model_type }} is {{ $value }}s"
      
      # Info: Model Drift Detected
      - alert: ResilienceAIModelDrift
        expr: |
          avg_over_time(resilienceai_prediction_confidence[1h]) < 
          avg_over_time(resilienceai_prediction_confidence[1h] offset 24h) * 0.9
        for: 15m
        labels:
          severity: info
          team: ml
          service: prediction
        annotations:
          summary: "Potential model drift detected"
          description: "Average confidence for {{ $labels.model_type }} has decreased by >10%"

  - name: resilienceai_business_alerts
    rules:
      # Warning: User Activity Drop
      - alert: ResilienceAIUserActivityDrop
        expr: |
          sum(rate(resilienceai_user_actions_total[1h])) < 
          sum(rate(resilienceai_user_actions_total[1h] offset 24h)) * 0.5
        for: 15m
        labels:
          severity: warning
          team: product
          service: business
        annotations:
          summary: "User activity has dropped significantly"
          description: "User activity is 50% lower than same time yesterday"
      
      # Warning: Risk Assessment Spike
      - alert: ResilienceAIRiskAssessmentSpike
        expr: |
          sum by (risk_level) (
            rate(resilienceai_risk_assessments_total{risk_level="high"}[1h])
          ) > 100
        for: 10m
        labels:
          severity: warning
          team: product
          service: business
        annotations:
          summary: "High risk assessment spike"
          description: "High risk assessments have spiked to {{ $value }}/hour"

  - name: resilienceai_slo_alerts
    rules:
      # Critical: SLO Breach - Availability
      - alert: ResilienceAISLOAvailabilityBreach
        expr: resilienceai:slo_api_availability_1h < 0.999
        for: 5m
        labels:
          severity: critical
          team: platform
          slo: availability
        annotations:
          summary: "SLO breach: API availability"
          description: "API availability ({{ $value | humanizePercentage }}) is below SLO (99.9%)"
      
      # Warning: SLO At Risk - Availability
      - alert: ResilienceAISLOAvailabilityAtRisk
        expr: resilienceai:slo_api_availability_1h < 0.9995
        for: 10m
        labels:
          severity: warning
          team: platform
          slo: availability
        annotations:
          summary: "SLO at risk: API availability"
          description: "API availability ({{ $value | humanizePercentage }}) is approaching SLO threshold"
      
      # Warning: SLO At Risk - Latency
      - alert: ResilienceAISLOLatencyAtRisk
        expr: resilienceai:slo_api_latency_1h < 0.95
        for: 10m
        labels:
          severity: warning
          team: platform
          slo: latency
        annotations:
          summary: "SLO at risk: API latency"
          description: "Only {{ $value | humanizePercentage }} of requests are under 500ms"

  - name: resilienceai_security_alerts
    rules:
      # Critical: Unusual Authentication Pattern
      - alert: ResilienceAIUnusualAuthPattern
        expr: |
          sum by (auth_method) (
            rate(resilienceai_user_sessions_total[5m])
          ) > 1000
        for: 5m
        labels:
          severity: critical
          team: security
          service: auth
        annotations:
          summary: "Unusual authentication pattern detected"
          description: "High rate of authentication attempts: {{ $value }}/second"
      
      # Warning: Failed Authentication Spike
      - alert: ResilienceAIFailedAuthSpike
        expr: |
          sum(rate(resilienceai_errors_total{error_type="authentication_failed"}[5m])) > 50
        for: 5m
        labels:
          severity: warning
          team: security
          service: auth
        annotations:
          summary: "Failed authentication spike"
          description: "Failed authentication rate is {{ $value }}/second"
```

---

## 3. Grafana Dashboards

### 3.1 Main Dashboard Configuration

**File: `/opt/monitoring/grafana/dashboards/resilienceai-main.json`**

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "description": "ResilienceAI Main Dashboard - System Overview",
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "collapsed": false,
      "datasource": null,
      "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0},
      "id": 100,
      "title": "System Overview",
      "type": "row"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "red", "value": null},
              {"color": "yellow", "value": 0.99},
              {"color": "green", "value": 0.999}
            ]
          },
          "unit": "percentunit"
        }
      },
      "gridPos": {"h": 4, "w": 6, "x": 0, "y": 1},
      "id": 101,
      "options": {
        "colorMode": "background",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "1 - (sum(rate(resilienceai_http_requests_total{status_code=~\"5..\"}[1h])) / sum(rate(resilienceai_http_requests_total[1h])))",
          "refId": "A"
        }
      ],
      "title": "API Availability (1h)",
      "type": "stat"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 0.5},
              {"color": "red", "value": 1.0}
            ]
          },
          "unit": "s"
        }
      },
      "gridPos": {"h": 4, "w": 6, "x": 6, "y": 1},
      "id": 102,
      "options": {
        "colorMode": "background",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        }
      },
      "targets": [
        {
          "expr": "histogram_quantile(0.99, sum(rate(resilienceai_http_request_duration_seconds_bucket[5m])) by (le))",
          "refId": "A"
        }
      ],
      "title": "P99 Latency",
      "type": "stat"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 100},
              {"color": "red", "value": 500}
            ]
          },
          "unit": "reqps"
        }
      },
      "gridPos": {"h": 4, "w": 6, "x": 12, "y": 1},
      "id": 103,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        }
      },
      "targets": [
        {
          "expr": "sum(rate(resilienceai_http_requests_total[5m]))",
          "refId": "A"
        }
      ],
      "title": "Request Rate",
      "type": "stat"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 0.01},
              {"color": "red", "value": 0.05}
            ]
          },
          "unit": "percentunit"
        }
      },
      "gridPos": {"h": 4, "w": 6, "x": 18, "y": 1},
      "id": 104,
      "options": {
        "colorMode": "background",
        "graphMode": "area",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        }
      },
      "targets": [
        {
          "expr": "sum(rate(resilienceai_http_requests_total{status_code=~\"5..\"}[5m])) / sum(rate(resilienceai_http_requests_total[5m]))",
          "refId": "A"
        }
      ],
      "title": "Error Rate",
      "type": "stat"
    },
    {
      "collapsed": false,
      "datasource": null,
      "gridPos": {"h": 1, "w": 24, "x": 0, "y": 5},
      "id": 200,
      "title": "API Performance",
      "type": "row"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "barAlignment": 0,
            "lineWidth": 1,
            "fillOpacity": 10,
            "gradientMode": "none",
            "spanNulls": true,
            "showPoints": "never",
            "pointSize": 5,
            "stacking": {"mode": "none", "group": "A"},
            "axisPlacement": "auto",
            "axisLabel": "",
            "scaleDistribution": {"type": "linear"},
            "hideFrom": {"tooltip": false, "viz": false, "legend": false},
            "thresholdsStyle": {"mode": "off"}
          },
          "color": {"mode": "palette-classic"},
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "green", "value": null},
              {"color": "red", "value": 80}
            ]
          },
          "unit": "reqps"
        }
      },
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
      "id": 201,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom", "calcs": []}
      },
      "targets": [
        {
          "expr": "sum by (endpoint) (rate(resilienceai_http_requests_total[5m]))",
          "legendFormat": "{{ endpoint }}",
          "refId": "A"
        }
      ],
      "title": "Request Rate by Endpoint",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10,
            "spanNulls": true,
            "showPoints": "never"
          },
          "color": {"mode": "palette-classic"},
          "unit": "s"
        }
      },
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
      "id": 202,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum by (le, endpoint) (rate(resilienceai_http_request_duration_seconds_bucket[5m])))",
          "legendFormat": "P50 - {{ endpoint }}",
          "refId": "A"
        },
        {
          "expr": "histogram_quantile(0.95, sum by (le, endpoint) (rate(resilienceai_http_request_duration_seconds_bucket[5m])))",
          "legendFormat": "P95 - {{ endpoint }}",
          "refId": "B"
        },
        {
          "expr": "histogram_quantile(0.99, sum by (le, endpoint) (rate(resilienceai_http_request_duration_seconds_bucket[5m])))",
          "legendFormat": "P99 - {{ endpoint }}",
          "refId": "C"
        }
      ],
      "title": "Latency Percentiles by Endpoint",
      "type": "timeseries"
    },
    {
      "collapsed": false,
      "datasource": null,
      "gridPos": {"h": 1, "w": 24, "x": 0, "y": 14},
      "id": 300,
      "title": "ML/Prediction Metrics",
      "type": "row"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "reqps"
        }
      },
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 15},
      "id": 301,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "sum by (model_type) (rate(resilienceai_prediction_requests_total[5m]))",
          "legendFormat": "{{ model_type }}",
          "refId": "A"
        }
      ],
      "title": "Prediction Rate by Model",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "s"
        }
      },
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 15},
      "id": 302,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le, model_type) (rate(resilienceai_prediction_duration_seconds_bucket[5m])))",
          "legendFormat": "P95 - {{ model_type }}",
          "refId": "A"
        },
        {
          "expr": "histogram_quantile(0.99, sum by (le, model_type) (rate(resilienceai_prediction_duration_seconds_bucket[5m])))",
          "legendFormat": "P99 - {{ model_type }}",
          "refId": "B"
        }
      ],
      "title": "Prediction Latency",
      "type": "timeseries"
    },
    {
      "collapsed": false,
      "datasource": null,
      "gridPos": {"h": 1, "w": 24, "x": 0, "y": 23},
      "id": 400,
      "title": "Infrastructure",
      "type": "row"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 0, "y": 24},
      "id": 401,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
          "legendFormat": "{{ instance }}",
          "refId": "A"
        }
      ],
      "title": "CPU Usage",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 8, "y": 24},
      "id": 402,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
          "legendFormat": "{{ instance }}",
          "refId": "A"
        }
      ],
      "title": "Memory Usage",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 16, "y": 24},
      "id": 403,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "list", "placement": "bottom"}
      },
      "targets": [
        {
          "expr": "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100",
          "legendFormat": "{{ instance }} - {{ mountpoint }}",
          "refId": "A"
        }
      ],
      "title": "Disk Usage",
      "type": "timeseries"
    }
  ],
  "refresh": "30s",
  "schemaVersion": 27,
  "style": "dark",
  "tags": ["resilienceai", "overview"],
  "templating": {
    "list": [
      {
        "current": {"selected": false, "text": "Prometheus", "value": "Prometheus"},
        "hide": 0,
        "includeAll": false,
        "label": "Data Source",
        "multi": false,
        "name": "datasource",
        "options": [],
        "query": "prometheus",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "type": "datasource"
      },
      {
        "current": {"selected": false, "text": "All", "value": "$__all"},
        "hide": 0,
        "includeAll": true,
        "label": "Environment",
        "multi": true,
        "name": "environment",
        "options": [
          {"selected": true, "text": "All", "value": "$__all"},
          {"selected": false, "text": "production", "value": "production"},
          {"selected": false, "text": "staging", "value": "staging"}
        ],
        "query": "production, staging",
        "skipUrlSync": false,
        "type": "custom"
      }
    ]
  },
  "time": {"from": "now-1h", "to": "now"},
  "timepicker": {},
  "timezone": "browser",
  "title": "ResilienceAI - Main Dashboard",
  "uid": "resilienceai-main",
  "version": 1
}
```



### 3.2 SLO Dashboard

**File: `/opt/monitoring/grafana/dashboards/resilienceai-slo.json`**

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "description": "ResilienceAI SLO Dashboard - Service Level Objectives",
  "editable": true,
  "id": 2,
  "panels": [
    {
      "collapsed": false,
      "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0},
      "id": 100,
      "title": "Service Level Objectives",
      "type": "row"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "max": 100,
          "min": 99,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "red", "value": null},
              {"color": "yellow", "value": 99.9},
              {"color": "green", "value": 99.95}
            ]
          },
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 0, "y": 1},
      "id": 101,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "resilienceai:slo_api_availability_1h * 100",
          "refId": "A"
        }
      ],
      "title": "API Availability SLO (99.9%)",
      "type": "gauge"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "max": 100,
          "min": 90,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "red", "value": null},
              {"color": "yellow", "value": 95},
              {"color": "green", "value": 99}
            ]
          },
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 8, "y": 1},
      "id": 102,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "targets": [
        {
          "expr": "resilienceai:slo_api_latency_1h * 100",
          "refId": "A"
        }
      ],
      "title": "API Latency SLO (95% < 500ms)",
      "type": "gauge"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "mappings": [],
          "max": 100,
          "min": 95,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "red", "value": null},
              {"color": "yellow", "value": 98},
              {"color": "green", "value": 99}
            ]
          },
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 8, "x": 16, "y": 1},
      "id": 103,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "targets": [
        {
          "expr": "(1 - sum(rate(resilienceai_prediction_requests_total{status=\"error\"}[1h])) / sum(rate(resilienceai_prediction_requests_total[1h]))) * 100",
          "refId": "A"
        }
      ],
      "title": "Prediction Success SLO (99%)",
      "type": "gauge"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "fillOpacity": 10
          },
          "color": {"mode": "palette-classic"},
          "unit": "percent"
        }
      },
      "gridPos": {"h": 10, "w": 24, "x": 0, "y": 9},
      "id": 201,
      "options": {
        "tooltip": {"mode": "single"},
        "legend": {"displayMode": "table", "placement": "right", "calcs": ["mean", "min", "max"]}
      },
      "targets": [
        {
          "expr": "resilienceai:slo_api_availability_1h * 100",
          "legendFormat": "Availability",
          "refId": "A"
        },
        {
          "expr": "resilienceai:slo_api_latency_1h * 100",
          "legendFormat": "Latency",
          "refId": "B"
        }
      ],
      "title": "SLO Trends (1h window)",
      "type": "timeseries"
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {
            "displayMode": "gradient",
            "filterable": false
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 0.95},
              {"color": "red", "value": 0.99}
            ]
          },
          "unit": "percent"
        }
      },
      "gridPos": {"h": 8, "w": 24, "x": 0, "y": 19},
      "id": 301,
      "options": {
        "showHeader": true
      },
      "pluginVersion": "8.0.0",
      "targets": [
        {
          "expr": "avg by (endpoint) (resilienceai:slo_api_availability_1h) * 100",
          "format": "table",
          "instant": true,
          "refId": "A"
        }
      ],
      "title": "SLO by Endpoint",
      "transformations": [
        {
          "id": "organize",
          "options": {
            "indexByName": {},
            "renameByName": {
              "Value": "Availability %",
              "endpoint": "Endpoint"
            }
          }
        }
      ],
      "type": "table"
    }
  ],
  "refresh": "1m",
  "schemaVersion": 27,
  "style": "dark",
  "tags": ["resilienceai", "slo"],
  "title": "ResilienceAI - SLO Dashboard",
  "uid": "resilienceai-slo",
  "version": 1
}
```

---

## 4. Distributed Tracing

### 4.1 Jaeger Deployment

**File: `/opt/monitoring/jaeger/jaeger-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
  labels:
    app: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.45
          ports:
            - containerPort: 5775
              protocol: UDP
            - containerPort: 6831
              protocol: UDP
            - containerPort: 6832
              protocol: UDP
            - containerPort: 5778
            - containerPort: 16686
            - containerPort: 14268
            - containerPort: 14250
            - containerPort: 9411
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
            - name: SPAN_STORAGE_TYPE
              value: "elasticsearch"
            - name: ES_SERVER_URLS
              value: "http://elasticsearch:9200"
            - name: ES_INDEX_PREFIX
              value: "jaeger"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-query
  namespace: monitoring
  labels:
    app: jaeger
spec:
  type: ClusterIP
  ports:
    - port: 16686
      targetPort: 16686
      name: query
  selector:
    app: jaeger
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-collector
  namespace: monitoring
  labels:
    app: jaeger
spec:
  type: ClusterIP
  ports:
    - port: 14268
      targetPort: 14268
      name: jaeger-collector-http
    - port: 14250
      targetPort: 14250
      name: jaeger-collector-grpc
    - port: 4317
      targetPort: 4317
      name: otlp-grpc
    - port: 4318
      targetPort: 4318
      name: otlp-http
  selector:
    app: jaeger
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-agent
  namespace: monitoring
  labels:
    app: jaeger
spec:
  type: ClusterIP
  ports:
    - port: 5775
      targetPort: 5775
      protocol: UDP
      name: agent-zipkin-thrift
    - port: 6831
      targetPort: 6831
      protocol: UDP
      name: agent-compact
    - port: 6832
      targetPort: 6832
      protocol: UDP
      name: agent-binary
    - port: 5778
      targetPort: 5778
      name: agent-configs
  selector:
    app: jaeger
```

### 4.2 OpenTelemetry Configuration

**File: `/opt/monitoring/otel/otel-collector-config.yml`**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          scrape_interval: 10s
          static_configs:
            - targets: ['localhost:8888']

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  resource:
    attributes:
      - key: service.namespace
        value: resilienceai
        action: upsert
      - key: deployment.environment
        value: production
        action: upsert

  attributes:
    actions:
      - key: environment
        value: production
        action: insert

exporters:
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true

  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write

  logging:
    loglevel: debug

  otlp/jaeger:
    endpoint: jaeger-collector:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [jaeger, logging]
    
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch, resource]
      exporters: [prometheusremotewrite]
    
    logs:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [logging]
```

### 4.3 Application Tracing Instrumentation (Python/FastAPI)

**File: `/app/resilienceai/monitoring/tracing.py`**

```python
"""
ResilienceAI Distributed Tracing Configuration
"""
import os
from functools import wraps
from typing import Callable, Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3Format


class TracingConfig:
    """Tracing configuration for ResilienceAI"""
    
    def __init__(
        self,
        service_name: str = "resilienceai-api",
        service_version: str = "1.0.0",
        environment: str = "production",
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        sampling_rate: float = 1.0
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.jaeger_endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268/api/traces")
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
        self.sampling_rate = sampling_rate
        self._provider: Optional[TracerProvider] = None
    
    def initialize(self) -> TracerProvider:
        """Initialize the tracing provider"""
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            DEPLOYMENT_ENVIRONMENT: self.environment,
            "service.namespace": "resilienceai",
            "host.name": os.getenv("HOSTNAME", "unknown"),
        })
        
        # Create provider
        self._provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self._provider)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            collector_endpoint=self.jaeger_endpoint,
        )
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.otlp_endpoint,
            insecure=True
        )
        
        # Add span processors
        self._provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        self._provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        # Add console exporter for debugging (only in dev)
        if self.environment == "development":
            self._provider.add_span_processor(
                BatchSpanProcessor(ConsoleSpanExporter())
            )
        
        # Set global propagator
        set_global_textmap(B3Format())
        
        return self._provider
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="/health,/metrics,/ready"
        )
    
    def instrument_databases(self, engine):
        """Instrument SQLAlchemy"""
        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            enable_commenter=True,
            commenter_options={}
        )
    
    def instrument_celery(self):
        """Instrument Celery"""
        CeleryInstrumentor().instrument()
    
    def instrument_redis(self):
        """Instrument Redis"""
        RedisInstrumentor().instrument()
    
    def instrument_http_clients(self):
        """Instrument HTTP clients"""
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
    
    def get_tracer(self, name: str = __name__):
        """Get a tracer instance"""
        return trace.get_tracer(name)


# Global tracing instance
tracing = TracingConfig()


def trace_function(
    operation_name: Optional[str] = None,
    attributes: Optional[dict] = None,
    kind = trace.SpanKind.INTERNAL
):
    """Decorator to trace function execution"""
    def decorator(func: Callable) -> Callable:
        tracer = tracing.get_tracer(func.__module__)
        span_name = operation_name or func.__name__
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name, kind=kind) as span:
                # Add attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # Add function info
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name, kind=kind) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def trace_prediction(model_type: str):
    """Decorator specifically for prediction functions"""
    return trace_function(
        operation_name=f"prediction.{model_type}",
        attributes={"prediction.model_type": model_type},
        kind=trace.SpanKind.INTERNAL
    )


def trace_database_query(query_type: str, table: str):
    """Decorator for database queries"""
    return trace_function(
        operation_name=f"db.query.{query_type}",
        attributes={
            "db.query_type": query_type,
            "db.table": table
        },
        kind=trace.SpanKind.CLIENT
    )


def trace_external_api(api_name: str, endpoint: str):
    """Decorator for external API calls"""
    return trace_function(
        operation_name=f"external_api.{api_name}",
        attributes={
            "external_api.name": api_name,
            "external_api.endpoint": endpoint
        },
        kind=trace.SpanKind.CLIENT
    )


class SpanContextManager:
    """Context manager for manual span creation"""
    
    def __init__(
        self,
        operation_name: str,
        attributes: Optional[dict] = None,
        kind = trace.SpanKind.INTERNAL
    ):
        self.operation_name = operation_name
        self.attributes = attributes or {}
        self.kind = kind
        self.span = None
        self.tracer = tracing.get_tracer()
    
    def __enter__(self):
        self.span = self.tracer.start_span(self.operation_name, kind=self.kind)
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            self.span.record_exception(exc_val)
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()


# Example usage in application code
"""
from resilienceai.monitoring.tracing import trace_function, trace_prediction, SpanContextManager

# Initialize tracing
tracing.initialize()

# Trace a function
@trace_function(operation_name="risk_assessment.calculate")
async def calculate_risk_score(data: dict) -> float:
    # Function implementation
    pass

# Trace a prediction
@trace_prediction(model_type="credit_default")
async def predict_credit_default(features: dict) -> dict:
    # Prediction implementation
    pass

# Manual span creation
async def complex_operation():
    with SpanContextManager("complex_operation", attributes={"operation.id": "123"}) as span:
        # Do work
        span.set_attribute("operation.step", "validation")
        # More work
        pass
"""
```



---

## 5. Centralized Logging (ELK Stack)

### 5.1 Filebeat Configuration

**File: `/opt/monitoring/filebeat/filebeat.yml`**

```yaml
filebeat.inputs:
  # Application logs
  - type: log
    enabled: true
    paths:
      - /var/log/resilienceai/api/*.log
      - /var/log/resilienceai/worker/*.log
    fields:
      service: resilienceai
      log_type: application
    fields_under_root: true
    multiline.pattern: '^\d{4}-\d{2}-\d{2}'
    multiline.negate: true
    multiline.match: after
    processors:
      - add_tags:
          tags: [application]

  # Nginx/Access logs
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
      - /var/log/nginx/error.log
    fields:
      service: nginx
      log_type: access
    fields_under_root: true
    processors:
      - add_tags:
          tags: [nginx]

  # System logs
  - type: log
    enabled: true
    paths:
      - /var/log/syslog
      - /var/log/auth.log
    fields:
      service: system
      log_type: system
    fields_under_root: true
    processors:
      - add_tags:
          tags: [system]

  # Kubernetes logs
  - type: container
    enabled: true
    paths:
      - /var/log/containers/*.log
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
      - add_tags:
          tags: [kubernetes]

  # Docker logs
  - type: docker
    enabled: true
    containers.ids: '*'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"
      - add_tags:
          tags: [docker]

# Filebeat modules
filebeat.modules:
  - module: system
    syslog:
      enabled: true
    auth:
      enabled: true
  
  - module: nginx
    access:
      enabled: true
      var.paths: ["/var/log/nginx/access.log"]
    error:
      enabled: true
      var.paths: ["/var/log/nginx/error.log"]
  
  - module: postgresql
    log:
      enabled: true
      var.paths: ["/var/log/postgresql/*.log"]
  
  - module: redis
      log:
      enabled: true
      var.paths: ["/var/log/redis/*.log"]

# General settings
filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: true
  reload.period: 10s

# Output to Logstash
output.logstash:
  hosts: ["logstash:5044"]
  loadbalance: true
  compression_level: 3
  ssl:
    enabled: true
    certificate_authorities: ["/etc/filebeat/certs/ca.crt"]
    certificate: "/etc/filebeat/certs/filebeat.crt"
    key: "/etc/filebeat/certs/filebeat.key"

# Output to Elasticsearch (alternative)
# output.elasticsearch:
#   hosts: ["elasticsearch:9200"]
#   protocol: "https"
#   username: "${ES_USERNAME}"
#   password: "${ES_PASSWORD}"
#   ssl:
#     certificate_authorities: ["/etc/filebeat/certs/ca.crt"]

# Processors
processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
  - decode_json_fields:
      fields: ["message"]
      target: "json"
      overwrite_keys: true
      when:
        contains:
          message: '{'
  - timestamp:
      field: json.timestamp
      layouts:
        - '2006-01-02T15:04:05Z'
        - '2006-01-02T15:04:05.999Z'
        - '2006-01-02T15:04:05.999-07:00'
      test:
        - '2024-01-15T10:30:00Z'
  - drop_fields:
      fields: ["agent", "ecs", "input", "log", "offset"]
      ignore_missing: true

# Logging
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644

# Monitoring
monitoring:
  enabled: true
  elasticsearch:
    hosts: ["elasticsearch:9200"]
    username: "${ES_MONITORING_USERNAME}"
    password: "${ES_MONITORING_PASSWORD}"
```

### 5.2 Logstash Pipeline Configuration

**File: `/opt/monitoring/logstash/pipelines/resilienceai.conf`**

```ruby
input {
  beats {
    port => 5044
    ssl => true
    ssl_certificate_authorities => ["/etc/logstash/certs/ca.crt"]
    ssl_certificate => "/etc/logstash/certs/logstash.crt"
    ssl_key => "/etc/logstash/certs/logstash.key"
    ssl_verify_mode => "force_peer"
  }
  
  tcp {
    port => 5000
    codec => json_lines
  }
  
  udp {
    port => 5000
    codec => json_lines
  }
}

filter {
  # Parse JSON logs
  if [message] =~ /^\s*\{/ {
    json {
      source => "message"
      target => "parsed"
      skip_on_invalid_json => true
    }
    
    if [parsed] {
      mutate {
        rename => {
          "[parsed][level]" => "log.level"
          "[parsed][message]" => "log.message"
          "[parsed][timestamp]" => "@timestamp"
          "[parsed][logger]" => "log.logger"
          "[parsed][request_id]" => "trace.id"
          "[parsed][user_id]" => "user.id"
          "[parsed][session_id]" => "session.id"
        }
        remove_field => ["parsed", "message"]
      }
    }
  }
  
  # Parse application log format
  grok {
    match => {
      "message" => [
        "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:log.level} %{DATA:log.logger}: %{GREEDYDATA:log.message}",
        "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:log.level} %{GREEDYDATA:log.message}"
      ]
    }
    overwrite => ["message"]
  }
  
  # Parse Nginx access logs
  if [tags] contains "nginx" and [message] =~ /^(\d+\.\d+\.\d+\.\d+)/ {
    grok {
      match => {
        "message" => '%{IPORHOST:nginx.access.remote_ip} - %{DATA:nginx.access.user_name} \[%{HTTPDATE:nginx.access.time}\] "%{WORD:nginx.access.method} %{DATA:nginx.access.url} HTTP/%{NUMBER:nginx.access.http_version}" %{NUMBER:nginx.access.response_code} %{NUMBER:nginx.access.body_sent.bytes} "%{DATA:nginx.access.referrer}" "%{DATA:nginx.access.agent}"'
      }
    }
    
    mutate {
      add_field => {
        "event.category" => "web"
        "event.dataset" => "nginx.access"
        "event.kind" => "event"
        "event.outcome" => "%{nginx.access.response_code}"
      }
    }
    
    # Set outcome based on response code
    if [nginx][access][response_code] =~ /^[23]\d{2}$/ {
      mutate {
        replace => { "event.outcome" => "success" }
      }
    } else {
      mutate {
        replace => { "event.outcome" => "failure" }
      }
    }
  }
  
  # Parse PostgreSQL slow query logs
  if [tags] contains "postgresql" {
    grok {
      match => {
        "message" => [
          "%{TIMESTAMP_ISO8601:timestamp} %{DATA:postgresql.log.timezone} \[%{NUMBER:postgresql.log.process_id}\] %{DATA:postgresql.log.user}@%{DATA:postgresql.log.database} %{WORD:postgresql.log.level}:  duration: %{NUMBER:postgresql.log.duration:float} ms  statement: %{GREEDYDATA:postgresql.log.query}"
        ]
      }
    }
    
    if [postgresql][log][duration] > 1000 {
      mutate {
        add_tag => ["slow_query"]
      }
    }
  }
  
  # Add environment fields
  mutate {
    add_field => {
      "service.name" => "resilienceai"
      "service.environment" => "${ENVIRONMENT:production}"
      "host.name" => "${HOSTNAME:unknown}"
    }
  }
  
  # Parse user agent
  if [nginx][access][agent] {
    useragent {
      source => "[nginx][access][agent]"
      target => "user_agent"
    }
  }
  
  # GeoIP lookup
  if [nginx][access][remote_ip] {
    geoip {
      source => "[nginx][access][remote_ip]"
      target => "source.geo"
      database => "/usr/share/GeoIP/GeoLite2-City.mmdb"
    }
  }
  
  # Date parsing
  date {
    match => ["timestamp", "ISO8601", "yyyy-MM-dd HH:mm:ss,SSS", "dd/MMM/yyyy:HH:mm:ss Z"]
    target => "@timestamp"
    remove_field => ["timestamp"]
  }
  
  # Remove unnecessary fields
  mutate {
    remove_field => ["@version", "beat", "input", "offset", "prospector", "source"]
  }
  
  # Add ECS (Elastic Common Schema) fields
  if [log.level] == "ERROR" or [log.level] == "FATAL" {
    mutate {
      add_field => {
        "event.kind" => "event"
        "event.category" => "process"
        "event.type" => ["error"]
        "event.severity" => 4
      }
    }
  }
}

output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["${ELASTICSEARCH_HOSTS:elasticsearch:9200}"]
    user => "${ELASTICSEARCH_USERNAME:elastic}"
    password => "${ELASTICSEARCH_PASSWORD:changeme}"
    ssl => true
    ssl_certificate_verification => true
    cacert => "/etc/logstash/certs/ca.crt"
    
    # Index naming based on log type and date
    index => "%{[@metadata][beat]}-%{[service.environment]}-%{+YYYY.MM.dd}"
    
    # Use ILM (Index Lifecycle Management)
    ilm_enabled => true
    ilm_rollover_alias => "resilienceai-logs"
    ilm_pattern => "{now/d}-000001"
    ilm_policy => "resilienceai-logs-policy"
    
    # Template management
    template_name => "resilienceai-logs"
    template_overwrite => true
    template => "/etc/logstash/templates/resilienceai-logs-template.json"
  }
  
  # Send errors to separate index
  if [log.level] in ["ERROR", "FATAL", "CRITICAL"] {
    elasticsearch {
      hosts => ["${ELASTICSEARCH_HOSTS:elasticsearch:9200}"]
      user => "${ELASTICSEARCH_USERNAME}"
      password => "${ELASTICSEARCH_PASSWORD}"
      index => "resilienceai-errors-%{+YYYY.MM.dd}"
    }
  }
  
  # Debug output (only in development)
  if "${ENVIRONMENT}" == "development" {
    stdout {
      codec => rubydebug
    }
  }
}
```

### 5.3 Elasticsearch Index Template

**File: `/opt/monitoring/elasticsearch/templates/resilienceai-logs-template.json`**

```json
{
  "index_patterns": ["resilienceai-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.refresh_interval": "5s",
    "index.mapping.total_fields.limit": 10000,
    "index.mapping.depth.limit": 20,
    "index.mapping.nested_fields.limit": 50,
    "index.lifecycle.name": "resilienceai-logs-policy",
    "index.lifecycle.rollover_alias": "resilienceai-logs"
  },
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_keywords": {
          "match_mapping_type": "string",
          "mapping": {
            "type": "keyword",
            "ignore_above": 1024
          }
        }
      },
      {
        "long_fields": {
          "match_mapping_type": "long",
          "mapping": {
            "type": "long"
          }
        }
      },
      {
        "double_fields": {
          "match_mapping_type": "double",
          "mapping": {
            "type": "float"
          }
        }
      }
    ],
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "message": {
        "type": "text",
        "norms": false
      },
      "log": {
        "properties": {
          "level": {
            "type": "keyword"
          },
          "logger": {
            "type": "keyword"
          },
          "message": {
            "type": "text",
            "norms": false
          }
        }
      },
      "service": {
        "properties": {
          "name": {
            "type": "keyword"
          },
          "version": {
            "type": "keyword"
          },
          "environment": {
            "type": "keyword"
          }
        }
      },
      "trace": {
        "properties": {
          "id": {
            "type": "keyword"
          },
          "span": {
            "type": "keyword"
          }
        }
      },
      "user": {
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "keyword"
          },
          "email": {
            "type": "keyword"
          }
        }
      },
      "source": {
        "properties": {
          "ip": {
            "type": "ip"
          },
          "geo": {
            "properties": {
              "location": {
                "type": "geo_point"
              },
              "country_name": {
                "type": "keyword"
              },
              "city_name": {
                "type": "keyword"
              }
            }
          }
        }
      },
      "event": {
        "properties": {
          "kind": {
            "type": "keyword"
          },
          "category": {
            "type": "keyword"
          },
          "type": {
            "type": "keyword"
          },
          "outcome": {
            "type": "keyword"
          },
          "severity": {
            "type": "long"
          }
        }
      },
      "http": {
        "properties": {
          "request": {
            "properties": {
              "method": {
                "type": "keyword"
              },
              "body": {
                "properties": {
                  "bytes": {
                    "type": "long"
                  }
                }
              }
            }
          },
          "response": {
            "properties": {
              "status_code": {
                "type": "long"
              },
              "body": {
                "properties": {
                  "bytes": {
                    "type": "long"
                  }
                }
              }
            }
          }
        }
      },
      "nginx": {
        "properties": {
          "access": {
            "properties": {
              "remote_ip": {
                "type": "ip"
              },
              "method": {
                "type": "keyword"
              },
              "url": {
                "type": "keyword"
              },
              "response_code": {
                "type": "long"
              },
              "body_sent": {
                "properties": {
                  "bytes": {
                    "type": "long"
                  }
                }
              }
            }
          }
        }
      },
      "postgresql": {
        "properties": {
          "log": {
            "properties": {
              "database": {
                "type": "keyword"
              },
              "user": {
                "type": "keyword"
              },
              "level": {
                "type": "keyword"
              },
              "duration": {
                "type": "float"
              },
              "query": {
                "type": "text",
                "norms": false
              }
            }
          }
        }
      }
    }
  }
}
```

### 5.4 Application Logging Configuration (Python)

**File: `/app/resilienceai/monitoring/logging_config.py`**

```python
"""
ResilienceAI Structured Logging Configuration
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import traceback

import structlog
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add source location
        log_record['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Add thread/process info
        log_record['process'] = {
            'pid': record.process,
            'thread_id': record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'stacktrace': traceback.format_exception(*record.exc_info)
            }


def configure_logging(
    level: str = "INFO",
    environment: str = "production",
    service_name: str = "resilienceai-api",
    json_format: bool = True
) -> None:
    """Configure structured logging for the application"""
    
    # Configure standard library logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if json_format:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [console_handler]
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


class ContextualLogger:
    """Logger with context binding support"""
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        self.logger = structlog.get_logger(name)
        self.context = context or {}
    
    def bind(self, **kwargs) -> 'ContextualLogger':
        """Bind additional context"""
        new_context = {**self.context, **kwargs}
        return ContextualLogger(self.logger.name, new_context)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method with context"""
        log_data = {**self.context, **kwargs}
        getattr(self.logger, level)(message, **log_data)
    
    def debug(self, message: str, **kwargs):
        self._log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log('critical', message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with stack trace"""
        self._log('exception', message, **kwargs)


# Request context middleware for FastAPI
class RequestContextMiddleware:
    """Middleware to add request context to logs"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = scope.get("headers", {}).get(b"x-request-id", b"").decode() or str(uuid.uuid4())
            
            # Bind request context
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(
                request_id=request_id,
                method=scope.get("method"),
                path=scope.get("path"),
                client=scope.get("client", ["", ""])[0]
            )
        
        await self.app(scope, receive, send)


# Usage example
"""
from resilienceai.monitoring.logging_config import configure_logging, ContextualLogger

# Configure logging at application startup
configure_logging(
    level="INFO",
    environment="production",
    service_name="resilienceai-api",
    json_format=True
)

# Get logger
logger = ContextualLogger("resilienceai.api")

# Log with context
logger.info(
    "Processing prediction request",
    user_id="user-123",
    model_type="credit_default",
    request_id="req-456"
)

# Log with bound context
request_logger = logger.bind(request_id="req-789", user_id="user-456")
request_logger.info("Starting prediction")
request_logger.info("Prediction completed", confidence=0.95, risk_score=42)
"""
```



---

## 6. Alertmanager Configuration

### 6.1 Alertmanager Main Configuration

**File: `/opt/monitoring/alertmanager/alertmanager.yml`**

```yaml
global:
  # SMTP configuration for email alerts
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@resilienceai.io'
  smtp_auth_username: '${SMTP_USERNAME}'
  smtp_auth_password: '${SMTP_PASSWORD}'
  smtp_require_tls: true
  
  # Slack API URL
  slack_api_url: '${SLACK_WEBHOOK_URL}'
  
  # PagerDuty configuration
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'
  
  # OpsGenie configuration
  opsgenie_api_key: '${OPSGENIE_API_KEY}'
  opsgenie_api_url: 'https://api.opsgenie.com/'
  
  # Resolve timeout
  resolve_timeout: 5m

# Templates
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route tree - defines how alerts are routed
route:
  # Default receiver
  receiver: 'default'
  
  # Group alerts by these labels
  group_by: ['alertname', 'cluster', 'service', 'severity']
  
  # Wait before sending notification for group
  group_wait: 30s
  
  # Interval between notifications for same group
  group_interval: 5m
  
  # Interval before resending resolved notification
  repeat_interval: 4h
  
  # Routes
  routes:
    # Critical alerts - immediate notification
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 0s
      repeat_interval: 15m
      continue: true
    
    # Warning alerts - standard notification
    - match:
        severity: warning
      receiver: 'warning-alerts'
      group_wait: 1m
      repeat_interval: 2h
      continue: true
    
    # Info alerts - minimal notification
    - match:
        severity: info
      receiver: 'info-alerts'
      group_wait: 5m
      repeat_interval: 24h
      continue: true
    
    # Platform team alerts
    - match_re:
        team: platform|sre|devops
      receiver: 'platform-team'
      routes:
        - match:
            severity: critical
          receiver: 'platform-critical'
    
    # ML team alerts
    - match_re:
        team: ml|data-science
      receiver: 'ml-team'
      routes:
        - match:
            severity: critical
          receiver: 'ml-critical'
    
    # Database team alerts
    - match_re:
        team: data|database
      receiver: 'data-team'
    
    # Security alerts
    - match_re:
        team: security
      receiver: 'security-team'
      routes:
        - match:
            severity: critical
          receiver: 'security-critical'
    
    # Business/Product alerts
    - match_re:
        team: product|business
      receiver: 'product-team'
    
    # SLO breach alerts
    - match:
        slo: availability
      receiver: 'slo-team'
      repeat_interval: 1h

# Inhibition rules - suppress certain alerts
inhibit_rules:
  # Inhibit warning if critical is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
  
  # Inhibit info if warning is firing
  - source_match:
      severity: 'warning'
    target_match:
      severity: 'info'
    equal: ['alertname', 'cluster', 'service']

# Receivers - define notification endpoints
receivers:
  # Default receiver
  - name: 'default'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'
        actions:
          - type: button
            text: 'Runbook'
            url: '{{ .CommonAnnotations.runbook_url }}'
          - type: button
            text: 'Dashboard'
            url: '{{ .CommonAnnotations.dashboard_url }}'
          - type: button
            text: 'Silence'
            url: '{{ template "__alert_silence_link" . }}'

  # Critical alerts receiver
  - name: 'critical-alerts'
    slack_configs:
      - channel: '#critical-alerts'
        send_resolved: true
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ template "slack.critical.text" . }}'
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
        actions:
          - type: button
            text: 'Runbook'
            url: '{{ .CommonAnnotations.runbook_url }}'
          - type: button
            text: 'Dashboard'
            url: '{{ .CommonAnnotations.dashboard_url }}'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        send_resolved: true
        severity: critical
        description: '{{ .GroupLabels.alertname }}'
        details:
          firing: '{{ template "pagerduty.default.instances" .Alerts.Firing }}'
          resolved: '{{ template "pagerduty.default.instances" .Alerts.Resolved }}'
          num_firing: '{{ .Alerts.Firing | len }}'
          num_resolved: '{{ .Alerts.Resolved | len }}'
    opsgenie_configs:
      - api_key: '${OPSGENIE_API_KEY}'
        send_resolved: true
        priority: P1
        message: '{{ .GroupLabels.alertname }}'
        description: '{{ template "opsgenie.default.description" . }}'
        responders:
          - name: 'Platform Team'
            type: team
    email_configs:
      - to: 'oncall@resilienceai.io'
        send_resolved: true
        subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
        html: '{{ template "email.critical.html" . }}'

  # Warning alerts receiver
  - name: 'warning-alerts'
    slack_configs:
      - channel: '#warnings'
        send_resolved: true
        title: '⚠️ WARNING: {{ .GroupLabels.alertname }}'
        text: '{{ template "slack.warning.text" . }}'
        color: '{{ if eq .Status "firing" }}warning{{ else }}good{{ end }}'
    email_configs:
      - to: 'team@resilienceai.io'
        send_resolved: true
        subject: '[WARNING] {{ .GroupLabels.alertname }}'

  # Info alerts receiver
  - name: 'info-alerts'
    slack_configs:
      - channel: '#info-alerts'
        send_resolved: true
        title: 'ℹ️ INFO: {{ .GroupLabels.alertname }}'
        text: '{{ template "slack.info.text" . }}'
        color: '#439FE0'

  # Platform team
  - name: 'platform-team'
    slack_configs:
      - channel: '#platform-alerts'
        send_resolved: true

  - name: 'platform-critical'
    slack_configs:
      - channel: '#platform-critical'
        send_resolved: true
        mention_users: ['U123456', 'U789012']
    pagerduty_configs:
      - service_key: '${PAGERDUTY_PLATFORM_KEY}'
        send_resolved: true

  # ML team
  - name: 'ml-team'
    slack_configs:
      - channel: '#ml-alerts'
        send_resolved: true

  - name: 'ml-critical'
    slack_configs:
      - channel: '#ml-critical'
        send_resolved: true
        mention_users: ['U345678']
    pagerduty_configs:
      - service_key: '${PAGERDUTY_ML_KEY}'
        send_resolved: true

  # Data team
  - name: 'data-team'
    slack_configs:
      - channel: '#data-alerts'
        send_resolved: true

  # Security team
  - name: 'security-team'
    slack_configs:
      - channel: '#security-alerts'
        send_resolved: true

  - name: 'security-critical'
    slack_configs:
      - channel: '#security-critical'
        send_resolved: true
        mention_groups: ['S123456']
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SECURITY_KEY}'
        send_resolved: true
        severity: critical

  # Product team
  - name: 'product-team'
    slack_configs:
      - channel: '#product-alerts'
        send_resolved: true

  # SLO team
  - name: 'slo-team'
    slack_configs:
      - channel: '#slo-alerts'
        send_resolved: true
        title: '📊 SLO Alert: {{ .GroupLabels.alertname }}'
        text: '{{ template "slack.slo.text" . }}'

# Time intervals for muted alerts
time_intervals:
  - name: business-hours
    time_intervals:
      - times:
          - start_time: '09:00'
            end_time: '17:00'
        weekdays: ['monday:friday']
        location: 'America/New_York'
  
  - name: maintenance-windows
    time_intervals:
      - times:
          - start_time: '02:00'
            end_time: '04:00'
        weekdays: ['sunday']
```

### 6.2 Alertmanager Templates

**File: `/opt/monitoring/alertmanager/templates/slack.tmpl`**

```gotemplate
{{ define "slack.default.title" }}{{ .Status | toUpper }}: {{ .GroupLabels.alertname }}{{ end }}

{{ define "slack.default.text" }}
{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05" }}
{{ if .Labels.runbook_url }}*Runbook:* {{ .Labels.runbook_url }}{{ end }}
{{ end }}
{{ end }}

{{ define "slack.critical.text" }}
🚨 *CRITICAL ALERT* 🚨

{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Service:* {{ .Labels.service }}
*Instance:* {{ .Labels.instance }}
*Severity:* {{ .Labels.severity }}
*Description:* {{ .Annotations.description }}
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}

{{ if .Annotations.runbook_url }}📚 *Runbook:* <{{ .Annotations.runbook_url }}|View Runbook>{{ end }}
{{ if .Annotations.dashboard_url }}📊 *Dashboard:* <{{ .Annotations.dashboard_url }}|View Dashboard>{{ end }}
{{ end }}

*Firing:* {{ .Alerts.Firing | len }} | *Resolved:* {{ .Alerts.Resolved | len }}
{{ end }}

{{ define "slack.warning.text" }}
⚠️ *WARNING ALERT*

{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Service:* {{ .Labels.service }}
*Instance:* {{ .Labels.instance }}
*Description:* {{ .Annotations.description }}
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}
{{ end }}
{{ end }}

{{ define "slack.info.text" }}
ℹ️ *Information*

{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
{{ end }}
{{ end }}

{{ define "slack.slo.text" }}
📊 *SLO Alert*

{{ range .Alerts }}
*SLO:* {{ .Labels.slo }}
*Service:* {{ .Labels.service }}
*Current Value:* {{ .Annotations.current_value }}
*Target:* {{ .Annotations.target }}
*Description:* {{ .Annotations.description }}
{{ end }}
{{ end }}

{{ define "__alert_silence_link" -}}
    {{ .ExternalURL }}/#/silences/new?filter=%7B
    {{- range .CommonLabels.SortedPairs -}}
        {{- if ne .Name "alertname" -}}
            {{- .Name }}%3D"{{- .Value | urlquery -}}"%2C%20
        {{- end -}}
    {{- end -}}
    alertname%3D"{{- .CommonLabels.alertname -}}"%7D
{{- end }}
```

**File: `/opt/monitoring/alertmanager/templates/email.tmpl`**

```gotemplate
{{ define "email.critical.html" }}
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #dc3545; color: white; padding: 20px; }
        .alert { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
        .firing { border-left: 5px solid #dc3545; }
        .resolved { border-left: 5px solid #28a745; }
        .label { font-weight: bold; color: #666; }
        .value { color: #333; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .button { 
            display: inline-block; 
            padding: 10px 20px; 
            background-color: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 CRITICAL ALERT</h1>
        <p>Status: {{ .Status | toUpper }}</p>
        <p>Alert Group: {{ .GroupLabels.alertname }}</p>
    </div>

    <h2>Summary</h2>
    <table>
        <tr>
            <th>Firing Alerts</th>
            <th>Resolved Alerts</th>
            <th>Group Labels</th>
        </tr>
        <tr>
            <td>{{ .Alerts.Firing | len }}</td>
            <td>{{ .Alerts.Resolved | len }}</td>
            <td>
                {{ range .GroupLabels.SortedPairs }}
                {{ .Name }}: {{ .Value }}<br>
                {{ end }}
            </td>
        </tr>
    </table>

    <h2>Actions</h2>
    <p>
        <a href="{{ .ExternalURL }}" class="button">View in Alertmanager</a>
        {{ if .CommonAnnotations.runbook_url }}
        <a href="{{ .CommonAnnotations.runbook_url }}" class="button">View Runbook</a>
        {{ end }}
        {{ if .CommonAnnotations.dashboard_url }}
        <a href="{{ .CommonAnnotations.dashboard_url }}" class="button">View Dashboard</a>
        {{ end }}
    </p>

    <h2>Alert Details</h2>
    {{ range .Alerts }}
    <div class="alert {{ .Status }}">
        <h3>{{ .Annotations.summary }}</h3>
        <p><span class="label">Status:</span> <span class="value">{{ .Status | toUpper }}</span></p>
        <p><span class="label">Started:</span> <span class="value">{{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}</span></p>
        {{ if .EndsAt }}
        <p><span class="label">Ended:</span> <span class="value">{{ .EndsAt.Format "2006-01-02 15:04:05 UTC" }}</span></p>
        {{ end }}
        <p><span class="label">Description:</span> <span class="value">{{ .Annotations.description }}</span></p>
        
        <h4>Labels</h4>
        <table>
            {{ range .Labels.SortedPairs }}
            <tr>
                <td>{{ .Name }}</td>
                <td>{{ .Value }}</td>
            </tr>
            {{ end }}
        </table>
    </div>
    {{ end }}
</body>
</html>
{{ end }}
```

---

## 7. SLO/SLI Definitions

### 7.1 SLO Document

**File: `/opt/monitoring/slo/resilienceai-slo.yml`**

```yaml
# ResilienceAI Service Level Objectives
# Version: 1.0.0
# Last Updated: 2024-01-15

metadata:
  service: ResilienceAI
  version: 1.0.0
  owner: Platform Team
  reviewers:
    - platform-team@resilienceai.io
    - sre-team@resilienceai.io
  approval_date: "2024-01-15"
  review_cycle: quarterly

# Service Level Indicators (SLIs) and Objectives (SLOs)
slos:
  # API Availability SLO
  - name: api-availability
    display_name: "API Availability"
    description: "The proportion of successful HTTP requests (2xx/3xx) out of total requests"
    
    sli:
      type: availability
      query: |
        sum(rate(resilienceai_http_requests_total{status_code!~"5.."}[window]))
        /
        sum(rate(resilienceai_http_requests_total[window]))
    
    objectives:
      - window: 1h
        target: 0.999
        alert_threshold: 0.995
      - window: 1d
        target: 0.999
        alert_threshold: 0.998
      - window: 28d
        target: 0.999
        alert_threshold: 0.999
    
    error_budget:
      policy: 0.1%  # 0.1% of requests can fail
      burn_rate_alerts:
        - name: fast-burn
          multiplier: 14.4  # Burn 2% budget in 1 hour
          severity: critical
        - name: slow-burn
          multiplier: 2  # Burn 5% budget in 3 days
          severity: warning
    
    consequences:
      breach: "Escalate to on-call engineer, review incident within 24 hours"
      repeated_breach: "Schedule architectural review, consider service degradation mode"
    
    dashboard: "https://grafana.resilienceai.io/d/resilienceai-slo"
    runbook: "https://wiki.resilienceai.io/runbooks/api-availability"

  # API Latency SLO
  - name: api-latency
    display_name: "API Latency"
    description: "The proportion of requests that complete within the target latency"
    
    sli:
      type: latency
      query: |
        histogram_quantile(0.95,
          sum(rate(resilienceai_http_request_duration_seconds_bucket[window])) by (le)
        )
    
    objectives:
      - window: 1h
        target: 0.95  # 95% of requests under 500ms
        threshold: 0.5
        alert_threshold: 0.90
      - window: 1d
        target: 0.95
        threshold: 0.5
        alert_threshold: 0.93
    
    error_budget:
      policy: "5% of requests can exceed 500ms"
    
    dashboard: "https://grafana.resilienceai.io/d/resilienceai-latency"
    runbook: "https://wiki.resilienceai.io/runbooks/api-latency"

  # Prediction Service SLO
  - name: prediction-success-rate
    display_name: "Prediction Success Rate"
    description: "The proportion of successful predictions out of total prediction requests"
    
    sli:
      type: availability
      query: |
        sum(rate(resilienceai_prediction_requests_total{status="success"}[window]))
        /
        sum(rate(resilienceai_prediction_requests_total[window]))
    
    objectives:
      - window: 1h
        target: 0.99
        alert_threshold: 0.95
      - window: 1d
        target: 0.99
        alert_threshold: 0.98
    
    dashboard: "https://grafana.resilienceai.io/d/prediction-slo"
    runbook: "https://wiki.resilienceai.io/runbooks/prediction-failures"

  # Prediction Latency SLO
  - name: prediction-latency
    display_name: "Prediction Latency"
    description: "The proportion of predictions that complete within target time"
    
    sli:
      type: latency
      query: |
        histogram_quantile(0.99,
          sum(rate(resilienceai_prediction_duration_seconds_bucket[window])) by (le)
        )
    
    objectives:
      - window: 1h
        target: 0.99  # 99% under 5 seconds
        threshold: 5.0
        alert_threshold: 0.95
    
    dashboard: "https://grafana.resilienceai.io/d/prediction-latency"

  # Database Availability SLO
  - name: database-availability
    display_name: "Database Availability"
    description: "The proportion of successful database operations"
    
    sli:
      type: availability
      query: |
        sum(rate(resilienceai_db_query_duration_seconds_count[window]))
        -
        sum(rate(resilienceai_db_query_errors_total[window]))
        /
        sum(rate(resilienceai_db_query_duration_seconds_count[window]))
    
    objectives:
      - window: 1h
        target: 0.9999
        alert_threshold: 0.999
      - window: 1d
        target: 0.9999
        alert_threshold: 0.9995
    
    dashboard: "https://grafana.resilienceai.io/d/database-slo"

  # Worker Task Success Rate SLO
  - name: worker-task-success
    display_name: "Worker Task Success Rate"
    description: "The proportion of successfully completed background tasks"
    
    sli:
      type: availability
      query: |
        sum(rate(resilienceai_celery_tasks_total{status="success"}[window]))
        /
        sum(rate(resilienceai_celery_tasks_total[window]))
    
    objectives:
      - window: 1h
        target: 0.995
        alert_threshold: 0.99
      - window: 1d
        target: 0.995
        alert_threshold: 0.992
    
    dashboard: "https://grafana.resilienceai.io/d/worker-slo"

  # Cache Hit Ratio SLO
  - name: cache-hit-ratio
    display_name: "Cache Hit Ratio"
    description: "The proportion of cache operations that are hits"
    
    sli:
      type: ratio
      query: |
        sum(rate(resilienceai_cache_operations_total{operation="get",result="hit"}[window]))
        /
        sum(rate(resilienceai_cache_operations_total{operation="get"}[window]))
    
    objectives:
      - window: 1h
        target: 0.80
        alert_threshold: 0.70
    
    dashboard: "https://grafana.resilienceai.io/d/cache-slo"

# Service Level Agreements (SLAs) - External commitments
slas:
  - name: enterprise-availability
    description: "Availability commitment for Enterprise customers"
    target: 0.9995  # 99.95% uptime
    measurement_window: 1month
    penalty: "10% monthly credit for each 0.1% below target"
    
  - name: standard-availability
    description: "Availability commitment for Standard customers"
    target: 0.99  # 99% uptime
    measurement_window: 1month
    penalty: "5% monthly credit for each 1% below target"

# Error Budget Policies
error_budget_policies:
  - name: standard
    description: "Standard error budget policy"
    budget: 0.001  # 0.1% for 99.9% SLO
    burn_rate_alerts:
      - name: fast-burn
        burn_rate: 14.4
        lookback: 1h
        alert_after: 2m
        severity: critical
      - name: slow-burn
        burn_rate: 2
        lookback: 3d
        alert_after: 1h
        severity: warning
    
  - name: relaxed
    description: "Relaxed error budget policy for non-critical services"
    budget: 0.01  # 1% for 99% SLO
    burn_rate_alerts:
      - name: fast-burn
        burn_rate: 10
        lookback: 1h
        alert_after: 5m
        severity: warning

# SLO Reporting
reporting:
  frequency: weekly
  recipients:
    - platform-team@resilienceai.io
    - leadership@resilienceai.io
  dashboard: "https://grafana.resilienceai.io/d/slo-report"
  
# Escalation Policy
escalation:
  levels:
    - level: 1
      condition: "SLO at risk (< 95% of target)"
      action: "Notify on-call engineer via Slack"
      time_to_respond: 15m
    
    - level: 2
      condition: "SLO breach (> 50% error budget consumed in 1 hour)"
      action: "Page on-call engineer, notify team lead"
      time_to_respond: 5m
    
    - level: 3
      condition: "Multiple SLOs breached or SLA at risk"
      action: "Page all team leads, initiate incident response"
      time_to_respond: 2m
```

### 7.2 SLO Alert Rules

**File: `/opt/monitoring/prometheus/rules/slo_alerts.yml`**

```yaml
groups:
  - name: slo_burn_rate_alerts
    rules:
      # Fast burn alert - 2% budget in 1 hour (14.4x burn rate)
      - alert: SLOFastBurn
        expr: |
          (
            sum by (service, slo) (rate(resilienceai_http_requests_total{status_code=~"5.."}[1h]))
            /
            sum by (service, slo) (rate(resilienceai_http_requests_total[1h]))
          ) > 14.4 * (1 - 0.999)
        for: 2m
        labels:
          severity: critical
          team: platform
          alert_type: slo_burn_rate
        annotations:
          summary: "Fast error budget burn detected"
          description: "Service {{ $labels.service }} is burning error budget at {{ $value | humanizePercentage }} rate"
          runbook_url: "https://wiki.resilienceai.io/runbooks/slo-fast-burn"
      
      # Slow burn alert - 5% budget in 3 days (2x burn rate)
      - alert: SLOSlowBurn
        expr: |
          (
            sum by (service, slo) (rate(resilienceai_http_requests_total{status_code=~"5.."}[3d]))
            /
            sum by (service, slo) (rate(resilienceai_http_requests_total[3d]))
          ) > 2 * (1 - 0.999)
        for: 1h
        labels:
          severity: warning
          team: platform
          alert_type: slo_burn_rate
        annotations:
          summary: "Slow error budget burn detected"
          description: "Service {{ $labels.service }} is slowly burning error budget"

  - name: slo_availability_alerts
    rules:
      # API availability SLO breach
      - alert: APIAvailabilitySLOBreach
        expr: |
          (
            1 - (
              sum(rate(resilienceai_http_requests_total{status_code=~"5.."}[1h]))
              /
              sum(rate(resilienceai_http_requests_total[1h]))
            )
          ) < 0.999
        for: 5m
        labels:
          severity: critical
          team: platform
          slo: availability
        annotations:
          summary: "API Availability SLO breached"
          description: "Current availability is {{ $value | humanizePercentage }}, below SLO of 99.9%"
      
      # API availability at risk
      - alert: APIAvailabilitySLOAtRisk
        expr: |
          (
            1 - (
              sum(rate(resilienceai_http_requests_total{status_code=~"5.."}[1h]))
              /
              sum(rate(resilienceai_http_requests_total[1h]))
            )
          ) < 0.9995
        for: 10m
        labels:
          severity: warning
          team: platform
          slo: availability
        annotations:
          summary: "API Availability SLO at risk"
          description: "Current availability is {{ $value | humanizePercentage }}, approaching SLO threshold"

  - name: slo_latency_alerts
    rules:
      # API latency SLO breach
      - alert: APILatencySLOBreach
        expr: |
          (
            sum(rate(resilienceai_http_request_duration_seconds_bucket{le="0.5"}[1h]))
            /
            sum(rate(resilienceai_http_request_duration_seconds_count[1h]))
          ) < 0.95
        for: 10m
        labels:
          severity: warning
          team: platform
          slo: latency
        annotations:
          summary: "API Latency SLO breached"
          description: "Only {{ $value | humanizePercentage }} of requests are under 500ms"
```



---

## 8. Error Tracking (Sentry)

### 8.1 Sentry SDK Configuration

**File: `/app/resilienceai/monitoring/sentry_config.py`**

```python
"""
ResilienceAI Sentry Error Tracking Configuration
"""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
import logging


def initialize_sentry(
    dsn: str = None,
    environment: str = "production",
    release: str = "1.0.0",
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1
) -> None:
    """
    Initialize Sentry SDK with all integrations
    
    Args:
        dsn: Sentry DSN (defaults to SENTRY_DSN env var)
        environment: Deployment environment
        release: Application release version
        sample_rate: Error sampling rate (1.0 = 100%)
        traces_sample_rate: Performance tracing sample rate
        profiles_sample_rate: Profiling sample rate
    """
    
    dsn = dsn or os.getenv("SENTRY_DSN")
    
    if not dsn:
        logging.warning("Sentry DSN not configured, error tracking disabled")
        return
    
    # Configure logging integration
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture INFO and above as breadcrumbs
        event_level=logging.ERROR  # Send ERROR and above as events
    )
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        
        # Sample rates
        sample_rate=sample_rate,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # Enable all integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            sentry_logging,
            AsyncioIntegration(),
            AioHttpIntegration(),
            HttpxIntegration(),
        ],
        
        # Additional configuration
        attach_stacktrace=True,
        include_source_context=True,
        include_local_variables=True,
        max_value_length=1024,
        send_default_pii=False,  # Don't send personally identifiable info
        
        # Before-send hook for filtering
        before_send=before_send_event,
        before_send_transaction=before_send_transaction,
        
        # In-app frames
        in_app_include=["resilienceai"],
        
        # Server name
        server_name=os.getenv("HOSTNAME", "unknown"),
        
        # Tags
        default_tags={
            "service": "resilienceai-api",
            "team": "platform"
        }
    )
    
    # Set user context (will be populated per-request)
    sentry_sdk.set_context("app", {
        "name": "ResilienceAI",
        "version": release,
        "environment": environment
    })


def before_send_event(event, hint):
    """
    Filter events before sending to Sentry
    
    Returns None to drop the event
    """
    # Drop certain error types
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Ignore expected errors
        if exc_type.__name__ in ['ValidationError', 'HTTPException']:
            return None
        
        # Ignore 404s for common paths
        if exc_type.__name__ == 'NotFoundError':
            if event.get('request', {}).get('url', '').endswith(('/favicon.ico', '/robots.txt')):
                return None
    
    # Add custom tags
    if 'tags' not in event:
        event['tags'] = {}
    
    event['tags']['error_category'] = categorize_error(event)
    
    return event


def before_send_transaction(transaction, hint):
    """
    Filter transactions before sending to Sentry
    """
    # Drop health check transactions
    if transaction.get('transaction', '').endswith(('/health', '/ready', '/metrics')):
        return None
    
    return transaction


def categorize_error(event):
    """Categorize error for better organization"""
    exception = event.get('exception', {})
    values = exception.get('values', [])
    
    if not values:
        return 'unknown'
    
    exc_type = values[0].get('type', 'Unknown')
    
    categories = {
        'DatabaseError': 'database',
        'ConnectionError': 'network',
        'TimeoutError': 'timeout',
        'ValidationError': 'validation',
        'AuthenticationError': 'auth',
        'AuthorizationError': 'auth',
        'PredictionError': 'ml',
        'ModelError': 'ml',
    }
    
    return categories.get(exc_type, 'application')


class SentryContext:
    """Context manager for Sentry scopes"""
    
    def __init__(self, **context):
        self.context = context
        self.scope = None
    
    def __enter__(self):
        self.scope = sentry_sdk.push_scope()
        for key, value in self.context.items():
            self.scope.set_extra(key, value)
        return self.scope
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sentry_sdk.pop_scope()


def set_user_context(user_id: str = None, email: str = None, **kwargs):
    """Set user context for current scope"""
    with sentry_sdk.configure_scope() as scope:
        scope.user = {
            "id": user_id,
            "email": email,
            **kwargs
        }


def set_request_context(request_id: str = None, **kwargs):
    """Set request context for current scope"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("request_id", request_id)
        for key, value in kwargs.items():
            scope.set_extra(key, value)


def capture_prediction_error(model_type: str, error: Exception, **context):
    """Capture prediction-specific errors"""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("error_type", "prediction")
        scope.set_tag("model_type", model_type)
        scope.set_extra("model_type", model_type)
        scope.set_extra("context", context)
        sentry_sdk.capture_exception(error)


def capture_ml_error(model_name: str, error: Exception, features: dict = None):
    """Capture ML model errors"""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("error_type", "ml")
        scope.set_tag("model_name", model_name)
        scope.set_extra("model_name", model_name)
        if features:
            # Sanitize features before logging
            scope.set_extra("feature_count", len(features))
        sentry_sdk.capture_exception(error)


def capture_business_event(event_type: str, **data):
    """Capture business events as Sentry messages"""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("event_type", event_type)
        scope.set_level("info")
        sentry_sdk.capture_message(
            f"Business Event: {event_type}",
            extras=data
        )


# FastAPI middleware for Sentry context
class SentryContextMiddleware:
    """Middleware to add request context to Sentry"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = scope.get("headers", {}).get(b"x-request-id", b"").decode() or str(uuid.uuid4())
            
            with sentry_sdk.configure_scope() as sentry_scope:
                sentry_scope.set_tag("request_id", request_id)
                sentry_scope.set_extra("method", scope.get("method"))
                sentry_scope.set_extra("path", scope.get("path"))
                
                # Start transaction
                transaction = sentry_sdk.start_transaction(
                    op="http.server",
                    name=f"{scope.get('method')} {scope.get('path')}"
                )
                
                try:
                    await self.app(scope, receive, send)
                    transaction.set_http_status(200)
                except Exception as e:
                    transaction.set_http_status(500)
                    raise
                finally:
                    transaction.finish()
        else:
            await self.app(scope, receive, send)


# Usage example
"""
from resilienceai.monitoring.sentry_config import (
    initialize_sentry,
    SentryContext,
    set_user_context,
    capture_prediction_error
)

# Initialize at application startup
initialize_sentry(
    environment="production",
    release="1.0.0",
    traces_sample_rate=0.1
)

# Use context manager
with SentryContext(prediction_id="123", model_type="credit_default"):
    result = make_prediction(data)

# Capture specific errors
try:
    prediction = model.predict(features)
except Exception as e:
    capture_prediction_error("credit_default", e, features_count=len(features))
    raise
"""
```

### 8.2 Sentry Deployment

**File: `/opt/monitoring/sentry/sentry-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentry-web
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sentry-web
  template:
    metadata:
      labels:
        app: sentry-web
    spec:
      containers:
        - name: sentry-web
          image: getsentry/sentry:23.11.0
          command:
            - sentry
            - run
            - web
          ports:
            - containerPort: 9000
          env:
            - name: SENTRY_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: sentry-secrets
                  key: secret-key
            - name: SENTRY_POSTGRES_HOST
              value: sentry-postgres
            - name: SENTRY_DB_NAME
              value: sentry
            - name: SENTRY_DB_USER
              value: sentry
            - name: SENTRY_DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: sentry-secrets
                  key: db-password
            - name: SENTRY_REDIS_HOST
              value: sentry-redis
            - name: SENTRY_EMAIL_HOST
              value: smtp.gmail.com
            - name: SENTRY_EMAIL_PORT
              value: "587"
            - name: SENTRY_EMAIL_USER
              valueFrom:
                secretKeyRef:
                  name: sentry-secrets
                  key: email-user
            - name: SENTRY_EMAIL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: sentry-secrets
                  key: email-password
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: sentry-web
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 9000
      targetPort: 9000
  selector:
    app: sentry-web
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentry-worker
  namespace: monitoring
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentry-worker
  template:
    metadata:
      labels:
        app: sentry-worker
    spec:
      containers:
        - name: sentry-worker
          image: getsentry/sentry:23.11.0
          command:
            - sentry
            - run
            - worker
          env:
            - name: SENTRY_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: sentry-secrets
                  key: secret-key
            - name: SENTRY_POSTGRES_HOST
              value: sentry-postgres
            - name: SENTRY_REDIS_HOST
              value: sentry-redis
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
```

---

## 9. Performance Monitoring

### 9.1 Application Performance Monitoring (APM)

**File: `/app/resilienceai/monitoring/apm.py`**

```python
"""
ResilienceAI Application Performance Monitoring
"""
import time
import functools
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio
from contextlib import contextmanager

from prometheus_client import Histogram, Counter, Gauge, Info
import psutil
import objgraph


# Performance metrics
PERFORMANCE_METRICS = {
    'function_calls': Counter(
        'resilienceai_function_calls_total',
        'Total function calls',
        ['function', 'module']
    ),
    'function_duration': Histogram(
        'resilienceai_function_duration_seconds',
        'Function execution duration',
        ['function', 'module'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    ),
    'memory_usage': Gauge(
        'resilienceai_memory_usage_bytes',
        'Memory usage in bytes',
        ['type']
    ),
    'cpu_usage': Gauge(
        'resilienceai_cpu_usage_percent',
        'CPU usage percentage',
        ['type']
    ),
    'gc_objects': Gauge(
        'resilienceai_gc_objects_total',
        'Number of objects tracked by GC',
        ['generation']
    ),
    'active_connections': Gauge(
        'resilienceai_active_connections',
        'Number of active connections',
        ['service']
    ),
}


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    open_files: int
    thread_count: int
    gc_objects: Dict[int, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used_mb': self.memory_used_mb,
            'memory_available_mb': self.memory_available_mb,
            'disk_usage_percent': self.disk_usage_percent,
            'open_files': self.open_files,
            'thread_count': self.thread_count,
            'gc_objects': self.gc_objects
        }


class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self._running = False
        self._task = None
        self._snapshots: list = []
        self._max_snapshots = 1000
    
    async def start(self):
        """Start performance monitoring"""
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop performance monitoring"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                snapshot = self._collect_metrics()
                self._snapshots.append(snapshot)
                
                # Keep only recent snapshots
                if len(self._snapshots) > self._max_snapshots:
                    self._snapshots = self._snapshots[-self._max_snapshots:]
                
                # Export to Prometheus
                self._export_to_prometheus(snapshot)
                
            except Exception as e:
                logger.error(f"Error collecting performance metrics: {e}")
            
            await asyncio.sleep(self.collection_interval)
    
    def _collect_metrics(self) -> PerformanceSnapshot:
        """Collect current performance metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        open_files = len(process.open_files())
        thread_count = process.num_threads()
        
        # GC objects
        gc_objects = {
            0: len(objgraph.by_type('dict')),  # Simplified
            1: len(objgraph.by_type('list')),
            2: len(objgraph.by_type('set'))
        }
        
        return PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=(disk.used / disk.total) * 100,
            open_files=open_files,
            thread_count=thread_count,
            gc_objects=gc_objects
        )
    
    def _export_to_prometheus(self, snapshot: PerformanceSnapshot):
        """Export metrics to Prometheus"""
        PERFORMANCE_METRICS['memory_usage'].labels(type='used').set(
            snapshot.memory_used_mb * 1024 * 1024
        )
        PERFORMANCE_METRICS['memory_usage'].labels(type='available').set(
            snapshot.memory_available_mb * 1024 * 1024
        )
        PERFORMANCE_METRICS['cpu_usage'].labels(type='total').set(
            snapshot.cpu_percent
        )
        
        for gen, count in snapshot.gc_objects.items():
            PERFORMANCE_METRICS['gc_objects'].labels(generation=str(gen)).set(count)
    
    def get_snapshots(self, count: int = 100) -> list:
        """Get recent performance snapshots"""
        return self._snapshots[-count:]
    
    def get_current(self) -> Optional[PerformanceSnapshot]:
        """Get current performance snapshot"""
        if self._snapshots:
            return self._snapshots[-1]
        return None


def profile_function(func: Callable) -> Callable:
    """Decorator to profile function performance"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        module = func.__module__
        name = func.__name__
        
        PERFORMANCE_METRICS['function_calls'].labels(
            function=name,
            module=module
        ).inc()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            PERFORMANCE_METRICS['function_duration'].labels(
                function=name,
                module=module
            ).observe(duration)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        module = func.__module__
        name = func.__name__
        
        PERFORMANCE_METRICS['function_calls'].labels(
            function=name,
            module=module
        ).inc()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            PERFORMANCE_METRICS['function_duration'].labels(
                function=name,
                module=module
            ).observe(duration)
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


@contextmanager
def profile_block(name: str, module: str = "__main__"):
    """Context manager to profile a block of code"""
    start_time = time.perf_counter()
    
    PERFORMANCE_METRICS['function_calls'].labels(
        function=name,
        module=module
    ).inc()
    
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        PERFORMANCE_METRICS['function_duration'].labels(
            function=name,
            module=module
        ).observe(duration)


class MemoryProfiler:
    """Memory profiling utilities"""
    
    @staticmethod
    def get_top_objects(limit: int = 20) -> list:
        """Get top memory-consuming object types"""
        return objgraph.most_common_types(limit=limit)
    
    @staticmethod
    def get_growth_since(reference: dict = None) -> dict:
        """Get object growth since reference point"""
        current = dict(objgraph.most_common_types())
        
        if reference is None:
            return current
        
        growth = {}
        for obj_type, count in current.items():
            ref_count = reference.get(obj_type, 0)
            if count > ref_count:
                growth[obj_type] = count - ref_count
        
        return growth
    
    @staticmethod
    def find_leaking_objects(obj_type: str, limit: int = 10) -> list:
        """Find potentially leaking objects of a specific type"""
        return objgraph.by_type(obj_type)[:limit]


class DatabasePerformanceMonitor:
    """Monitor database query performance"""
    
    def __init__(self):
        self.query_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'max_time': 0,
            'errors': 0
        })
    
    def record_query(self, query_type: str, duration: float, error: bool = False):
        """Record a database query"""
        stats = self.query_stats[query_type]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], duration)
        
        if error:
            stats['errors'] += 1
    
    def get_slow_queries(self, threshold: float = 1.0) -> list:
        """Get queries exceeding threshold"""
        slow = []
        for query_type, stats in self.query_stats.items():
            if stats['avg_time'] > threshold:
                slow.append({
                    'query_type': query_type,
                    'avg_time': stats['avg_time'],
                    'max_time': stats['max_time'],
                    'count': stats['count']
                })
        return sorted(slow, key=lambda x: x['avg_time'], reverse=True)
    
    def get_stats(self) -> Dict:
        """Get all query statistics"""
        return dict(self.query_stats)


# Usage example
"""
from resilienceai.monitoring.apm import (
    PerformanceMonitor,
    profile_function,
    profile_block,
    DatabasePerformanceMonitor
)

# Start performance monitoring
monitor = PerformanceMonitor(collection_interval=60)
await monitor.start()

# Profile a function
@profile_function
async def expensive_operation():
    # Some expensive operation
    pass

# Profile a block
with profile_block("data_processing", module="predictions"):
    process_data(data)

# Monitor database queries
db_monitor = DatabasePerformanceMonitor()
db_monitor.record_query("SELECT", duration=0.5)
slow_queries = db_monitor.get_slow_queries(threshold=1.0)
"""
```



---

## 10. Uptime Monitoring

### 10.1 Blackbox Exporter Configuration

**File: `/opt/monitoring/blackbox/blackbox.yml`**

```yaml
modules:
  # HTTP 2xx probe
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 301, 302]
      method: GET
      headers:
        User-Agent: "Blackbox-Exporter/1.0"
      fail_if_ssl: false
      tls_config:
        insecure_skip_verify: false
      preferred_ip_protocol: "ip4"

  # HTTP 2xx with authentication
  http_2xx_auth:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      headers:
        Authorization: "Bearer ${API_TOKEN}"
      fail_if_ssl: false

  # HTTP POST probe
  http_post:
    prober: http
    timeout: 10s
    http:
      method: POST
      headers:
        Content-Type: "application/json"
      body: '{"health_check": true}'
      valid_status_codes: [200, 201]

  # TCP probe
  tcp_connect:
    prober: tcp
    timeout: 5s
    tcp:
      preferred_ip_protocol: "ip4"

  # TCP with TLS
  tcp_tls:
    prober: tcp
    timeout: 5s
    tcp:
      tls: true
      preferred_ip_protocol: "ip4"

  # ICMP ping probe
  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"

  # DNS probe
  dns:
    prober: dns
    timeout: 5s
    dns:
      preferred_ip_protocol: "ip4"
      transport_protocol: "udp"
      query_name: "resilienceai.io"
      query_type: "A"
      valid_rcodes:
        - NOERROR

  # gRPC health probe
  grpc:
    prober: grpc
    timeout: 5s
    grpc:
      tls: true
      preferred_ip_protocol: "ip4"
      service: "health"

  # API health endpoint probe
  api_health:
    prober: http
    timeout: 10s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      fail_if_body_not_matches_regexp:
        - '"status":\s*"healthy"'
      fail_if_ssl: false

  # Frontend probe
  frontend:
    prober: http
    timeout: 10s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      fail_if_body_not_matches_regexp:
        - '<html'
        - '</html>'
```

### 10.2 Prometheus Blackbox Scrape Configuration

**File: `/opt/monitoring/prometheus/blackbox-scrape.yml`**

```yaml
# Add to prometheus.yml scrape_configs

scrape_configs:
  # External endpoint monitoring
  - job_name: 'blackbox-external'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://resilienceai.io
        - https://app.resilienceai.io
        - https://api.resilienceai.io/health
        - https://api.resilienceai.io/docs
        - https://status.resilienceai.io
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # API health checks
  - job_name: 'blackbox-api-health'
    metrics_path: /probe
    params:
      module: [api_health]
    static_configs:
      - targets:
        - https://api.resilienceai.io/health
        - https://api.resilienceai.io/v1/health/deep
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # Internal service monitoring
  - job_name: 'blackbox-internal'
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
        - postgres:5432
        - redis:6379
        - elasticsearch:9200
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # Database connectivity
  - job_name: 'blackbox-database'
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
        - postgres-primary:5432
        - postgres-replica:5432
        - redis-primary:6379
        - redis-replica:6379
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # DNS monitoring
  - job_name: 'blackbox-dns'
    metrics_path: /probe
    params:
      module: [dns]
    static_configs:
      - targets:
        - 8.8.8.8
        - 1.1.1.1
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # ICMP ping monitoring
  - job_name: 'blackbox-icmp'
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets:
        - api.resilienceai.io
        - app.resilienceai.io
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### 10.3 Uptime Alert Rules

**File: `/opt/monitoring/prometheus/alerts/uptime_alerts.yml`**

```yaml
groups:
  - name: uptime_alerts
    rules:
      # Website down
      - alert: WebsiteDown
        expr: probe_success{job=~"blackbox.*"} == 0
        for: 1m
        labels:
          severity: critical
          team: platform
          alert_type: uptime
        annotations:
          summary: "Website/Service is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"
          runbook_url: "https://wiki.resilienceai.io/runbooks/website-down"

      # High response time
      - alert: HighResponseTime
        expr: probe_duration_seconds{job=~"blackbox.*"} > 5
        for: 2m
        labels:
          severity: warning
          team: platform
          alert_type: performance
        annotations:
          summary: "High response time detected"
          description: "{{ $labels.instance }} response time is {{ $value }}s"

      # SSL certificate expiring soon
      - alert: SSLCertificateExpiringSoon
        expr: |
          (probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
        for: 1h
        labels:
          severity: warning
          team: platform
          alert_type: security
        annotations:
          summary: "SSL certificate expiring soon"
          description: "SSL certificate for {{ $labels.instance }} expires in {{ $value | humanizeDuration }}"

      # SSL certificate expired
      - alert: SSLCertificateExpired
        expr: |
          probe_ssl_earliest_cert_expiry - time() <= 0
        for: 1m
        labels:
          severity: critical
          team: platform
          alert_type: security
        annotations:
          summary: "SSL certificate has expired"
          description: "SSL certificate for {{ $labels.instance }} has expired"

      # DNS resolution failure
      - alert: DNSResolutionFailure
        expr: probe_success{job="blackbox-dns"} == 0
        for: 2m
        labels:
          severity: warning
          team: platform
          alert_type: dns
        annotations:
          summary: "DNS resolution failure"
          description: "DNS resolution failed for {{ $labels.instance }}"

      # High packet loss (ICMP)
      - alert: HighPacketLoss
        expr: |
          rate(probe_icmp_duration_seconds_count{job="blackbox-icmp"}[5m]) -
          rate(probe_icmp_reply_hop_limit{job="blackbox-icmp"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          team: platform
          alert_type: network
        annotations:
          summary: "High packet loss detected"
          description: "High packet loss to {{ $labels.instance }}"
```

### 10.4 Status Page Configuration

**File: `/opt/monitoring/statuspage/config.yml`**

```yaml
# Status page configuration using Cachet or similar

name: "ResilienceAI Status"
url: "https://status.resilienceai.io"

checks:
  - name: "Main Website"
    url: "https://resilienceai.io"
    interval: 60
    timeout: 10
    expected_status: 200
    
  - name: "API"
    url: "https://api.resilienceai.io/health"
    interval: 30
    timeout: 5
    expected_status: 200
    expected_body: '{"status":"healthy"}'
    
  - name: "Web Application"
    url: "https://app.resilienceai.io"
    interval: 60
    timeout: 10
    expected_status: 200
    
  - name: "Prediction Service"
    url: "https://api.resilienceai.io/v1/health/ml"
    interval: 60
    timeout: 10
    expected_status: 200
    
  - name: "Database"
    url: "https://api.resilienceai.io/health/db"
    interval: 30
    timeout: 5
    expected_status: 200

components:
  - name: "Website"
    description: "Main marketing website"
    status: operational
    
  - name: "API"
    description: "REST API for all services"
    status: operational
    
  - name: "Web Application"
    description: "Customer dashboard and interface"
    status: operational
    
  - name: "Prediction Service"
    description: "ML model inference service"
    status: operational
    
  - name: "Database"
    description: "Primary database cluster"
    status: operational
    
  - name: "Authentication"
    description: "User authentication service"
    status: operational

incident_templates:
  investigating:
    name: "Investigating {{ component }} Issue"
    message: "We are currently investigating issues with {{ component }}. We will provide updates as more information becomes available."
    status: investigating
    
  identified:
    name: "{{ component }} Issue Identified"
    message: "We have identified the issue with {{ component }} and are working on a resolution."
    status: identified
    
  monitoring:
    name: "{{ component }} Issue Resolved - Monitoring"
    message: "We have resolved the issue with {{ component }} and are monitoring the situation."
    status: monitoring
    
  resolved:
    name: "{{ component }} Issue Resolved"
    message: "The issue with {{ component }} has been fully resolved. Thank you for your patience."
    status: resolved
```

---

## 11. Cost Monitoring

### 11.1 Cloud Cost Exporter Configuration

**File: `/opt/monitoring/cost-exporter/config.yml`**

```yaml
# Cloud cost monitoring configuration

exporters:
  # AWS Cost Explorer
  aws:
    enabled: true
    region: us-east-1
    metrics:
      - name: aws_daily_cost
        query: |
          SELECT SUM(UnblendedCost) as cost
          FROM cost_explorer
          WHERE UsageStartDate >= CURRENT_DATE - INTERVAL '1' DAY
        labels:
          - service
          - region
      
      - name: aws_monthly_cost
        query: |
          SELECT SUM(UnblendedCost) as cost
          FROM cost_explorer
          WHERE UsageStartDate >= DATE_TRUNC('month', CURRENT_DATE)
        labels:
          - service
          - region
      
      - name: aws_forecasted_cost
        query: |
          SELECT ForecastedCost
          FROM cost_forecast
          WHERE TimePeriodEnd >= DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1' MONTH)

  # GCP Billing
  gcp:
    enabled: false
    project_id: ""
    metrics:
      - name: gcp_daily_cost
        query: "daily_cost"
      
      - name: gcp_monthly_cost
        query: "monthly_cost"

  # Azure Cost Management
  azure:
    enabled: false
    subscription_id: ""
    metrics:
      - name: azure_daily_cost
        query: "daily_cost"

# Cost allocation tags
tags:
  - environment
  - service
  - team
  - project

# Budget alerts
budgets:
  - name: monthly-total
    amount: 10000
    currency: USD
    period: monthly
    alerts:
      - threshold: 50
        notification: email
      - threshold: 80
        notification: slack
      - threshold: 100
        notification: pagerduty
  
  - name: daily-compute
    amount: 500
    currency: USD
    period: daily
    filter:
      service: EC2
    alerts:
      - threshold: 100
        notification: slack

# Resource optimization recommendations
optimization:
  enabled: true
  checks:
    - name: idle_instances
      enabled: true
      threshold_hours: 24
    
    - name: oversized_instances
      enabled: true
      threshold_cpu: 20
      threshold_memory: 30
    
    - name: unattached_volumes
      enabled: true
    
    - name: unused_load_balancers
      enabled: true
      threshold_connections: 10
```

### 11.2 Cost Metrics Collection

**File: `/app/resilienceai/monitoring/cost_metrics.py`**

```python
"""
ResilienceAI Cost Monitoring and Metrics
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from prometheus_client import Counter, Gauge, Histogram, Info


# Cost metrics
COST_METRICS = {
    'api_calls_by_tier': Counter(
        'resilienceai_api_calls_by_tier_total',
        'API calls by pricing tier',
        ['tier', 'endpoint', 'method']
    ),
    'resource_usage': Gauge(
        'resilienceai_resource_usage',
        'Resource usage for cost tracking',
        ['resource_type', 'service', 'environment']
    ),
    'compute_hours': Counter(
        'resilienceai_compute_hours_total',
        'Compute hours consumed',
        ['instance_type', 'service']
    ),
    'storage_usage_bytes': Gauge(
        'resilienceai_storage_usage_bytes',
        'Storage usage in bytes',
        ['storage_type', 'service']
    ),
    'data_transfer_bytes': Counter(
        'resilienceai_data_transfer_bytes_total',
        'Data transfer in bytes',
        ['direction', 'service', 'region']
    ),
    'ml_prediction_cost': Counter(
        'resilienceai_ml_prediction_cost_total',
        'ML prediction cost in currency units',
        ['model_type', 'complexity']
    ),
    'cost_estimate': Gauge(
        'resilienceai_cost_estimate',
        'Estimated cost for current period',
        ['category', 'service']
    ),
}


@dataclass
class ResourceUsage:
    """Resource usage record"""
    timestamp: datetime
    service: str
    resource_type: str
    quantity: float
    unit: str
    cost_per_unit: float
    total_cost: float
    metadata: Dict = None


class CostTracker:
    """Track and report resource costs"""
    
    # Pricing tiers
    PRICING_TIERS = {
        'free': {'requests_per_month': 1000, 'cost_per_request': 0},
        'basic': {'requests_per_month': 10000, 'cost_per_request': 0.001},
        'pro': {'requests_per_month': 100000, 'cost_per_request': 0.0005},
        'enterprise': {'requests_per_month': float('inf'), 'cost_per_request': 0.0002}
    }
    
    # ML prediction costs
    ML_COSTS = {
        'credit_default': {'simple': 0.01, 'complex': 0.05},
        'fraud_detection': {'simple': 0.02, 'complex': 0.10},
        'risk_assessment': {'simple': 0.015, 'complex': 0.08}
    }
    
    def __init__(self):
        self.usage_records: List[ResourceUsage] = []
    
    def track_api_call(self, tier: str, endpoint: str, method: str = 'GET'):
        """Track an API call for cost calculation"""
        COST_METRICS['api_calls_by_tier'].labels(
            tier=tier,
            endpoint=endpoint,
            method=method
        ).inc()
    
    def track_prediction(self, model_type: str, complexity: str = 'simple'):
        """Track ML prediction cost"""
        cost = self.ML_COSTS.get(model_type, {}).get(complexity, 0.01)
        COST_METRICS['ml_prediction_cost'].labels(
            model_type=model_type,
            complexity=complexity
        ).inc(cost)
    
    def track_compute(self, instance_type: str, service: str, hours: float):
        """Track compute resource usage"""
        COST_METRICS['compute_hours'].labels(
            instance_type=instance_type,
            service=service
        ).inc(hours)
    
    def track_storage(self, storage_type: str, service: str, bytes_used: int):
        """Track storage usage"""
        COST_METRICS['storage_usage_bytes'].labels(
            storage_type=storage_type,
            service=service
        ).set(bytes_used)
    
    def track_data_transfer(
        self,
        direction: str,
        service: str,
        region: str,
        bytes_transferred: int
    ):
        """Track data transfer"""
        COST_METRICS['data_transfer_bytes'].labels(
            direction=direction,
            service=service,
            region=region
        ).inc(bytes_transferred)
    
    def update_resource_usage(
        self,
        resource_type: str,
        service: str,
        environment: str,
        usage_value: float
    ):
        """Update resource usage gauge"""
        COST_METRICS['resource_usage'].labels(
            resource_type=resource_type,
            service=service,
            environment=environment
        ).set(usage_value)
    
    def estimate_monthly_cost(self, category: str, service: str, estimate: float):
        """Update cost estimate"""
        COST_METRICS['cost_estimate'].labels(
            category=category,
            service=service
        ).set(estimate)
    
    def get_tier_for_usage(self, monthly_requests: int) -> str:
        """Determine pricing tier based on usage"""
        for tier, config in self.PRICING_TIERS.items():
            if monthly_requests <= config['requests_per_month']:
                return tier
        return 'enterprise'
    
    def calculate_api_cost(self, tier: str, requests: int) -> float:
        """Calculate API cost for given tier and requests"""
        config = self.PRICING_TIERS.get(tier, self.PRICING_TIERS['enterprise'])
        return requests * config['cost_per_request']


class CostAlertManager:
    """Manage cost alerts and budgets"""
    
    def __init__(self):
        self.budgets: Dict[str, Dict] = {}
        self.alerts: List[Dict] = []
    
    def set_budget(self, name: str, amount: float, period: str = 'monthly'):
        """Set a budget"""
        self.budgets[name] = {
            'amount': amount,
            'period': period,
            'spent': 0,
            'alerts_triggered': []
        }
    
    def check_budget(self, name: str, current_spend: float) -> List[Dict]:
        """Check budget and return triggered alerts"""
        if name not in self.budgets:
            return []
        
        budget = self.budgets[name]
        percentage = (current_spend / budget['amount']) * 100
        
        alerts = []
        
        if percentage >= 100 and '100' not in budget['alerts_triggered']:
            alerts.append({
                'level': 'critical',
                'message': f'Budget {name} exceeded: {percentage:.1f}%',
                'percentage': percentage
            })
            budget['alerts_triggered'].append('100')
        
        elif percentage >= 80 and '80' not in budget['alerts_triggered']:
            alerts.append({
                'level': 'warning',
                'message': f'Budget {name} at {percentage:.1f}%',
                'percentage': percentage
            })
            budget['alerts_triggered'].append('80')
        
        elif percentage >= 50 and '50' not in budget['alerts_triggered']:
            alerts.append({
                'level': 'info',
                'message': f'Budget {name} at {percentage:.1f}%',
                'percentage': percentage
            })
            budget['alerts_triggered'].append('50')
        
        return alerts
    
    def get_cost_report(self) -> Dict:
        """Generate cost report"""
        return {
            'budgets': self.budgets,
            'total_budget': sum(b['amount'] for b in self.budgets.values()),
            'total_spent': sum(b.get('spent', 0) for b in self.budgets.values()),
            'alerts': self.alerts
        }


# Usage example
"""
from resilienceai.monitoring.cost_metrics import CostTracker, CostAlertManager

# Initialize cost tracking
cost_tracker = CostTracker()
cost_alerts = CostAlertManager()

# Set budgets
cost_alerts.set_budget('monthly-api', 5000)
cost_alerts.set_budget('monthly-ml', 3000)

# Track API calls
cost_tracker.track_api_call('pro', '/api/v1/predict', 'POST')

# Track ML predictions
cost_tracker.track_prediction('credit_default', complexity='complex')

# Track resource usage
cost_tracker.track_compute('c5.xlarge', 'api', hours=24)
cost_tracker.track_storage('s3', 'backups', bytes_used=1024**4)

# Check budgets
alerts = cost_alerts.check_budget('monthly-api', current_spend=4500)
for alert in alerts:
    print(f"{alert['level']}: {alert['message']}")
"""
```

### 11.3 Cost Alert Rules

**File: `/opt/monitoring/prometheus/alerts/cost_alerts.yml`**

```yaml
groups:
  - name: cost_alerts
    rules:
      # High API cost
      - alert: HighAPICost
        expr: |
          sum(increase(resilienceai_api_calls_by_tier_total[1d])) * 0.001 > 100
        for: 1h
        labels:
          severity: warning
          team: finance
          alert_type: cost
        annotations:
          summary: "High API cost detected"
          description: "Daily API cost is approaching budget"

      # High ML prediction cost
      - alert: HighMLCost
        expr: |
          sum(increase(resilienceai_ml_prediction_cost_total[1d])) > 500
        for: 1h
        labels:
          severity: warning
          team: finance
          alert_type: cost
        annotations:
          summary: "High ML prediction cost"
          description: "Daily ML prediction cost is ${{ $value }}"

      # Unusual compute usage
      - alert: UnusualComputeUsage
        expr: |
          sum(rate(resilienceai_compute_hours_total[1d])) > 
          avg_over_time(sum(rate(resilienceai_compute_hours_total[1d]))[7d:1d]) * 2
        for: 2h
        labels:
          severity: info
          team: platform
          alert_type: cost
        annotations:
          summary: "Unusual compute usage detected"
          description: "Compute usage is 2x higher than 7-day average"

      # Storage growth rate
      - alert: RapidStorageGrowth
        expr: |
          (
            resilienceai_storage_usage_bytes / 
            resilienceai_storage_usage_bytes offset 1d
          ) > 1.5
        for: 1h
        labels:
          severity: info
          team: platform
          alert_type: cost
        annotations:
          summary: "Rapid storage growth"
          description: "Storage has grown by 50% in the last 24 hours"
```



---

## 12. Deployment Guide

### 12.1 Docker Compose Deployment

**File: `/opt/monitoring/docker-compose.yml`**

```yaml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    volumes:
      - ./alertmanager:/etc/alertmanager
      - alertmanager-data:/alertmanager
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped
    environment:
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - PAGERDUTY_SERVICE_KEY=${PAGERDUTY_SERVICE_KEY}

  # Grafana
  grafana:
    image: grafana/grafana:10.1.0
    container_name: grafana
    volumes:
      - ./grafana:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - monitoring
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=https://grafana.resilienceai.io
    restart: unless-stopped

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:v1.6.1
    container_name: node-exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped

  # Blackbox Exporter
  blackbox-exporter:
    image: prom/blackbox-exporter:v0.24.0
    container_name: blackbox-exporter
    command:
      - '--config.file=/etc/blackbox/blackbox.yml'
    volumes:
      - ./blackbox:/etc/blackbox
    ports:
      - "9115:9115"
    networks:
      - monitoring
    restart: unless-stopped

  # Jaeger
  jaeger:
    image: jaegertracing/all-in-one:1.49
    container_name: jaeger
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - monitoring
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    restart: unless-stopped

  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.87.0
    container_name: otel-collector
    command: ["--config=/etc/otel-collector-config.yml"]
    volumes:
      - ./otel:/etc/otel-collector-config.yml
    ports:
      - "4317:4317"
      - "4318:4318"
      - "8888:8888"
      - "8889:8889"
    networks:
      - monitoring
    restart: unless-stopped

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - monitoring
    restart: unless-stopped

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    container_name: logstash
    volumes:
      - ./logstash/pipelines:/usr/share/logstash/pipeline
      - ./logstash/templates:/usr/share/logstash/templates
    ports:
      - "5044:5044"
      - "5000:5000"
      - "9600:9600"
    networks:
      - monitoring
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    restart: unless-stopped

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    container_name: kibana
    ports:
      - "5601:5601"
    networks:
      - monitoring
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    restart: unless-stopped

  # Filebeat
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.10.0
    container_name: filebeat
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks:
      - monitoring
    restart: unless-stopped

  # Sentry (simplified - use official Helm chart for production)
  sentry-redis:
    image: redis:7-alpine
    container_name: sentry-redis
    volumes:
      - sentry-redis-data:/data
    networks:
      - monitoring
    restart: unless-stopped

  sentry-postgres:
    image: postgres:15-alpine
    container_name: sentry-postgres
    environment:
      - POSTGRES_USER=sentry
      - POSTGRES_PASSWORD=sentry
      - POSTGRES_DB=sentry
    volumes:
      - sentry-postgres-data:/var/lib/postgresql/data
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:
  elasticsearch-data:
  sentry-redis-data:
  sentry-postgres-data:

networks:
  monitoring:
    driver: bridge
```

### 12.2 Kubernetes Deployment

**File: `/opt/monitoring/k8s/monitoring-namespace.yml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    name: monitoring
    pod-security.kubernetes.io/enforce: privileged
```

**File: `/opt/monitoring/k8s/prometheus-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
        - name: prometheus
          image: prom/prometheus:v2.47.0
          args:
            - '--config.file=/etc/prometheus/prometheus.yml'
            - '--storage.tsdb.path=/prometheus'
            - '--storage.tsdb.retention.time=15d'
            - '--web.enable-lifecycle'
          ports:
            - containerPort: 9090
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: storage
              mountPath: /prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: storage
          persistentVolumeClaim:
            claimName: prometheus-storage
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 9090
      targetPort: 9090
  selector:
    app: prometheus
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources:
      - nodes
      - nodes/proxy
      - services
      - endpoints
      - pods
    verbs: ["get", "list", "watch"]
  - apiGroups:
      - extensions
      - networking.k8s.io
    resources:
      - ingresses
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-storage
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

**File: `/opt/monitoring/k8s/grafana-deployment.yml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:10.1.0
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          env:
            - name: GF_SECURITY_ADMIN_USER
              valueFrom:
                secretKeyRef:
                  name: grafana-credentials
                  key: admin-user
            - name: GF_SECURITY_ADMIN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: grafana-credentials
                  key: admin-password
            - name: GF_USERS_ALLOW_SIGN_UP
              value: "false"
          volumeMounts:
            - name: grafana-storage
              mountPath: /var/lib/grafana
            - name: grafana-datasources
              mountPath: /etc/grafana/provisioning/datasources
            - name: grafana-dashboards
              mountPath: /etc/grafana/provisioning/dashboards
      volumes:
        - name: grafana-storage
          persistentVolumeClaim:
            claimName: grafana-storage
        - name: grafana-datasources
          configMap:
            name: grafana-datasources
        - name: grafana-dashboards
          configMap:
            name: grafana-dashboards
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: grafana
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana
  namespace: monitoring
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - grafana.resilienceai.io
      secretName: grafana-tls
  rules:
    - host: grafana.resilienceai.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: grafana
                port:
                  number: 3000
```

### 12.3 Helm Chart Deployment

**File: `/opt/monitoring/helm/Chart.yaml`**

```yaml
apiVersion: v2
name: resilienceai-monitoring
description: ResilienceAI Monitoring Stack
type: application
version: 1.0.0
appVersion: "1.0.0"
dependencies:
  - name: prometheus
    version: 25.0.0
    repository: https://prometheus-community.github.io/helm-charts
    condition: prometheus.enabled
  
  - name: grafana
    version: 6.60.0
    repository: https://grafana.github.io/helm-charts
    condition: grafana.enabled
  
  - name: jaeger
    version: 0.71.0
    repository: https://jaegertracing.github.io/helm-charts
    condition: jaeger.enabled
  
  - name: elasticsearch
    version: 19.13.0
    repository: https://charts.bitnami.com/bitnami
    condition: elasticsearch.enabled
  
  - name: kube-prometheus-stack
    version: 51.0.0
    repository: https://prometheus-community.github.io/helm-charts
    condition: kube-prometheus-stack.enabled
```

**File: `/opt/monitoring/helm/values.yaml`**

```yaml
# Default values for resilienceai-monitoring

prometheus:
  enabled: true
  server:
    persistentVolume:
      enabled: true
      size: 50Gi
    retention: "15d"
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 2Gi
        cpu: 1000m
  
  alertmanager:
    enabled: true
    persistence:
      enabled: true
      size: 10Gi
  
  nodeExporter:
    enabled: true
  
  pushgateway:
    enabled: false

grafana:
  enabled: true
  persistence:
    enabled: true
    size: 10Gi
  
  admin:
    existingSecret: grafana-credentials
    userKey: admin-user
    passwordKey: admin-password
  
  ingress:
    enabled: true
    hosts:
      - grafana.resilienceai.io
    tls:
      - secretName: grafana-tls
        hosts:
          - grafana.resilienceai.io
  
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          url: http://prometheus-server.monitoring.svc.cluster.local
          access: proxy
          isDefault: true
        
        - name: Jaeger
          type: jaeger
          url: http://jaeger-query.monitoring.svc.cluster.local:16686
          access: proxy
        
        - name: Elasticsearch
          type: elasticsearch
          url: http://elasticsearch.monitoring.svc.cluster.local:9200
          access: proxy
          database: "resilienceai-*"
  
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
        - name: 'default'
          orgId: 1
          folder: ''
          type: file
          disableDeletion: false
          editable: true
          options:
            path: /var/lib/grafana/dashboards/default
  
  dashboards:
    default:
      resilienceai-main:
        url: https://raw.githubusercontent.com/resilienceai/monitoring/main/dashboards/main.json
      resilienceai-slo:
        url: https://raw.githubusercontent.com/resilienceai/monitoring/main/dashboards/slo.json

jaeger:
  enabled: true
  storage:
    type: elasticsearch
    elasticsearch:
      serverUrls: http://elasticsearch.monitoring.svc.cluster.local:9200
  
  agent:
    enabled: true
  
  collector:
    enabled: true
    service:
      zipkin:
        port: 9411

elasticsearch:
  enabled: true
  master:
    replicas: 1
    persistence:
      enabled: true
      size: 30Gi
  
  data:
    replicas: 1
    persistence:
      enabled: true
      size: 50Gi
  
  coordinating:
    replicas: 1
  
  ingest:
    enabled: false

kube-prometheus-stack:
  enabled: true
  
  prometheus:
    prometheusSpec:
      retention: 15d
      storageSpec:
        volumeClaimTemplate:
          spec:
            resources:
              requests:
                storage: 50Gi
  
  alertmanager:
    enabled: true
    config:
      global:
        resolve_timeout: 5m
        slack_api_url: '${SLACK_WEBHOOK_URL}'
      route:
        receiver: 'default'
        routes:
          - match:
              severity: critical
            receiver: 'critical'
      receivers:
        - name: 'default'
          slack_configs:
            - channel: '#alerts'
        - name: 'critical'
          slack_configs:
            - channel: '#critical-alerts'
          pagerduty_configs:
            - service_key: '${PAGERDUTY_KEY}'
```

### 12.4 Deployment Scripts

**File: `/opt/monitoring/deploy.sh`**

```bash
#!/bin/bash
set -e

# ResilienceAI Monitoring Stack Deployment Script

ENVIRONMENT=${1:-production}
NAMESPACE="monitoring"
echo "Deploying ResilienceAI Monitoring Stack to ${ENVIRONMENT}..."

# Create namespace
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Create secrets
echo "Creating secrets..."
kubectl create secret generic grafana-credentials \
  --from-literal=admin-user=admin \
  --from-literal=admin-password=$(openssl rand -base64 20) \
  -n ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic alertmanager-credentials \
  --from-literal=slack-webhook-url="${SLACK_WEBHOOK_URL}" \
  --from-literal=pagerduty-key="${PAGERDUTY_KEY}" \
  -n ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy Prometheus
echo "Deploying Prometheus..."
kubectl apply -f k8s/prometheus-deployment.yml -n ${NAMESPACE}

# Deploy Grafana
echo "Deploying Grafana..."
kubectl apply -f k8s/grafana-deployment.yml -n ${NAMESPACE}

# Deploy Alertmanager
echo "Deploying Alertmanager..."
kubectl apply -f k8s/alertmanager-deployment.yml -n ${NAMESPACE}

# Deploy Jaeger
echo "Deploying Jaeger..."
kubectl apply -f k8s/jaeger-deployment.yml -n ${NAMESPACE}

# Deploy ELK Stack
echo "Deploying ELK Stack..."
kubectl apply -f k8s/elasticsearch-deployment.yml -n ${NAMESPACE}
kubectl apply -f k8s/logstash-deployment.yml -n ${NAMESPACE}
kubectl apply -f k8s/kibana-deployment.yml -n ${NAMESPACE}

# Wait for deployments
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/prometheus -n ${NAMESPACE}
kubectl rollout status deployment/grafana -n ${NAMESPACE}
kubectl rollout status deployment/alertmanager -n ${NAMESPACE}

# Apply Prometheus rules
echo "Applying Prometheus rules..."
kubectl create configmap prometheus-rules \
  --from-file=prometheus/rules/ \
  -n ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Apply Grafana dashboards
echo "Applying Grafana dashboards..."
kubectl create configmap grafana-dashboards \
  --from-file=grafana/dashboards/ \
  -n ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

echo "Deployment complete!"
echo ""
echo "Access URLs:"
echo "  Grafana: https://grafana.resilienceai.io"
echo "  Prometheus: https://prometheus.resilienceai.io"
echo "  Alertmanager: https://alertmanager.resilienceai.io"
echo "  Jaeger: https://jaeger.resilienceai.io"
echo "  Kibana: https://kibana.resilienceai.io"
```

---

## 13. Implementation Priority

### 13.1 Phase 1: Foundation (Week 1-2) - CRITICAL

| Component | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| Prometheus Server | P0 | 2 days | None |
| Node Exporter | P0 | 1 day | Prometheus |
| Application Metrics | P0 | 3 days | Prometheus |
| Basic Grafana Dashboards | P0 | 2 days | Prometheus |
| Core Alerting Rules | P0 | 2 days | Prometheus |
| Alertmanager | P0 | 1 day | Alerting Rules |

**Deliverables:**
- System metrics collection
- Application metrics (HTTP requests, errors, latency)
- Basic dashboards (System, API overview)
- Critical alerts (service down, high error rate)
- Slack notifications

### 13.2 Phase 2: Observability (Week 3-4) - HIGH

| Component | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| Distributed Tracing (Jaeger) | P1 | 3 days | Application instrumentation |
| Centralized Logging (ELK) | P1 | 4 days | Filebeat, Logstash |
| Error Tracking (Sentry) | P1 | 2 days | Application SDK |
| Advanced Dashboards | P1 | 3 days | All metrics sources |
| SLO Definitions | P1 | 2 days | Metrics baseline |

**Deliverables:**
- Request tracing across services
- Centralized log aggregation
- Error tracking and reporting
- Business metrics dashboards
- Initial SLO definitions

### 13.3 Phase 3: Advanced Monitoring (Week 5-6) - MEDIUM

| Component | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| SLO Alerting | P2 | 2 days | SLO definitions |
| Performance Monitoring | P2 | 3 days | Application instrumentation |
| Uptime Monitoring (Blackbox) | P2 | 1 day | External endpoints |
| Cost Monitoring | P2 | 3 days | Cloud provider APIs |
| Custom Business Metrics | P2 | 2 days | Application changes |

**Deliverables:**
- SLO-based alerting
- Performance profiling
- External endpoint monitoring
- Cost tracking and alerts
- ML model performance metrics

### 13.4 Phase 4: Optimization (Week 7-8) - LOW

| Component | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| Long-term Storage (Thanos) | P3 | 3 days | Prometheus |
| Advanced Analytics | P3 | 4 days | All data sources |
| Automated Runbooks | P3 | 3 days | Alerting maturity |
| Capacity Planning | P3 | 2 days | Historical data |
| ML-based Anomaly Detection | P3 | 5 days | Sufficient data |

**Deliverables:**
- Historical metric retention
- Predictive analytics
- Automated incident response
- Resource optimization recommendations

### 13.5 Implementation Checklist

```markdown
## Phase 1: Foundation
- [ ] Deploy Prometheus server
- [ ] Configure Prometheus scraping
- [ ] Deploy Node Exporter
- [ ] Instrument application with Prometheus client
- [ ] Create basic HTTP metrics middleware
- [ ] Deploy Grafana
- [ ] Create main system dashboard
- [ ] Create API overview dashboard
- [ ] Configure Alertmanager
- [ ] Create critical alert rules
- [ ] Configure Slack notifications
- [ ] Test alert flow end-to-end

## Phase 2: Observability
- [ ] Deploy Jaeger
- [ ] Instrument application with OpenTelemetry
- [ ] Configure distributed tracing
- [ ] Deploy Elasticsearch
- [ ] Deploy Logstash
- [ ] Deploy Kibana
- [ ] Configure Filebeat
- [ ] Set up log parsing pipelines
- [ ] Deploy Sentry
- [ ] Configure Sentry SDK
- [ ] Create error tracking dashboards
- [ ] Define initial SLOs

## Phase 3: Advanced Monitoring
- [ ] Implement SLO alerting
- [ ] Deploy Blackbox Exporter
- [ ] Configure uptime monitoring
- [ ] Implement performance profiling
- [ ] Set up cost tracking
- [ ] Create cost dashboards
- [ ] Add ML model metrics
- [ ] Create business metrics dashboards

## Phase 4: Optimization
- [ ] Deploy Thanos for long-term storage
- [ ] Implement capacity planning
- [ ] Create automated runbooks
- [ ] Set up anomaly detection
- [ ] Implement predictive alerting
- [ ] Create executive dashboards
```

---

## 14. Summary

This comprehensive monitoring and observability design for ResilienceAI includes:

### Core Components
1. **Prometheus** - Metrics collection and alerting
2. **Grafana** - Visualization and dashboards
3. **Jaeger** - Distributed tracing
4. **ELK Stack** - Centralized logging
5. **Sentry** - Error tracking
6. **Alertmanager** - Alert routing and notifications

### Key Features
- **SLO-based monitoring** with error budgets
- **Multi-layered alerting** (critical, warning, info)
- **Full observability** (metrics, logs, traces)
- **Business metrics** tracking
- **Cost monitoring** and optimization
- **Automated deployment** with Kubernetes/Helm

### File Locations
All configuration files are organized under `/opt/monitoring/`:
- `prometheus/` - Prometheus configuration
- `grafana/` - Grafana dashboards and datasources
- `alertmanager/` - Alertmanager configuration
- `jaeger/` - Jaeger deployment
- `otel/` - OpenTelemetry configuration
- `elk/` - ELK stack configuration
- `sentry/` - Sentry deployment
- `k8s/` - Kubernetes manifests
- `helm/` - Helm charts

---

*Document Version: 1.0*
*Last Updated: 2024-01-15*
*Owner: Platform Team*
