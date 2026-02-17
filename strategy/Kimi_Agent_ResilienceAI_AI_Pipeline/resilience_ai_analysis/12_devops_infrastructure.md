# ResilienceAI DevOps & Infrastructure Enhancement Plan

## Executive Summary

This document provides a comprehensive analysis of the current ResilienceAI deployment architecture and proposes enterprise-grade DevOps enhancements for production-scale deployment. The current setup includes Streamlit Cloud deployment, basic Kubernetes configuration, GitHub Actions CI/CD, and Archia Cloud integration.

**Current State Analysis:**
- ✅ Streamlit Cloud deployment configured
- ✅ Basic Kubernetes deployment manifest (436 lines)
- ✅ GitHub Actions CI/CD workflows (6 workflows)
- ✅ Archia Cloud integration
- ⚠️ Missing: Helm charts, Terraform, ArgoCD, advanced monitoring

---

## 1. Current Deployment Architecture Analysis

### 1.1 Existing Components

| Component | Current State | Location | Notes |
|-----------|--------------|----------|-------|
| Streamlit Config | ✅ Basic | `.streamlit/config.toml` | Theme + server settings |
| Kubernetes Manifest | ✅ Comprehensive | `archia/deployment.yaml` | 436 lines, production-ready |
| GitHub Actions | ✅ 6 workflows | `.github/workflows/` | CI/CD + agent automation |
| Archia Config | ✅ Configured | `archia/archia.toml` | Cloud orchestration |
| MCP Servers | ✅ Defined | `archia/mcp-servers.toml` | 23 MCP tools |
| Docker | ⚠️ Not found | N/A | Needs Dockerfile |
| Helm Charts | ❌ Missing | N/A | Required for K8s management |
| Terraform | ❌ Missing | N/A | Required for IaC |
| ArgoCD | ❌ Missing | N/A | Required for GitOps |
| Monitoring | ⚠️ Partial | K8s annotations only | Needs Prometheus/Grafana |

### 1.2 Current Kubernetes Configuration (archia/deployment.yaml)

```yaml
# Key Components Identified:
- Namespace: resilienceai
- Deployment: 2 replicas, RollingUpdate strategy
- Resources: 2Gi-4Gi memory, 1000m-2000m CPU
- HPA: 2-10 replicas, CPU 70%, Memory 80%
- PVC: 10Gi data, 5Gi models
- Ingress: nginx with TLS (cert-manager)
- NetworkPolicy: Restricted ingress/egress
- PDB: minAvailable 1
- CronJob: Daily data refresh at 2 AM
- ServiceAccount + RBAC
```

### 1.3 Current CI/CD Workflows

| Workflow | Purpose | Triggers |
|----------|---------|----------|
| `agent-swarm.yml` | Main CI validation | push: KIMI-2.5-Agent-Swarm, main |
| `gemini-dispatch.yml` | Agent dispatch | Manual/issue events |
| `gemini-invoke.yml` | Agent invocation | Manual triggers |
| `gemini-review.yml` | Code review | PR events |
| `gemini-triage.yml` | Issue triage | Issue events |
| `gemini-scheduled-triage.yml` | Scheduled triage | Cron schedule |

---

## 2. Proposed DevOps Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOUD PROVIDER                                  │
│                    (AWS/GCP/Azure - Multi-Region)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        VPC / Virtual Network                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │  Public     │  │  Private    │  │  Database   │  │  Bastion   │ │   │
│  │  │  Subnet     │  │  Subnet     │  │  Subnet     │  │  Host      │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────────┘ │   │
│  │         │                │                │                        │   │
│  │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐                │   │
│  │  │  Ingress    │  │  EKS/GKE/   │  │  RDS/       │                │   │
│  │  │  Controller │  │  AKS        │  │  Cloud SQL  │                │   │
│  │  │  (NLB/ALB)  │  │  (K8s)      │  │  (Postgres) │                │   │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────┘                │   │
│  │         │                │                                        │   │
│  │         │         ┌──────▼──────┐                                 │   │
│  │         │         │  Worker     │                                 │   │
│  │         │         │  Nodes      │                                 │   │
│  │         │         │  (Auto-scaled)│                               │   │
│  │         │         └──────┬──────┘                                 │   │
│  │         │                │                                        │   │
│  │         │         ┌──────▼──────┐                                 │   │
│  │         │         │  Pods       │                                 │   │
│  │         │         │  (ResilienceAI)│                              │   │
│  │         │         └─────────────┘                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     MANAGEMENT & MONITORING                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │  ArgoCD     │  │  Prometheus │  │  Grafana    │  │  Loki      │ │   │
│  │  │  (GitOps)   │  │  (Metrics)  │  │  (Dashboard)│  │  (Logs)    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           GITHUB & CI/CD PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Code    │───▶│  Build   │───▶│  Test    │───▶│  Deploy  │              │
│  │  Push    │    │  Image   │    │  Suite   │    │  (ArgoCD)│              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│       │               │               │               │                     │
│       ▼               ▼               ▼               ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  GitHub  │    │  Docker  │    │  pytest  │    │  Helm    │              │
│  │  Actions │    │  Build   │    │  security│    │  Upgrade │              │
│  │  (CI)    │    │  (ECR)   │    │  scan    │    │  (CD)    │              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Folder Structure Proposal

