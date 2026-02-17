# ResilienceAI Service Mesh Architecture

## Executive Summary

This document provides a comprehensive service mesh implementation for ResilienceAI using Istio. The service mesh enables secure, observable, and resilient microservice communication with advanced traffic management capabilities.

---

## Table of Contents

1. [Service Mesh Architecture](#1-service-mesh-architecture)
2. [Istio Installation & Configuration](#2-istio-installation--configuration)
3. [Traffic Management](#3-traffic-management)
4. [Mutual TLS & Security](#4-mutual-tls--security)
5. [Observability Stack](#5-observability-stack)
6. [Circuit Breaking](#6-circuit-breaking)
7. [Canary Deployments](#7-canary-deployments)
8. [A/B Testing](#8-ab-testing)
9. [Performance Optimization](#9-performance-optimization)
10. [Implementation Priority](#10-implementation-priority)

---

## 1. Service Mesh Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Service Mesh                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────────────────────────┐ │
│  │   Ingress   │    │              Istio Control Plane                     │ │
│  │   Gateway   │───▶│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │ │
│  │  (Envoy)    │    │  │  Pilot  │  │ Citadel │  │ Galley  │  │Sidecar │ │ │
│  └─────────────┘    │  │(xDS/ADS)│  │  (mTLS) │  │(Config) │  │Injector│ │ │
│                     │  └─────────┘  └─────────┘  └─────────┘  └────────┘ │ │
│                     └─────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Data Plane (Envoy Sidecars)                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │ API      │  │ Auth     │  │ ML       │  │ Analytics│  │ Notification│ │
│  │  │ Gateway  │  │ Service  │  │ Engine   │  │ Service  │  │ Service  │ │ │
│  │  │(Envoy)   │  │(Envoy)   │  │(Envoy)   │  │(Envoy)   │  │(Envoy)   │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Observability Stack                                │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │Prometheus│  │  Grafana │  │  Jaeger  │  │  Kiali   │  │   Zipkin │ │ │
│  │  │(Metrics) │  │(Dashboard)│  │(Tracing) │  │(Topology)│  │(Tracing) │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Ingress Gateway** | External traffic entry point | Istio Gateway + Envoy |
| **Egress Gateway** | Controlled external access | Istio Egress Gateway |
| **Pilot** | Service discovery & traffic management | Istio Control Plane |
| **Citadel** | Certificate management & mTLS | Istio Security |
| **Galley** | Configuration validation | Istio Config |
| **Sidecar Injector** | Automatic proxy injection | Istio Webhook |
| **Envoy Proxy** | Data plane proxy | Envoy |

### 1.3 Service Mesh Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI Namespace                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   External Clients                                                          │
│        │                                                                    │
│        ▼                                                                    │
│   ┌─────────┐     ┌─────────────┐     ┌─────────────────────────────────┐  │
│   │   WAF   │────▶│ Istio       │────▶│  API Gateway Service            │  │
│   │ (AWS/   │     │ Ingress     │     │  - Rate Limiting                │  │
│   │ CloudFlare│   │ Gateway     │     │  - Authentication               │  │
│   └─────────┘     └─────────────┘     │  - Request Routing              │  │
│                                       └─────────────────────────────────┘  │
│                                                    │                        │
│        ┌───────────────────────────────────────────┼──────────────────┐    │
│        │                                           │                  │    │
│        ▼                                           ▼                  ▼    │
│   ┌──────────┐                              ┌──────────┐       ┌──────────┐│
│   │  Auth    │                              │  ML      │       │ Analytics││
│   │ Service  │◀────────────────────────────▶│ Engine   │◀─────▶│ Service  ││
│   │ - JWT    │                              │ - Predict│       │ - Metrics││
│   │ - OAuth2 │                              │ - Train  │       │ - Reports││
│   └──────────┘                              └──────────┘       └──────────┘│
│        │                                           │                        │
│        │                                    ┌──────┴──────┐                 │
│        │                                    ▼             ▼                 │
│        │                              ┌──────────┐  ┌──────────┐           │
│        │                              │ Model    │  │ Feature  │           │
│        │                              │ Registry │  │ Store    │           │
│        │                              └──────────┘  └──────────┘           │
│        │                                                                    │
│        └──────────────────────────────────────────────────────────────┐    │
│                                                                       ▼    │
│                                                                 ┌──────────┐│
│                                                                 │Notification│
│                                                                 │ Service  ││
│                                                                 │ - Email  ││
│                                                                 │ - Slack  ││
│                                                                 │ - Webhook││
│                                                                 └──────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Istio Installation & Configuration

### 2.1 Istio Installation (Istioctl)

```bash
# Download and install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.20.0
export PATH=$PWD/bin:$PATH

# Install Istio with default profile
istioctl install --set profile=default -y

# Verify installation
kubectl get pods -n istio-system
```

### 2.2 Custom Istio Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/istio-operator.yaml`**

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: resilience-ai-istio
spec:
  profile: default
  hub: docker.io/istio
  tag: 1.20.0
  
  # Global mesh configuration
  meshConfig:
    defaultConfig:
      proxyMetadata:
        ISTIO_META_DNS_CAPTURE: "true"
      tracing:
        sampling: 100.0
        customTags:
          environment:
            literal:
              value: "production"
      proxyStatsMatcher:
        inclusionRegexps:
          - ".*outlier_detection.*"
          - ".*circuit_breakers.*"
    enableAutoMtls: true
    enableTracing: true
    accessLogFile: /dev/stdout
    accessLogEncoding: JSON
    accessLogFormat: |
      {
        "timestamp": "%START_TIME%",
        "source": "%UPSTREAM_HOST%",
        "destination": "%DOWNSTREAM_REMOTE_ADDRESS%",
        "method": "%REQ(:METHOD)%",
        "path": "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%",
        "protocol": "%PROTOCOL%",
        "response_code": "%RESPONSE_CODE%",
        "response_flags": "%RESPONSE_FLAGS%",
        "bytes_received": "%BYTES_RECEIVED%",
        "bytes_sent": "%BYTES_SENT%",
        "duration": "%DURATION%",
        "upstream_service_time": "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%",
        "x_forwarded_for": "%REQ(X-FORWARDED-FOR)%",
        "user_agent": "%REQ(USER-AGENT)%",
        "request_id": "%REQ(X-REQUEST-ID)%",
        "authority": "%REQ(:AUTHORITY)%",
        "upstream_host": "%UPSTREAM_HOST%",
        "upstream_cluster": "%UPSTREAM_CLUSTER%",
        "upstream_local_address": "%UPSTREAM_LOCAL_ADDRESS%",
        "downstream_local_address": "%DOWNSTREAM_LOCAL_ADDRESS%",
        "downstream_remote_address": "%DOWNSTREAM_REMOTE_ADDRESS%",
        "requested_server_name": "%REQUESTED_SERVER_NAME%",
        "istio_policy_status": "%DYNAMIC_METADATA(istio.mixer:status)%"
      }
    
    # Enable telemetry
    defaultProviders:
      metrics:
      - prometheus
      tracing:
      - zipkin
  
  # Component configuration
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
        hpaSpec:
          minReplicas: 2
          maxReplicas: 5
          metrics:
          - type: Resource
            resource:
              name: cpu
              targetAverageUtilization: 80
        podDisruptionBudget:
          minAvailable: 1
        
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 512Mi
        hpaSpec:
          minReplicas: 2
          maxReplicas: 10
          metrics:
          - type: Resource
            resource:
              name: cpu
              targetAverageUtilization: 70
        service:
          type: LoadBalancer
          ports:
          - name: status-port
            port: 15021
            targetPort: 15021
          - name: http2
            port: 80
            targetPort: 8080
          - name: https
            port: 443
            targetPort: 8443
          - name: grpc
            port: 50051
            targetPort: 50051
          - name: tls
            port: 15443
            targetPort: 15443
        overlays:
        - apiVersion: apps/v1
          kind: Deployment
          name: istio-ingressgateway
          patches:
          - path: spec.template.spec.containers.[name:istio-proxy].securityContext.capabilities.add
            value: ["NET_ADMIN"]
            
    egressGateways:
    - name: istio-egressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        hpaSpec:
          minReplicas: 1
          maxReplicas: 5
          
  # Addon components
  addonComponents:
    grafana:
      enabled: true
    prometheus:
      enabled: true
    tracing:
      enabled: true
    kiali:
      enabled: true
      
  # Values configuration
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 500m
            memory: 256Mi
      
    pilot:
      env:
        PILOT_ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY: "true"
        PILOT_ENABLE_K8S_SELECT_WORKLOAD_ENTRIES: "true"
        PILOT_ENABLE_ANALYSIS: "true"
        
    grafana:
      enabled: true
      persist: true
      storageClassName: standard
      accessMode: ReadWriteOnce
      
    prometheus:
      enabled: true
      retention: 30d
      
    kiali:
      enabled: true
      dashboard:
        auth:
          strategy: anonymous
        viewOnlyMode: false
```

### 2.3 Namespace Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/namespace-labels.yaml`**

```yaml
# Enable automatic sidecar injection for ResilienceAI namespace
apiVersion: v1
kind: Namespace
metadata:
  name: resilience-ai
  labels:
    istio-injection: enabled
    app.kubernetes.io/name: resilience-ai
    app.kubernetes.io/part-of: resilience-ai-platform
---
# Production namespace
apiVersion: v1
kind: Namespace
metadata:
  name: resilience-ai-prod
  labels:
    istio-injection: enabled
    environment: production
---
# Staging namespace
apiVersion: v1
kind: Namespace
metadata:
  name: resilience-ai-staging
  labels:
    istio-injection: enabled
    environment: staging
---
# Canary namespace
apiVersion: v1
kind: Namespace
metadata:
  name: resilience-ai-canary
  labels:
    istio-injection: enabled
    environment: canary
```

---

## 3. Traffic Management

### 3.1 Gateway Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/gateway.yaml`**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: resilience-ai-gateway
  namespace: resilience-ai
  annotations:
    description: "Main ingress gateway for ResilienceAI platform"
spec:
  selector:
    istio: ingressgateway
  servers:
  # HTTP - Redirect to HTTPS
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "resilience-ai.example.com"
    - "api.resilience-ai.example.com"
    - "*.resilience-ai.example.com"
    tls:
      httpsRedirect: true
  
  # HTTPS - Primary traffic
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: resilience-ai-tls-cert
      minProtocolVersion: TLSV1_2
      cipherSuites:
      - ECDHE-RSA-AES256-GCM-SHA384
      - ECDHE-RSA-AES128-GCM-SHA256
    hosts:
    - "resilience-ai.example.com"
    - "api.resilience-ai.example.com"
    - "*.resilience-ai.example.com"
  
  # gRPC for internal services
  - port:
      number: 50051
      name: grpc
      protocol: GRPC
    tls:
      mode: SIMPLE
      credentialName: resilience-ai-tls-cert
    hosts:
    - "grpc.resilience-ai.example.com"
---
# Internal gateway for service-to-service communication
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: resilience-ai-internal-gateway
  namespace: resilience-ai
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 15443
      name: tls
      protocol: TLS
    tls:
      mode: ISTIO_MUTUAL
    hosts:
    - "*.resilience-ai.svc.cluster.local"
```

### 3.2 VirtualService - Main API Routing

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/virtualservice-api.yaml`**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-gateway-vs
  namespace: resilience-ai
spec:
  hosts:
  - "api.resilience-ai.example.com"
  gateways:
  - resilience-ai-gateway
  http:
  # Authentication routes
  - match:
    - uri:
        prefix: /api/v1/auth
    route:
    - destination:
        host: auth-service
        port:
          number: 8080
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
    
  # ML Engine routes
  - match:
    - uri:
        prefix: /api/v1/ml
    route:
    - destination:
        host: ml-engine
        port:
          number: 8080
      weight: 100
    timeout: 30s
    retries:
      attempts: 2
      perTryTimeout: 15s
      retryOn: gateway-error,connect-failure,refused-stream,cancelled,deadline-exceeded
    corsPolicy:
      allowOrigins:
      - exact: "https://resilience-ai.example.com"
      - exact: "https://app.resilience-ai.example.com"
      allowMethods:
      - GET
      - POST
      - PUT
      - DELETE
      - OPTIONS
      allowHeaders:
      - authorization
      - content-type
      - x-request-id
      allowCredentials: true
      maxAge: "24h"
    
  # Analytics routes
  - match:
    - uri:
        prefix: /api/v1/analytics
    route:
    - destination:
        host: analytics-service
        port:
          number: 8080
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
    
  # Prediction routes - High priority
  - match:
    - uri:
        prefix: /api/v1/predict
    - headers:
        x-priority:
          exact: high
    route:
    - destination:
        host: ml-engine
        port:
          number: 8080
        subset: stable
      weight: 90
    - destination:
        host: ml-engine
        port:
          number: 8080
        subset: canary
      weight: 10
    timeout: 5s
    
  # Default routes
  - route:
    - destination:
        host: api-gateway
        port:
          number: 8080
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
---
# Web UI VirtualService
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: web-ui-vs
  namespace: resilience-ai
spec:
  hosts:
  - "resilience-ai.example.com"
  - "app.resilience-ai.example.com"
  gateways:
  - resilience-ai-gateway
  http:
  # Static assets - Long cache
  - match:
    - uri:
        prefix: /static/
    route:
    - destination:
        host: web-ui
        port:
          number: 80
    cache:
      maxAge: 1h
    
  # API calls
  - match:
    - uri:
        prefix: /api/
    route:
    - destination:
        host: api-gateway
        port:
          number: 8080
    
  # Default - Serve React app
  - route:
    - destination:
        host: web-ui
        port:
          number: 80
```

### 3.3 DestinationRule - Service Subsets & Load Balancing

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/destinationrules.yaml`**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-engine-dr
  namespace: resilience-ai
spec:
  host: ml-engine
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30ms
        tcpKeepalive:
          time: 300s
          interval: 75s
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 100
        maxRetries: 3
    loadBalancer:
      simple: LEAST_REQUEST
      localityLbSetting:
        enabled: true
        failover:
        - from: us-east-1
          to: us-west-2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      consecutiveGatewayErrors: 3
      consecutiveLocalOriginFailures: 5
    portLevelSettings:
    - port:
        number: 8080
      connectionPool:
        http:
          http2MaxRequests: 500
  subsets:
  - name: stable
    labels:
      version: stable
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
  - name: canary
    labels:
      version: canary
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
  - name: experimental
    labels:
      version: experimental
    trafficPolicy:
      connectionPool:
        http:
          http2MaxRequests: 100
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: auth-service-dr
  namespace: resilience-ai
spec:
  host: auth-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 50
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 50
    loadBalancer:
      simple: ROUND_ROBIN
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: analytics-service-dr
  namespace: resilience-ai
spec:
  host: analytics-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 200
      http:
        http2MaxRequests: 2000
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutive5xxErrors: 10
      interval: 60s
      baseEjectionTime: 60s
  subsets:
  - name: stable
    labels:
      version: stable
  - name: beta
    labels:
      version: beta
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: notification-service-dr
  namespace: resilience-ai
spec:
  host: notification-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 30
      http:
        http1MaxPendingRequests: 30
    loadBalancer:
      simple: ROUND_ROBIN
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: stable
    labels:
      version: stable
```

### 3.4 ServiceEntry - External Services

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/serviceentries.yaml`**

```yaml
# AWS S3 for model storage
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: aws-s3
  namespace: resilience-ai
spec:
  hosts:
  - s3.amazonaws.com
  - *.s3.amazonaws.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
---
# Redis cache
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: redis-cache
  namespace: resilience-ai
spec:
  hosts:
  - redis-cache.resilience-ai.svc.cluster.local
  ports:
  - number: 6379
    name: redis
    protocol: TCP
  resolution: DNS
  location: MESH_INTERNAL
---
# PostgreSQL database
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: postgres-db
  namespace: resilience-ai
spec:
  hosts:
  - postgres.resilience-ai.svc.cluster.local
  ports:
  - number: 5432
    name: postgres
    protocol: TCP
  resolution: DNS
  location: MESH_INTERNAL
---
# External ML API (e.g., OpenAI)
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-ml-api
  namespace: resilience-ai
spec:
  hosts:
  - api.openai.com
  - api.anthropic.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
---
# Prometheus monitoring
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: prometheus-monitoring
  namespace: resilience-ai
spec:
  hosts:
  - prometheus.monitoring.svc.cluster.local
  ports:
  - number: 9090
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_INTERNAL
```

### 3.5 EnvoyFilter - Custom Envoy Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/envoyfilters.yaml`**

```yaml
# Custom rate limiting at Envoy level
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit-filter
  namespace: resilience-ai
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/udpa.type.v1.TypedStruct
          type_url: type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          value:
            stat_prefix: http_local_rate_limiter
            token_bucket:
              max_tokens: 1000
              tokens_per_fill: 100
              fill_interval: 1s
            filter_enabled:
              runtime_key: local_rate_limit_enabled
              default_value:
                numerator: 100
                denominator: HUNDRED
            filter_enforced:
              runtime_key: local_rate_limit_enforced
              default_value:
                numerator: 100
                denominator: HUNDRED
            response_headers_to_add:
            - append_action: OVERWRITE_IF_EXISTS_OR_ADD
              header:
                key: x-local-rate-limit
                value: 'true'
---
# Custom Lua script for request transformation
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: lua-transform
  namespace: resilience-ai
spec:
  workloadSelector:
    labels:
      app: ml-engine
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.lua
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inlineCode: |
            function envoy_on_request(request_handle)
              -- Add request ID if not present
              local request_id = request_handle:headers():get("x-request-id")
              if not request_id or request_id == "" then
                request_handle:headers():add("x-request-id", request_handle:streamInfo():dynamicMetadata():get("request.id"))
              end
              
              -- Add timestamp
              request_handle:headers():add("x-request-timestamp", os.date("%Y-%m-%dT%H:%M:%SZ"))
              
              -- Log request
              request_handle:logInfo("Request to ML Engine: " .. request_handle:headers():get(":path"))
            end
            
            function envoy_on_response(response_handle)
              -- Add response headers
              response_handle:headers():add("x-resilience-ai-version", "1.0.0")
              response_handle:headers():add("x-envoy-upstream-service-time", response_handle:headers():get("x-envoy-upstream-service-time") or "0")
            end
```

---

## 4. Mutual TLS & Security

### 4.1 PeerAuthentication - mTLS Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/security/peerauthentication.yaml`**

```yaml
# Global mTLS policy - STRICT mode
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: resilience-ai
spec:
  mtls:
    mode: STRICT
---
# Allow PERMISSIVE for specific services during migration
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: legacy-services
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: legacy-service
  mtls:
    mode: PERMISSIVE
  portLevelMtls:
    8080:
      mode: STRICT
---
# Port-level mTLS for specific ports
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: ml-engine-mtls
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: ml-engine
  mtls:
    mode: STRICT
  portLevelMtls:
    50051:  # gRPC port
      mode: STRICT
    8080:   # HTTP port
      mode: STRICT
```

### 4.2 RequestAuthentication - JWT Validation

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/security/requestauthentication.yaml`**

```yaml
# JWT authentication for API
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: api-jwt-auth
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  # Auth0 JWT
  - issuer: "https://resilience-ai.auth0.com/"
    jwksUri: "https://resilience-ai.auth0.com/.well-known/jwks.json"
    audiences:
    - "https://api.resilience-ai.example.com"
    forwardOriginalToken: true
    outputPayloadToHeader: x-jwt-payload
    fromHeaders:
    - name: authorization
      prefix: "Bearer "
    - name: x-access-token
  
  # Internal service JWT
  - issuer: "resilience-ai-internal"
    jwksUri: "http://auth-service.resilience-ai.svc.cluster.local:8080/.well-known/jwks.json"
    audiences:
    - "resilience-ai-services"
    forwardOriginalToken: false
---
# JWT for ML Engine
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: ml-engine-jwt-auth
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: ml-engine
  jwtRules:
  - issuer: "https://resilience-ai.auth0.com/"
    jwksUri: "https://resilience-ai.auth0.com/.well-known/jwks.json"
    forwardOriginalToken: true
```

### 4.3 AuthorizationPolicy - Access Control

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/security/authorizationpolicy.yaml`**

```yaml
# Deny all by default
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: resilience-ai
spec:
  {}
---
# Allow ingress gateway to all services
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-ingress
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: api-gateway
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account
---
# ML Engine authorization
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: ml-engine-authz
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: ml-engine
  action: ALLOW
  rules:
  # Allow from API Gateway
  - from:
    - source:
        principals:
        - cluster.local/ns/resilience-ai/sa/api-gateway
    to:
    - operation:
        methods:
        - GET
        - POST
        paths:
        - /api/v1/predict
        - /api/v1/ml/*
        - /health
        - /ready
  
  # Allow internal services
  - from:
    - source:
        principals:
        - cluster.local/ns/resilience-ai/sa/analytics-service
        - cluster.local/ns/resilience-ai/sa/notification-service
    to:
    - operation:
        methods:
        - GET
        - POST
        paths:
        - /api/v1/ml/models/*
  
  # Allow admin role for model management
  - from:
    - source:
        requestPrincipals:
        - "*"
    to:
    - operation:
        methods:
        - POST
        - PUT
        - DELETE
        paths:
        - /api/v1/ml/models
        - /api/v1/ml/models/*
        - /api/v1/ml/training/*
    when:
    - key: request.auth.claims[roles]
      values:
      - "admin"
      - "ml-engineer"
---
# Auth Service - Allow public access to login/register
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: auth-service-public
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: auth-service
  action: ALLOW
  rules:
  - to:
    - operation:
        methods:
        - POST
        paths:
        - /api/v1/auth/login
        - /api/v1/auth/register
        - /api/v1/auth/refresh
        - /api/v1/auth/forgot-password
        - /api/v1/auth/reset-password
        - /.well-known/jwks.json
  - to:
    - operation:
        methods:
        - GET
        paths:
        - /health
        - /ready
        - /metrics
---
# Analytics Service - Role-based access
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: analytics-service-authz
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: analytics-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/resilience-ai/sa/api-gateway
        - cluster.local/ns/resilience-ai/sa/ml-engine
    to:
    - operation:
        methods:
        - GET
        - POST
        paths:
        - /api/v1/analytics/*
  
  # Admin access to all analytics
  - from:
    - source:
        requestPrincipals:
        - "*"
    to:
    - operation:
        methods:
        - GET
        - POST
        - DELETE
        paths:
        - /api/v1/analytics/admin/*
    when:
    - key: request.auth.claims[roles]
      values:
      - "admin"
      - "analyst"
---
# Notification Service - Internal only
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: notification-service-authz
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: notification-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/resilience-ai/sa/api-gateway
        - cluster.local/ns/resilience-ai/sa/ml-engine
        - cluster.local/ns/resilience-ai/sa/analytics-service
        - cluster.local/ns/resilience-ai/sa/auth-service
    to:
    - operation:
        methods:
        - POST
        paths:
        - /api/v1/notifications/*
        - /api/v1/notifications/email
        - /api/v1/notifications/slack
        - /api/v1/notifications/webhook
```

### 4.4 Certificate Management

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/security/certificates.yaml`**

```yaml
# TLS certificate for ingress gateway
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: resilience-ai-tls
  namespace: istio-system
spec:
  secretName: resilience-ai-tls-cert
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - resilience-ai.example.com
  - api.resilience-ai.example.com
  - app.resilience-ai.example.com
  - grpc.resilience-ai.example.com
  - *.resilience-ai.example.com
---
# ClusterIssuer for Let's Encrypt
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@resilience-ai.example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: istio
---
# Internal CA for service-to-service mTLS
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: resilience-ai-ca
  namespace: resilience-ai
spec:
  ca:
    secretName: resilience-ai-ca-secret
```

---

## 5. Observability Stack

### 5.1 Prometheus Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/observability/prometheus.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: resilience-ai-prometheus
  namespace: monitoring
spec:
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      app: resilience-ai
  podMonitorSelector:
    matchLabels:
      app: resilience-ai
  retention: 30d
  retentionSize: 50GB
  resources:
    requests:
      memory: 2Gi
      cpu: 500m
    limits:
      memory: 8Gi
      cpu: 2000m
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: standard
        resources:
          requests:
            storage: 100Gi
  additionalScrapeConfigs:
  # Istio metrics
  - job_name: 'istio-mesh'
    kubernetes_sd_configs:
    - role: endpoints
      namespaces:
        names:
        - istio-system
    relabel_configs:
    - source_labels: [__meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: istio-proxy;http-envoy-prom
  
  # Envoy stats
  - job_name: 'envoy-stats'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - resilience-ai
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_container_port_name]
      action: keep
      regex: .*-envoy-prom
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:15090
      target_label: __address__
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: resilience-ai-services
  namespace: monitoring
  labels:
    app: resilience-ai
spec:
  namespaceSelector:
    matchNames:
    - resilience-ai
  selector:
    matchLabels:
      app: resilience-ai
  endpoints:
  - port: http-metrics
    interval: 15s
    path: /metrics
  - port: envoy-metrics
    interval: 15s
    path: /stats/prometheus
```

### 5.2 Grafana Dashboards

**File: `/mnt/okcomputer/output/resilience_ai_analysis/observability/grafana-dashboards.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: resilience-ai-dashboards
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  service-mesh-dashboard.json: |
    {
      "dashboard": {
        "title": "ResilienceAI Service Mesh",
        "tags": ["istio", "resilience-ai"],
        "timezone": "UTC",
        "panels": [
          {
            "id": 1,
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(istio_requests_total{namespace=\"resilience-ai\"}[5m])) by (destination_service)",
                "legendFormat": "{{ destination_service }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
          },
          {
            "id": 2,
            "title": "Error Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(istio_requests_total{namespace=\"resilience-ai\",response_code=~\"5..\"}[5m])) by (destination_service)",
                "legendFormat": "{{ destination_service }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
          },
          {
            "id": 3,
            "title": "P95 Latency",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{namespace=\"resilience-ai\"}[5m])) by (le, destination_service))",
                "legendFormat": "{{ destination_service }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
          },
          {
            "id": 4,
            "title": "Active Connections",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(envoy_cluster_upstream_cx_active{namespace=\"resilience-ai\"}) by (cluster_name)",
                "legendFormat": "{{ cluster_name }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
          },
          {
            "id": 5,
            "title": "Circuit Breaker Status",
            "type": "stat",
            "targets": [
              {
                "expr": "sum(envoy_cluster_circuit_breakers_default_cx_open{namespace=\"resilience-ai\"}) by (cluster_name)",
                "legendFormat": "{{ cluster_name }}"
              }
            ],
            "gridPos": {"h": 4, "w": 24, "x": 0, "y": 16}
          },
          {
            "id": 6,
            "title": "mTLS Status",
            "type": "table",
            "targets": [
              {
                "expr": "istio_mtls_connections_secure{namespace=\"resilience-ai\"}",
                "format": "table"
              }
            ],
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 20}
          }
        ]
      }
    }
  
  ml-engine-dashboard.json: |
    {
      "dashboard": {
        "title": "ML Engine Performance",
        "tags": ["ml", "resilience-ai"],
        "panels": [
          {
            "id": 1,
            "title": "Prediction Latency",
            "type": "heatmap",
            "targets": [
              {
                "expr": "sum(rate(ml_prediction_duration_seconds_bucket[5m])) by (le)",
                "legendFormat": ""
              }
            ]
          },
          {
            "id": 2,
            "title": "Model Load Time",
            "type": "graph",
            "targets": [
              {
                "expr": "ml_model_load_duration_seconds{namespace=\"resilience-ai\"}",
                "legendFormat": "{{ model_name }}"
              }
            ]
          },
          {
            "id": 3,
            "title": "Prediction Throughput",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(ml_predictions_total{namespace=\"resilience-ai\"}[5m])",
                "legendFormat": "{{ model_version }}"
              }
            ]
          }
        ]
      }
    }
```

### 5.3 Jaeger Tracing Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/observability/jaeger.yaml`**

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: resilience-ai-jaeger
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
        index-prefix: resilience-ai
  ingress:
    enabled: true
    hosts:
    - jaeger.resilience-ai.example.com
  resources:
    requests:
      memory: 2Gi
      cpu: 500m
    limits:
      memory: 8Gi
      cpu: 2000m
  collector:
    replicas: 2
    options:
      collector:
        queue-size: 2000
  agent:
    sidecar:
      injection: true
---
# Distributed tracing configuration for services
apiVersion: v1
kind: ConfigMap
metadata:
  name: tracing-config
  namespace: resilience-ai
data:
  tracing.yaml: |
    tracing:
      sampling:
        type: probabilistic
        param: 0.1
      zipkin:
        address: jaeger-collector.observability.svc.cluster.local:9411
      tags:
        service.name: ${SERVICE_NAME}
        service.namespace: resilience-ai
        deployment.environment: production
```

### 5.4 Kiali Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/observability/kiali.yaml`**

```yaml
apiVersion: kiali.io/v1alpha1
kind: Kiali
metadata:
  name: resilience-ai-kiali
  namespace: istio-system
spec:
  auth:
    strategy: anonymous
  deployment:
    accessible_namespaces:
    - "**"
    resources:
      requests:
        memory: 128Mi
        cpu: 100m
      limits:
        memory: 1Gi
        cpu: 500m
  server:
    web_root: /kiali
  external_services:
    prometheus:
      url: http://prometheus.monitoring.svc.cluster.local:9090
    grafana:
      enabled: true
      in_cluster_url: http://grafana.monitoring.svc.cluster.local:3000
      url: https://grafana.resilience-ai.example.com
    tracing:
      enabled: true
      in_cluster_url: http://jaeger-query.observability.svc.cluster.local:16686
      url: https://jaeger.resilience-ai.example.com
  kiali_feature_flags:
    validations:
      ignore: ["KIA1201"]
```

### 5.5 Custom Metrics with Telemetry API

**File: `/mnt/okcomputer/output/resilience_ai_analysis/observability/telemetry.yaml`**

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: resilience-ai-metrics
  namespace: resilience-ai
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    # Custom metric for ML predictions
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        model_name:
          operation: UPSERT
          value: "unknown"
        prediction_type:
          operation: UPSERT
          value: "unknown"
    # Custom metric for circuit breaker events
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        circuit_breaker_status:
          operation: UPSERT
          value: "closed"
  
  accessLogging:
  - providers:
    - name: envoy
    filter:
      expression: "response.code >= 400 || request.url_path.matches('.*admin.*')"
  
  tracing:
  - providers:
    - name: zipkin
    randomSamplingPercentage: 10.0
    customTags:
      service_mesh:
        literal:
          value: "istio"
      environment:
        environment:
          name: ENVIRONMENT
          defaultValue: "production"
```

---

## 6. Circuit Breaking

### 6.1 Circuit Breaker Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/circuit-breaking.yaml`**

```yaml
# ML Engine Circuit Breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-engine-circuit-breaker
  namespace: resilience-ai
spec:
  host: ml-engine
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30ms
        tcpKeepalive:
          time: 300s
          interval: 75s
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 100
        maxRetries: 3
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      # Eject host after 5 consecutive 5xx errors
      consecutive5xxErrors: 5
      # Check interval
      interval: 10s
      # Base ejection time (increases with each ejection)
      baseEjectionTime: 30s
      # Maximum percentage of hosts that can be ejected
      maxEjectionPercent: 50
      # Also consider gateway errors
      consecutiveGatewayErrors: 3
      # Consider local origin failures
      consecutiveLocalOriginFailures: 5
      # Success rate criteria
      successRate:
        minimumHosts: 3
        requestVolume: 100
        standardDeviationFactor: 1.4
---
# Auth Service Circuit Breaker - More strict
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: auth-service-circuit-breaker
  namespace: resilience-ai
spec:
  host: auth-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 50
        connectTimeout: 50ms
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 50
        maxRetries: 2
    loadBalancer:
      simple: ROUND_ROBIN
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 5s
      baseEjectionTime: 60s
      maxEjectionPercent: 30
      consecutiveGatewayErrors: 2
---
# Analytics Service Circuit Breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: analytics-service-circuit-breaker
  namespace: resilience-ai
spec:
  host: analytics-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 200
        connectTimeout: 100ms
      http:
        http1MaxPendingRequests: 200
        http2MaxRequests: 2000
        maxRequestsPerConnection: 200
        maxRetries: 5
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutive5xxErrors: 10
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 40
---
# External API Circuit Breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-api-circuit-breaker
  namespace: resilience-ai
spec:
  host: "api.openai.com"
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 20
        connectTimeout: 5s
      http:
        http1MaxPendingRequests: 20
        http2MaxRequests: 100
        maxRequestsPerConnection: 20
        maxRetries: 3
    loadBalancer:
      simple: ROUND_ROBIN
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 60s
      baseEjectionTime: 300s
      maxEjectionPercent: 100
```

### 6.2 Retry Policies

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/retry-policies.yaml`**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: retry-policies
  namespace: resilience-ai
spec:
  hosts:
  - ml-engine
  - auth-service
  - analytics-service
  http:
  # ML Engine - Retry on transient failures
  - match:
    - sourceLabels:
        app: api-gateway
    route:
    - destination:
        host: ml-engine
    retries:
      attempts: 3
      perTryTimeout: 10s
      retryOn: gateway-error,connect-failure,refused-stream,cancelled,deadline-exceeded,unavailable,internal
      retriableStatusCodes:
      - 503
      - 504
    timeout: 30s
    
  # Auth Service - Quick retries
  - match:
    - sourceLabels:
        app: api-gateway
    route:
    - destination:
        host: auth-service
    retries:
      attempts: 2
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
    timeout: 5s
    
  # Analytics Service - Longer retries for heavy queries
  - match:
    - sourceLabels:
        app: api-gateway
    route:
    - destination:
        host: analytics-service
    retries:
      attempts: 5
      perTryTimeout: 30s
      retryOn: gateway-error,connect-failure,refused-stream,unavailable
    timeout: 120s
```

### 6.3 Timeout Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/timeouts.yaml`**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: timeout-policies
  namespace: resilience-ai
spec:
  hosts:
  - "api.resilience-ai.example.com"
  http:
  # Quick operations
  - match:
    - uri:
        prefix: /api/v1/auth
    route:
    - destination:
        host: auth-service
    timeout: 5s
    
  # ML predictions
  - match:
    - uri:
        prefix: /api/v1/predict
    route:
    - destination:
        host: ml-engine
    timeout: 10s
    
  # Model training
  - match:
    - uri:
        prefix: /api/v1/ml/train
    route:
    - destination:
        host: ml-engine
    timeout: 300s  # 5 minutes for training
    
  # Analytics queries
  - match:
    - uri:
        prefix: /api/v1/analytics/reports
    route:
    - destination:
        host: analytics-service
    timeout: 60s
    
  # Default timeout
  - route:
    - destination:
        host: api-gateway
    timeout: 30s
```

---

## 7. Canary Deployments

### 7.1 Canary Deployment Strategy

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/canary-deployment.yaml`**

```yaml
# Canary deployment for ML Engine
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-engine-canary
  namespace: resilience-ai
spec:
  hosts:
  - ml-engine
  http:
  # Route based on headers for testing
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: ml-engine
        subset: canary
      weight: 100
    
  # Route based on user segment
  - match:
    - headers:
        x-user-segment:
          exact: "beta"
    route:
    - destination:
        host: ml-engine
        subset: canary
      weight: 100
    
  # Weighted traffic split
  - route:
    - destination:
        host: ml-engine
        subset: stable
      weight: 95
    - destination:
        host: ml-engine
        subset: canary
      weight: 5
---
# DestinationRule with subsets for canary
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-engine-canary-dr
  namespace: resilience-ai
spec:
  host: ml-engine
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
    loadBalancer:
      simple: ROUND_ROBIN
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: stable
    labels:
      version: stable
    trafficPolicy:
      connectionPool:
        http:
          http2MaxRequests: 1000
  - name: canary
    labels:
      version: canary
    trafficPolicy:
      connectionPool:
        http:
          http2MaxRequests: 500
---
# Progressive canary rollout
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ml-engine
  namespace: resilience-ai
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-engine
  service:
    port: 8080
    targetPort: 8080
    gateways:
    - resilience-ai-gateway
    hosts:
    - ml-engine.resilience-ai.svc.cluster.local
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.resilience-ai/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://ml-engine.resilience-ai.svc.cluster.local:8080/health"
    - name: conformance-test
      type: pre-rollout
      url: http://flagger-loadtester.resilience-ai/
      timeout: 30s
      metadata:
        type: bash
        cmd: "curl -sf http://ml-engine-canary.resilience-ai.svc.cluster.local:8080/ready"
    - name: promotion-gate
      type: confirm-promotion
      url: http://flagger-loadtester.resilience-ai/gate/check
      timeout: 10s
```

### 7.2 Automated Canary Analysis

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/canary-analysis.yaml`**

```yaml
# Prometheus metrics for canary analysis
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: canary-analysis-rules
  namespace: monitoring
spec:
  groups:
  - name: canary
    interval: 30s
    rules:
    # Success rate for canary
    - alert: CanaryHighErrorRate
      expr: |
        (
          sum(rate(istio_requests_total{namespace="resilience-ai",subset="canary",response_code!~"2.."}[5m]))
          /
          sum(rate(istio_requests_total{namespace="resilience-ai",subset="canary"}[5m]))
        ) > 0.01
      for: 2m
      labels:
        severity: warning
        service: ml-engine
      annotations:
        summary: "Canary deployment has high error rate"
        description: "Canary error rate is above 1%"
    
    # Latency comparison
    - alert: CanaryHighLatency
      expr: |
        (
          histogram_quantile(0.99, 
            sum(rate(istio_request_duration_milliseconds_bucket{namespace="resilience-ai",subset="canary"}[5m])) by (le)
          )
          >
          histogram_quantile(0.99, 
            sum(rate(istio_request_duration_milliseconds_bucket{namespace="resilience-ai",subset="stable"}[5m])) by (le)
          ) * 1.5
        )
      for: 2m
      labels:
        severity: warning
        service: ml-engine
      annotations:
        summary: "Canary latency is significantly higher than stable"
        description: "Canary P99 latency is 50% higher than stable"
---
# Automated rollback on failure
apiVersion: batch/v1
kind: CronJob
metadata:
  name: canary-rollback-monitor
  namespace: resilience-ai
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: rollback-check
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              ERROR_RATE=$(kubectl exec -n istio-system deploy/istio-ingressgateway -- \
                curl -s 'http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=sum(rate(istio_requests_total{namespace="resilience-ai",subset="canary",response_code=~"5.."}[5m]))/sum(rate(istio_requests_total{namespace="resilience-ai",subset="canary"}[5m]))' | \
                jq -r '.data.result[0].value[1] // "0"')
              
              if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
                echo "Canary error rate too high: $ERROR_RATE, triggering rollback"
                kubectl patch virtualservice ml-engine-canary -n resilience-ai --type='merge' -p '{"spec":{"http":[{"route":[{"destination":{"host":"ml-engine","subset":"stable"},"weight":100}]}]}}'
                kubectl patch deployment ml-engine-canary -n resilience-ai --type='merge' -p '{"spec":{"replicas":0}}'
              fi
          restartPolicy: OnFailure
```

---

## 8. A/B Testing

### 8.1 A/B Testing Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/ab-testing.yaml`**

```yaml
# A/B Testing for ML Model Versions
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-model-ab-test
  namespace: resilience-ai
spec:
  hosts:
  - ml-engine
  http:
  # Route based on user ID hash (consistent routing)
  - match:
    - headers:
        x-user-id:
          regex: "^[0-3].*"
    route:
    - destination:
        host: ml-engine
        subset: model-v1
      weight: 100
    
  # Route based on user ID hash (consistent routing)
  - match:
    - headers:
        x-user-id:
          regex: "^[4-7].*"
    route:
    - destination:
        host: ml-engine
        subset: model-v2
      weight: 100
    
  # Route based on A/B test cookie
  - match:
    - headers:
        cookie:
          regex: ".*ab_test_group=A.*"
    route:
    - destination:
        host: ml-engine
        subset: model-v1
      weight: 100
    
  - match:
    - headers:
        cookie:
          regex: ".*ab_test_group=B.*"
    route:
    - destination:
        host: ml-engine
        subset: model-v2
      weight: 100
    
  # Default split
  - route:
    - destination:
        host: ml-engine
        subset: model-v1
      weight: 50
    - destination:
        host: ml-engine
        subset: model-v2
      weight: 50
---
# DestinationRule for A/B test subsets
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-model-ab-dr
  namespace: resilience-ai
spec:
  host: ml-engine
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
    loadBalancer:
      simple: ROUND_ROBIN
  subsets:
  - name: model-v1
    labels:
      model-version: v1
      ab-test-group: control
  - name: model-v2
    labels:
      model-version: v2
      ab-test-group: treatment
---
# A/B Test for UI Features
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: web-ui-ab-test
  namespace: resilience-ai
spec:
  hosts:
  - web-ui
  http:
  # Route based on user agent
  - match:
    - headers:
        user-agent:
          regex: ".*Mobile.*"
    route:
    - destination:
        host: web-ui
        subset: mobile-version
      weight: 100
    
  # Route based on custom header from frontend
  - match:
    - headers:
        x-ui-version:
          exact: "v2"
    route:
    - destination:
        host: web-ui
        subset: v2
      weight: 100
    
  # Geographic routing
  - match:
    - headers:
        x-geo-region:
          exact: "EU"
    route:
    - destination:
        host: web-ui
        subset: eu-version
      weight: 100
    
  # Default
  - route:
    - destination:
        host: web-ui
        subset: v1
      weight: 80
    - destination:
        host: web-ui
        subset: v2
      weight: 20
```

### 8.2 A/B Test Metrics Collection

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/ab-test-metrics.yaml`**

```yaml
# Custom metrics for A/B testing
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: ab-test-metrics
  namespace: resilience-ai
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        ab_test_group:
          operation: UPSERT
          value: "unknown"
        model_version:
          operation: UPSERT
          value: "unknown"
  
  accessLogging:
  - providers:
    - name: envoy
    filter:
      expression: |
        request.headers['x-ab-test-group'] != '' || 
        request.headers['x-model-version'] != ''
---
# Prometheus recording rules for A/B test analysis
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ab-test-analysis
  namespace: monitoring
spec:
  groups:
  - name: ab-test
    interval: 30s
    rules:
    # Request count by A/B group
    - record: ab_test:request_count:rate5m
      expr: |
        sum(rate(istio_requests_total{namespace="resilience-ai"}[5m])) by (ab_test_group, destination_service)
    
    # Error rate by A/B group
    - record: ab_test:error_rate:rate5m
      expr: |
        sum(rate(istio_requests_total{namespace="resilience-ai",response_code=~"5.."}[5m])) by (ab_test_group, destination_service)
        /
        sum(rate(istio_requests_total{namespace="resilience-ai"}[5m])) by (ab_test_group, destination_service)
    
    # Latency by A/B group
    - record: ab_test:latency_p99:rate5m
      expr: |
        histogram_quantile(0.99,
          sum(rate(istio_request_duration_milliseconds_bucket{namespace="resilience-ai"}[5m])) by (le, ab_test_group, destination_service)
        )
    
    # Conversion rate (custom metric)
    - record: ab_test:conversion_rate:rate5m
      expr: |
        sum(rate(resilience_ai_conversion_total{namespace="resilience-ai"}[5m])) by (ab_test_group)
        /
        sum(rate(resilience_ai_page_view_total{namespace="resilience-ai"}[5m])) by (ab_test_group)
---
# Grafana dashboard for A/B testing
apiVersion: v1
kind: ConfigMap
metadata:
  name: ab-test-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  ab-test-dashboard.json: |
    {
      "dashboard": {
        "title": "A/B Test Analysis",
        "tags": ["ab-test", "resilience-ai"],
        "panels": [
          {
            "id": 1,
            "title": "Traffic Split",
            "type": "piechart",
            "targets": [
              {
                "expr": "sum(rate(istio_requests_total{namespace=\"resilience-ai\"}[5m])) by (ab_test_group)",
                "legendFormat": "{{ ab_test_group }}"
              }
            ]
          },
          {
            "id": 2,
            "title": "Error Rate by Group",
            "type": "graph",
            "targets": [
              {
                "expr": "ab_test:error_rate:rate5m",
                "legendFormat": "{{ ab_test_group }} - {{ destination_service }}"
              }
            ]
          },
          {
            "id": 3,
            "title": "P99 Latency by Group",
            "type": "graph",
            "targets": [
              {
                "expr": "ab_test:latency_p99:rate5m",
                "legendFormat": "{{ ab_test_group }} - {{ destination_service }}"
              }
            ]
          },
          {
            "id": 4,
            "title": "Conversion Rate",
            "type": "stat",
            "targets": [
              {
                "expr": "ab_test:conversion_rate:rate5m",
                "legendFormat": "{{ ab_test_group }}"
              }
            ]
          }
        ]
      }
    }
```

---

## 9. Performance Optimization

### 9.1 Performance Tuning Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/performance-tuning.yaml`**

```yaml
# Global performance settings
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: global-performance
  namespace: resilience-ai
spec:
  host: "*.resilience-ai.svc.cluster.local"
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
        connectTimeout: 10ms
        tcpKeepalive:
          time: 300s
          interval: 75s
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 1000
        http2MaxRequests: 5000
        maxRequestsPerConnection: 1000
        maxRetries: 3
    loadBalancer:
      simple: LEAST_REQUEST
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-east-1
          to:
            us-east-1a: 40
            us-east-1b: 35
            us-east-1c: 25
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
---
# Connection pool optimization for high-throughput services
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: high-throughput-optimization
  namespace: resilience-ai
spec:
  host: ml-engine
  trafficPolicy:
    portLevelSettings:
    - port:
        number: 50051  # gRPC
      connectionPool:
        http:
          h2UpgradePolicy: UPGRADE
          http2MaxRequests: 10000
          maxRequestsPerConnection: 1000
    - port:
        number: 8080  # HTTP
      connectionPool:
        http:
          http1MaxPendingRequests: 2000
          http2MaxRequests: 5000
---
# Envoy performance tuning
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: performance-envoy-filter
  namespace: resilience-ai
spec:
  configPatches:
  - applyTo: NETWORK_FILTER
    match:
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.tcp_proxy
    patch:
      operation: MERGE
      value:
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.tcp_proxy.v3.TcpProxy
          idle_timeout: 300s
          
  - applyTo: CLUSTER
    patch:
      operation: MERGE
      value:
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
          common_tls_context:
            tls_params:
              tls_minimum_protocol_version: TLSv1_2
              tls_maximum_protocol_version: TLSv1_3
              cipher_suites:
              - ECDHE-RSA-AES256-GCM-SHA384
              - ECDHE-RSA-AES128-GCM-SHA256
---
# Sidecar resource optimization
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: resilience-ai
spec:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY
  egress:
  - hosts:
    - "./*"
    - "istio-system/*"
    - "monitoring/*"
  - hosts:
    - "*/s3.amazonaws.com"
    - "*/api.openai.com"
    captureMode: NONE
---
# Sidecar proxy resources
apiVersion: v1
kind: ConfigMap
metadata:
  name: sidecar-resources
  namespace: resilience-ai
data:
  proxy.istio.io/config: |
    proxyMetadata:
      ISTIO_META_DNS_CAPTURE: "true"
      ISTIO_META_DNS_AUTO_ALLOCATE: "true"
    concurrency: 2
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 500m
        memory: 256Mi
```

### 9.2 Caching Strategy

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/caching.yaml`**

```yaml
# Envoy cache filter for API responses
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: api-cache
  namespace: resilience-ai
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.cache
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.cache.v3.CacheConfig
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.cache.simple_http_cache.v3.SimpleHttpCacheConfig
          max_body_bytes: 1048576  # 1MB
          allowed_vary_headers:
          - exact: accept
          - exact: accept-language
---
# Cache control headers
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: cache-control
  namespace: resilience-ai
spec:
  hosts:
  - ml-engine
  - analytics-service
  http:
  - match:
    - uri:
        prefix: /api/v1/models
    route:
    - destination:
        host: ml-engine
    headers:
      response:
        set:
          Cache-Control: "public, max-age=3600"
          X-Cache-Status: "HIT"
    
  - match:
    - uri:
        prefix: /api/v1/predict
    route:
    - destination:
        host: ml-engine
    headers:
      response:
        set:
          Cache-Control: "no-cache, no-store, must-revalidate"
          Pragma: "no-cache"
          Expires: "0"
```

### 9.3 Compression Configuration

**File: `/mnt/okcomputer/output/resilience_ai_analysis/istio/compression.yaml`**

```yaml
# Gzip compression for responses
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: gzip-compression
  namespace: resilience-ai
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.compressor
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.compressor.v3.Compressor
          compressor_library:
            name: text_optimized
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.compression.gzip.compressor.v3.Gzip
              memory_level: 9
              compression_level: BEST_SPEED
              compression_strategy: DEFAULT_STRATEGY
          response_direction_config:
            common_config:
              enabled:
                default_value: true
                runtime_key: response_compression_enabled
              content_type:
              - text/html
              - text/plain
              - text/css
              - application/javascript
              - application/json
              - application/xml
              - text/xml
              min_content_length: 100
          request_direction_config:
            common_config:
              enabled:
                default_value: true
                runtime_key: request_decompression_enabled
```

---

## 10. Implementation Priority

### 10.1 Implementation Roadmap

| Phase | Priority | Components | Timeline |
|-------|----------|------------|----------|
| **Phase 1** | Critical | Istio Installation, mTLS, Basic Traffic Management | Week 1-2 |
| **Phase 2** | High | Observability Stack, Security Policies | Week 3-4 |
| **Phase 3** | Medium | Circuit Breaking, Retry Policies | Week 5-6 |
| **Phase 4** | Medium | Canary Deployments, A/B Testing | Week 7-8 |
| **Phase 5** | Low | Performance Optimization, Advanced Features | Week 9-10 |

### 10.2 Phase 1: Foundation (Week 1-2)

```bash
#!/bin/bash
# Phase 1 Implementation Script
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/phase1-install.sh

echo "=== Phase 1: Service Mesh Foundation ==="

# 1. Install Istio
echo "Installing Istio..."
istioctl install -f ../istio/istio-operator.yaml -y

# 2. Label namespaces
echo "Configuring namespaces..."
kubectl apply -f ../istio/namespace-labels.yaml

# 3. Install certificates
echo "Installing certificates..."
kubectl apply -f ../istio/security/certificates.yaml

# 4. Configure gateways
echo "Configuring gateways..."
kubectl apply -f ../istio/gateway.yaml

# 5. Apply basic traffic management
echo "Applying traffic management..."
kubectl apply -f ../istio/virtualservice-api.yaml
kubectl apply -f ../istio/destinationrules.yaml

# 6. Enable mTLS
echo "Enabling mTLS..."
kubectl apply -f ../istio/security/peerauthentication.yaml

# 7. Verify installation
echo "Verifying installation..."
kubectl get pods -n istio-system
kubectl get gateway -n resilience-ai
kubectl get virtualservice -n resilience-ai
kubectl get destinationrule -n resilience-ai

echo "Phase 1 complete!"
```

### 10.3 Phase 2: Observability (Week 3-4)

```bash
#!/bin/bash
# Phase 2 Implementation Script
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/phase2-observability.sh

echo "=== Phase 2: Observability Stack ==="

# 1. Install Prometheus
echo "Installing Prometheus..."
kubectl apply -f ../observability/prometheus.yaml

# 2. Install Grafana
echo "Installing Grafana dashboards..."
kubectl apply -f ../observability/grafana-dashboards.yaml

# 3. Install Jaeger
echo "Installing Jaeger..."
kubectl apply -f ../observability/jaeger.yaml

# 4. Install Kiali
echo "Installing Kiali..."
kubectl apply -f ../observability/kiali.yaml

# 5. Configure telemetry
echo "Configuring telemetry..."
kubectl apply -f ../observability/telemetry.yaml

# 6. Apply security policies
echo "Applying security policies..."
kubectl apply -f ../istio/security/requestauthentication.yaml
kubectl apply -f ../istio/security/authorizationpolicy.yaml

echo "Phase 2 complete!"
```

### 10.4 Phase 3: Resilience (Week 5-6)

```bash
#!/bin/bash
# Phase 3 Implementation Script
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/phase3-resilience.sh

echo "=== Phase 3: Resilience Patterns ==="

# 1. Apply circuit breakers
echo "Applying circuit breakers..."
kubectl apply -f ../istio/circuit-breaking.yaml

# 2. Apply retry policies
echo "Applying retry policies..."
kubectl apply -f ../istio/retry-policies.yaml

# 3. Apply timeout policies
echo "Applying timeout policies..."
kubectl apply -f ../istio/timeouts.yaml

echo "Phase 3 complete!"
```

### 10.5 Phase 4: Advanced Deployments (Week 7-8)

```bash
#!/bin/bash
# Phase 4 Implementation Script
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/phase4-deployments.sh

echo "=== Phase 4: Advanced Deployment Patterns ==="

# 1. Install Flagger
echo "Installing Flagger..."
helm repo add flagger https://flagger.app
helm upgrade -i flagger flagger/flagger \
  --namespace=istio-system \
  --set crd.create=true \
  --set meshProvider=istio \
  --set metricsServer=http://prometheus:9090

# 2. Apply canary configuration
echo "Applying canary configuration..."
kubectl apply -f ../istio/canary-deployment.yaml
kubectl apply -f ../istio/canary-analysis.yaml

# 3. Apply A/B testing configuration
echo "Applying A/B testing configuration..."
kubectl apply -f ../istio/ab-testing.yaml
kubectl apply -f ../istio/ab-test-metrics.yaml

echo "Phase 4 complete!"
```

### 10.6 Phase 5: Performance (Week 9-10)

```bash
#!/bin/bash
# Phase 5 Implementation Script
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/phase5-performance.sh

echo "=== Phase 5: Performance Optimization ==="

# 1. Apply performance tuning
echo "Applying performance tuning..."
kubectl apply -f ../istio/performance-tuning.yaml

# 2. Apply caching
echo "Applying caching configuration..."
kubectl apply -f ../istio/caching.yaml

# 3. Apply compression
echo "Applying compression configuration..."
kubectl apply -f ../istio/compression.yaml

# 4. Apply service entries
echo "Applying service entries..."
kubectl apply -f ../istio/serviceentries.yaml

# 5. Apply envoy filters
echo "Applying envoy filters..."
kubectl apply -f ../istio/envoyfilters.yaml

echo "Phase 5 complete!"
echo "Service mesh implementation complete!"
```

---

## 11. Operational Runbooks

### 11.1 Common Operations

**File: `/mnt/okcomputer/output/resilience_ai_analysis/operations/runbooks.md`**

```markdown
# Service Mesh Operational Runbooks

## Check Service Mesh Health

```bash
# Check Istio control plane
kubectl get pods -n istio-system

# Check proxy status
istioctl proxy-status

# Check proxy config for a pod
istioctl proxy-config cluster <pod-name> -n resilience-ai
istioctl proxy-config listener <pod-name> -n resilience-ai
istioctl proxy-config route <pod-name> -n resilience-ai
```

## Debug Traffic Issues

```bash
# Check virtual services
kubectl get virtualservice -n resilience-ai -o yaml

# Check destination rules
kubectl get destinationrule -n resilience-ai -o yaml

# Test traffic routing
kubectl exec -it <source-pod> -n resilience-ai -- curl -v http://<destination-service>/path
```

## Handle Circuit Breaker Events

```bash
# Check circuit breaker status
kubectl exec -it <pod> -c istio-proxy -- curl localhost:15000/stats | grep outlier

# Reset circuit breaker (restart pod)
kubectl rollout restart deployment/<deployment-name> -n resilience-ai
```

## Rollback Deployments

```bash
# Rollback canary
kubectl patch virtualservice ml-engine-canary -n resilience-ai --type='merge' -p '{"spec":{"http":[{"route":[{"destination":{"host":"ml-engine","subset":"stable"},"weight":100}]}]}}'

# Rollback deployment
kubectl rollout undo deployment/<deployment-name> -n resilience-ai
```
```

---

## 12. Summary

This comprehensive service mesh implementation for ResilienceAI provides:

### Key Features Implemented:

1. **Service Mesh Architecture**: Complete Istio-based service mesh with control and data planes
2. **Istio Configuration**: Production-ready Istio operator configuration
3. **Traffic Management**: Advanced routing, load balancing, and traffic splitting
4. **Mutual TLS**: End-to-end encryption with automatic certificate management
5. **Observability**: Full stack with Prometheus, Grafana, Jaeger, and Kiali
6. **Circuit Breaking**: Automatic failure detection and traffic isolation
7. **Canary Deployments**: Automated progressive rollouts with Flagger
8. **A/B Testing**: Header-based and cookie-based traffic splitting
9. **Security Policies**: JWT authentication and fine-grained authorization
10. **Performance Optimization**: Connection pooling, caching, and compression

### File Structure:

```
/mnt/okcomputer/output/resilience_ai_analysis/
├── 88_service_mesh.md                    # This document
├── istio/
│   ├── istio-operator.yaml               # Istio installation config
│   ├── namespace-labels.yaml             # Namespace configuration
│   ├── gateway.yaml                      # Ingress gateway
│   ├── virtualservice-api.yaml           # API routing
│   ├── destinationrules.yaml             # Service subsets
│   ├── serviceentries.yaml               # External services
│   ├── envoyfilters.yaml                 # Custom Envoy config
│   ├── circuit-breaking.yaml             # Circuit breaker config
│   ├── retry-policies.yaml               # Retry configuration
│   ├── timeouts.yaml                     # Timeout policies
│   ├── performance-tuning.yaml           # Performance config
│   ├── caching.yaml                      # Caching strategy
│   ├── compression.yaml                  # Compression config
│   ├── canary-deployment.yaml            # Canary config
│   ├── canary-analysis.yaml              # Canary analysis
│   ├── ab-testing.yaml                   # A/B testing config
│   ├── ab-test-metrics.yaml              # A/B test metrics
│   └── security/
│       ├── peerauthentication.yaml       # mTLS config
│       ├── requestauthentication.yaml    # JWT config
│       ├── authorizationpolicy.yaml      # Access control
│       └── certificates.yaml             # Certificate management
├── observability/
│   ├── prometheus.yaml                   # Prometheus config
│   ├── grafana-dashboards.yaml           # Grafana dashboards
│   ├── jaeger.yaml                       # Jaeger tracing
│   ├── kiali.yaml                        # Kiali config
│   └── telemetry.yaml                    # Istio telemetry
├── scripts/
│   ├── phase1-install.sh                 # Phase 1 script
│   ├── phase2-observability.sh           # Phase 2 script
│   ├── phase3-resilience.sh              # Phase 3 script
│   ├── phase4-deployments.sh             # Phase 4 script
│   └── phase5-performance.sh             # Phase 5 script
└── operations/
    └── runbooks.md                       # Operational runbooks
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Platform Team*
