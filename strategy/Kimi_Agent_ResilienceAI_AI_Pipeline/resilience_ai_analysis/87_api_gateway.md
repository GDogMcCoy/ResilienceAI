# ResilienceAI Comprehensive API Gateway Design

## Executive Summary

This document provides a comprehensive API gateway architecture for ResilienceAI, implementing enterprise-grade API management capabilities including request routing, load balancing, authentication, rate limiting, caching, transformation, logging, versioning, and developer portal. The design supports high availability, horizontal scalability, and multi-tenant deployments.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Gateway Components](#gateway-components)
3. [Request Routing](#request-routing)
4. [Load Balancing](#load-balancing)
5. [Authentication & Authorization](#authentication--authorization)
6. [Rate Limiting](#rate-limiting)
7. [Caching Layer](#caching-layer)
8. [Request/Response Transformation](#requestresponse-transformation)
9. [Logging & Monitoring](#logging--monitoring)
10. [API Versioning](#api-versioning)
11. [Developer Portal](#developer-portal)
12. [Implementation Code](#implementation-code)
13. [Deployment Configuration](#deployment-configuration)
14. [Integration Approach](#integration-approach)
15. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              RESILIENCEAI API GATEWAY ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              EDGE LAYER (CDN/WAF)                                    │   │
│  │                    CloudFlare / AWS CloudFront / Azure Front Door                     │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                                  │
│                                           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           API GATEWAY CLUSTER (Kong/AWS/Azure)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │   Gateway   │  │   Gateway   │  │   Gateway   │  │   Gateway   │  │  Health   │ │   │
│  │  │   Node 1    │  │   Node 2    │  │   Node 3    │  │   Node N    │  │  Checker  │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘ │   │
│  │         └─────────────────┴─────────────────┴─────────────────┘               │       │   │
│  │                              │                                                │       │   │
│  │                    ┌─────────┴─────────┐                                      │       │   │
│  │                    │  Load Balancer    │                                      │       │   │
│  │                    │  (Nginx/Envoy)    │                                      │       │   │
│  │                    └─────────┬─────────┘                                      │       │   │
│  └──────────────────────────────┼────────────────────────────────────────────────┘       │   │
│                                 │                                                         │
│  ┌──────────────────────────────┼────────────────────────────────────────────────────────┘   │
│  │                    CORE GATEWAY SERVICES                                                  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  │   Router     │  │   Rate       │  │    Auth      │  │   Cache      │  │ Transform │  │
│  │  │   Engine     │  │   Limiter    │  │   Handler    │  │   Manager    │  │  Engine   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  │   Circuit    │  │   Load       │  │   Logger     │  │   Metrics    │  │  Version  │  │
│  │  │   Breaker    │  │   Balancer   │  │   Service    │  │   Collector  │  │  Manager  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘
│                                           │
│                                           ▼
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐
│  │                         BACKEND SERVICE MESH                                        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  │  Analytics  │  │   Agent     │  │   Data      │  │    ML       │  │  Report   │ │
│  │  │   Service   │  │   Service   │  │   Service   │  │  Service    │  │  Service  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  │  Geospatial │  │   Alert     │  │  Scenario   │  │   Export    │  │  Search   │ │
│  │  │   Service   │  │   Service   │  │   Service   │  │  Service    │  │  Service  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Request Flow:
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Client  │───▶│   CDN   │───▶│  WAF    │───▶│ Gateway │───▶│ Routing │───▶│  Auth   │
│ Request │    │ (Cache) │    │ (Sec)   │    │ (LB)    │    │ (Match) │    │ (JWT)   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └────┬────┘
                                                                                  │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│ Backend │◀───│ Service │◀───│ Circuit │◀───│  Rate   │◀───│  Cache  │◀────────┘
│ Service │    │  Mesh   │    │ Breaker │    │  Limit  │    │  Check  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │
     ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│Transform│───▶│  Cache  │───▶│  Log    │───▶│ Metrics │───▶│ Client  │
│Response │    │  Store  │    │  Event  │    │ Record  │    │Response │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## Gateway Components

### Core Components Table

| Component | Technology | Purpose | Scaling |
|-----------|------------|---------|---------|
| API Gateway | Kong/AWS API Gateway/Azure APIM | Request routing & management | Horizontal |
| Load Balancer | Nginx/Envoy/HAProxy | Traffic distribution | Active-Active |
| Auth Service | OAuth2/JWT/Keycloak | Authentication & authorization | Horizontal |
| Rate Limiter | Redis + Lua | Traffic control | Distributed |
| Cache Layer | Redis Cluster | Response caching | Clustered |
| Circuit Breaker | Custom/Hystrix | Failure isolation | Per-instance |
| Logger | Fluentd/Logstash | Log aggregation | Sharded |
| Metrics | Prometheus/Grafana | Monitoring & alerting | Federated |

---

## Request Routing

### Routing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REQUEST ROUTING ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         Route Matcher                                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Path      │  │   Method    │  │   Host      │  │   Header    │  │ │
│  │  │   Match     │  │   Match     │  │   Match     │  │   Match     │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Route Configuration                               │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Route: /api/v1/analytics/*                                      │  │ │
│  │  │  ├── Methods: GET, POST                                          │  │ │
│  │  │  ├── Upstream: analytics-service                                 │  │ │
│  │  │  ├── Plugins: [auth, rate-limit, cache]                          │  │ │
│  │  │  └── Priority: 100                                               │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Route: /api/v1/agents/{id}/execute                            │  │ │
│  │  │  ├── Methods: POST                                               │  │ │
│  │  │  ├── Upstream: agent-service                                     │  │ │
│  │  │  ├── Plugins: [auth, rate-limit]                                 │  │ │
│  │  │  └── Priority: 200                                               │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Routing Configuration (Kong)

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/kong-routes.yaml

_format_version: "3.0"

services:
  # Analytics Service
  - name: analytics-service
    url: http://analytics-service:8080
    routes:
      - name: analytics-routes
        paths:
          - /api/v1/analytics
        methods:
          - GET
          - POST
        strip_path: false
        preserve_host: false
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: redis
          redis_host: redis-cluster
      - name: jwt
        config:
          uri_param_names: []
          cookie_names: []
          key_claim_name: iss
          secret_is_base64: false
          claims_to_verify:
            - exp
      - name: proxy-cache
        config:
          response_code:
            - 200
          request_method:
            - GET
          content_type:
            - application/json
          cache_ttl: 300
          strategy: redis
          redis_host: redis-cluster

  # Agent Service
  - name: agent-service
    url: http://agent-service:8081
    routes:
      - name: agent-routes
        paths:
          - /api/v1/agents
        methods:
          - GET
          - POST
          - PUT
          - DELETE
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 50
          policy: redis
      - name: jwt
      - name: request-transformer
        config:
          add:
            headers:
              - X-Request-ID:$(request_id)
              - X-Service-Name:agent-service

  # Data Service
  - name: data-service
    url: http://data-service:8082
    routes:
      - name: data-routes
        paths:
          - /api/v1/data
          - /api/v1/datasets
          - /api/v1/sources
        methods:
          - GET
          - POST
          - PUT
          - DELETE
    plugins:
      - name: rate-limiting
        config:
          minute: 200
      - name: jwt
      - name: cors
        config:
          origins:
            - "https://resilienceai.io"
            - "https://app.resilienceai.io"
          methods:
            - GET
            - POST
            - PUT
            - DELETE
          headers:
            - Authorization
            - Content-Type
          max_age: 3600

  # ML Service
  - name: ml-service
    url: http://ml-service:8083
    routes:
      - name: ml-routes
        paths:
          - /api/v1/ml
          - /api/v1/predictions
          - /api/v1/models
        methods:
          - GET
          - POST
    plugins:
      - name: rate-limiting
        config:
          minute: 30
      - name: jwt
      - name: request-size-limiting
        config:
          allowed_payload_size: 10
          require_content_length: true

  # Geospatial Service
  - name: geospatial-service
    url: http://geospatial-service:8084
    routes:
      - name: geospatial-routes
        paths:
          - /api/v1/geo
          - /api/v1/maps
          - /api/v1/spatial
        methods:
          - GET
          - POST
    plugins:
      - name: rate-limiting
        config:
          minute: 150
      - name: jwt
      - name: proxy-cache
        config:
          cache_ttl: 600

  # Report Service
  - name: report-service
    url: http://report-service:8085
    routes:
      - name: report-routes
        paths:
          - /api/v1/reports
          - /api/v1/exports
        methods:
          - GET
          - POST
    plugins:
      - name: rate-limiting
        config:
          minute: 20
      - name: jwt
      - name: request-termination
        config:
          status_code: 503
          message: "Report generation temporarily unavailable"
        enabled: false  # Enable during maintenance

  # Health Check Endpoint (No Auth)
  - name: health-service
    url: http://gateway-health:8089
    routes:
      - name: health-routes
        paths:
          - /health
          - /ready
          - /alive
        methods:
          - GET
    plugins: []  # No plugins for health checks

  # Developer Portal (Public)
  - name: developer-portal
    url: http://developer-portal:8090
    routes:
      - name: portal-routes
        paths:
          - /docs
          - /api-docs
          - /swagger
        methods:
          - GET
    plugins:
      - name: rate-limiting
        config:
          minute: 1000
```

### Dynamic Router Implementation (Python)

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/router.py
"""
Dynamic Request Router for ResilienceAI API Gateway
Provides path-based, header-based, and query-based routing
"""

from typing import Dict, List, Optional, Callable, Any, Pattern
from dataclasses import dataclass, field
from enum import Enum, auto
import re
import fnmatch
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class RouteMatchType(Enum):
    """Types of route matching"""
    EXACT = auto()
    PREFIX = auto()
    REGEX = auto()
    GLOB = auto()
    PARAMETERIZED = auto()


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RouteCondition:
    """Route matching condition"""
    type: RouteMatchType
    pattern: str
    case_sensitive: bool = True
    _compiled_pattern: Optional[Pattern] = field(default=None, repr=False)
    
    def __post_init__(self):
        if self.type == RouteMatchType.REGEX:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            self._compiled_pattern = re.compile(self.pattern, flags)
    
    def matches(self, value: str) -> bool:
        """Check if value matches condition"""
        if not self.case_sensitive:
            value = value.lower()
            pattern = self.pattern.lower()
        else:
            pattern = self.pattern
            
        if self.type == RouteMatchType.EXACT:
            return value == pattern
        elif self.type == RouteMatchType.PREFIX:
            return value.startswith(pattern)
        elif self.type == RouteMatchType.REGEX:
            return bool(self._compiled_pattern.match(value))
        elif self.type == RouteMatchType.GLOB:
            return fnmatch.fnmatch(value, pattern)
        elif self.type == RouteMatchType.PARAMETERIZED:
            return self._match_parameterized(value, pattern)
        return False
    
    def _match_parameterized(self, value: str, pattern: str) -> bool:
        """Match parameterized paths like /users/{id}/posts"""
        # Convert pattern to regex
        regex_pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', pattern)
        regex_pattern = f"^{regex_pattern}$"
        return bool(re.match(regex_pattern, value))
    
    def extract_params(self, value: str) -> Dict[str, str]:
        """Extract parameters from parameterized path"""
        if self.type != RouteMatchType.PARAMETERIZED:
            return {}
        
        regex_pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', self.pattern)
        match = re.match(f"^{regex_pattern}$", value)
        return match.groupdict() if match else {}


@dataclass
class Route:
    """API Route definition"""
    id: str
    name: str
    path_conditions: List[RouteCondition]
    method_conditions: List[HTTPMethod]
    host_conditions: Optional[List[str]] = None
    header_conditions: Optional[Dict[str, RouteCondition]] = None
    query_conditions: Optional[Dict[str, RouteCondition]] = None
    upstream: str = ""
    upstream_service: str = ""
    strip_path: bool = False
    preserve_host: bool = False
    plugins: List[str] = field(default_factory=list)
    priority: int = 100
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def matches(self, request: 'GatewayRequest') -> tuple[bool, Dict[str, Any]]:
        """
        Check if route matches request
        Returns: (matches, match_context)
        """
        context = {"params": {}, "headers": {}, "query": {}}
        
        # Check path match
        path_matched = False
        for condition in self.path_conditions:
            if condition.matches(request.path):
                path_matched = True
                context["params"].update(condition.extract_params(request.path))
                break
        
        if not path_matched:
            return False, context
        
        # Check method match
        if self.method_conditions:
            if request.method not in [m.value for m in self.method_conditions]:
                return False, context
        
        # Check host match
        if self.host_conditions:
            if request.host not in self.host_conditions:
                return False, context
        
        # Check header conditions
        if self.header_conditions:
            for header_name, condition in self.header_conditions.items():
                header_value = request.headers.get(header_name, "")
                if not condition.matches(header_value):
                    return False, context
                context["headers"][header_name] = header_value
        
        # Check query conditions
        if self.query_conditions:
            for param_name, condition in self.query_conditions.items():
                param_value = request.query_params.get(param_name, "")
                if not condition.matches(param_value):
                    return False, context
                context["query"][param_name] = param_value
        
        return True, context


@dataclass
class GatewayRequest:
    """Incoming gateway request"""
    method: str
    path: str
    host: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[bytes] = None
    client_ip: str = ""
    request_id: str = ""
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            import time
            self.timestamp = time.time()


class RouterEngine:
    """
    High-performance routing engine with caching
    """
    
    def __init__(self):
        self.routes: List[Route] = []
        self._route_cache: Dict[str, tuple[Optional[Route], Dict[str, Any]]] = {}
        self._cache_enabled = True
        self._cache_size = 10000
        
    def add_route(self, route: Route) -> None:
        """Add a route to the engine"""
        self.routes.append(route)
        # Sort by priority (higher first)
        self.routes.sort(key=lambda r: r.priority, reverse=True)
        self._clear_cache()
        logger.info(f"Added route: {route.name} (priority: {route.priority})")
    
    def remove_route(self, route_id: str) -> bool:
        """Remove a route by ID"""
        for i, route in enumerate(self.routes):
            if route.id == route_id:
                self.routes.pop(i)
                self._clear_cache()
                logger.info(f"Removed route: {route_id}")
                return True
        return False
    
    def find_route(self, request: GatewayRequest) -> tuple[Optional[Route], Dict[str, Any]]:
        """
        Find matching route for request
        Returns: (route, match_context)
        """
        # Check cache
        cache_key = self._get_cache_key(request)
        if self._cache_enabled and cache_key in self._route_cache:
            return self._route_cache[cache_key]
        
        # Find matching route
        for route in self.routes:
            if not route.enabled:
                continue
                
            matches, context = route.matches(request)
            if matches:
                # Cache result
                if self._cache_enabled:
                    self._cache_route(cache_key, route, context)
                return route, context
        
        # No match found
        if self._cache_enabled:
            self._cache_route(cache_key, None, {})
        return None, {}
    
    def _get_cache_key(self, request: GatewayRequest) -> str:
        """Generate cache key for request"""
        return f"{request.method}:{request.path}:{request.host}"
    
    def _cache_route(self, key: str, route: Optional[Route], context: Dict[str, Any]) -> None:
        """Cache route lookup result"""
        if len(self._route_cache) >= self._cache_size:
            # Simple LRU: remove oldest entries
            self._route_cache.clear()
        self._route_cache[key] = (route, context)
    
    def _clear_cache(self) -> None:
        """Clear route cache"""
        self._route_cache.clear()
    
    def get_routes_by_service(self, service_name: str) -> List[Route]:
        """Get all routes for a service"""
        return [r for r in self.routes if r.upstream_service == service_name]
    
    def get_route_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "total_routes": len(self.routes),
            "enabled_routes": sum(1 for r in self.routes if r.enabled),
            "cache_size": len(self._route_cache),
            "cache_enabled": self._cache_enabled,
            "services": list(set(r.upstream_service for r in self.routes if r.upstream_service))
        }


# Predefined route configurations for ResilienceAI
ROUTES_CONFIG = [
    Route(
        id="analytics-list",
        name="Analytics List",
        path_conditions=[RouteCondition(RouteMatchType.PREFIX, "/api/v1/analytics")],
        method_conditions=[HTTPMethod.GET],
        upstream="http://analytics-service:8080",
        upstream_service="analytics",
        plugins=["auth", "rate-limit", "cache"],
        priority=100
    ),
    Route(
        id="analytics-create",
        name="Analytics Create",
        path_conditions=[RouteCondition(RouteMatchType.EXACT, "/api/v1/analytics")],
        method_conditions=[HTTPMethod.POST],
        upstream="http://analytics-service:8080",
        upstream_service="analytics",
        plugins=["auth", "rate-limit"],
        priority=110
    ),
    Route(
        id="agent-execute",
        name="Agent Execute",
        path_conditions=[RouteCondition(RouteMatchType.PARAMETERIZED, "/api/v1/agents/{id}/execute")],
        method_conditions=[HTTPMethod.POST],
        upstream="http://agent-service:8081",
        upstream_service="agent",
        plugins=["auth", "rate-limit"],
        priority=200
    ),
    Route(
        id="agent-crud",
        name="Agent CRUD",
        path_conditions=[RouteCondition(RouteMatchType.PARAMETERIZED, "/api/v1/agents/{id}")],
        method_conditions=[HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE],
        upstream="http://agent-service:8081",
        upstream_service="agent",
        plugins=["auth", "rate-limit"],
        priority=150
    ),
    Route(
        id="data-query",
        name="Data Query",
        path_conditions=[RouteCondition(RouteMatchType.PREFIX, "/api/v1/data/query")],
        method_conditions=[HTTPMethod.POST],
        upstream="http://data-service:8082",
        upstream_service="data",
        plugins=["auth", "rate-limit", "cache"],
        priority=100
    ),
    Route(
        id="ml-predict",
        name="ML Prediction",
        path_conditions=[RouteCondition(RouteMatchType.PREFIX, "/api/v1/ml/predict")],
        method_conditions=[HTTPMethod.POST],
        upstream="http://ml-service:8083",
        upstream_service="ml",
        plugins=["auth", "rate-limit"],
        priority=100
    ),
    Route(
        id="geo-spatial",
        name="Geospatial Query",
        path_conditions=[RouteCondition(RouteMatchType.PREFIX, "/api/v1/geo")],
        method_conditions=[HTTPMethod.GET, HTTPMethod.POST],
        upstream="http://geospatial-service:8084",
        upstream_service="geospatial",
        plugins=["auth", "rate-limit", "cache"],
        priority=100
    ),
    Route(
        id="health-check",
        name="Health Check",
        path_conditions=[RouteCondition(RouteMatchType.EXACT, "/health")],
        method_conditions=[HTTPMethod.GET],
        upstream="http://gateway-health:8089",
        upstream_service="health",
        plugins=[],
        priority=1000
    ),
]


def create_router() -> RouterEngine:
    """Factory function to create configured router"""
    router = RouterEngine()
    for route_config in ROUTES_CONFIG:
        router.add_route(route_config)
    return router
```

---

## Load Balancing

### Load Balancing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LOAD BALANCING LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         Load Balancer                                  │ │
│  │                    (Nginx/Envoy/HAProxy)                               │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Round     │  │   Least     │  │    IP       │  │   Weighted  │  │ │
│  │  │   Robin     │  │ Connections │  │   Hash      │  │   Round     │  │ │
│  │  │             │  │             │  │             │  │   Robin     │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│  ┌──────▼──────┐          ┌────────▼────────┐        ┌────────▼────────┐   │
│  │   Upstream  │          │    Upstream     │        │    Upstream     │   │
│  │   Pool 1    │          │    Pool 2       │        │    Pool 3       │   │
│  │             │          │                 │        │                 │   │
│  │ ┌─────────┐ │          │ ┌─────────┐     │        │ ┌─────────┐     │   │
│  │ │Instance │ │          │ │Instance │     │        │ │Instance │     │   │
│  │ │  1A     │ │          │ │  2A     │     │        │ │  3A     │     │   │
│  │ │(Healthy)│ │          │ │(Healthy)│     │        │ │(Healthy)│     │   │
│  │ └─────────┘ │          │ └─────────┘     │        │ └─────────┘     │   │
│  │ ┌─────────┐ │          │ ┌─────────┐     │        │ ┌─────────┐     │   │
│  │ │Instance │ │          │ │Instance │     │        │ │Instance │     │   │
│  │ │  1B     │ │          │ │  2B     │     │        │ │  3B     │     │   │
│  │ │(Healthy)│ │          │ │(Unhealthy)│   │        │ │(Healthy)│     │   │
│  │ └─────────┘ │          │ └─────────┘     │        │ └─────────┘     │   │
│  │ ┌─────────┐ │          │                 │        │ ┌─────────┐     │   │
│  │ │Instance │ │          │                 │        │ │Instance │     │   │
│  │ │  1C     │ │          │                 │        │ │  3C     │     │   │
│  │ │(Healthy)│ │          │                 │        │ │(Healthy)│     │   │
│  │ └─────────┘ │          │                 │        │ └─────────┘     │   │
│  └─────────────┘          └─────────────────┘        └─────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Load Balancer Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/load_balancer.py
"""
Load Balancer for ResilienceAI API Gateway
Supports multiple algorithms: Round Robin, Least Connections, IP Hash, Weighted
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import hashlib
import random
import time
import threading
import logging
from collections import deque

logger = logging.getLogger(__name__)


class LoadBalanceAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = auto()
    WEIGHTED_ROUND_ROBIN = auto()
    LEAST_CONNECTIONS = auto()
    IP_HASH = auto()
    RANDOM = auto()
    LATENCY_BASED = auto()


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    enabled: bool = True
    interval_seconds: float = 10.0
    timeout_seconds: float = 5.0
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    path: str = "/health"
    expected_status: int = 200


@dataclass
class BackendInstance:
    """Backend service instance"""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        return self.health_status == HealthStatus.HEALTHY
    
    def record_request_start(self):
        """Record request start"""
        self.current_connections += 1
        self.total_requests += 1
    
    def record_request_end(self, success: bool, response_time_ms: float):
        """Record request completion"""
        self.current_connections = max(0, self.current_connections - 1)
        
        if not success:
            self.failed_requests += 1
        
        # Update average response time (exponential moving average)
        alpha = 0.2
        self.avg_response_time_ms = (
            alpha * response_time_ms + (1 - alpha) * self.avg_response_time_ms
        )


@dataclass
class UpstreamPool:
    """Upstream backend pool"""
    name: str
    algorithm: LoadBalanceAlgorithm
    instances: List[BackendInstance]
    health_check: HealthCheckConfig
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: float = 0.5  # Failure rate threshold


class LoadBalancer:
    """
    Advanced load balancer with health checking and multiple algorithms
    """
    
    def __init__(self):
        self.pools: Dict[str, UpstreamPool] = {}
        self._round_robin_indices: Dict[str, int] = {}
        self._weighted_indices: Dict[str, deque] = {}
        self._health_check_threads: Dict[str, threading.Thread] = {}
        self._shutdown = False
        self._lock = threading.RLock()
        
    def register_pool(self, pool: UpstreamPool) -> None:
        """Register an upstream pool"""
        with self._lock:
            self.pools[pool.name] = pool
            self._round_robin_indices[pool.name] = 0
            self._init_weighted_indices(pool)
            
            if pool.health_check.enabled:
                self._start_health_checks(pool)
        
        logger.info(f"Registered upstream pool: {pool.name} "
                   f"({len(pool.instances)} instances, {pool.algorithm.name})")
    
    def _init_weighted_indices(self, pool: UpstreamPool) -> None:
        """Initialize weighted round robin indices"""
        indices = deque()
        for instance in pool.instances:
            for _ in range(instance.weight):
                indices.append(instance.id)
        self._weighted_indices[pool.name] = indices
    
    def get_backend(self, pool_name: str, client_ip: str = "") -> Optional[BackendInstance]:
        """
        Select a backend instance from pool
        
        Args:
            pool_name: Name of the upstream pool
            client_ip: Client IP for IP hash algorithm
            
        Returns:
            Selected backend instance or None
        """
        with self._lock:
            pool = self.pools.get(pool_name)
            if not pool:
                logger.error(f"Pool not found: {pool_name}")
                return None
            
            # Filter healthy instances
            healthy_instances = [i for i in pool.instances if i.is_healthy]
            if not healthy_instances:
                logger.warning(f"No healthy instances in pool: {pool_name}")
                return None
            
            # Apply load balancing algorithm
            if pool.algorithm == LoadBalanceAlgorithm.ROUND_ROBIN:
                return self._round_robin(pool_name, healthy_instances)
            elif pool.algorithm == LoadBalanceAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin(pool_name, healthy_instances)
            elif pool.algorithm == LoadBalanceAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections(healthy_instances)
            elif pool.algorithm == LoadBalanceAlgorithm.IP_HASH:
                return self._ip_hash(healthy_instances, client_ip)
            elif pool.algorithm == LoadBalanceAlgorithm.RANDOM:
                return self._random_select(healthy_instances)
            elif pool.algorithm == LoadBalanceAlgorithm.LATENCY_BASED:
                return self._latency_based(healthy_instances)
            
            return healthy_instances[0]
    
    def _round_robin(self, pool_name: str, instances: List[BackendInstance]) -> BackendInstance:
        """Round robin selection"""
        idx = self._round_robin_indices[pool_name]
        instance = instances[idx % len(instances)]
        self._round_robin_indices[pool_name] = (idx + 1) % len(instances)
        return instance
    
    def _weighted_round_robin(self, pool_name: str, 
                              instances: List[BackendInstance]) -> BackendInstance:
        """Weighted round robin selection"""
        indices = self._weighted_indices[pool_name]
        
        # Filter to healthy instances
        healthy_ids = {i.id for i in instances}
        
        # Rotate until we find a healthy instance
        for _ in range(len(indices)):
            instance_id = indices[0]
            indices.rotate(-1)
            if instance_id in healthy_ids:
                return next(i for i in instances if i.id == instance_id)
        
        return instances[0]
    
    def _least_connections(self, instances: List[BackendInstance]) -> BackendInstance:
        """Least connections selection"""
        return min(instances, key=lambda i: i.current_connections)
    
    def _ip_hash(self, instances: List[BackendInstance], client_ip: str) -> BackendInstance:
        """IP hash selection for session affinity"""
        if not client_ip:
            return self._random_select(instances)
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return instances[hash_value % len(instances)]
    
    def _random_select(self, instances: List[BackendInstance]) -> BackendInstance:
        """Random selection"""
        return random.choice(instances)
    
    def _latency_based(self, instances: List[BackendInstance]) -> BackendInstance:
        """Latency-based selection (favors faster instances)"""
        # Use inverse latency as weight
        total_weight = sum(1 / (i.avg_response_time_ms + 1) for i in instances)
        pick = random.uniform(0, total_weight)
        current = 0
        
        for instance in instances:
            weight = 1 / (instance.avg_response_time_ms + 1)
            current += weight
            if current >= pick:
                return instance
        
        return instances[-1]
    
    def _start_health_checks(self, pool: UpstreamPool) -> None:
        """Start health check thread for pool"""
        def health_check_loop():
            while not self._shutdown:
                for instance in pool.instances:
                    self._check_health(instance, pool.health_check)
                time.sleep(pool.health_check.interval_seconds)
        
        thread = threading.Thread(
            target=health_check_loop,
            name=f"health-check-{pool.name}",
            daemon=True
        )
        thread.start()
        self._health_check_threads[pool.name] = thread
    
    def _check_health(self, instance: BackendInstance, config: HealthCheckConfig) -> None:
        """Perform health check on instance"""
        import urllib.request
        
        url = f"http://{instance.address}{config.path}"
        start_time = time.time()
        
        try:
            req = urllib.request.Request(url, method='GET')
            response = urllib.request.urlopen(req, timeout=config.timeout_seconds)
            
            response_time_ms = (time.time() - start_time) * 1000
            instance.avg_response_time_ms = response_time_ms
            
            if response.status == config.expected_status:
                instance.consecutive_successes += 1
                instance.consecutive_failures = 0
                
                if instance.consecutive_successes >= config.healthy_threshold:
                    instance.health_status = HealthStatus.HEALTHY
            else:
                instance.consecutive_failures += 1
                instance.consecutive_successes = 0
                
                if instance.consecutive_failures >= config.unhealthy_threshold:
                    instance.health_status = HealthStatus.UNHEALTHY
                    
        except Exception as e:
            instance.consecutive_failures += 1
            instance.consecutive_successes = 0
            
            if instance.consecutive_failures >= config.unhealthy_threshold:
                instance.health_status = HealthStatus.UNHEALTHY
                logger.warning(f"Health check failed for {instance.address}: {e}")
        
        instance.last_health_check = time.time()
    
    def get_pool_stats(self, pool_name: str) -> Dict[str, Any]:
        """Get statistics for a pool"""
        pool = self.pools.get(pool_name)
        if not pool:
            return {}
        
        return {
            "name": pool.name,
            "algorithm": pool.algorithm.name,
            "total_instances": len(pool.instances),
            "healthy_instances": sum(1 for i in pool.instances if i.is_healthy),
            "instances": [
                {
                    "id": i.id,
                    "address": i.address,
                    "status": i.health_status.value,
                    "connections": i.current_connections,
                    "total_requests": i.total_requests,
                    "failed_requests": i.failed_requests,
                    "avg_response_time_ms": i.avg_response_time_ms
                }
                for i in pool.instances
            ]
        }
    
    def shutdown(self) -> None:
        """Shutdown load balancer"""
        self._shutdown = True
        for thread in self._health_check_threads.values():
            thread.join(timeout=5.0)


# Predefined upstream pools for ResilienceAI
UPSTREAM_POOLS = [
    UpstreamPool(
        name="analytics-pool",
        algorithm=LoadBalanceAlgorithm.LEAST_CONNECTIONS,
        instances=[
            BackendInstance(id="analytics-1", host="analytics-1", port=8080, weight=2),
            BackendInstance(id="analytics-2", host="analytics-2", port=8080, weight=2),
            BackendInstance(id="analytics-3", host="analytics-3", port=8080, weight=1),
        ],
        health_check=HealthCheckConfig(
            enabled=True,
            interval_seconds=10,
            path="/health"
        )
    ),
    UpstreamPool(
        name="agent-pool",
        algorithm=LoadBalanceAlgorithm.IP_HASH,  # Session affinity for agents
        instances=[
            BackendInstance(id="agent-1", host="agent-1", port=8081, weight=1),
            BackendInstance(id="agent-2", host="agent-2", port=8081, weight=1),
        ],
        health_check=HealthCheckConfig(
            enabled=True,
            interval_seconds=10,
            path="/health"
        )
    ),
    UpstreamPool(
        name="data-pool",
        algorithm=LoadBalanceAlgorithm.WEIGHTED_ROUND_ROBIN,
        instances=[
            BackendInstance(id="data-1", host="data-1", port=8082, weight=3),
            BackendInstance(id="data-2", host="data-2", port=8082, weight=3),
            BackendInstance(id="data-3", host="data-3", port=8082, weight=2),
        ],
        health_check=HealthCheckConfig(
            enabled=True,
            interval_seconds=10,
            path="/health"
        )
    ),
    UpstreamPool(
        name="ml-pool",
        algorithm=LoadBalanceAlgorithm.LATENCY_BASED,  # ML inference latency varies
        instances=[
            BackendInstance(id="ml-1", host="ml-1", port=8083, weight=1),
            BackendInstance(id="ml-2", host="ml-2", port=8083, weight=1),
            BackendInstance(id="ml-gpu-1", host="ml-gpu-1", port=8083, weight=2),
        ],
        health_check=HealthCheckConfig(
            enabled=True,
            interval_seconds=15,
            path="/health"
        )
    ),
]


def create_load_balancer() -> LoadBalancer:
    """Factory function to create configured load balancer"""
    lb = LoadBalancer()
    for pool in UPSTREAM_POOLS:
        lb.register_pool(pool)
    return lb
```

### Nginx Load Balancer Configuration

```nginx
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/nginx-upstreams.conf

upstream analytics_backend {
    least_conn;
    
    server analytics-1:8080 weight=2 max_fails=3 fail_timeout=30s;
    server analytics-2:8080 weight=2 max_fails=3 fail_timeout=30s;
    server analytics-3:8080 weight=1 backup;
    
    keepalive 32;
    keepalive_timeout 60s;
    keepalive_requests 1000;
}

upstream agent_backend {
    ip_hash;  # Session affinity
    
    server agent-1:8081 max_fails=3 fail_timeout=30s;
    server agent-2:8081 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

upstream data_backend {
    server data-1:8082 weight=3 max_fails=3 fail_timeout=30s;
    server data-2:8082 weight=3 max_fails=3 fail_timeout=30s;
    server data-3:8082 weight=2 backup;
    
    keepalive 64;
}

upstream ml_backend {
    server ml-1:8083 max_fails=3 fail_timeout=30s;
    server ml-2:8083 max_fails=3 fail_timeout=30s;
    server ml-gpu-1:8083 weight=2 max_fails=3 fail_timeout=30s;
    
    keepalive 16;
}

upstream geospatial_backend {
    least_conn;
    
    server geo-1:8084 max_fails=3 fail_timeout=30s;
    server geo-2:8084 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

upstream report_backend {
    server report-1:8085 max_fails=3 fail_timeout=30s;
    server report-2:8085 backup;
    
    keepalive 16;
}

# Health check endpoints
server {
    listen 8089;
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 10.0.0.0/8;
        deny all;
    }
}
```


---

## Authentication & Authorization

### Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION & AUTHORIZATION                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        Authentication Flow                             │ │
│  │                                                                        │ │
│  │   Client ──▶ Gateway ──▶ Auth Check ──▶ [Cache] ──▶ Identity Provider │ │
│  │              │              │                       │                  │ │
│  │              │              ▼                       ▼                  │ │
│  │              │         [Valid?] ──Yes──▶ RBAC Check ──▶ Service       │ │
│  │              │              │                                        │ │
│  │              │              No                                       │ │
│  │              │              │                                        │ │
│  │              ▼              ▼                                        │ │
│  │         401/403 Response                                             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Auth Methods Supported                            │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │    JWT      │  │   OAuth2    │  │   API Key   │  │    mTLS     │  │ │
│  │  │   Token     │  │    Flow     │  │             │  │  (Mutual)   │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   SAML      │  │    OIDC     │  │   LDAP/AD   │  │   Custom    │  │ │
│  │  │             │  │             │  │             │  │   Plugin    │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### JWT Authentication Handler

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/auth_handler.py
"""
Authentication Handler for ResilienceAI API Gateway
Supports JWT, OAuth2, API Keys, and mTLS
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import jwt
import hashlib
import hmac
import base64
import time
import logging
from functools import wraps
import redis

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods"""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    MTLS = "mtls"
    SAML = "saml"
    OIDC = "oidc"


class AuthError(Exception):
    """Authentication error"""
    def __init__(self, message: str, status_code: int = 401, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


@dataclass
class JWTConfig:
    """JWT configuration"""
    secret_key: str
    algorithm: str = "HS256"
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "resilienceai"
    audience: Optional[str] = None
    require_exp: bool = True
    require_iat: bool = True


@dataclass
class APIKeyConfig:
    """API Key configuration"""
    header_name: str = "X-API-Key"
    query_param_name: str = "api_key"
    cache_ttl: int = 300
    rate_limit_prefix: str = "apikey"


@dataclass
class AuthContext:
    """Authentication context"""
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    scopes: List[str] = None
    roles: List[str] = None
    permissions: List[str] = None
    authenticated: bool = False
    auth_method: Optional[AuthMethod] = None
    token_data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []
        if self.token_data is None:
            self.token_data = {}
        if self.metadata is None:
            self.metadata = {}
    
    def has_scope(self, scope: str) -> bool:
        """Check if context has scope"""
        return scope in self.scopes or "*" in self.scopes
    
    def has_role(self, role: str) -> bool:
        """Check if context has role"""
        return role in self.roles or "admin" in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Check if context has permission"""
        return permission in self.permissions or "*" in self.permissions


class JWTHandler:
    """JWT token handler"""
    
    def __init__(self, config: JWTConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis = redis_client
        self._revoked_cache: set = set()
    
    def generate_token(
        self,
        user_id: str,
        scopes: List[str],
        roles: List[str],
        additional_claims: Optional[Dict[str, Any]] = None,
        token_type: str = "access"
    ) -> str:
        """Generate JWT token"""
        now = time.time()
        
        if token_type == "access":
            expires = now + (self.config.access_token_expire_minutes * 60)
        else:  # refresh
            expires = now + (self.config.refresh_token_expire_days * 86400)
        
        payload = {
            "sub": user_id,
            "iss": self.config.issuer,
            "iat": now,
            "exp": expires,
            "type": token_type,
            "jti": self._generate_jti(),
            "scopes": scopes,
            "roles": roles
        }
        
        if self.config.audience:
            payload["aud"] = self.config.audience
        
        if additional_claims:
            payload.update(additional_claims)
        
        key = self.config.private_key or self.config.secret_key
        return jwt.encode(payload, key, algorithm=self.config.algorithm)
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            key = self.config.public_key or self.config.secret_key
            
            payload = jwt.decode(
                token,
                key,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                audience=self.config.audience,
                options={
                    "require": ["exp", "iat"] if self.config.require_exp else []
                }
            )
            
            # Check if token is revoked
            jti = payload.get("jti")
            if jti and self._is_revoked(jti):
                raise AuthError("Token has been revoked", 401, "TOKEN_REVOKED")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401, "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401, "INVALID_TOKEN")
    
    def revoke_token(self, jti: str, expires_in: int = 3600) -> None:
        """Revoke a token by JTI"""
        if self.redis:
            self.redis.setex(f"revoked:{jti}", expires_in, "1")
        else:
            self._revoked_cache.add(jti)
    
    def _is_revoked(self, jti: str) -> bool:
        """Check if token is revoked"""
        if self.redis:
            return bool(self.redis.exists(f"revoked:{jti}"))
        return jti in self._revoked_cache
    
    def _generate_jti(self) -> str:
        """Generate unique token ID"""
        import uuid
        return str(uuid.uuid4())
    
    def extract_token_from_header(self, auth_header: str) -> str:
        """Extract token from Authorization header"""
        if not auth_header:
            raise AuthError("Missing Authorization header", 401, "MISSING_AUTH")
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthError("Invalid Authorization header format", 401, "INVALID_AUTH_FORMAT")
        
        return parts[1]


class APIKeyHandler:
    """API Key authentication handler"""
    
    def __init__(self, config: APIKeyConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis = redis_client
    
    def validate_api_key(self, api_key: str) -> AuthContext:
        """Validate API key"""
        if not api_key:
            raise AuthError("Missing API key", 401, "MISSING_API_KEY")
        
        # Check cache
        cache_key = f"apikey:{api_key}"
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                import json
                data = json.loads(cached)
                return self._create_context_from_key_data(data)
        
        # Validate against database (placeholder)
        key_data = self._lookup_api_key(api_key)
        if not key_data:
            raise AuthError("Invalid API key", 401, "INVALID_API_KEY")
        
        if not key_data.get("active", False):
            raise AuthError("API key is deactivated", 401, "KEY_DEACTIVATED")
        
        if key_data.get("expires_at") and key_data["expires_at"] < time.time():
            raise AuthError("API key has expired", 401, "KEY_EXPIRED")
        
        # Cache result
        if self.redis:
            import json
            self.redis.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps(key_data)
            )
        
        return self._create_context_from_key_data(key_data)
    
    def _lookup_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Look up API key in database (placeholder)"""
        # This would query the actual database
        # For demo, return mock data
        return {
            "key_id": "key_123",
            "client_id": "client_456",
            "scopes": ["read:analytics", "read:data"],
            "rate_limit": 1000,
            "active": True,
            "expires_at": None
        }
    
    def _create_context_from_key_data(self, data: Dict[str, Any]) -> AuthContext:
        """Create auth context from key data"""
        return AuthContext(
            client_id=data.get("client_id"),
            scopes=data.get("scopes", []),
            authenticated=True,
            auth_method=AuthMethod.API_KEY,
            metadata={
                "key_id": data.get("key_id"),
                "rate_limit": data.get("rate_limit")
            }
        )
    
    def extract_api_key(self, headers: Dict[str, str], query_params: Dict[str, str]) -> Optional[str]:
        """Extract API key from request"""
        # Check header
        api_key = headers.get(self.config.header_name)
        if api_key:
            return api_key
        
        # Check query param
        return query_params.get(self.config.query_param_name)


class AuthHandler:
    """Main authentication handler"""
    
    def __init__(
        self,
        jwt_config: Optional[JWTConfig] = None,
        api_key_config: Optional[APIKeyConfig] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        self.jwt_handler = JWTHandler(jwt_config, redis_client) if jwt_config else None
        self.api_key_handler = APIKeyHandler(api_key_config, redis_client) if api_key_config else None
        self.redis = redis_client
    
    def authenticate(
        self,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        required_scopes: Optional[List[str]] = None
    ) -> AuthContext:
        """
        Authenticate request
        
        Tries authentication methods in order:
        1. JWT (Authorization header)
        2. API Key
        """
        # Try JWT first
        auth_header = headers.get("Authorization")
        if auth_header and self.jwt_handler:
            try:
                token = self.jwt_handler.extract_token_from_header(auth_header)
                payload = self.jwt_handler.validate_token(token)
                
                context = AuthContext(
                    user_id=payload.get("sub"),
                    scopes=payload.get("scopes", []),
                    roles=payload.get("roles", []),
                    authenticated=True,
                    auth_method=AuthMethod.JWT,
                    token_data=payload
                )
                
                # Check required scopes
                if required_scopes:
                    for scope in required_scopes:
                        if not context.has_scope(scope):
                            raise AuthError(
                                f"Missing required scope: {scope}",
                                403,
                                "INSUFFICIENT_SCOPE"
                            )
                
                return context
                
            except AuthError:
                raise
            except Exception as e:
                logger.warning(f"JWT validation failed: {e}")
        
        # Try API Key
        if self.api_key_handler:
            api_key = self.api_key_handler.extract_api_key(headers, query_params)
            if api_key:
                context = self.api_key_handler.validate_api_key(api_key)
                
                # Check required scopes
                if required_scopes:
                    for scope in required_scopes:
                        if not context.has_scope(scope):
                            raise AuthError(
                                f"Missing required scope: {scope}",
                                403,
                                "INSUFFICIENT_SCOPE"
                            )
                
                return context
        
        raise AuthError("Authentication required", 401, "AUTH_REQUIRED")
    
    def require_auth(self, scopes: Optional[List[str]] = None):
        """Decorator to require authentication"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract headers and params from request context
                # This is a simplified version
                return func(*args, **kwargs)
            return wrapper
        return decorator


# RBAC Implementation
class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self.roles: Dict[str, List[str]] = {}
        self.permissions: Dict[str, Dict[str, Any]] = {}
        self.role_hierarchy: Dict[str, List[str]] = {}
    
    def define_role(self, role: str, permissions: List[str], inherits: Optional[List[str]] = None):
        """Define a role with permissions"""
        self.roles[role] = permissions
        if inherits:
            self.role_hierarchy[role] = inherits
    
    def check_permission(self, context: AuthContext, resource: str, action: str) -> bool:
        """Check if context has permission for action on resource"""
        required_permission = f"{action}:{resource}"
        
        # Check direct permissions
        if context.has_permission(required_permission):
            return True
        
        # Check role permissions
        for role in context.roles:
            if self._role_has_permission(role, required_permission):
                return True
        
        return False
    
    def _role_has_permission(self, role: str, permission: str) -> bool:
        """Check if role has permission (including inherited)"""
        if role not in self.roles:
            return False
        
        if permission in self.roles[role] or "*:*" in self.roles[role]:
            return True
        
        # Check inherited roles
        for inherited_role in self.role_hierarchy.get(role, []):
            if self._role_has_permission(inherited_role, permission):
                return True
        
        return False


# Predefined RBAC configuration for ResilienceAI
RBAC_CONFIG = {
    "roles": {
        "admin": {
            "permissions": ["*:*"],
            "inherits": []
        },
        "analyst": {
            "permissions": [
                "read:analytics",
                "read:data",
                "read:reports",
                "write:analytics",
                "execute:agents"
            ],
            "inherits": ["viewer"]
        },
        "data_engineer": {
            "permissions": [
                "read:data",
                "write:data",
                "read:sources",
                "write:sources",
                "execute:etl"
            ],
            "inherits": ["viewer"]
        },
        "viewer": {
            "permissions": [
                "read:analytics",
                "read:data",
                "read:reports",
                "read:maps"
            ],
            "inherits": []
        },
        "api_client": {
            "permissions": [
                "read:analytics",
                "read:data"
            ],
            "inherits": []
        }
    }
}


def create_auth_handler(redis_client: Optional[redis.Redis] = None) -> AuthHandler:
    """Factory function to create configured auth handler"""
    jwt_config = JWTConfig(
        secret_key="your-secret-key-change-in-production",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        issuer="resilienceai"
    )
    
    api_key_config = APIKeyConfig(
        header_name="X-API-Key",
        cache_ttl=300
    )
    
    return AuthHandler(jwt_config, api_key_config, redis_client)


def create_rbac_manager() -> RBACManager:
    """Factory function to create configured RBAC manager"""
    rbac = RBACManager()
    
    for role_name, config in RBAC_CONFIG["roles"].items():
        rbac.define_role(
            role_name,
            config["permissions"],
            config.get("inherits")
        )
    
    return rbac
```

---

## Rate Limiting

### Rate Limiting Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RATE LIMITING SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Rate Limiting Layers                              │ │
│  │                                                                        │ │
│  │  Layer 1: Edge (CDN) ──▶ Layer 2: Gateway ──▶ Layer 3: Application   │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Token     │  │   Sliding   │  │  Leaky      │  │  Fixed      │  │ │
│  │  │   Bucket    │  │   Window    │  │  Bucket     │  │  Window     │  │ │
│  │  │             │  │   Counter   │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Rate Limit Strategies                             │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Global    │  │   Per-User  │  │  Per-API    │  │  Per-Client │  │ │
│  │  │             │  │             │  │  Key        │  │  IP         │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │  Per-Route  │  │  Per-Method │  │  Tiered     │  │  Burst      │  │ │
│  │  │             │  │             │  │  Plans      │  │  Allowance  │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rate Limiter Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/rate_limiter.py
"""
Rate Limiter for ResilienceAI API Gateway
Supports multiple algorithms: Token Bucket, Sliding Window, Fixed Window
"""

from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
import time
import threading
import logging
import redis
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = auto()
    SLIDING_WINDOW = auto()
    FIXED_WINDOW = auto()
    LEAKY_BUCKET = auto()


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    def __init__(
        self,
        limit: int,
        remaining: int,
        reset_time: float,
        retry_after: int
    ):
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    algorithm: RateLimitAlgorithm
    requests_per_second: float = 10.0
    burst_size: int = 20
    window_size_seconds: int = 60
    key_prefix: str = "ratelimit"
    enabled: bool = True
    
    # Tiered limits
    tier_limits: Optional[Dict[str, Dict[str, Any]]] = None


class RateLimiterBackend(ABC):
    """Abstract base class for rate limiter backends"""
    
    @abstractmethod
    def check_rate_limit(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit"""
        pass
    
    @abstractmethod
    def get_rate_limit_status(self, key: str, config: RateLimitConfig) -> Dict[str, Any]:
        """Get current rate limit status"""
        pass


class InMemoryRateLimiter(RateLimiterBackend):
    """In-memory rate limiter (per-instance)"""
    
    def __init__(self):
        self._buckets: Dict[str, Dict[str, Any]] = {}
        self._windows: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def check_rate_limit(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return self._check_token_bucket(key, config)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return self._check_fixed_window(key, config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return self._check_sliding_window(key, config)
        else:
            return self._check_token_bucket(key, config)
    
    def _check_token_bucket(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Token bucket algorithm"""
        with self._lock:
            now = time.time()
            bucket_key = f"{config.key_prefix}:{key}:tokens"
            
            if bucket_key not in self._buckets:
                self._buckets[bucket_key] = {
                    "tokens": config.burst_size,
                    "last_update": now
                }
            
            bucket = self._buckets[bucket_key]
            
            # Refill tokens
            elapsed = now - bucket["last_update"]
            tokens_to_add = elapsed * config.requests_per_second
            bucket["tokens"] = min(config.burst_size, bucket["tokens"] + tokens_to_add)
            bucket["last_update"] = now
            
            # Check if we can consume a token
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True, {
                    "limit": config.burst_size,
                    "remaining": int(bucket["tokens"]),
                    "reset_time": now + (1 / config.requests_per_second),
                    "window": "token_bucket"
                }
            else:
                retry_after = int((1 - bucket["tokens"]) / config.requests_per_second) + 1
                return False, {
                    "limit": config.burst_size,
                    "remaining": 0,
                    "reset_time": now + retry_after,
                    "retry_after": retry_after,
                    "window": "token_bucket"
                }
    
    def _check_fixed_window(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Fixed window counter algorithm"""
        with self._lock:
            now = time.time()
            window_start = int(now / config.window_size_seconds) * config.window_size_seconds
            window_key = f"{config.key_prefix}:{key}:window:{window_start}"
            
            limit = int(config.requests_per_second * config.window_size_seconds)
            
            if window_key not in self._windows:
                self._windows[window_key] = {"count": 0}
            
            window = self._windows[window_key]
            
            if window["count"] < limit:
                window["count"] += 1
                return True, {
                    "limit": limit,
                    "remaining": limit - window["count"],
                    "reset_time": window_start + config.window_size_seconds,
                    "window": "fixed"
                }
            else:
                reset_time = window_start + config.window_size_seconds
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": int(reset_time - now),
                    "window": "fixed"
                }
    
    def _check_sliding_window(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Sliding window log algorithm"""
        with self._lock:
            now = time.time()
            window_key = f"{config.key_prefix}:{key}:sliding"
            limit = int(config.requests_per_second * config.window_size_seconds)
            
            if window_key not in self._windows:
                self._windows[window_key] = {"requests": []}
            
            window = self._windows[window_key]
            
            # Remove old requests outside the window
            cutoff = now - config.window_size_seconds
            window["requests"] = [t for t in window["requests"] if t > cutoff]
            
            if len(window["requests"]) < limit:
                window["requests"].append(now)
                return True, {
                    "limit": limit,
                    "remaining": limit - len(window["requests"]),
                    "reset_time": window["requests"][0] + config.window_size_seconds if window["requests"] else now,
                    "window": "sliding"
                }
            else:
                reset_time = window["requests"][0] + config.window_size_seconds
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": int(reset_time - now),
                    "window": "sliding"
                }
    
    def get_rate_limit_status(self, key: str, config: RateLimitConfig) -> Dict[str, Any]:
        allowed, status = self.check_rate_limit(key, config)
        status["allowed"] = allowed
        return status


class RedisRateLimiter(RateLimiterBackend):
    """Distributed rate limiter using Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._token_bucket_script = self._load_token_bucket_script()
    
    def _load_token_bucket_script(self) -> str:
        """Load Lua script for atomic token bucket operations"""
        return """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or capacity
        local last_update = tonumber(bucket[2]) or now
        
        -- Calculate tokens to add
        local elapsed = now - last_update
        local tokens_to_add = elapsed * rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        -- Try to consume tokens
        local allowed = tokens >= requested
        if allowed then
            tokens = tokens - requested
        end
        
        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, 60)
        
        return {allowed and 1 or 0, tokens, capacity}
        """
    
    def check_rate_limit(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return self._check_token_bucket_redis(key, config)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return self._check_fixed_window_redis(key, config)
        else:
            return self._check_token_bucket_redis(key, config)
    
    def _check_token_bucket_redis(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Token bucket with Redis"""
        bucket_key = f"{config.key_prefix}:{key}:tokens"
        now = time.time()
        
        try:
            result = self.redis.eval(
                self._token_bucket_script,
                1,
                bucket_key,
                config.requests_per_second,
                config.burst_size,
                now,
                1
            )
            
            allowed = result[0] == 1
            tokens = result[1]
            capacity = result[2]
            
            if allowed:
                return True, {
                    "limit": capacity,
                    "remaining": int(tokens),
                    "reset_time": now + (1 / config.requests_per_second),
                    "window": "token_bucket"
                }
            else:
                retry_after = int((1 - tokens) / config.requests_per_second) + 1
                return False, {
                    "limit": capacity,
                    "remaining": 0,
                    "reset_time": now + retry_after,
                    "retry_after": retry_after,
                    "window": "token_bucket"
                }
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fail open in case of Redis error
            return True, {"limit": config.burst_size, "remaining": config.burst_size}
    
    def _check_fixed_window_redis(self, key: str, config: RateLimitConfig) -> tuple[bool, Dict[str, Any]]:
        """Fixed window with Redis"""
        now = time.time()
        window_start = int(now / config.window_size_seconds) * config.window_size_seconds
        window_key = f"{config.key_prefix}:{key}:window:{window_start}"
        limit = int(config.requests_per_second * config.window_size_seconds)
        
        try:
            pipe = self.redis.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, config.window_size_seconds)
            results = pipe.execute()
            
            count = results[0]
            
            if count <= limit:
                return True, {
                    "limit": limit,
                    "remaining": max(0, limit - count),
                    "reset_time": window_start + config.window_size_seconds,
                    "window": "fixed"
                }
            else:
                reset_time = window_start + config.window_size_seconds
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": int(reset_time - now),
                    "window": "fixed"
                }
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True, {"limit": limit, "remaining": limit}
    
    def get_rate_limit_status(self, key: str, config: RateLimitConfig) -> Dict[str, Any]:
        allowed, status = self.check_rate_limit(key, config)
        status["allowed"] = allowed
        return status


class RateLimiter:
    """
    Main rate limiter with support for multiple strategies
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.backend = RedisRateLimiter(redis_client) if redis_client else InMemoryRateLimiter()
        
        # Default configs for different endpoint types
        self.configs: Dict[str, RateLimitConfig] = {
            "default": RateLimitConfig(
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                requests_per_second=10,
                burst_size=20
            ),
            "analytics": RateLimitConfig(
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                requests_per_second=50,
                burst_size=100
            ),
            "agent": RateLimitConfig(
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                requests_per_second=20,
                burst_size=40
            ),
            "ml": RateLimitConfig(
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                requests_per_second=5,
                burst_size=10
            ),
            "data": RateLimitConfig(
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                requests_per_second=100,
                window_size_seconds=60
            ),
            "export": RateLimitConfig(
                algorithm=RateLimitAlgorithm.FIXED_WINDOW,
                requests_per_second=0.1,  # 6 per minute
                window_size_seconds=60
            )
        }
    
    def check(
        self,
        key: str,
        config_name: str = "default",
        custom_config: Optional[RateLimitConfig] = None
    ) -> Dict[str, Any]:
        """
        Check rate limit for a key
        
        Args:
            key: Rate limit key (e.g., user_id, api_key, ip)
            config_name: Named configuration to use
            custom_config: Optional custom configuration
            
        Returns:
            Rate limit status dict
        """
        config = custom_config or self.configs.get(config_name, self.configs["default"])
        
        if not config.enabled:
            return {"allowed": True, "limit": -1, "remaining": -1}
        
        allowed, status = self.backend.check_rate_limit(key, config)
        status["allowed"] = allowed
        
        if not allowed:
            raise RateLimitExceeded(
                limit=status["limit"],
                remaining=status["remaining"],
                reset_time=status["reset_time"],
                retry_after=status.get("retry_after", 60)
            )
        
        return status
    
    def get_limit_key(
        self,
        request_type: str,
        identifier: str,
        route: Optional[str] = None
    ) -> str:
        """Generate rate limit key"""
        parts = [request_type, identifier]
        if route:
            parts.append(route.replace("/", "_"))
        return ":".join(parts)
    
    def add_headers(self, headers: Dict[str, str], status: Dict[str, Any]) -> Dict[str, str]:
        """Add rate limit headers to response"""
        headers["X-RateLimit-Limit"] = str(status.get("limit", -1))
        headers["X-RateLimit-Remaining"] = str(status.get("remaining", -1))
        headers["X-RateLimit-Reset"] = str(int(status.get("reset_time", 0)))
        
        if "retry_after" in status:
            headers["Retry-After"] = str(status["retry_after"])
        
        return headers


# Tiered rate limits for different user types
TIERED_LIMITS = {
    "free": {
        "requests_per_day": 1000,
        "requests_per_minute": 20,
        "concurrent_requests": 5
    },
    "basic": {
        "requests_per_day": 10000,
        "requests_per_minute": 100,
        "concurrent_requests": 20
    },
    "professional": {
        "requests_per_day": 100000,
        "requests_per_minute": 500,
        "concurrent_requests": 50
    },
    "enterprise": {
        "requests_per_day": -1,  # Unlimited
        "requests_per_minute": 2000,
        "concurrent_requests": 200
    }
}


def create_rate_limiter(redis_client: Optional[redis.Redis] = None) -> RateLimiter:
    """Factory function to create configured rate limiter"""
    return RateLimiter(redis_client)
```

---

## Caching Layer

### Caching Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CACHING LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Multi-Level Cache                                 │ │
│  │                                                                        │ │
│  │   L1 (Memory) ──▶ L2 (Redis) ──▶ L3 (CDN) ──▶ Origin                 │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Local     │  │  Distributed│  │   Edge      │  │  Backend    │  │ │
│  │  │   Cache     │  │   Cache     │  │   Cache     │  │  Services   │  │ │
│  │  │   (LRU)     │  │  (Redis)    │  │  (CDN)      │  │             │  │ │
│  │  │  ~10ms      │  │  ~1ms       │  │  ~50ms      │  │  ~100ms+    │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Cache Strategies                                  │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Cache     │  │   Cache     │  │   Stale     │  │   Cache     │  │ │
│  │  │   Aside     │  │   Through   │  │   While     │  │   Warming   │  │ │
│  │  │             │  │             │  │   Revalidate│  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cache Manager Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/cache_manager.py
"""
Cache Manager for ResilienceAI API Gateway
Multi-level caching with Redis and in-memory layers
"""

from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
import hashlib
import json
import time
import pickle
import logging
import threading
from functools import wraps
import redis

logger = logging.getLogger(__name__)
T = TypeVar('T')


class CacheStrategy(Enum):
    """Cache strategies"""
    CACHE_ASIDE = auto()
    CACHE_THROUGH = auto()
    CACHE_BEHIND = auto()


class CacheEvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = auto()
    LFU = auto()
    FIFO = auto()
    TTL = auto()


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl_seconds: int = 300
    max_size: int = 10000
    eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU
    compression: bool = True
    encryption: bool = False
    stale_while_revalidate: bool = False
    stale_ttl_seconds: int = 60


class CacheBackend(ABC):
    """Abstract cache backend"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache"""
        pass


class InMemoryCache(CacheBackend):
    """In-memory LRU cache"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: List[str] = []
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            
            # Check TTL
            if entry.get("expires_at") and entry["expires_at"] < time.time():
                self.delete(key)
                return None
            
            # Update access order for LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            entry["access_count"] = entry.get("access_count", 0) + 1
            
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.config.max_size and key not in self._cache:
                self._evict_lru()
            
            expires_at = None
            if ttl:
                expires_at = time.time() + ttl
            elif self.config.ttl_seconds:
                expires_at = time.time() + self.config.ttl_seconds
            
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
                "access_count": 0
            }
            
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    def exists(self, key: str) -> bool:
        return self.get(key) is not None
    
    def clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            return True
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                del self._cache[lru_key]


class RedisCache(CacheBackend):
    """Redis cache backend"""
    
    def __init__(self, redis_client: redis.Redis, config: CacheConfig):
        self.redis = redis_client
        self.config = config
    
    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            data = pickle.dumps(value)
            ttl = ttl or self.config.ttl_seconds
            
            if ttl:
                self.redis.setex(key, ttl, data)
            else:
                self.redis.set(key, data)
            
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return self.redis.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def clear(self) -> bool:
        try:
            # Use scan to clear keys safely
            for key in self.redis.scan_iter(match="cache:*"):
                self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            return -1


class MultiLevelCache:
    """
    Multi-level cache with L1 (memory) and L2 (Redis)
    """
    
    def __init__(
        self,
        l1_config: Optional[CacheConfig] = None,
        l2_redis: Optional[redis.Redis] = None,
        l2_config: Optional[CacheConfig] = None
    ):
        self.l1 = InMemoryCache(l1_config or CacheConfig(ttl_seconds=60, max_size=1000))
        self.l2 = RedisCache(l2_redis, l2_config or CacheConfig(ttl_seconds=300)) if l2_redis else None
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "total_requests": 0
        }
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 -> L2)"""
        with self._lock:
            self.stats["total_requests"] += 1
        
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            with self._lock:
                self.stats["l1_hits"] += 1
            return value
        
        with self._lock:
            self.stats["l1_misses"] += 1
        
        # Try L2
        if self.l2:
            value = self.l2.get(key)
            if value is not None:
                # Promote to L1
                self.l1.set(key, value)
                with self._lock:
                    self.stats["l2_hits"] += 1
                return value
            
            with self._lock:
                self.stats["l2_misses"] += 1
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        l1_ttl: Optional[int] = None,
        l2_ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache (both L1 and L2)"""
        success = self.l1.set(key, value, l1_ttl)
        
        if self.l2:
            success = success and self.l2.set(key, value, l2_ttl)
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete value from cache (both L1 and L2)"""
        l1_success = self.l1.delete(key)
        l2_success = self.l2.delete(key) if self.l2 else True
        return l1_success or l2_success
    
    def get_or_set(
        self,
        key: str,
        fetch_func: Callable[[], T],
        l1_ttl: Optional[int] = None,
        l2_ttl: Optional[int] = None
    ) -> T:
        """Get from cache or fetch and cache"""
        value = self.get(key)
        if value is not None:
            return value
        
        value = fetch_func()
        self.set(key, value, l1_ttl, l2_ttl)
        return value
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        count = 0
        # This is simplified - in production, use Redis SCAN
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            stats = self.stats.copy()
        
        total_hits = stats["l1_hits"] + stats["l2_hits"]
        total_requests = stats["total_requests"]
        
        stats["hit_rate"] = total_hits / total_requests if total_requests > 0 else 0
        stats["l1_hit_rate"] = stats["l1_hits"] / (stats["l1_hits"] + stats["l1_misses"]) if (stats["l1_hits"] + stats["l1_misses"]) > 0 else 0
        stats["l2_hit_rate"] = stats["l2_hits"] / (stats["l2_hits"] + stats["l2_misses"]) if (stats["l2_hits"] + stats["l2_misses"]) > 0 else 0
        
        return stats


class ResponseCache:
    """
    HTTP response cache for API Gateway
    """
    
    def __init__(self, cache: MultiLevelCache):
        self.cache = cache
        self.cacheable_methods = {"GET", "HEAD", "OPTIONS"}
        self.cacheable_status = {200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501}
    
    def generate_key(
        self,
        method: str,
        path: str,
        query_string: str = "",
        vary_headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate cache key from request"""
        key_parts = [method, path]
        
        if query_string:
            key_parts.append(query_string)
        
        if vary_headers:
            for header, value in sorted(vary_headers.items()):
                key_parts.append(f"{header}:{value}")
        
        key_string = "|".join(key_parts)
        return f"response:{hashlib.sha256(key_string.encode()).hexdigest()}"
    
    def is_cacheable_request(
        self,
        method: str,
        headers: Dict[str, str]
    ) -> bool:
        """Check if request is cacheable"""
        if method not in self.cacheable_methods:
            return False
        
        # Check Cache-Control header
        cache_control = headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    def is_cacheable_response(
        self,
        status_code: int,
        headers: Dict[str, str]
    ) -> bool:
        """Check if response is cacheable"""
        if status_code not in self.cacheable_status:
            return False
        
        # Check Cache-Control header
        cache_control = headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control or "private" in cache_control:
            return False
        
        return True
    
    def get_ttl_from_headers(self, headers: Dict[str, str]) -> int:
        """Extract TTL from response headers"""
        # Check Cache-Control max-age
        cache_control = headers.get("Cache-Control", "")
        if "max-age=" in cache_control:
            try:
                max_age = int(cache_control.split("max-age=")[1].split(",")[0])
                return max_age
            except (ValueError, IndexError):
                pass
        
        # Check Expires header
        expires = headers.get("Expires")
        if expires:
            try:
                from email.utils import parsedate_to_datetime
                expires_dt = parsedate_to_datetime(expires)
                ttl = int((expires_dt.timestamp() - time.time()))
                return max(0, ttl)
            except Exception:
                pass
        
        # Default TTL
        return 300
    
    def cache_response(
        self,
        key: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache response"""
        if ttl is None:
            ttl = self.get_ttl_from_headers(response.get("headers", {}))
        
        return self.cache.set(key, response, l1_ttl=min(ttl, 60), l2_ttl=ttl)
    
    def get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        return self.cache.get(key)


def create_cache_manager(redis_client: Optional[redis.Redis] = None) -> ResponseCache:
    """Factory function to create configured cache manager"""
    l1_config = CacheConfig(ttl_seconds=60, max_size=10000)
    l2_config = CacheConfig(ttl_seconds=300, max_size=1000000)
    
    multi_cache = MultiLevelCache(l1_config, redis_client, l2_config)
    return ResponseCache(multi_cache)
```


---

## Request/Response Transformation

### Transformation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REQUEST/RESPONSE TRANSFORMATION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Request Transformation                            │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Header    │  │   Body      │  │   Path      │  │   Query     │  │ │
│  │  │   Modify    │  │   Transform │  │   Rewrite   │  │   Modify    │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Response Transformation                           │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Header    │  │   Body      │  │   Status    │  │   Format    │  │ │
│  │  │   Modify    │  │   Transform │  │   Override  │  │   Convert   │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Transformation Types                              │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   JSON      │  │   XML       │  │  GraphQL    │  │  Protocol   │  │ │
│  │  │   <> XML    │  │   <> JSON   │  │  <> REST    │  │  Buffer     │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Transformation Engine Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/transformer.py
"""
Request/Response Transformer for ResilienceAI API Gateway
Supports header modification, body transformation, and format conversion
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
import json
import xml.etree.ElementTree as ET
import re
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class TransformType(Enum):
    """Transformation types"""
    HEADER_ADD = auto()
    HEADER_REMOVE = auto()
    HEADER_REPLACE = auto()
    BODY_MODIFY = auto()
    PATH_REWRITE = auto()
    QUERY_MODIFY = auto()
    STATUS_OVERRIDE = auto()


class ContentType(Enum):
    """Content types"""
    JSON = "application/json"
    XML = "application/xml"
    FORM = "application/x-www-form-urlencoded"
    PROTOBUF = "application/x-protobuf"
    TEXT = "text/plain"


@dataclass
class TransformRule:
    """Transformation rule"""
    type: TransformType
    condition: Optional[str] = None  # Condition to apply rule
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    enabled: bool = True


@dataclass
class TransformContext:
    """Transformation context"""
    method: str
    path: str
    query_params: Dict[str, str]
    headers: Dict[str, str]
    body: Optional[Union[str, bytes, Dict]]
    status_code: Optional[int] = None
    route: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Transformer(ABC):
    """Abstract transformer"""
    
    @abstractmethod
    def transform(self, context: TransformContext, rule: TransformRule) -> TransformContext:
        """Apply transformation"""
        pass


class HeaderTransformer(Transformer):
    """Header transformation"""
    
    def transform(self, context: TransformContext, rule: TransformRule) -> TransformContext:
        if rule.type == TransformType.HEADER_ADD:
            for key, value in rule.config.get("add", {}).items():
                # Support template variables
                value = self._interpolate_template(value, context)
                context.headers[key] = value
        
        elif rule.type == TransformType.HEADER_REMOVE:
            for key in rule.config.get("remove", []):
                context.headers.pop(key, None)
        
        elif rule.type == TransformType.HEADER_REPLACE:
            for key, value in rule.config.get("replace", {}).items():
                value = self._interpolate_template(value, context)
                context.headers[key] = value
        
        return context
    
    def _interpolate_template(self, template: str, context: TransformContext) -> str:
        """Interpolate template variables"""
        # Replace $(variable) with context values
        def replace_var(match):
            var_name = match.group(1)
            if var_name == "request_id":
                return context.metadata.get("request_id", "")
            elif var_name == "client_ip":
                return context.metadata.get("client_ip", "")
            elif var_name == "timestamp":
                import time
                return str(int(time.time()))
            elif var_name.startswith("header."):
                header_name = var_name[7:]
                return context.headers.get(header_name, "")
            elif var_name.startswith("query."):
                query_name = var_name[6:]
                return context.query_params.get(query_name, "")
            return match.group(0)
        
        return re.sub(r'\$\((\w+(?:\.\w+)*)\)', replace_var, template)


class BodyTransformer(Transformer):
    """Body transformation"""
    
    def transform(self, context: TransformContext, rule: TransformRule) -> TransformContext:
        if rule.type != TransformType.BODY_MODIFY:
            return context
        
        operations = rule.config.get("operations", [])
        
        for op in operations:
            op_type = op.get("type")
            
            if op_type == "add_field":
                context = self._add_field(context, op)
            elif op_type == "remove_field":
                context = self._remove_field(context, op)
            elif op_type == "rename_field":
                context = self._rename_field(context, op)
            elif op_type == "transform_value":
                context = self._transform_value(context, op)
            elif op_type == "json_to_xml":
                context = self._json_to_xml(context)
            elif op_type == "xml_to_json":
                context = self._xml_to_json(context)
        
        return context
    
    def _parse_body(self, context: TransformContext) -> Dict[str, Any]:
        """Parse body based on content type"""
        if not context.body:
            return {}
        
        content_type = context.headers.get("Content-Type", "")
        
        if "application/json" in content_type:
            if isinstance(context.body, dict):
                return context.body
            try:
                return json.loads(context.body)
            except json.JSONDecodeError:
                return {}
        
        return {"_raw": context.body}
    
    def _serialize_body(self, data: Dict[str, Any], content_type: str) -> str:
        """Serialize body based on content type"""
        if "application/json" in content_type:
            return json.dumps(data)
        return str(data)
    
    def _add_field(self, context: TransformContext, op: Dict[str, Any]) -> TransformContext:
        """Add field to body"""
        body = self._parse_body(context)
        path = op.get("path", "").split(".")
        value = op.get("value")
        
        # Navigate to parent and add field
        current = body
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        if path:
            current[path[-1]] = value
        
        context.body = self._serialize_body(body, context.headers.get("Content-Type", "application/json"))
        return context
    
    def _remove_field(self, context: TransformContext, op: Dict[str, Any]) -> TransformContext:
        """Remove field from body"""
        body = self._parse_body(context)
        path = op.get("path", "").split(".")
        
        current = body
        for key in path[:-1]:
            if key not in current:
                return context
            current = current[key]
        
        if path and path[-1] in current:
            del current[path[-1]]
        
        context.body = self._serialize_body(body, context.headers.get("Content-Type", "application/json"))
        return context
    
    def _rename_field(self, context: TransformContext, op: Dict[str, Any]) -> TransformContext:
        """Rename field in body"""
        body = self._parse_body(context)
        old_path = op.get("from", "").split(".")
        new_name = op.get("to", "")
        
        current = body
        for key in old_path[:-1]:
            if key not in current:
                return context
            current = current[key]
        
        if old_path and old_path[-1] in current:
            value = current.pop(old_path[-1])
            current[new_name] = value
        
        context.body = self._serialize_body(body, context.headers.get("Content-Type", "application/json"))
        return context
    
    def _transform_value(self, context: TransformContext, op: Dict[str, Any]) -> TransformContext:
        """Transform field value"""
        body = self._parse_body(context)
        path = op.get("path", "").split(".")
        transform = op.get("transform", "uppercase")
        
        current = body
        for key in path[:-1]:
            if key not in current:
                return context
            current = current[key]
        
        if path and path[-1] in current:
            value = current[path[-1]]
            if transform == "uppercase":
                current[path[-1]] = str(value).upper()
            elif transform == "lowercase":
                current[path[-1]] = str(value).lower()
            elif transform == "hash":
                import hashlib
                current[path[-1]] = hashlib.sha256(str(value).encode()).hexdigest()
        
        context.body = self._serialize_body(body, context.headers.get("Content-Type", "application/json"))
        return context
    
    def _json_to_xml(self, context: TransformContext) -> TransformContext:
        """Convert JSON body to XML"""
        body = self._parse_body(context)
        xml_str = self._dict_to_xml(body, "root")
        context.body = xml_str
        context.headers["Content-Type"] = "application/xml"
        return context
    
    def _xml_to_json(self, context: TransformContext) -> TransformContext:
        """Convert XML body to JSON"""
        if not context.body:
            return context
        
        try:
            root = ET.fromstring(context.body)
            data = self._xml_to_dict(root)
            context.body = json.dumps(data)
            context.headers["Content-Type"] = "application/json"
        except ET.ParseError:
            logger.warning("Failed to parse XML body")
        
        return context
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dict to XML string"""
        root = ET.Element(root_name)
        self._build_xml(root, data)
        return ET.tostring(root, encoding="unicode")
    
    def _build_xml(self, parent: ET.Element, data: Any):
        """Build XML element from data"""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, key)
                self._build_xml(child, value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, "item")
                self._build_xml(child, item)
        else:
            parent.text = str(data)
    
    def _xml_to_dict(self, element: ET.Element) -> Any:
        """Convert XML element to dict"""
        children = list(element)
        if not children:
            return element.text
        
        result = {}
        for child in children:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result


class PathTransformer(Transformer):
    """Path transformation"""
    
    def transform(self, context: TransformContext, rule: TransformRule) -> TransformContext:
        if rule.type != TransformType.PATH_REWRITE:
            return context
        
        patterns = rule.config.get("patterns", [])
        
        for pattern in patterns:
            match = re.match(pattern["from"], context.path)
            if match:
                context.path = match.expand(pattern["to"])
                break
        
        return context


class QueryTransformer(Transformer):
    """Query parameter transformation"""
    
    def transform(self, context: TransformContext, rule: TransformRule) -> TransformContext:
        if rule.type != TransformType.QUERY_MODIFY:
            return context
        
        # Add query params
        for key, value in rule.config.get("add", {}).items():
            context.query_params[key] = value
        
        # Remove query params
        for key in rule.config.get("remove", []):
            context.query_params.pop(key, None)
        
        # Rename query params
        for old_key, new_key in rule.config.get("rename", {}).items():
            if old_key in context.query_params:
                context.query_params[new_key] = context.query_params.pop(old_key)
        
        return context


class TransformEngine:
    """
    Main transformation engine
    """
    
    def __init__(self):
        self.transformers = {
            TransformType.HEADER_ADD: HeaderTransformer(),
            TransformType.HEADER_REMOVE: HeaderTransformer(),
            TransformType.HEADER_REPLACE: HeaderTransformer(),
            TransformType.BODY_MODIFY: BodyTransformer(),
            TransformType.PATH_REWRITE: PathTransformer(),
            TransformType.QUERY_MODIFY: QueryTransformer(),
        }
        self.rules: List[TransformRule] = []
    
    def add_rule(self, rule: TransformRule) -> None:
        """Add transformation rule"""
        self.rules.append(rule)
        # Sort by priority
        self.rules.sort(key=lambda r: r.priority)
    
    def transform_request(self, context: TransformContext) -> TransformContext:
        """Apply request transformations"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check condition
            if rule.condition and not self._evaluate_condition(rule.condition, context):
                continue
            
            transformer = self.transformers.get(rule.type)
            if transformer:
                try:
                    context = transformer.transform(context, rule)
                except Exception as e:
                    logger.error(f"Transformation error: {e}")
        
        return context
    
    def transform_response(self, context: TransformContext) -> TransformContext:
        """Apply response transformations"""
        # Similar to request transformation but for responses
        return context
    
    def _evaluate_condition(self, condition: str, context: TransformContext) -> bool:
        """Evaluate transformation condition"""
        # Simple condition evaluation
        # Example: "header.X-Version == 'v2'"
        try:
            parts = condition.split("==")
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip().strip("'\"")
                
                if left.startswith("header."):
                    header_name = left[7:]
                    return context.headers.get(header_name) == right
                elif left.startswith("query."):
                    query_name = left[6:]
                    return context.query_params.get(query_name) == right
        except Exception:
            pass
        
        return True


# Predefined transformation rules for ResilienceAI
DEFAULT_TRANSFORM_RULES = [
    # Add request ID header
    TransformRule(
        type=TransformType.HEADER_ADD,
        config={"add": {"X-Request-ID": "$(request_id)"}},
        priority=1
    ),
    # Add client IP header
    TransformRule(
        type=TransformType.HEADER_ADD,
        config={"add": {"X-Client-IP": "$(client_ip)"}},
        priority=2
    ),
    # Remove sensitive headers from request
    TransformRule(
        type=TransformType.HEADER_REMOVE,
        config={"remove": ["X-Internal-Token", "X-Debug"]},
        priority=3
    ),
    # API version path rewrite
    TransformRule(
        type=TransformType.PATH_REWRITE,
        config={"patterns": [{"from": r"^/api/v1/(.*)$", "to": r"/v1/\1"}]},
        priority=10
    ),
]


def create_transform_engine() -> TransformEngine:
    """Factory function to create configured transform engine"""
    engine = TransformEngine()
    for rule in DEFAULT_TRANSFORM_RULES:
        engine.add_rule(rule)
    return engine
```

---

## Logging & Monitoring

### Logging Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOGGING & MONITORING                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Log Collection Pipeline                           │ │
│  │                                                                        │ │
│  │  Gateway ──▶ Fluentd ──▶ Kafka ──▶ Logstash ──▶ Elasticsearch        │ │
│  │              │                    │                    │               │ │
│  │              ▼                    ▼                    ▼               │ │
│  │         File Logs            Metrics Stream       Kibana Dashboards    │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Metrics Collection                                │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │ Prometheus  │  │   StatsD    │  │   Jaeger    │  │   Grafana   │  │ │
│  │  │  Metrics    │  │   Counters  │  │  Tracing    │  │ Dashboards  │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Logging Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/logger.py
"""
Logging Service for ResilienceAI API Gateway
Structured logging with correlation IDs and performance metrics
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import logging
import uuid
from functools import wraps
from contextvars import ContextVar
import structlog

# Context variable for request correlation
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    message: str
    correlation_id: str
    service: str
    component: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "service": self.service,
            "component": self.component,
            **self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class AccessLogEntry:
    """HTTP access log entry"""
    timestamp: str
    correlation_id: str
    client_ip: str
    method: str
    path: str
    query_string: str
    status_code: int
    response_time_ms: float
    request_size: int
    response_size: int
    user_agent: str
    referer: str
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StructuredLogger:
    """Structured logger with correlation tracking"""
    
    def __init__(self, service_name: str = "api-gateway"):
        self.service_name = service_name
        self.logger = structlog.get_logger(service_name)
        
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
    
    def set_correlation_id(self, cid: Optional[str] = None) -> str:
        """Set correlation ID for current context"""
        if cid is None:
            cid = str(uuid.uuid4())
        correlation_id.set(cid)
        return cid
    
    def get_correlation_id(self) -> str:
        """Get current correlation ID"""
        return correlation_id.get()
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        component: str = "gateway",
        **kwargs
    ) -> None:
        """Internal log method"""
        cid = self.get_correlation_id()
        
        log_data = {
            "correlation_id": cid,
            "component": component,
            **kwargs
        }
        
        if level == LogLevel.DEBUG:
            self.logger.debug(message, **log_data)
        elif level == LogLevel.INFO:
            self.logger.info(message, **log_data)
        elif level == LogLevel.WARNING:
            self.logger.warning(message, **log_data)
        elif level == LogLevel.ERROR:
            self.logger.error(message, **log_data)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message, **log_data)
    
    def debug(self, message: str, component: str = "gateway", **kwargs) -> None:
        self._log(LogLevel.DEBUG, message, component, **kwargs)
    
    def info(self, message: str, component: str = "gateway", **kwargs) -> None:
        self._log(LogLevel.INFO, message, component, **kwargs)
    
    def warning(self, message: str, component: str = "gateway", **kwargs) -> None:
        self._log(LogLevel.WARNING, message, component, **kwargs)
    
    def error(self, message: str, component: str = "gateway", **kwargs) -> None:
        self._log(LogLevel.ERROR, message, component, **kwargs)
    
    def critical(self, message: str, component: str = "gateway", **kwargs) -> None:
        self._log(LogLevel.CRITICAL, message, component, **kwargs)
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        client_ip: str,
        user_agent: str,
        **kwargs
    ) -> None:
        """Log HTTP request"""
        self.info(
            f"{method} {path} {status_code}",
            component="access",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=round(response_time_ms, 2),
            client_ip=client_ip,
            user_agent=user_agent,
            **kwargs
        )
    
    def log_error(
        self,
        error: Exception,
        component: str = "gateway",
        **kwargs
    ) -> None:
        """Log error with stack trace"""
        self.error(
            str(error),
            component=component,
            error_type=type(error).__name__,
            exc_info=True,
            **kwargs
        )


class MetricsCollector:
    """Metrics collector for Prometheus"""
    
    def __init__(self):
        try:
            from prometheus_client import Counter, Histogram, Gauge, Info
            
            # Request metrics
            self.request_count = Counter(
                'gateway_requests_total',
                'Total requests',
                ['method', 'route', 'status_code']
            )
            self.request_duration = Histogram(
                'gateway_request_duration_seconds',
                'Request duration',
                ['method', 'route'],
                buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            )
            self.request_size = Histogram(
                'gateway_request_size_bytes',
                'Request size',
                ['method', 'route'],
                buckets=[100, 1000, 10000, 100000, 1000000]
            )
            self.response_size = Histogram(
                'gateway_response_size_bytes',
                'Response size',
                ['method', 'route'],
                buckets=[100, 1000, 10000, 100000, 1000000]
            )
            
            # Rate limit metrics
            self.rate_limit_hits = Counter(
                'gateway_rate_limit_hits_total',
                'Rate limit hits',
                ['key_type', 'route']
            )
            
            # Cache metrics
            self.cache_hits = Counter(
                'gateway_cache_hits_total',
                'Cache hits',
                ['cache_level', 'route']
            )
            self.cache_misses = Counter(
                'gateway_cache_misses_total',
                'Cache misses',
                ['cache_level', 'route']
            )
            
            # Auth metrics
            self.auth_attempts = Counter(
                'gateway_auth_attempts_total',
                'Authentication attempts',
                ['method', 'result']
            )
            
            # Circuit breaker metrics
            self.circuit_breaker_state = Gauge(
                'gateway_circuit_breaker_state',
                'Circuit breaker state',
                ['service']
            )
            
            # Backend metrics
            self.backend_health = Gauge(
                'gateway_backend_health',
                'Backend health status',
                ['service', 'instance']
            )
            
            self._enabled = True
            
        except ImportError:
            self._enabled = False
            logging.warning("prometheus_client not installed, metrics disabled")
    
    def record_request(
        self,
        method: str,
        route: str,
        status_code: int,
        duration_seconds: float,
        request_size: int = 0,
        response_size: int = 0
    ) -> None:
        """Record request metrics"""
        if not self._enabled:
            return
        
        self.request_count.labels(
            method=method,
            route=route,
            status_code=str(status_code)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            route=route
        ).observe(duration_seconds)
        
        if request_size > 0:
            self.request_size.labels(
                method=method,
                route=route
            ).observe(request_size)
        
        if response_size > 0:
            self.response_size.labels(
                method=method,
                route=route
            ).observe(response_size)
    
    def record_rate_limit_hit(self, key_type: str, route: str) -> None:
        """Record rate limit hit"""
        if self._enabled:
            self.rate_limit_hits.labels(key_type=key_type, route=route).inc()
    
    def record_cache_hit(self, cache_level: str, route: str) -> None:
        """Record cache hit"""
        if self._enabled:
            self.cache_hits.labels(cache_level=cache_level, route=route).inc()
    
    def record_cache_miss(self, cache_level: str, route: str) -> None:
        """Record cache miss"""
        if self._enabled:
            self.cache_misses.labels(cache_level=cache_level, route=route).inc()
    
    def record_auth_attempt(self, method: str, success: bool) -> None:
        """Record authentication attempt"""
        if self._enabled:
            result = "success" if success else "failure"
            self.auth_attempts.labels(method=method, result=result).inc()
    
    def set_circuit_breaker_state(self, service: str, state: int) -> None:
        """Set circuit breaker state (0=closed, 1=open, 2=half-open)"""
        if self._enabled:
            self.circuit_breaker_state.labels(service=service).set(state)
    
    def set_backend_health(self, service: str, instance: str, healthy: bool) -> None:
        """Set backend health status"""
        if self._enabled:
            self.backend_health.labels(service=service, instance=instance).set(1 if healthy else 0)


class TracingManager:
    """Distributed tracing manager"""
    
    def __init__(self, service_name: str = "api-gateway"):
        self.service_name = service_name
        self._enabled = False
        
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            
            # Configure tracer
            provider = TracerProvider()
            processor = BatchSpanProcessor(JaegerExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            
            self.tracer = trace.get_tracer(service_name)
            self._enabled = True
            
        except ImportError:
            logging.warning("opentelemetry not installed, tracing disabled")
    
    def start_span(self, name: str, parent_span=None, **kwargs):
        """Start a new span"""
        if not self._enabled:
            return None
        
        context = trace.set_span_in_context(parent_span) if parent_span else None
        return self.tracer.start_span(name, context=context, **kwargs)
    
    def inject_headers(self, headers: Dict[str, str], span) -> None:
        """Inject tracing headers"""
        if not self._enabled:
            return
        
        from opentelemetry.propagate import inject
        carrier = {}
        inject(carrier)
        headers.update(carrier)


def create_logger() -> StructuredLogger:
    """Factory function to create configured logger"""
    return StructuredLogger(service_name="resilienceai-gateway")


def create_metrics_collector() -> MetricsCollector:
    """Factory function to create metrics collector"""
    return MetricsCollector()


def create_tracing_manager() -> TracingManager:
    """Factory function to create tracing manager"""
    return TracingManager(service_name="resilienceai-gateway")
```

---

## API Versioning

### Versioning Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API VERSIONING                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Versioning Strategies                             │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   URL Path  │  │   Header    │  │   Query     │  │  Content    │  │ │
│  │  │  /api/v1/   │  │  X-Version  │  │  ?v=1       │  │  Type       │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Version Lifecycle                                 │ │
│  │                                                                        │ │
│  │  Current ──▶ Deprecated ──▶ Sunset ──▶ Retired                       │ │
│  │     │            │           │           │                            │ │
│  │     │            │           │           ▼                            │ │
│  │     │            │           │      410 Gone                          │ │
│  │     │            │           ▼                                        │ │
│  │     │            │      301 Redirect to Current                       │ │
│  │     │            ▼                                                   │ │
│  │     │       Deprecation Warning Header                               │ │
│  │     ▼                                                                │ │
│  │  Full Support                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Version Manager Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/version_manager.py
"""
API Version Manager for ResilienceAI API Gateway
Handles versioning, deprecation, and migration
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """API version status"""
    CURRENT = "current"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    RETIRED = "retired"


class VersionStrategy(Enum):
    """Version identification strategies"""
    URL_PATH = auto()
    HEADER = auto()
    QUERY_PARAM = auto()
    CONTENT_TYPE = auto()


@dataclass
class APIVersion:
    """API version definition"""
    version: str
    status: VersionStatus
    release_date: datetime
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    changes: List[str] = None
    migration_guide: Optional[str] = None
    documentation_url: Optional[str] = None
    
    def __post_init__(self):
        if self.changes is None:
            self.changes = []
    
    @property
    def is_active(self) -> bool:
        """Check if version is still active"""
        return self.status not in [VersionStatus.RETIRED]
    
    @property
    def is_deprecated(self) -> bool:
        """Check if version is deprecated"""
        return self.status in [VersionStatus.DEPRECATED, VersionStatus.SUNSET]


@dataclass
class VersionConfig:
    """Version configuration"""
    strategy: VersionStrategy
    header_name: str = "X-API-Version"
    query_param_name: str = "api-version"
    content_type_prefix: str = "application/vnd.resilienceai"
    default_version: str = "v1"
    supported_versions: List[str] = None
    
    def __post_init__(self):
        if self.supported_versions is None:
            self.supported_versions = ["v1"]


class VersionManager:
    """
    API Version Manager
    """
    
    def __init__(self, config: VersionConfig):
        self.config = config
        self.versions: Dict[str, APIVersion] = {}
        self._version_aliases: Dict[str, str] = {}
    
    def register_version(self, version: APIVersion) -> None:
        """Register an API version"""
        self.versions[version.version] = version
        logger.info(f"Registered API version: {version.version} ({version.status.value})")
    
    def add_alias(self, alias: str, target_version: str) -> None:
        """Add version alias"""
        self._version_aliases[alias] = target_version
    
    def extract_version(
        self,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str]
    ) -> Optional[str]:
        """Extract API version from request"""
        if self.config.strategy == VersionStrategy.URL_PATH:
            return self._extract_from_path(path)
        elif self.config.strategy == VersionStrategy.HEADER:
            return headers.get(self.config.header_name)
        elif self.config.strategy == VersionStrategy.QUERY_PARAM:
            return query_params.get(self.config.query_param_name)
        elif self.config.strategy == VersionStrategy.CONTENT_TYPE:
            return self._extract_from_content_type(headers.get("Content-Type", ""))
        
        return None
    
    def _extract_from_path(self, path: str) -> Optional[str]:
        """Extract version from URL path"""
        # Match patterns like /api/v1/, /v2/, /api/v1.2/
        match = re.search(r'/(?:api/)?(v\d+(?:\.\d+)?)(?:/|$)', path)
        return match.group(1) if match else None
    
    def _extract_from_content_type(self, content_type: str) -> Optional[str]:
        """Extract version from Content-Type header"""
        # Match patterns like application/vnd.resilienceai.v1+json
        pattern = f"{re.escape(self.config.content_type_prefix)}\\.(v\\d+(?:\\.\\d+)?)"
        match = re.search(pattern, content_type)
        return match.group(1) if match else None
    
    def resolve_version(self, version: Optional[str]) -> str:
        """Resolve version (handle aliases and defaults)"""
        if not version:
            return self.config.default_version
        
        # Check aliases
        if version in self._version_aliases:
            version = self._version_aliases[version]
        
        # Check if version exists
        if version in self.versions:
            return version
        
        # Return default if version not found
        logger.warning(f"Unknown API version: {version}, using default")
        return self.config.default_version
    
    def validate_version(self, version: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate API version
        Returns: (is_valid, warning_info)
        """
        version = self.resolve_version(version)
        
        if version not in self.versions:
            return False, None
        
        version_info = self.versions[version]
        
        if not version_info.is_active:
            return False, {
                "error": "Version retired",
                "message": f"API version {version} has been retired",
                "code": "VERSION_RETIRED"
            }
        
        warning = None
        if version_info.is_deprecated:
            warning = {
                "warning": "Version deprecated",
                "message": f"API version {version} is deprecated",
                "deprecation_date": version_info.deprecation_date.isoformat() if version_info.deprecation_date else None,
                "sunset_date": version_info.sunset_date.isoformat() if version_info.sunset_date else None,
                "migration_guide": version_info.migration_guide,
                "code": "VERSION_DEPRECATED"
            }
        
        return True, warning
    
    def get_version_headers(self, version: str) -> Dict[str, str]:
        """Get version-related response headers"""
        headers = {}
        
        version_info = self.versions.get(version)
        if not version_info:
            return headers
        
        headers["X-API-Version"] = version
        
        if version_info.is_deprecated:
            headers["Deprecation"] = "true"
            if version_info.sunset_date:
                headers["Sunset"] = version_info.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Link to latest version
        current_version = self.get_current_version()
        if current_version and current_version != version:
            headers["Link"] = f'</api/{current_version}/>; rel="latest-version"'
        
        return headers
    
    def get_current_version(self) -> Optional[str]:
        """Get current API version"""
        for version, info in self.versions.items():
            if info.status == VersionStatus.CURRENT:
                return version
        return None
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported versions"""
        return [
            v for v, info in self.versions.items()
            if info.is_active
        ]
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get version information"""
        info = self.versions.get(version)
        if not info:
            return None
        
        return {
            "version": info.version,
            "status": info.status.value,
            "release_date": info.release_date.isoformat(),
            "deprecation_date": info.deprecation_date.isoformat() if info.deprecation_date else None,
            "sunset_date": info.sunset_date.isoformat() if info.sunset_date else None,
            "changes": info.changes,
            "migration_guide": info.migration_guide,
            "documentation_url": info.documentation_url
        }
    
    def transform_path(self, path: str, from_version: str, to_version: str) -> str:
        """Transform path between versions"""
        # Simple path transformation
        return path.replace(f"/{from_version}/", f"/{to_version}/")


# ResilienceAI API Versions
RESILIENCEAI_VERSIONS = [
    APIVersion(
        version="v1",
        status=VersionStatus.STABLE,
        release_date=datetime(2024, 1, 1),
        changes=["Initial API release"],
        documentation_url="https://docs.resilienceai.io/api/v1"
    ),
    APIVersion(
        version="v2",
        status=VersionStatus.CURRENT,
        release_date=datetime(2025, 1, 1),
        changes=[
            "Added GraphQL support",
            "Improved pagination",
            "New analytics endpoints",
            "Enhanced geospatial queries"
        ],
        documentation_url="https://docs.resilienceai.io/api/v2"
    ),
    APIVersion(
        version="v3-beta",
        status=VersionStatus.CURRENT,
        release_date=datetime(2025, 6, 1),
        changes=[
            "Streaming API support",
            "WebSocket real-time updates",
            "Advanced ML model management"
        ],
        documentation_url="https://docs.resilienceai.io/api/v3"
    ),
]


def create_version_manager() -> VersionManager:
    """Factory function to create configured version manager"""
    config = VersionConfig(
        strategy=VersionStrategy.URL_PATH,
        default_version="v2",
        supported_versions=["v1", "v2", "v3-beta"]
    )
    
    manager = VersionManager(config)
    
    for version in RESILIENCEAI_VERSIONS:
        manager.register_version(version)
    
    # Add aliases
    manager.add_alias("latest", "v2")
    manager.add_alias("beta", "v3-beta")
    
    return manager
```


---

## Developer Portal

### Developer Portal Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DEVELOPER PORTAL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Portal Components                                 │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   API       │  │   SDK       │  │   API Key   │  │   Usage     │  │ │
│  │  │   Docs      │  │   Downloads │  │   Management│  │   Analytics │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │ Interactive │  │   Code      │  │   Webhook   │  │   Support   │  │ │
│  │  │   Console   │  │   Examples  │  │   Config    │  │   Tickets   │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Portal Features                                   │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │ OpenAPI/S   │  │   GraphQL   │  │   Changelog │  │   Status    │  │ │
│  │  │ wagger UI   │  │   Playground│  │   Tracking  │  │   Page      │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Developer Portal Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/developer_portal.py
"""
Developer Portal for ResilienceAI API Gateway
Provides API documentation, key management, and interactive console
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


class APIKeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class UserTier(Enum):
    """User subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class APIKey:
    """API Key definition"""
    id: str
    key: str  # Hashed key
    name: str
    user_id: str
    tier: UserTier
    status: APIKeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    scopes: List[str]
    rate_limit: int
    allowed_ips: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if key is active"""
        if self.status != APIKeyStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def to_dict(self, include_key: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "scopes": self.scopes,
            "rate_limit": self.rate_limit,
            "allowed_ips": self.allowed_ips
        }
        
        if include_key:
            result["key"] = self.key
        
        return result


@dataclass
class APIEndpoint:
    """API endpoint documentation"""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    deprecated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "method": self.method,
            "summary": self.summary,
            "description": self.description,
            "parameters": self.parameters,
            "requestBody": self.request_body,
            "responses": self.responses,
            "tags": self.tags,
            "deprecated": self.deprecated
        }


@dataclass
class SDKPackage:
    """SDK package information"""
    language: str
    version: str
    download_url: str
    install_command: str
    documentation_url: str
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "version": self.version,
            "download_url": self.download_url,
            "install_command": self.install_command,
            "documentation_url": self.documentation_url,
            "last_updated": self.last_updated.isoformat()
        }


class APIKeyManager:
    """API Key management service"""
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}  # key_id -> APIKey
        self.key_index: Dict[str, str] = {}  # hashed_key -> key_id
        self.user_keys: Dict[str, List[str]] = {}  # user_id -> [key_ids]
    
    def generate_key(
        self,
        user_id: str,
        name: str,
        tier: UserTier = UserTier.FREE,
        scopes: Optional[List[str]] = None,
        expires_days: Optional[int] = None
    ) -> tuple[APIKey, str]:
        """
        Generate new API key
        Returns: (APIKey object, plain key string)
        """
        key_id = str(uuid.uuid4())
        plain_key = f"rai_{secrets.token_urlsafe(32)}"
        hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Get rate limit for tier
        rate_limit = self._get_tier_rate_limit(tier)
        
        api_key = APIKey(
            id=key_id,
            key=hashed_key,
            name=name,
            user_id=user_id,
            tier=tier,
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used_at=None,
            scopes=scopes or ["read:analytics"],
            rate_limit=rate_limit,
            allowed_ips=[]
        )
        
        # Store key
        self.keys[key_id] = api_key
        self.key_index[hashed_key] = key_id
        
        if user_id not in self.user_keys:
            self.user_keys[user_id] = []
        self.user_keys[user_id].append(key_id)
        
        logger.info(f"Generated API key: {key_id} for user: {user_id}")
        
        return api_key, plain_key
    
    def _get_tier_rate_limit(self, tier: UserTier) -> int:
        """Get rate limit for tier"""
        limits = {
            UserTier.FREE: 100,
            UserTier.BASIC: 1000,
            UserTier.PROFESSIONAL: 10000,
            UserTier.ENTERPRISE: 100000
        }
        return limits.get(tier, 100)
    
    def validate_key(self, plain_key: str) -> Optional[APIKey]:
        """Validate API key"""
        hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
        key_id = self.key_index.get(hashed_key)
        
        if not key_id:
            return None
        
        api_key = self.keys.get(key_id)
        if not api_key:
            return None
        
        if not api_key.is_active:
            return None
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        
        return api_key
    
    def revoke_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        api_key = self.keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return False
        
        api_key.status = APIKeyStatus.REVOKED
        logger.info(f"Revoked API key: {key_id}")
        return True
    
    def get_user_keys(self, user_id: str) -> List[APIKey]:
        """Get all keys for a user"""
        key_ids = self.user_keys.get(user_id, [])
        return [self.keys[kid] for kid in key_ids if kid in self.keys]
    
    def update_key_scopes(self, key_id: str, scopes: List[str]) -> bool:
        """Update key scopes"""
        api_key = self.keys.get(key_id)
        if not api_key:
            return False
        
        api_key.scopes = scopes
        return True


class DocumentationManager:
    """API documentation manager"""
    
    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self.openapi_spec: Optional[Dict[str, Any]] = None
    
    def add_endpoint(self, endpoint: APIEndpoint) -> None:
        """Add API endpoint documentation"""
        self.endpoints.append(endpoint)
    
    def generate_openapi_spec(self, version: str = "3.0.0") -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        spec = {
            "openapi": version,
            "info": {
                "title": "ResilienceAI API",
                "description": "API for ResilienceAI platform",
                "version": "2.0.0",
                "contact": {
                    "name": "ResilienceAI Support",
                    "email": "api@resilienceai.io",
                    "url": "https://support.resilienceai.io"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": "https://api.resilienceai.io",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.resilienceai.io",
                    "description": "Staging server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    },
                    "apiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                },
                "schemas": self._get_schemas()
            },
            "security": [
                {"bearerAuth": []},
                {"apiKeyAuth": []}
            ],
            "tags": [
                {"name": "Analytics", "description": "Analytics operations"},
                {"name": "Agents", "description": "Agent management"},
                {"name": "Data", "description": "Data operations"},
                {"name": "ML", "description": "Machine learning operations"},
                {"name": "Geospatial", "description": "Geospatial queries"}
            ]
        }
        
        # Group endpoints by path
        for endpoint in self.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}
            
            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": endpoint.parameters,
                "requestBody": endpoint.request_body,
                "responses": endpoint.responses,
                "deprecated": endpoint.deprecated
            }
        
        self.openapi_spec = spec
        return spec
    
    def _get_schemas(self) -> Dict[str, Any]:
        """Get common schemas"""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "string"},
                    "details": {"type": "object"}
                }
            },
            "AnalyticsRequest": {
                "type": "object",
                "properties": {
                    "dataset": {"type": "string"},
                    "metrics": {"type": "array", "items": {"type": "string"}},
                    "filters": {"type": "object"},
                    "time_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string", "format": "date-time"},
                            "end": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            },
            "AnalyticsResponse": {
                "type": "object",
                "properties": {
                    "data": {"type": "object"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "total_records": {"type": "integer"},
                            "page": {"type": "integer"},
                            "page_size": {"type": "integer"}
                        }
                    }
                }
            }
        }


class SDKManager:
    """SDK package manager"""
    
    def __init__(self):
        self.packages: Dict[str, SDKPackage] = {}
    
    def register_package(self, package: SDKPackage) -> None:
        """Register SDK package"""
        key = f"{package.language}-{package.version}"
        self.packages[key] = package
    
    def get_packages(self, language: Optional[str] = None) -> List[SDKPackage]:
        """Get SDK packages"""
        if language:
            return [p for p in self.packages.values() if p.language == language]
        return list(self.packages.values())
    
    def get_latest_package(self, language: str) -> Optional[SDKPackage]:
        """Get latest package for language"""
        packages = self.get_packages(language)
        if not packages:
            return None
        return max(packages, key=lambda p: p.last_updated)


class DeveloperPortal:
    """
    Main Developer Portal service
    """
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.doc_manager = DocumentationManager()
        self.sdk_manager = SDKManager()
        self._init_default_data()
    
    def _init_default_data(self) -> None:
        """Initialize default portal data"""
        # Register SDK packages
        self.sdk_manager.register_package(SDKPackage(
            language="python",
            version="2.1.0",
            download_url="https://pypi.org/project/resilienceai/",
            install_command="pip install resilienceai",
            documentation_url="https://docs.resilienceai.io/python",
            last_updated=datetime(2025, 1, 15)
        ))
        
        self.sdk_manager.register_package(SDKPackage(
            language="javascript",
            version="2.0.5",
            download_url="https://www.npmjs.com/package/resilienceai",
            install_command="npm install resilienceai",
            documentation_url="https://docs.resilienceai.io/javascript",
            last_updated=datetime(2025, 1, 10)
        ))
        
        self.sdk_manager.register_package(SDKPackage(
            language="java",
            version="2.0.0",
            download_url="https://maven.resilienceai.io/",
            install_command="<dependency>...",
            documentation_url="https://docs.resilienceai.io/java",
            last_updated=datetime(2025, 1, 5)
        ))
    
    def get_portal_info(self) -> Dict[str, Any]:
        """Get portal information"""
        return {
            "name": "ResilienceAI Developer Portal",
            "version": "2.0.0",
            "api_base_url": "https://api.resilienceai.io",
            "documentation_url": "https://docs.resilienceai.io",
            "support_url": "https://support.resilienceai.io",
            "status_page_url": "https://status.resilienceai.io",
            "features": [
                "api_documentation",
                "interactive_console",
                "api_key_management",
                "sdk_downloads",
                "usage_analytics",
                "webhook_configuration"
            ]
        }


# Predefined API endpoints for documentation
DEFAULT_ENDPOINTS = [
    APIEndpoint(
        path="/api/v2/analytics",
        method="GET",
        summary="List analytics",
        description="Retrieve a list of available analytics datasets",
        parameters=[
            {
                "name": "page",
                "in": "query",
                "description": "Page number",
                "schema": {"type": "integer", "default": 1}
            },
            {
                "name": "page_size",
                "in": "query",
                "description": "Items per page",
                "schema": {"type": "integer", "default": 20, "maximum": 100}
            }
        ],
        request_body=None,
        responses={
            "200": {
                "description": "List of analytics datasets",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AnalyticsResponse"}
                    }
                }
            }
        },
        tags=["Analytics"]
    ),
    APIEndpoint(
        path="/api/v2/analytics/query",
        method="POST",
        summary="Query analytics data",
        description="Execute an analytics query",
        parameters=[],
        request_body={
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/AnalyticsRequest"}
                }
            }
        },
        responses={
            "200": {
                "description": "Query results",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AnalyticsResponse"}
                    }
                }
            }
        },
        tags=["Analytics"]
    ),
]


def create_developer_portal() -> DeveloperPortal:
    """Factory function to create configured developer portal"""
    portal = DeveloperPortal()
    
    for endpoint in DEFAULT_ENDPOINTS:
        portal.doc_manager.add_endpoint(endpoint)
    
    return portal
```

---

## Implementation Code

### Main Gateway Application

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/main.py
"""
ResilienceAI API Gateway - Main Application
Entry point for the API gateway service
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from .router import create_router, GatewayRequest
from .load_balancer import create_load_balancer
from .auth_handler import create_auth_handler, AuthError
from .rate_limiter import create_rate_limiter, RateLimitExceeded
from .cache_manager import create_cache_manager
from .transformer import create_transform_engine, TransformContext
from .logger import create_logger, create_metrics_collector
from .version_manager import create_version_manager
from .developer_portal import create_developer_portal


# Global services
gateway_logger = None
metrics_collector = None
redis_client = None
router = None
load_balancer = None
auth_handler = None
rate_limiter = None
cache_manager = None
transform_engine = None
version_manager = None
developer_portal = None


async def initialize_services():
    """Initialize gateway services"""
    global gateway_logger, metrics_collector, redis_client
    global router, load_balancer, auth_handler, rate_limiter
    global cache_manager, transform_engine, version_manager, developer_portal
    
    # Initialize logger
    gateway_logger = create_logger()
    gateway_logger.info("Initializing ResilienceAI API Gateway...")
    
    # Initialize metrics
    metrics_collector = create_metrics_collector()
    
    # Initialize Redis
    try:
        redis_client = redis.Redis(
            host="redis-cluster",
            port=6379,
            decode_responses=True
        )
        await redis_client.ping()
        gateway_logger.info("Connected to Redis")
    except Exception as e:
        gateway_logger.warning(f"Redis connection failed: {e}, using in-memory fallback")
        redis_client = None
    
    # Initialize services
    router = create_router()
    load_balancer = create_load_balancer()
    auth_handler = create_auth_handler(redis_client)
    rate_limiter = create_rate_limiter(redis_client)
    cache_manager = create_cache_manager(redis_client)
    transform_engine = create_transform_engine()
    version_manager = create_version_manager()
    developer_portal = create_developer_portal()
    
    gateway_logger.info("All services initialized successfully")


async def shutdown_services():
    """Shutdown gateway services"""
    gateway_logger.info("Shutting down ResilienceAI API Gateway...")
    
    if redis_client:
        await redis_client.close()
    
    if load_balancer:
        load_balancer.shutdown()
    
    gateway_logger.info("Gateway shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    await initialize_services()
    yield
    await shutdown_services()


# Create FastAPI application
app = FastAPI(
    title="ResilienceAI API Gateway",
    description="Unified API Gateway for ResilienceAI Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resilienceai.io", "https://app.resilienceai.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)


@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Main gateway middleware"""
    import time
    
    start_time = time.time()
    
    # Generate correlation ID
    correlation_id = gateway_logger.set_correlation_id()
    
    # Create gateway request
    gateway_request = GatewayRequest(
        method=request.method,
        path=request.url.path,
        host=request.headers.get("host", ""),
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        client_ip=request.client.host if request.client else "",
        request_id=correlation_id
    )
    
    try:
        # Find matching route
        route, match_context = router.find_route(gateway_request)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Check API version
        version = version_manager.extract_version(
            request.url.path,
            dict(request.headers),
            dict(request.query_params)
        )
        version = version_manager.resolve_version(version)
        is_valid, version_warning = version_manager.validate_version(version)
        
        if not is_valid:
            raise HTTPException(status_code=410, detail=version_warning)
        
        # Authenticate request
        if "auth" in route.plugins:
            required_scopes = route.metadata.get("required_scopes", [])
            auth_context = auth_handler.authenticate(
                dict(request.headers),
                dict(request.query_params),
                required_scopes
            )
            metrics_collector.record_auth_attempt(
                auth_context.auth_method.value if auth_context.auth_method else "unknown",
                True
            )
        
        # Check rate limit
        if "rate-limit" in route.plugins:
            rate_limit_key = rate_limiter.get_limit_key(
                "user" if auth_context.user_id else "ip",
                auth_context.user_id or gateway_request.client_ip,
                route.path_conditions[0].pattern if route.path_conditions else "default"
            )
            rate_status = rate_limiter.check(rate_limit_key, route.upstream_service or "default")
        
        # Check cache
        cached_response = None
        if "cache" in route.plugins and request.method == "GET":
            cache_key = cache_manager.generate_key(
                request.method,
                request.url.path,
                str(request.query_params)
            )
            cached_response = cache_manager.get_cached_response(cache_key)
            if cached_response:
                metrics_collector.record_cache_hit("l1", route.upstream_service)
        
        if cached_response:
            response = JSONResponse(
                content=cached_response.get("body"),
                status_code=cached_response.get("status_code", 200),
                headers=cached_response.get("headers", {})
            )
        else:
            # Transform request
            transform_context = TransformContext(
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
                headers=dict(request.headers),
                body=None,
                metadata={
                    "request_id": correlation_id,
                    "client_ip": gateway_request.client_ip
                }
            )
            transform_context = transform_engine.transform_request(transform_context)
            
            # Route to backend
            backend = load_balancer.get_backend(route.upstream_service, gateway_request.client_ip)
            if not backend:
                raise HTTPException(status_code=503, detail="Service unavailable")
            
            # Forward request (simplified)
            response = await call_next(request)
        
        # Add version headers
        version_headers = version_manager.get_version_headers(version)
        for key, value in version_headers.items():
            response.headers[key] = value
        
        # Add rate limit headers
        if "rate-limit" in route.plugins:
            response.headers["X-RateLimit-Limit"] = str(rate_status.get("limit", -1))
            response.headers["X-RateLimit-Remaining"] = str(rate_status.get("remaining", -1))
        
        # Add correlation ID
        response.headers["X-Request-ID"] = correlation_id
        
        # Log request
        duration_ms = (time.time() - start_time) * 1000
        gateway_logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time_ms=duration_ms,
            client_ip=gateway_request.client_ip,
            user_agent=request.headers.get("user-agent", "")
        )
        
        # Record metrics
        metrics_collector.record_request(
            method=request.method,
            route=route.name,
            status_code=response.status_code,
            duration_seconds=duration_ms / 1000
        )
        
        return response
        
    except AuthError as e:
        gateway_logger.error(f"Authentication failed: {e.message}")
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.error_code, "message": e.message}
        )
    
    except RateLimitExceeded as e:
        gateway_logger.warning(f"Rate limit exceeded: {e}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": str(e),
                "retry_after": e.retry_after
            },
            headers={"Retry-After": str(e.retry_after)}
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        gateway_logger.error(f"Gateway error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "2.0.0",
        "timestamp": time.time()
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    checks = {
        "redis": redis_client is not None,
        "router": router is not None,
        "load_balancer": load_balancer is not None
    }
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks
    }


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Developer portal endpoints
@app.get("/docs/openapi.json")
async def openapi_spec():
    """OpenAPI specification"""
    return developer_portal.doc_manager.generate_openapi_spec()


@app.get("/docs/sdks")
async def list_sdks():
    """List available SDKs"""
    packages = developer_portal.sdk_manager.get_packages()
    return {
        "sdks": [p.to_dict() for p in packages]
    }


# Gateway stats endpoint
@app.get("/gateway/stats")
async def gateway_stats():
    """Get gateway statistics"""
    return {
        "router": router.get_route_stats() if router else {},
        "cache": cache_manager.cache.get_stats() if cache_manager else {},
        "uptime": time.time() - start_time if 'start_time' in globals() else 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        log_level="info"
    )
```

---

## Deployment Configuration

### Docker Compose Configuration

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/docker-compose.yml

version: '3.8'

services:
  # API Gateway
  gateway:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=info
      - WORKERS=4
    depends_on:
      - redis
      - nginx
    networks:
      - gateway-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-upstreams.conf:/etc/nginx/conf.d/upstreams.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - gateway-network
    depends_on:
      - gateway

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - gateway-network
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

  # Redis Sentinel (for HA)
  redis-sentinel:
    image: redis:7-alpine
    ports:
      - "26379:26379"
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf:ro
    networks:
      - gateway-network
    command: redis-sentinel /etc/redis/sentinel.conf

  # Prometheus Metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - gateway-network

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards:ro
    networks:
      - gateway-network
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  # Jaeger Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    networks:
      - gateway-network

  # Kong Admin (optional)
  kong:
    image: kong:latest
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8443:8443"
      - "8444:8444"
    environment:
      - KONG_DATABASE=off
      - KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml
      - KONG_PROXY_ACCESS_LOG=/dev/stdout
      - KONG_ADMIN_ACCESS_LOG=/dev/stdout
      - KONG_PROXY_ERROR_LOG=/dev/stderr
      - KONG_ADMIN_ERROR_LOG=/dev/stderr
      - KONG_PLUGINS=bundled
    volumes:
      - ./kong-routes.yaml:/kong/declarative/kong.yml:ro
    networks:
      - gateway-network

networks:
  gateway-network:
    driver: bridge

volumes:
  redis-data:
  prometheus-data:
  grafana-data:
```

### Kubernetes Deployment

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/k8s-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilienceai-gateway
  namespace: resilienceai
  labels:
    app: gateway
    version: v2.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
        version: v2.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: gateway
          image: resilienceai/gateway:v2.0.0
          ports:
            - containerPort: 8080
              name: http
              protocol: TCP
          env:
            - name: REDIS_URL
              value: "redis://redis-cluster:6379"
            - name: LOG_LEVEL
              value: "info"
            - name: WORKERS
              value: "4"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: gateway-config
---
apiVersion: v1
kind: Service
metadata:
  name: gateway-service
  namespace: resilienceai
  labels:
    app: gateway
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
      name: http
  selector:
    app: gateway
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gateway-ingress
  namespace: resilienceai
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.resilienceai.io
      secretName: gateway-tls
  rules:
    - host: api.resilienceai.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: gateway-service
                port:
                  number: 8080
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gateway-hpa
  namespace: resilienceai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resilienceai-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

---

## Integration Approach

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GATEWAY INTEGRATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Integration Patterns                              │ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │   Service   │  │   Event     │  │   Message   │  │   API       │  │ │
│  │  │   Mesh      │  │   Driven    │  │   Queue     │  │   Gateway   │  │ │
│  │  │             │  │             │  │             │  │             │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Backend Service Integration                       │ │
│  │                                                                        │ │
│  │  Gateway ──▶ Service Mesh (Istio/Linkerd) ──▶ Backend Services       │ │
│  │              │                                                          │ │
│  │              ├──▶ Analytics Service                                     │ │
│  │              ├──▶ Agent Service                                         │ │
│  │              ├──▶ Data Service                                          │ │
│  │              ├──▶ ML Service                                            │ │
│  │              └──▶ Geospatial Service                                    │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Configuration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/gateway/integration.py
"""
Backend Service Integration for ResilienceAI API Gateway
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Backend service endpoint"""
    name: str
    url: str
    health_path: str = "/health"
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    circuit_breaker_threshold: float = 0.5


class ServiceMesh:
    """Service mesh integration"""
    
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize service mesh"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self):
        """Close service mesh"""
        if self.session:
            await self.session.close()
    
    def register_service(self, endpoint: ServiceEndpoint):
        """Register backend service"""
        self.services[endpoint.name] = endpoint
        logger.info(f"Registered service: {endpoint.name}")
    
    async def call_service(
        self,
        service_name: str,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None
    ) -> tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Call backend service
        Returns: (status_code, body, response_headers)
        """
        service = self.services.get(service_name)
        if not service:
            raise ValueError(f"Unknown service: {service_name}")
        
        url = f"{service.url}{path}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=body
            ) as response:
                status = response.status
                body = await response.json() if response.content_type == 'application/json' else await response.text()
                response_headers = dict(response.headers)
                
                return status, body, response_headers
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {service_name}")
            raise
        except Exception as e:
            logger.error(f"Error calling {service_name}: {e}")
            raise


# Service mesh configuration
SERVICE_MESH_CONFIG = [
    ServiceEndpoint(
        name="analytics",
        url="http://analytics-service:8080",
        timeout_seconds=30.0
    ),
    ServiceEndpoint(
        name="agent",
        url="http://agent-service:8081",
        timeout_seconds=60.0
    ),
    ServiceEndpoint(
        name="data",
        url="http://data-service:8082",
        timeout_seconds=30.0
    ),
    ServiceEndpoint(
        name="ml",
        url="http://ml-service:8083",
        timeout_seconds=120.0
    ),
    ServiceEndpoint(
        name="geospatial",
        url="http://geospatial-service:8084",
        timeout_seconds=45.0
    ),
    ServiceEndpoint(
        name="report",
        url="http://report-service:8085",
        timeout_seconds=300.0
    ),
]


async def create_service_mesh() -> ServiceMesh:
    """Factory function to create service mesh"""
    mesh = ServiceMesh()
    await mesh.initialize()
    
    for endpoint in SERVICE_MESH_CONFIG:
        mesh.register_service(endpoint)
    
    return mesh
```

---

## Implementation Priority

### Implementation Roadmap

| Phase | Component | Priority | Effort | Dependencies |
|-------|-----------|----------|--------|--------------|
| 1 | Request Routing | Critical | Medium | None |
| 1 | Load Balancing | Critical | Medium | None |
| 1 | Health Checks | Critical | Low | None |
| 2 | Authentication (JWT) | High | Medium | None |
| 2 | Rate Limiting | High | Medium | Redis |
| 2 | Basic Caching | High | Medium | Redis |
| 3 | Request/Response Logging | High | Low | None |
| 3 | Metrics Collection | High | Low | Prometheus |
| 4 | API Versioning | Medium | Low | None |
| 4 | Request Transformation | Medium | Medium | None |
| 5 | Advanced Caching | Medium | Medium | Redis Cluster |
| 5 | Circuit Breaker | Medium | Medium | None |
| 6 | Developer Portal | Low | High | All above |
| 6 | Distributed Tracing | Low | Medium | Jaeger |
| 7 | WebSocket Support | Low | High | None |
| 7 | GraphQL Gateway | Low | High | None |

### Phase 1: Core Gateway (Weeks 1-4)

1. **Request Routing**
   - Path-based routing
   - Method matching
   - Header/query matching
   - Priority-based route selection

2. **Load Balancing**
   - Round-robin algorithm
   - Health checks
   - Backend pool management

3. **Health Checks**
   - /health endpoint
   - /ready endpoint
   - Backend health monitoring

### Phase 2: Security & Control (Weeks 5-8)

1. **Authentication**
   - JWT token validation
   - API key authentication
   - Scope/role checking

2. **Rate Limiting**
   - Token bucket algorithm
   - Per-user/per-IP limits
   - Redis-backed distributed limits

3. **Caching**
   - Response caching
   - Cache invalidation
   - TTL management

### Phase 3: Observability (Weeks 9-10)

1. **Logging**
   - Structured logging
   - Correlation IDs
   - Access logs

2. **Metrics**
   - Prometheus integration
   - Request metrics
   - Error tracking

### Phase 4: Advanced Features (Weeks 11-14)

1. **API Versioning**
   - Version extraction
   - Deprecation handling
   - Migration support

2. **Transformation**
   - Header modification
   - Body transformation
   - Format conversion

### Phase 5: Production Ready (Weeks 15-16)

1. **High Availability**
   - Redis clustering
   - Circuit breaker
   - Graceful degradation

2. **Developer Experience**
   - Developer portal
   - API documentation
   - SDK downloads

---

## Summary

This comprehensive API Gateway design for ResilienceAI provides:

1. **Scalable Architecture**: Multi-layer design with edge, gateway, and service mesh layers
2. **Security**: JWT authentication, API keys, RBAC, rate limiting
3. **Performance**: Multi-level caching, load balancing, circuit breakers
4. **Observability**: Structured logging, metrics, distributed tracing
5. **Developer Experience**: Interactive portal, API documentation, SDKs
6. **Flexibility**: Multiple versioning strategies, request transformation

The implementation follows cloud-native principles with Kubernetes deployment, horizontal scaling, and service mesh integration for enterprise-grade API management.

---

## File Paths Summary

| Component | File Path |
|-----------|-----------|
| Main Gateway | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/main.py` |
| Router | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/router.py` |
| Load Balancer | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/load_balancer.py` |
| Auth Handler | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/auth_handler.py` |
| Rate Limiter | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/rate_limiter.py` |
| Cache Manager | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/cache_manager.py` |
| Transformer | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/transformer.py` |
| Logger | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/logger.py` |
| Version Manager | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/version_manager.py` |
| Developer Portal | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/developer_portal.py` |
| Integration | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/integration.py` |
| Kong Routes | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/kong-routes.yaml` |
| Nginx Config | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/nginx-upstreams.conf` |
| Docker Compose | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/docker-compose.yml` |
| K8s Deployment | `/mnt/okcomputer/output/resilience_ai_analysis/gateway/k8s-deployment.yaml` |
| Documentation | `/mnt/okcomputer/output/resilience_ai_analysis/87_api_gateway.md` |