```
resilienceai-deployment/
├── README.md
├── docker/
│   ├── Dockerfile                    # Multi-stage build
│   ├── Dockerfile.dev                # Development image
│   ├── .dockerignore
│   └── docker-compose.yml            # Local development
├── kubernetes/
│   ├── base/                         # Kustomize base
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   └── network-policy.yaml
│   ├── overlays/
│   │   ├── development/
│   │   │   ├── kustomization.yaml
│   │   │   ├── replica-count.yaml
│   │   │   └── resource-limits.yaml
│   │   ├── staging/
│   │   │   ├── kustomization.yaml
│   │   │   └── patches/
│   │   └── production/
│   │       ├── kustomization.yaml
│   │       └── patches/
│   └── helm/                         # Helm charts
│       └── resilienceai/
│           ├── Chart.yaml
│           ├── values.yaml
│           ├── values-dev.yaml
│           ├── values-staging.yaml
│           ├── values-prod.yaml
│           └── templates/
│               ├── _helpers.tpl
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── ingress.yaml
│               ├── hpa.yaml
│               ├── pdb.yaml
│               ├── serviceaccount.yaml
│               ├── configmap.yaml
│               ├── secret.yaml
│               └── NOTES.txt
├── terraform/
│   ├── modules/
│   │   ├── vpc/
│   │   ├── eks/                      # or gke/ or aks/
│   │   ├── rds/                      # Database
│   │   ├── s3/                       # Object storage
│   │   ├── iam/
│   │   └── monitoring/
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── terraform.tfvars
│   │   ├── staging/
│   │   └── production/
│   └── backend.tf                    # Remote state
├── argocd/
│   ├── applications/
│   │   ├── resilienceai-dev.yaml
│   │   ├── resilienceai-staging.yaml
│   │   └── resilienceai-prod.yaml
│   ├── app-of-apps.yaml
│   └── projects/
│       └── resilienceai.yaml
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yaml
│   │   ├── service-monitor.yaml
│   │   └── rules/
│   │       ├── resilienceai-rules.yaml
│   │       └── alerts.yaml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── resilienceai-dashboard.json
│   │   │   └── kubernetes-dashboard.json
│   │   └── datasources.yaml
│   └── loki/
│       └── loki-config.yaml
├── github-actions/
│   ├── workflows/
│   │   ├── ci.yml                    # Main CI pipeline
│   │   ├── cd.yml                    # Deployment pipeline
│   │   ├── security-scan.yml
│   │   ├── terraform-apply.yml
│   │   └── release.yml
│   └── actions/
│       ├── build-image/
│       └── deploy-helm/
├── scripts/
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── setup-local.sh
│   └── migrate-data.sh
└── docs/
    ├── deployment-guide.md
    ├── operations-runbook.md
    └── disaster-recovery.md
```

---

## 4. Docker Optimization

### 4.1 Multi-Stage Dockerfile

```dockerfile
# File: docker/Dockerfile
# ResilienceAI Production Docker Image
# Multi-stage build for optimized production deployment

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# STAGE 2: Production
# ============================================================================
FROM python:3.10-slim AS production

# Security: Create non-root user
RUN groupadd -r resilienceai && useradd -r -g resilienceai resilienceai

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgeos-c1v5 \
    libproj25 \
    gdal-bin \
    libgdal32 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/resilienceai/.local

# Copy application code
COPY --chown=resilienceai:resilienceai . .

# Create necessary directories
RUN mkdir -p /data/processed /data/models /data/reports /app/logs \
    && chown -R resilienceai:resilienceai /app /data

# Set environment variables
ENV PATH=/home/resilienceai/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Switch to non-root user
USER resilienceai

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app/dashboard.py", "--server.address=0.0.0.0"]

# ============================================================================
# STAGE 3: Development
# ============================================================================
FROM production AS development

USER root

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython

USER resilienceai

# Default to shell for development
CMD ["/bin/bash"]
```

### 4.2 Docker Compose for Local Development

```yaml
# File: docker/docker-compose.yml
version: '3.8'

services:
  # Main ResilienceAI Application
  resilienceai:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    container_name: resilienceai-dev
    ports:
      - "8501:8501"
    volumes:
      - ../:/app
      - resilienceai-data:/data
    environment:
      - CENSUS_API_KEY=${CENSUS_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - STREAMLIT_SERVER_RUN_ON_SAVE=true
    networks:
      - resilienceai-network
    depends_on:
      - redis
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: resilienceai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - resilienceai-network

  # PostgreSQL for data storage
  postgres:
    image: postgres:15-alpine
    container_name: resilienceai-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=resilienceai
      - POSTGRES_PASSWORD=${DB_PASSWORD:-resilienceai}
      - POSTGRES_DB=resilienceai
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - resilienceai-network

  # MinIO for object storage (S3-compatible)
  minio:
    image: minio/minio:latest
    container_name: resilienceai-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    networks:
      - resilienceai-network

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: resilienceai-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ../monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - resilienceai-network

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: resilienceai-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ../monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ../monitoring/grafana/datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml
      - grafana-data:/var/lib/grafana
    networks:
      - resilienceai-network

volumes:
  resilienceai-data:
  redis-data:
  postgres-data:
  minio-data:
  prometheus-data:
  grafana-data:

networks:
  resilienceai-network:
    driver: bridge
```

---

## 5. Helm Charts

### 5.1 Chart.yaml

