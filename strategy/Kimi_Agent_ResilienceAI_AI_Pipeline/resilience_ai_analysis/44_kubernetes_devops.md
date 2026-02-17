# ResilienceAI - Comprehensive Kubernetes Deployment Guide

## Executive Summary

This document provides a complete Kubernetes deployment architecture for ResilienceAI, transitioning from Streamlit Cloud to a scalable, production-ready microservices infrastructure. The deployment includes Helm charts, Istio service mesh, monitoring, and automated operations.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Kubernetes Architecture](#kubernetes-architecture)
3. [File Structure](#file-structure)
4. [Deployment Components](#deployment-components)
5. [Helm Charts](#helm-charts)
6. [Istio Service Mesh](#istio-service-mesh)
7. [Monitoring & Observability](#monitoring--observability)
8. [Deployment Procedures](#deployment-procedures)
9. [Implementation Priority](#implementation-priority)
10. [Integration Points](#integration-points)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL TRAFFIC                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INGRESS CONTROLLER (NGINX/Istio)                    │
│  • TLS Termination    • Rate Limiting    • WAF    • DDoS Protection         │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
┌───────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   app.resilienceai.com │  │api.resilienceai.com│  │ml.resilienceai.com│
│   (Streamlit Frontend) │  │  (API Gateway)     │  │  (gRPC ML API)    │
└───────────┬───────────┘  └────────┬─────────┘  └────────┬─────────┘
            │                       │                     │
            ▼                       ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ISTIO SERVICE MESH                                   │
│  • mTLS Encryption    • Traffic Management    • Circuit Breakers            │
│  • Observability      • Canary Deployments    • Security Policies           │
└─────────────────────────────────────────────────────────────────────────────┘
            │                       │                     │
            ▼                       ▼                     ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  resilience-ai   │    │  resilience-ai   │    │  resilience-ai   │
│      -app        │◄──►│    -gateway      │◄──►│      -ml         │
│  (3-20 replicas) │    │  (2-10 replicas) │    │  (2-10 replicas) │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────┬───────┴───────┬───────────────┘
                         ▼               ▼
         ┌──────────────────┐    ┌──────────────────┐
         │    PostgreSQL    │    │      Redis       │
         │   (StatefulSet)  │    │   (StatefulSet)  │
         │    100GB SSD     │    │    20GB SSD      │
         └──────────────────┘    └──────────────────┘
```

---

## Kubernetes Architecture

### Namespace Structure

| Namespace | Purpose | Istio Injection |
|-----------|---------|-----------------|
| `resilience-ai` | Production workloads | Enabled |
| `resilience-ai-staging` | Staging environment | Enabled |
| `resilience-ai-dev` | Development environment | Enabled |
| `istio-system` | Istio control plane | N/A |
| `monitoring` | Prometheus, Grafana, Loki | Optional |

### Service Architecture

```yaml
# Service Communication Flow
Client → Ingress → Istio Gateway → VirtualService → DestinationRule → Pod

# Internal Communication
App → Istio Sidecar → ML Service → Istio Sidecar → Response
      (mTLS)                    (mTLS)
```

---

## File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/kubernetes/
├── base/                           # Raw Kubernetes manifests
│   ├── 00-namespace.yaml          # Namespace definitions
│   ├── 01-configmaps.yaml         # Application configuration
│   ├── 02-secrets.yaml            # Secret templates
│   ├── 03-deployment-main.yaml    # Main app deployment
│   ├── 04-deployment-gateway.yaml # API gateway deployment
│   ├── 05-deployment-ml.yaml      # ML service deployment
│   ├── 06-statefulset-postgres.yaml # PostgreSQL StatefulSet
│   ├── 07-statefulset-redis.yaml  # Redis StatefulSet
│   ├── 08-hpa.yaml                # Horizontal Pod Autoscalers
│   └── 09-persistent-volumes.yaml # Storage configuration
│
├── helm/                          # Helm charts
│   └── resilience-ai/
│       ├── Chart.yaml             # Chart metadata
│       ├── values.yaml            # Default values
│       ├── values-dev.yaml        # Development values
│       ├── values-staging.yaml    # Staging values
│       ├── values-production.yaml # Production values
│       └── templates/
│           ├── _helpers.tpl       # Helper templates
│           ├── deployment.yaml    # Main deployment
│           ├── service.yaml       # Services
│           ├── hpa.yaml           # Autoscaling
│           ├── configmap.yaml     # ConfigMaps
│           ├── secret.yaml        # Secrets
│           ├── ingress.yaml       # Ingress rules
│           └── istio-gateway.yaml # Istio configuration
│
├── istio/                         # Istio service mesh
│   ├── 01-gateway.yaml            # Istio Gateway
│   ├── 02-virtualservices.yaml    # Traffic routing
│   ├── 03-destinationrules.yaml   # Traffic policies
│   ├── 04-security-policies.yaml  # Authorization
│   └── 05-ingress-controller.yaml # NGINX alternative
│
├── monitoring/                    # Observability
│   └── prometheus-servicemonitor.yaml
│
└── scripts/                       # Deployment scripts
    └── deploy.sh                  # Main deployment script
```

---

## Deployment Components

### 1. Main Application Deployment

**File**: `base/03-deployment-main.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilience-ai-app
  namespace: resilience-ai
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0  # Zero-downtime deployments
  selector:
    matchLabels:
      app: resilience-ai
      component: frontend
  template:
    spec:
      serviceAccountName: resilience-ai-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: resilience-ai
          image: resilience-ai/app:v2.0.0
          ports:
            - containerPort: 8501
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8501
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8501
```

**Key Features**:
- Rolling updates with zero downtime
- Security context (non-root, read-only filesystem)
- Health checks (liveness, readiness, startup)
- Resource limits and requests
- Init containers for database migrations

### 2. Horizontal Pod Autoscaler

**File**: `base/08-hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resilience-ai-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resilience-ai-app
  minReplicas: 3
  maxReplicas: 20
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
    scaleDown:
      stabilizationWindowSeconds: 300
    scaleUp:
      stabilizationWindowSeconds: 0
```

**Scaling Triggers**:
- CPU utilization > 70%
- Memory utilization > 80%
- HTTP requests/second > 1000
- Request latency > 500ms

### 3. PostgreSQL StatefulSet

**File**: `base/06-statefulset-postgres.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 100Gi
```

**Features**:
- Persistent storage with SSD
- Automated backups
- Prometheus metrics exporter
- Configurable connection pooling

### 4. Redis StatefulSet

**File**: `base/07-statefulset-redis.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 1
  template:
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command:
            - redis-server
            - /etc/redis/redis.conf
```

**Configuration**:
- AOF persistence enabled
- Memory limit: 1GB
- LRU eviction policy
- Prometheus metrics

---

## Helm Charts

### Chart Structure

```yaml
# Chart.yaml
apiVersion: v2
name: resilience-ai
description: ResilienceAI Platform - AI-powered resilience assessment
version: 2.0.0
appVersion: "2.0.0"
dependencies:
  - name: postgresql
    version: 12.12.10
    repository: https://charts.bitnami.com/bitnami
  - name: redis
    version: 18.6.1
    repository: https://charts.bitnami.com/bitnami
  - name: kube-prometheus-stack
    version: 55.5.0
    repository: https://prometheus-community.github.io/helm-charts
```

### Installation Commands

```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# Install with default values
helm install resilience-ai ./helm/resilience-ai \
  --namespace resilience-ai \
  --create-namespace

# Install with custom values
helm install resilience-ai ./helm/resilience-ai \
  --namespace resilience-ai \
  --values values-production.yaml

# Upgrade deployment
helm upgrade resilience-ai ./helm/resilience-ai \
  --namespace resilience-ai \
  --values values-production.yaml \
  --wait

# Rollback to previous version
helm rollback resilience-ai 1
```

---

## Istio Service Mesh

### Gateway Configuration

**File**: `istio/01-gateway.yaml`

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: resilience-ai-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      hosts:
        - "resilienceai.com"
      tls:
        mode: SIMPLE
        credentialName: resilience-ai-tls-secret
```

### VirtualService for Traffic Routing

**File**: `istio/02-virtualservices.yaml`

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: resilience-ai-app-vs
spec:
  hosts:
    - "app.resilienceai.com"
  gateways:
    - resilience-ai-gateway
  http:
    - route:
        - destination:
            host: resilience-ai-app
            subset: stable
          weight: 90
        - destination:
            host: resilience-ai-app
            subset: canary
          weight: 10
      timeout: 60s
      retries:
        attempts: 3
        perTryTimeout: 20s
```

### DestinationRule for Circuit Breaking

**File**: `istio/03-destinationrules.yaml`

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: resilience-ai-app-dr
spec:
  host: resilience-ai-app
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
    - name: stable
      labels:
        version: v2.0.0
    - name: canary
      labels:
        version: v2.1.0-canary
```

### Security Policies

**File**: `istio/04-security-policies.yaml`

```yaml
# Enforce mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT

# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: resilience-ai-app-authz
spec:
  selector:
    matchLabels:
      app: resilience-ai
  action: ALLOW
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/istio-system/sa/istio-ingressgateway"
```

---

## Monitoring & Observability

### Prometheus ServiceMonitor

**File**: `monitoring/prometheus-servicemonitor.yaml`

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: resilience-ai-app-metrics
spec:
  selector:
    matchLabels:
      app: resilience-ai
  endpoints:
    - port: metrics
      path: /metrics
      interval: 15s
```

### Alert Rules

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: resilience-ai-alerts
spec:
  groups:
    - name: resilience-ai
      rules:
        - alert: ResilienceAIHighErrorRate
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[5m])) /
            sum(rate(http_requests_total[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
```

### Key Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `http_requests_total` | Total HTTP requests | N/A |
| `http_request_duration_seconds` | Request latency | P95 < 2s |
| `container_cpu_usage_seconds` | CPU usage | < 80% |
| `container_memory_working_set_bytes` | Memory usage | < 85% |
| `pg_up` | Database health | = 1 |

---

## Deployment Procedures

### Using the Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy to development
./scripts/deploy.sh dev install

# Deploy to staging
./scripts/deploy.sh staging install

# Deploy to production
./scripts/deploy.sh prod install

# Upgrade existing deployment
./scripts/deploy.sh prod upgrade

# Check status
./scripts/deploy.sh prod status

# Rollback
./scripts/deploy.sh prod rollback 2
```

### Manual Deployment Steps

```bash
# 1. Create namespace
kubectl create namespace resilience-ai
kubectl label namespace resilience-ai istio-injection=enabled

# 2. Create secrets
kubectl create secret generic resilience-ai-secrets \
  --from-literal=DB_PASSWORD=<password> \
  --from-literal=JWT_SECRET=<secret> \
  --from-literal=OPENAI_API_KEY=<key> \
  -n resilience-ai

# 3. Apply base manifests
kubectl apply -f base/00-namespace.yaml
kubectl apply -f base/01-configmaps.yaml
kubectl apply -f base/02-secrets.yaml

# 4. Apply deployments
kubectl apply -f base/03-deployment-main.yaml
kubectl apply -f base/04-deployment-gateway.yaml
kubectl apply -f base/05-deployment-ml.yaml

# 5. Apply StatefulSets
kubectl apply -f base/06-statefulset-postgres.yaml
kubectl apply -f base/07-statefulset-redis.yaml

# 6. Apply HPA
kubectl apply -f base/08-hpa.yaml

# 7. Apply Istio configurations
kubectl apply -f istio/

# 8. Verify deployment
kubectl get all -n resilience-ai
```

---

## Implementation Priority

### Phase 1: Foundation (Week 1-2)
1. ✅ Namespace and RBAC setup
2. ✅ ConfigMaps and Secrets management
3. ✅ PostgreSQL StatefulSet with persistence
4. ✅ Redis StatefulSet for caching
5. ✅ Basic application deployment

### Phase 2: Core Services (Week 3-4)
1. ✅ API Gateway deployment
2. ✅ ML service deployment
3. ✅ Horizontal Pod Autoscaling
4. ✅ Health checks and probes
5. ✅ Rolling update configuration

### Phase 3: Service Mesh (Week 5-6)
1. ✅ Istio installation
2. ✅ Gateway and VirtualServices
3. ✅ mTLS encryption
4. ✅ Circuit breakers
5. ✅ Traffic routing

### Phase 4: Production Hardening (Week 7-8)
1. ✅ Monitoring stack (Prometheus, Grafana)
2. ✅ Logging (Loki, Fluentd)
3. ✅ Distributed tracing (Jaeger)
4. ✅ Backup and disaster recovery
5. ✅ Security policies

---

## Integration Points

### External Services

| Service | Integration Type | Configuration |
|---------|-----------------|---------------|
| OpenAI API | REST API | `OPENAI_API_KEY` secret |
| SendGrid | SMTP | `SMTP_PASSWORD` secret |
| AWS S3 | Object Storage | `AWS_ACCESS_KEY_ID` secret |
| Datadog | Monitoring | `DATADOG_API_KEY` secret |

### Internal Services

| Service | Protocol | Endpoint |
|---------|----------|----------|
| PostgreSQL | TCP/5432 | `postgres:5432` |
| Redis | TCP/6379 | `redis:6379` |
| ML Service | HTTP/5000 | `resilience-ai-ml:5000` |
| API Gateway | HTTP/8080 | `resilience-ai-gateway:8080` |

---

## Generated Files

All Kubernetes deployment files have been generated and saved to:

```
/mnt/okcomputer/output/resilience_ai_analysis/kubernetes/
├── base/
│   ├── 00-namespace.yaml
│   ├── 01-configmaps.yaml
│   ├── 02-secrets.yaml
│   ├── 03-deployment-main.yaml
│   ├── 04-deployment-gateway.yaml
│   ├── 05-deployment-ml.yaml
│   ├── 06-statefulset-postgres.yaml
│   ├── 07-statefulset-redis.yaml
│   ├── 08-hpa.yaml
│   └── 09-persistent-volumes.yaml
├── helm/resilience-ai/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── hpa.yaml
│       ├── configmap.yaml
│       └── istio-gateway.yaml
├── istio/
│   ├── 01-gateway.yaml
│   ├── 02-virtualservices.yaml
│   ├── 03-destinationrules.yaml
│   ├── 04-security-policies.yaml
│   └── 05-ingress-controller.yaml
├── monitoring/
│   └── prometheus-servicemonitor.yaml
└── scripts/
    └── deploy.sh
```

---

## Next Steps

1. **Review and customize** the `values.yaml` for your environment
2. **Set up secrets** using your preferred secret management tool
3. **Configure DNS** to point to the ingress controller
4. **Install Istio** using the official installation guide
5. **Deploy monitoring stack** (Prometheus, Grafana)
6. **Run the deployment script** for your target environment
7. **Verify deployment** using the provided health check endpoints

---

## Support & Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs
- **Helm Documentation**: https://helm.sh/docs
- **Istio Documentation**: https://istio.io/latest/docs
- **Prometheus Documentation**: https://prometheus.io/docs

---

*Document Version: 2.0.0*
*Last Updated: January 2025*