```yaml
# File: kubernetes/helm/resilienceai/Chart.yaml
apiVersion: v2
name: resilienceai
description: A Helm chart for ResilienceAI - Disaster Vulnerability Assessment Platform
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - resilience
  - disaster
  - vulnerability
  - healthcare
  - ai
home: https://github.com/GDogMcCoy/ResilienceAI
sources:
  - https://github.com/GDogMcCoy/ResilienceAI
maintainers:
  - name: ResilienceAI Team
    email: team@resilienceai.io
dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: 17.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  - name: ingress-nginx
    version: 4.x.x
    repository: https://kubernetes.github.io/ingress-nginx
    condition: ingress-nginx.enabled
```

### 5.2 values.yaml (Base Configuration)

```yaml
# File: kubernetes/helm/resilienceai/values.yaml
# Default values for resilienceai
# This is a YAML-formatted file.

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================
global:
  environment: production
  imageRegistry: ""
  imagePullSecrets: []
  storageClass: "standard"

# =============================================================================
# IMAGE CONFIGURATION
# =============================================================================
image:
  repository: archia/resilienceai
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

# =============================================================================
# SERVICE ACCOUNT
# =============================================================================
serviceAccount:
  create: true
  annotations: {}
  name: ""

# =============================================================================
# POD SECURITY CONTEXT
# =============================================================================
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================
service:
  type: ClusterIP
  port: 80
  targetPort: 8501
  annotations: {}

# =============================================================================
# INGRESS CONFIGURATION
# =============================================================================
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: resilienceai.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: resilienceai-tls
      hosts:
        - resilienceai.example.com

# =============================================================================
# RESOURCE CONFIGURATION
# =============================================================================
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi

# =============================================================================
# HORIZONTAL POD AUTOSCALER
# =============================================================================
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max

# =============================================================================
# POD DISRUPTION BUDGET
# =============================================================================
podDisruptionBudget:
  enabled: true
  minAvailable: 1

# =============================================================================
# NETWORK POLICY
# =============================================================================
networkPolicy:
  enabled: true
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8501
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 8501
  egress:
    - to: []
      ports:
        - protocol: TCP
          port: 443
        - protocol: TCP
          port: 80

# =============================================================================
# PERSISTENT VOLUME CLAIMS
# =============================================================================
persistence:
  data:
    enabled: true
    size: 10Gi
    accessMode: ReadWriteOnce
    storageClass: "standard"
    mountPath: /data/processed
  models:
    enabled: true
    size: 5Gi
    accessMode: ReadWriteOnce
    storageClass: "standard"
    mountPath: /data/models

# =============================================================================
# CONFIGURATION
# =============================================================================
config:
  # Archia server configuration
  ARCHIA_HOST: "0.0.0.0"
  ARCHIA_PORT: "8080"
  ARCHIA_LOG_LEVEL: "info"
  ARCHIA_WORKERS: "4"
  
  # Model configuration
  MODEL_PROVIDER: "anthropic"
  MODEL_NAME: "claude-sonnet-4-5-20250929"
  MODEL_TEMPERATURE: "0.3"
  MODEL_MAX_TOKENS: "4096"
  
  # Data paths
  DATA_PATH: "/data/processed/county_features.csv"
  MODELS_DIR: "/data/models"
  REPORTS_DIR: "/data/reports"
  
  # Feature flags
  ENABLE_FHIR_EXPORT: "true"
  ENABLE_GEOJSON_EXPORT: "true"
  ENABLE_SCENARIO_SIMULATION: "true"
  ENABLE_NETWORK_ANALYSIS: "true"
  ENABLE_SPATIAL_ANALYSIS: "true"
  
  # MCP server settings
  MCP_LOCAL_ENABLED: "true"
  MCP_CENSUS_ENABLED: "false"
  MCP_FEMA_ENABLED: "false"

# =============================================================================
# SECRETS (Use external secret management in production)
# =============================================================================
secrets:
  ANTHROPIC_API_KEY: ""
  CENSUS_API_KEY: ""

# =============================================================================
# PROBE CONFIGURATION
# =============================================================================
livenessProbe:
  enabled: true
  httpGet:
    path: /healthz
    port: 8501
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  enabled: true
  httpGet:
    path: /healthz
    port: 8501
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2

startupProbe:
  enabled: true
  httpGet:
    path: /healthz
    port: 8501
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 30

# =============================================================================
# CRONJOB CONFIGURATION
# =============================================================================
cronjob:
  enabled: true
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  command:
    - python
    - -m
    - src.data_refresh

# =============================================================================
# MONITORING
# =============================================================================
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    path: /metrics
    port: 8501

# =============================================================================
# DEPENDENCIES
# =============================================================================
postgresql:
  enabled: false
  auth:
    username: resilienceai
    password: resilienceai
    database: resilienceai
  primary:
    persistence:
      enabled: true
      size: 10Gi

redis:
  enabled: false
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 5Gi
```

### 5.3 values-production.yaml

```yaml
# File: kubernetes/helm/resilienceai/values-production.yaml
# Production overrides for resilienceai

replicaCount: 3

image:
  pullPolicy: Always
  tag: "v1.0.0-stable"

ingress:
  enabled: true
  hosts:
    - host: resilienceai.io
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: resilienceai-tls-prod
      hosts:
        - resilienceai.io
        - www.resilienceai.io

resources:
  limits:
    cpu: 4000m
    memory: 8Gi
  requests:
    cpu: 2000m
    memory: 4Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20

persistence:
  data:
    size: 50Gi
    storageClass: "fast-ssd"
  models:
    size: 20Gi
    storageClass: "fast-ssd"

config:
  ARCHIA_LOG_LEVEL: "warn"
  ARCHIA_WORKERS: "8"

postgresql:
  enabled: true
  auth:
    existingSecret: "resilienceai-db-credentials"
  primary:
    persistence:
      size: 100Gi
      storageClass: "fast-ssd"

redis:
  enabled: true
  master:
    persistence:
      size: 20Gi
```

### 5.4 Helm Template - deployment.yaml

```yaml
# File: kubernetes/helm/resilienceai/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "resilienceai.fullname" . }}
  labels:
    {{- include "resilienceai.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "resilienceai.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "{{ .Values.monitoring.enabled }}"
        prometheus.io/port: "{{ .Values.service.targetPort }}"
        prometheus.io/path: "/metrics"
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secrets: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
      labels:
        {{- include "resilienceai.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "resilienceai.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ include "resilienceai.fullname" . }}-secrets
                  key: ANTHROPIC_API_KEY
            - name: CENSUS_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ include "resilienceai.fullname" . }}-secrets
                  key: CENSUS_API_KEY
          envFrom:
            - configMapRef:
                name: {{ include "resilienceai.fullname" . }}-config
          volumeMounts:
            - name: data-volume
              mountPath: /data/processed
            - name: models-volume
              mountPath: /data/models
            - name: tmp-volume
              mountPath: /tmp
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.livenessProbe.enabled }}
          livenessProbe:
            {{- toYaml .Values.livenessProbe | nindent 12 }}
          {{- end }}
          {{- if .Values.readinessProbe.enabled }}
          readinessProbe:
            {{- toYaml .Values.readinessProbe | nindent 12 }}
          {{- end }}
          {{- if .Values.startupProbe.enabled }}
          startupProbe:
            {{- toYaml .Values.startupProbe | nindent 12 }}
          {{- end }}
      volumes:
        - name: data-volume
          {{- if .Values.persistence.data.enabled }}
          persistentVolumeClaim:
            claimName: {{ include "resilienceai.fullname" . }}-data
          {{- else }}
          emptyDir: {}
          {{- end }}
        - name: models-volume
          {{- if .Values.persistence.models.enabled }}
          persistentVolumeClaim:
            claimName: {{ include "resilienceai.fullname" . }}-models
          {{- else }}
          emptyDir: {}
          {{- end }}
        - name: tmp-volume
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app.kubernetes.io/name
                      operator: In
                      values:
                        - {{ include "resilienceai.name" . }}
                topologyKey: kubernetes.io/hostname
```

---

## 6. Terraform Infrastructure as Code

### 6.1 AWS EKS Module

```hcl
# File: terraform/modules/eks/main.tf
# AWS EKS Cluster for ResilienceAI

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# =============================================================================
# EKS CLUSTER
# =============================================================================
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    general = {
      desired_size = var.node_desired_size
      min_size     = var.node_min_size
      max_size     = var.node_max_size

      instance_types = var.node_instance_types
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "general"
      }

      update_config = {
        max_unavailable_percentage = 25
      }

      tags = merge(var.tags, {
        Name = "${var.cluster_name}-general"
      })
    }

    spot = {
      desired_size = var.spot_desired_size
      min_size     = var.spot_min_size
      max_size     = var.spot_max_size

      instance_types = var.spot_instance_types
      capacity_type  = "SPOT"

      labels = {
        workload = "spot"
      }

      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]

      tags = merge(var.tags, {
        Name = "${var.cluster_name}-spot"
      })
    }
  }

  # Fargate Profiles (for serverless workloads)
  fargate_profiles = {
    kube_system = {
      name = "kube-system"
      selectors = [
        { namespace = "kube-system" }
      ]
    }
    monitoring = {
      name = "monitoring"
      selectors = [
        { namespace = "monitoring" }
      ]
    }
  }

  # Cluster Addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
    aws-efs-csi-driver = {
      most_recent = true
    }
  }

  # Enable IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  tags = var.tags
}

# =============================================================================
# KUBERNETES PROVIDER
# =============================================================================
data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

# =============================================================================
# INGRESS CONTROLLER (AWS Load Balancer Controller)
# =============================================================================
module "aws_load_balancer_controller" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-aws-load-balancer-controller"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }

  tags = var.tags
}

resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.6.0"

  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }

  set {
    name  = "serviceAccount.annotations.eks\.amazonaws\.com/role-arn"
    value = module.aws_load_balancer_controller.iam_role_arn
  }

  depends_on = [module.eks]
}

# =============================================================================
# CLUSTER AUTOSCALER
# =============================================================================
module "cluster_autoscaler" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-cluster-autoscaler"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }

  tags = var.tags
}

resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = "9.29.0"

  set {
    name  = "autoDiscovery.clusterName"
    value = module.eks.cluster_name
  }

  set {
    name  = "awsRegion"
    value = var.aws_region
  }

  set {
    name  = "rbac.serviceAccount.annotations.eks\.amazonaws\.com/role-arn"
    value = module.cluster_autoscaler.iam_role_arn
  }

  depends_on = [module.eks]
}

# =============================================================================
# METRICS SERVER
# =============================================================================
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.11.0"

  depends_on = [module.eks]
}

# =============================================================================
# CERT-MANAGER
# =============================================================================
module "cert_manager" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-cert-manager"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["cert-manager:cert-manager"]
    }
  }

  tags = var.tags
}

resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = "cert-manager"
  version    = "1.13.0"

  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  set {
    name  = "serviceAccount.annotations.eks\.amazonaws\.com/role-arn"
    value = module.cert_manager.iam_role_arn
  }

  depends_on = [module.eks]
}

# =============================================================================
# EXTERNAL DNS
# =============================================================================
module "external_dns" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-external-dns"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["external-dns:external-dns"]
    }
  }

  tags = var.tags
}

resource "helm_release" "external_dns" {
  name       = "external-dns"
  repository = "https://kubernetes-sigs.github.io/external-dns"
  chart      = "external-dns"
  namespace  = "external-dns"
  version    = "1.13.1"

  create_namespace = true

  set {
    name  = "serviceAccount.annotations.eks\.amazonaws\.com/role-arn"
    value = module.external_dns.iam_role_arn
  }

  set {
    name  = "provider"
    value = "aws"
  }

  depends_on = [module.eks]
}

# =============================================================================
# OUTPUTS
# =============================================================================
output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster CA data"
  value       = module.eks.cluster_certificate_authority_data
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN"
  value       = module.eks.oidc_provider_arn
}

output "node_security_group_id" {
  description = "Node security group ID"
  value       = module.eks.node_security_group_id
}
```

### 6.2 Terraform Variables

```hcl
# File: terraform/modules/eks/variables.tf
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "node_desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 5
}

variable "node_instance_types" {
  description = "EC2 instance types for nodes"
  type        = list(string)
  default     = ["m6i.xlarge"]
}

variable "spot_desired_size" {
  description = "Desired number of spot nodes"
  type        = number
  default     = 1
}

variable "spot_min_size" {
  description = "Minimum number of spot nodes"
  type        = number
  default     = 0
}

variable "spot_max_size" {
  description = "Maximum number of spot nodes"
  type        = number
  default     = 5
}

variable "spot_instance_types" {
  description = "EC2 instance types for spot nodes"
  type        = list(string)
  default     = ["m6i.large", "m5.large", "m5a.large"]
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
```

### 6.3 Production Environment Configuration

```hcl
# File: terraform/environments/production/main.tf
terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "resilienceai-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "resilienceai-terraform-locks"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "production"
      Project     = "ResilienceAI"
      ManagedBy   = "Terraform"
    }
  }
}

# =============================================================================
# VPC
# =============================================================================
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "resilienceai-production"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = {
    Name = "resilienceai-production"
  }
}

# =============================================================================
# EKS CLUSTER
# =============================================================================
module "eks" {
  source = "../../modules/eks"

  cluster_name       = "resilienceai-production"
  kubernetes_version = "1.28"

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets
  aws_region         = var.aws_region

  # Production sizing
  node_desired_size = 3
  node_min_size     = 2
  node_max_size     = 10
  node_instance_types = ["m6i.2xlarge"]

  spot_desired_size = 2
  spot_min_size     = 0
  spot_max_size     = 10
  spot_instance_types = ["m6i.xlarge", "m5.xlarge", "m5a.xlarge"]

  tags = {
    Environment = "production"
  }
}

# =============================================================================
# RDS POSTGRESQL
# =============================================================================
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "resilienceai-production"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "resilienceai"
  username = "resilienceai_admin"
  port     = 5432

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  deletion_protection = true
  skip_final_snapshot = false

  performance_insights_enabled    = true
  performance_insights_retention_period = 7

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Environment = "production"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "resilienceai-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# =============================================================================
# S3 BUCKET FOR DATA STORAGE
# =============================================================================
module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 3.0"

  bucket = "resilienceai-production-data"

  versioning = {
    enabled = true
  }

  lifecycle_rule = [
    {
      id      = "archive-old-versions"
      enabled = true
      noncurrent_version_transition = [
        {
          days          = 30
          storage_class = "STANDARD_IA"
        },
        {
          days          = 90
          storage_class = "GLACIER"
        }
      ]
      noncurrent_version_expiration = {
        days = 365
      }
    }
  ]

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Environment = "production"
  }
}

# =============================================================================
# ELASTICACHE REDIS
# =============================================================================
module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  cluster_id           = "resilienceai-production"
  description          = "ResilienceAI Redis cluster"
  node_type            = "cache.r6g.large"
  num_cache_nodes      = 2
  engine_version       = "7.0"
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.this.name
  security_group_ids   = [aws_security_group.elasticache.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  apply_immediately    = true

  tags = {
    Environment = "production"
  }
}

resource "aws_elasticache_subnet_group" "this" {
  name       = "resilienceai-production"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "elasticache" {
  name_prefix = "resilienceai-elasticache-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }
}

# =============================================================================
# OUTPUTS
# =============================================================================
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "redis_endpoint" {
  value = module.elasticache.cluster_endpoint
}

output "s3_bucket_name" {
  value = module.s3_bucket.s3_bucket_id
}
```

---

## 7. ArgoCD GitOps Configuration

### 7.1 Application Definition

```yaml
# File: argocd/applications/resilienceai-production.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilienceai-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  annotations:
    argocd.argoproj.io/sync-wave: "1"
spec:
  project: resilienceai
  source:
    repoURL: https://github.com/GDogMcCoy/ResilienceAI
    targetRevision: main
    path: kubernetes/helm/resilienceai
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: $ARGOCD_APP_REVISION
  destination:
    server: https://kubernetes.default.svc
    namespace: resilienceai-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  revisionHistoryLimit: 10
```

### 7.2 App of Apps Pattern

```yaml
# File: argocd/app-of-apps.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilienceai-app-of-apps
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/GDogMcCoy/ResilienceAI
    targetRevision: main
    path: argocd/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### 7.3 ArgoCD Project

```yaml
# File: argocd/projects/resilienceai.yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: resilienceai
  namespace: argocd
spec:
  description: ResilienceAI Project
  sourceRepos:
    - "https://github.com/GDogMcCoy/ResilienceAI"
  destinations:
    - namespace: resilienceai-*
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - group: ""
      kind: Namespace
    - group: rbac.authorization.k8s.io
      kind: ClusterRole
    - group: rbac.authorization.k8s.io
      kind: ClusterRoleBinding
  namespaceResourceWhitelist:
    - group: ""
      kind: "*"
    - group: apps
      kind: "*"
    - group: networking.k8s.io
      kind: "*"
    - group: autoscaling
      kind: "*"
    - group: batch
      kind: "*"
    - group: monitoring.coreos.com
      kind: "*"
  orphanedResources:
    warn: true
```

---

## 8. CI/CD Pipeline (GitHub Actions)

### 8.1 Main CI Pipeline

```yaml
# File: .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ===========================================================================
  # STAGE 1: BUILD & TEST
  # ===========================================================================
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black mypy

      - name: Lint with flake8
        run: |
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Format check with black
        run: |
          black --check src/ app/ tests/

      - name: Type check with mypy
        run: |
          mypy src/ --ignore-missing-imports

      - name: Test with pytest
        run: |
          pytest tests/ --cov=src --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

  # ===========================================================================
  # STAGE 2: SECURITY SCAN
  # ===========================================================================
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD

  # ===========================================================================
  # STAGE 3: BUILD & PUSH IMAGE
  # ===========================================================================
  build:
    name: Build & Push
    runs-on: ubuntu-latest
    needs: [test, security]
    permissions:
      contents: read
      packages: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=,suffix=,format=short

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  # ===========================================================================
  # STAGE 4: DEPLOY TO DEVELOPMENT
  # ===========================================================================
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment:
      name: development
      url: https://dev.resilienceai.io
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name resilienceai-development

      - name: Deploy with Helm
        run: |
          helm upgrade --install resilienceai ./kubernetes/helm/resilienceai \
            --namespace resilienceai-dev \
            --create-namespace \
            --values ./kubernetes/helm/resilienceai/values.yaml \
            --values ./kubernetes/helm/resilienceai/values-development.yaml \
            --set image.tag=${{ github.sha }} \
            --wait \
            --timeout 10m

  # ===========================================================================
  # STAGE 5: DEPLOY TO STAGING
  # ===========================================================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: staging
      url: https://staging.resilienceai.io
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name resilienceai-staging

      - name: Deploy with Helm
        run: |
          helm upgrade --install resilienceai ./kubernetes/helm/resilienceai \
            --namespace resilienceai-staging \
            --create-namespace \
            --values ./kubernetes/helm/resilienceai/values.yaml \
            --values ./kubernetes/helm/resilienceai/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --wait \
            --timeout 10m

      - name: Run smoke tests
        run: |
          curl -f https://staging.resilienceai.io/healthz || exit 1

  # ===========================================================================
  # STAGE 6: DEPLOY TO PRODUCTION
  # ===========================================================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: startsWith(github.ref, 'refs/tags/v')
    environment:
      name: production
      url: https://resilienceai.io
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name resilienceai-production

      - name: Deploy with Helm
        run: |
          helm upgrade --install resilienceai ./kubernetes/helm/resilienceai \
            --namespace resilienceai-production \
            --create-namespace \
            --values ./kubernetes/helm/resilienceai/values.yaml \
            --values ./kubernetes/helm/resilienceai/values-production.yaml \
            --set image.tag=${{ github.ref_name }} \
            --wait \
            --timeout 15m

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/resilienceai -n resilienceai-production
          curl -f https://resilienceai.io/healthz || exit 1

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          text: 'ResilienceAI ${{ github.ref_name }} deployed to production'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 9. Monitoring & Observability

### 9.1 Prometheus Service Monitor

```yaml
# File: monitoring/prometheus/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: resilienceai-metrics
  namespace: monitoring
  labels:
    app: resilienceai
    release: prometheus
spec:
  namespaceSelector:
    matchNames:
      - resilienceai-production
      - resilienceai-staging
  selector:
    matchLabels:
      app: resilienceai
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
```

### 9.2 Prometheus Rules

```yaml
# File: monitoring/prometheus/rules/resilienceai-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: resilienceai-rules
  namespace: monitoring
  labels:
    app: resilienceai
    release: prometheus
spec:
  groups:
    - name: resilienceai
      rules:
        # High error rate alert
        - alert: ResilienceAIHighErrorRate
          expr: |
            (
              sum(rate(http_requests_total{service="resilienceai",status=~"5.."}[5m]))
              /
              sum(rate(http_requests_total{service="resilienceai"}[5m]))
            ) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate on ResilienceAI"
            description: "Error rate is above 5% for more than 5 minutes"

        # High latency alert
        - alert: ResilienceAIHighLatency
          expr: |
            histogram_quantile(0.95,
              sum(rate(http_request_duration_seconds_bucket{service="resilienceai"}[5m])) by (le)
            ) > 2
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High latency on ResilienceAI"
            description: "95th percentile latency is above 2 seconds"

        # Pod crash looping
        - alert: ResilienceAIPodCrashLooping
          expr: |
            rate(kube_pod_container_status_restarts_total{namespace=~"resilienceai-.*"}[10m]) > 0
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Pod is crash looping"
            description: "Pod {{ $labels.pod }} is restarting frequently"

        # High memory usage
        - alert: ResilienceAIHighMemoryUsage
          expr: |
            (
              container_memory_usage_bytes{namespace=~"resilienceai-.*", container!="POD"}
              /
              container_spec_memory_limit_bytes{namespace=~"resilienceai-.*", container!="POD"}
            ) > 0.85
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High memory usage"
            description: "Memory usage is above 85%"

        # High CPU usage
        - alert: ResilienceAIHighCPUUsage
          expr: |
            (
              rate(container_cpu_usage_seconds_total{namespace=~"resilienceai-.*", container!="POD"}[5m])
              /
              container_spec_cpu_quota{namespace=~"resilienceai-.*", container!="POD"}
            ) > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High CPU usage"
            description: "CPU usage is above 80%"

        # HPA at max replicas
        - alert: ResilienceAIHPAMaxReplicas
          expr: |
            kube_horizontalpodautoscaler_status_current_replicas{namespace=~"resilienceai-.*"}
            ==
            kube_horizontalpodautoscaler_spec_max_replicas{namespace=~"resilienceai-.*"}
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "HPA at maximum replicas"
            description: "HPA has been at max replicas for 10 minutes"

        # PVC near full
        - alert: ResilienceAIPVCNearFull
          expr: |
            (
              kubelet_volume_stats_used_bytes{namespace=~"resilienceai-.*"}
              /
              kubelet_volume_stats_capacity_bytes{namespace=~"resilienceai-.*"}
            ) > 0.85
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "PVC near full"
            description: "PVC {{ $labels.persistentvolumeclaim }} is above 85% full"
```

### 9.3 Grafana Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "ResilienceAI - Application Dashboard",
    "tags": ["resilienceai", "application"],
    "timezone": "utc",
    "schemaVersion": 36,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"resilienceai\"}[5m]))",
            "legendFormat": "Requests/sec"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"resilienceai\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"resilienceai\"}[5m])) * 100",
            "legendFormat": "Error %"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Latency (p95)",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"resilienceai\"}[5m])) by (le))",
            "legendFormat": "p95 Latency"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Active Pods",
        "type": "stat",
        "targets": [
          {
            "expr": "kube_deployment_status_replicas_available{deployment=\"resilienceai\"}",
            "legendFormat": "Pods"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "Request Rate Over Time",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"resilienceai\"}[5m])) by (status)",
            "legendFormat": "{{status}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 6,
        "title": "Latency Distribution",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{service=\"resilienceai\"}[5m])) by (le))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"resilienceai\"}[5m])) by (le))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service=\"resilienceai\"}[5m])) by (le))",
            "legendFormat": "p99"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "id": 7,
        "title": "CPU Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{namespace=~\"resilienceai-.*\", container=\"resilienceai\"}[5m])",
            "legendFormat": "{{pod}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 8,
        "title": "Memory Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{namespace=~\"resilienceai-.*\", container=\"resilienceai\"}",
            "legendFormat": "{{pod}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      },
      {
        "id": 9,
        "title": "HPA Replicas",
        "type": "timeseries",
        "targets": [
          {
            "expr": "kube_horizontalpodautoscaler_status_current_replicas{namespace=~\"resilienceai-.*\"}",
            "legendFormat": "Current"
          },
          {
            "expr": "kube_horizontalpodautoscaler_spec_max_replicas{namespace=~\"resilienceai-.*\"}",
            "legendFormat": "Max"
          },
          {
            "expr": "kube_horizontalpodautoscaler_spec_min_replicas{namespace=~\"resilienceai-.*\"}",
            "legendFormat": "Min"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20}
      },
      {
        "id": 10,
        "title": "Disk Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "kubelet_volume_stats_used_bytes{namespace=~\"resilienceai-.*\"} / kubelet_volume_stats_capacity_bytes{namespace=~\"resilienceai-.*\"} * 100",
            "legendFormat": "{{persistentvolumeclaim}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20}
      }
    ]
  }
}
```

---

## 10. SSL/TLS Management

### 10.1 Cert-Manager ClusterIssuer

```yaml
# File: kubernetes/cert-manager/cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@resilienceai.io
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@resilienceai.io
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
      - http01:
          ingress:
            class: nginx
```

### 10.2 TLS Certificate

```yaml
# File: kubernetes/cert-manager/certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: resilienceai-tls
  namespace: resilienceai-production
spec:
  secretName: resilienceai-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - resilienceai.io
    - www.resilienceai.io
    - api.resilienceai.io
```

---

## 11. Cost Optimization

### 11.1 Spot Instance Configuration

```yaml
# File: kubernetes/cost-optimization/spot-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilienceai-spot
  namespace: resilienceai-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: resilienceai
      workload: spot
  template:
    metadata:
      labels:
        app: resilienceai
        workload: spot
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: node.kubernetes.io/capacity-type
                    operator: In
                    values:
                      - spot
      tolerations:
        - key: spot
          operator: Equal
          value: "true"
          effect: NoSchedule
      containers:
        - name: resilienceai
          image: archia/resilienceai:latest
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
```

### 11.2 KEDA for Event-Driven Scaling

```yaml
# File: kubernetes/cost-optimization/keda-scaledobject.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: resilienceai-scaler
  namespace: resilienceai-production
spec:
  scaleTargetRef:
    name: resilienceai-agent
  minReplicaCount: 1
  maxReplicaCount: 20
  cooldownPeriod: 300
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus.monitoring.svc:9090
        metricName: http_requests_per_second
        threshold: "100"
        query: sum(rate(http_requests_total{service="resilienceai"}[2m]))
    - type: cpu
      metadata:
        type: Utilization
        value: "70"
```

### 11.3 AWS Cost Allocation Tags

```hcl
# File: terraform/modules/cost-allocation/main.tf
# Enable cost allocation tags
resource "aws_ce_cost_allocation_tag" "environment" {
  tag_key = "Environment"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "project" {
  tag_key = "Project"
  status  = "Active"
}

# Budget alerts
resource "aws_budgets_budget" "monthly" {
  name              = "resilienceai-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "5000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  cost_filter {
    name = "TagKeyValue"
    values = [
      "Project$ResilienceAI",
    ]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["admin@resilienceai.io"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["admin@resilienceai.io"]
  }
}
```

---

## 12. Implementation Priority Order

### Phase 1: Foundation (Week 1-2)
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Create optimized Dockerfile | 4h | High |
| P0 | Set up Docker Compose for local dev | 4h | High |
| P0 | Create Helm chart structure | 8h | High |
| P1 | Implement basic Helm values files | 4h | Medium |
| P1 | Create Kustomize base manifests | 4h | Medium |

### Phase 2: Infrastructure (Week 3-4)
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Create Terraform VPC module | 8h | High |
| P0 | Create Terraform EKS module | 16h | High |
| P0 | Set up RDS PostgreSQL | 4h | High |
| P1 | Configure ElastiCache Redis | 4h | Medium |
| P1 | Set up S3 for data storage | 4h | Medium |

### Phase 3: CI/CD (Week 5-6)
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Create GitHub Actions CI pipeline | 8h | High |
| P0 | Implement security scanning | 4h | High |
| P0 | Set up multi-environment deployment | 8h | High |
| P1 | Configure ArgoCD GitOps | 8h | Medium |
| P1 | Implement automated rollback | 4h | Medium |

### Phase 4: Monitoring (Week 7-8)
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Deploy Prometheus stack | 8h | High |
| P0 | Configure Grafana dashboards | 8h | High |
| P0 | Set up alerting rules | 4h | High |
| P1 | Implement distributed tracing | 8h | Medium |
| P1 | Set up log aggregation (Loki) | 4h | Medium |

### Phase 5: Security & Optimization (Week 9-10)
| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | Configure cert-manager for TLS | 4h | High |
| P0 | Implement network policies | 4h | High |
| P1 | Set up spot instances | 4h | Medium |
| P1 | Configure KEDA scaling | 4h | Medium |
| P1 | Implement cost monitoring | 4h | Low |

---

## 13. Integration Points with Existing Code

### 13.1 Current Code Integration

| Existing File | Integration Point | Action Required |
|---------------|-------------------|-----------------|
| `archia/deployment.yaml` | Kubernetes base | Migrate to Helm/Kustomize |
| `.github/workflows/agent-swarm.yml` | CI/CD | Extend with deployment jobs |
| `.streamlit/config.toml` | App config | Mount as ConfigMap |
| `config.py` | Environment vars | Update to read from env |
| `requirements.txt` | Dependencies | Use in Dockerfile |

### 13.2 Environment Variable Mapping

```python
# Update config.py to support environment variables
import os
from pathlib import Path

# Base directories with env override
BASE_DIR = Path(os.environ.get('APP_BASE_DIR', Path(__file__).parent))
DATA_DIR = Path(os.environ.get('DATA_PATH', BASE_DIR / "data"))
MODELS_DIR = Path(os.environ.get('MODELS_DIR', BASE_DIR / "models"))

# API Keys from secrets
CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Feature flags
ENABLE_FHIR_EXPORT = os.environ.get('ENABLE_FHIR_EXPORT', 'true').lower() == 'true'
ENABLE_GEOJSON_EXPORT = os.environ.get('ENABLE_GEOJSON_EXPORT', 'true').lower() == 'true'
```

---

## 14. Summary

This comprehensive DevOps enhancement plan provides:

1. **Docker Optimization**: Multi-stage builds for production efficiency
2. **Kubernetes Management**: Helm charts + Kustomize for flexible deployments
3. **Infrastructure as Code**: Terraform modules for AWS/GCP/Azure
4. **GitOps**: ArgoCD for declarative continuous delivery
5. **CI/CD**: GitHub Actions with security scanning and multi-env deployment
6. **Monitoring**: Prometheus + Grafana with custom dashboards
7. **Auto-scaling**: HPA + KEDA for efficient resource usage
8. **Security**: Network policies, TLS, RBAC
9. **Cost Optimization**: Spot instances, KEDA, budget alerts

### Total Estimated Effort: 8-10 weeks
### Team Size Recommended: 2-3 DevOps engineers

---

## Appendix: Quick Start Commands

```bash
# Local Development
docker-compose -f docker/docker-compose.yml up -d

# Deploy to Kubernetes (Helm)
helm upgrade --install resilienceai ./kubernetes/helm/resilienceai \
  --namespace resilienceai \
  --create-namespace \
  --values ./kubernetes/helm/resilienceai/values.yaml

# Deploy with Terraform
cd terraform/environments/production
terraform init
terraform plan
terraform apply

# Access ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8080:443

# View logs
kubectl logs -f deployment/resilienceai -n resilienceai

# Scale deployment
kubectl scale deployment resilienceai --replicas=5 -n resilienceai
```
