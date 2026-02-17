# ResilienceAI GitOps Architecture & Implementation Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [GitOps Architecture Overview](#gitops-architecture-overview)
3. [Repository Structure](#repository-structure)
4. [ArgoCD Configuration](#argocd-configuration)
5. [Application Definitions](#application-definitions)
6. [Sync Policies & Automation](#sync-policies--automation)
7. [Multi-Environment Management](#multi-environment-management)
8. [Secret Management](#secret-management)
9. [Rollback Strategies](#rollback-strategies)
10. [Monitoring & Alerting](#monitoring--alerting)
11. [Security Best Practices](#security-best-practices)
12. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

This document provides a comprehensive GitOps implementation strategy for ResilienceAI, leveraging ArgoCD as the primary GitOps controller. The architecture enables declarative, version-controlled, and automated continuous delivery for all ResilienceAI components.

### Key Objectives
- **Declarative Infrastructure**: All infrastructure defined as code in Git
- **Automated Synchronization**: Continuous reconciliation between Git and cluster state
- **Multi-Environment Support**: Consistent deployments across dev, staging, and production
- **Security-First**: Encrypted secrets, RBAC, and audit trails
- **Rollback Capability**: Instant recovery through Git history

---

## GitOps Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GIT REPOSITORY                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Source     │  │   Config     │  │   Secrets    │  │   Policies   │      │
│  │   Code       │  │   (Kustomize)│  │   (Sealed)   │  │   (OPA)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ARGOCD CONTROL PLANE                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Server  │  │  Repository  │  │  Application │  │   Project    │      │
│  │              │  │   Server     │  │  Controller  │  │   Controller │      │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│    DEVELOPMENT          │ │      STAGING            │ │     PRODUCTION          │
│  ┌─────────────────┐    │ │  ┌─────────────────┐    │ │  ┌─────────────────┐    │
│  │ ResilienceAI    │    │ │  │ ResilienceAI    │    │ │  │ ResilienceAI    │    │
│  │ - Core API      │    │ │  │ - Core API      │    │ │  │ - Core API      │    │
│  │ - ML Pipeline   │    │ │  │ - ML Pipeline   │    │ │  │ - ML Pipeline   │    │
│  │ - Monitoring    │    │ │  │ - Monitoring    │    │ │  │ - Monitoring    │    │
│  │ - Data Platform │    │ │  │ - Data Platform │    │ │  │ - Data Platform │    │
│  └─────────────────┘    │ │  └─────────────────┘    │ │  └─────────────────┘    │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

### Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Git Repository | Single source of truth | GitHub/GitLab |
| ArgoCD | GitOps controller | ArgoCD v2.9+ |
| Kustomize | Configuration management | Native Kustomize |
| Helm | Package management | Helm 3.x |
| Sealed Secrets | Secret encryption | Bitnami Sealed Secrets |
| External Secrets | Secret synchronization | External Secrets Operator |
| OPA/Gatekeeper | Policy enforcement | OPA/Gatekeeper |

---

## Repository Structure

### Recommended Git Repository Layout

```
resilience-ai-gitops/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── onboarding.md
│   └── runbooks/
├── bootstrap/
│   ├── argocd/
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   └── install.yaml
│   └── projects/
│       ├── resilience-ai.yaml
│       └── infrastructure.yaml
├── apps/
│   ├── base/
│   │   ├── kustomization.yaml
│   │   ├── core-api/
│   │   ├── ml-pipeline/
│   │   ├── monitoring/
│   │   └── data-platform/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
├── infrastructure/
│   ├── base/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   ├── external-dns/
│   │   └── observability/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
├── secrets/
│   ├── sealed/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   └── external-secrets/
└── policies/
    ├── constraints/
    └── templates/
```

### Application-Specific Structure

```
apps/base/
├── core-api/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── serviceaccount.yaml
│   ├── networkpolicy.yaml
│   └── configmap.yaml
├── ml-pipeline/
│   ├── kustomization.yaml
│   ├── training-job.yaml
│   ├── inference-deployment.yaml
│   ├── model-registry.yaml
│   └── feature-store.yaml
├── monitoring/
│   ├── kustomization.yaml
│   ├── prometheus-rules.yaml
│   ├── grafana-dashboards.yaml
│   └── alertmanager-config.yaml
└── data-platform/
    ├── kustomization.yaml
    ├── kafka/
    ├── clickhouse/
    └── minio/
```

---

## ArgoCD Configuration

### 1. ArgoCD Installation

**File: `bootstrap/argocd/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: argocd

resources:
  # ArgoCD namespace
  - namespace.yaml
  # ArgoCD core installation
  - https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.3/manifests/install.yaml
  # ArgoCD Notifications for alerting
  - https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.3/notifications_catalog/install.yaml
  # Custom configurations
  - argocd-cm.yaml
  - argocd-rbac-cm.yaml
  - argocd-cmd-params-cm.yaml
  # Ingress configuration
  - ingress.yaml

patchesStrategicMerge:
  - argocd-server-deployment.yaml
  - argocd-repo-server-deployment.yaml

configMapGenerator:
  - name: argocd-notifications-cm
    behavior: merge
    files:
      - notifications/notifications.yaml
```

**File: `bootstrap/argocd/namespace.yaml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: argocd
  labels:
    app.kubernetes.io/name: argocd
    app.kubernetes.io/part-of: resilience-ai
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 2. ArgoCD ConfigMap Configuration

**File: `bootstrap/argocd/argocd-cm.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
  labels:
    app.kubernetes.io/name: argocd-cm
    app.kubernetes.io/part-of: argocd
data:
  # Application controller configuration
  application.instanceLabelKey: argocd.argoproj.io/instance
  
  # Resource inclusion/exclusion
  resource.exclusions: |
    - apiGroups:
      - cilium.io
      kinds:
      - CiliumIdentity
      clusters:
      - "*"
  
  # Resource customizations
  resource.customizations: |
    argoproj.io/Application:
      health.lua: |
        hs = {}
        hs.status = "Progressing"
        hs.message = ""
        if obj.status ~= nil then
          if obj.status.health ~= nil then
            hs.status = obj.status.health.status
            if obj.status.health.message ~= nil then
              hs.message = obj.status.health.message
            end
          end
        end
        return hs
  
  # Kustomize options
  kustomize.buildOptions: --enable-helm --load-restrictor LoadRestrictionsNone
  
  # Helm options
  helm.repositories: |
    - url: https://charts.bitnami.com/bitnami
      name: bitnami
    - url: https://prometheus-community.github.io/helm-charts
      name: prometheus-community
    - url: https://grafana.github.io/helm-charts
      name: grafana
  
  # OIDC Configuration (example with Keycloak)
  oidc.config: |
    name: Keycloak
    issuer: https://keycloak.resilience-ai.io/realms/resilience-ai
    clientID: argocd
    clientSecret: $oidc.keycloak.clientSecret
    requestedScopes: ["openid", "profile", "email", "groups"]
    requestedIDTokenClaims: {"groups": {"essential": true}}
  
  # URL configuration
  url: https://argocd.resilience-ai.io
```

### 3. ArgoCD RBAC Configuration

**File: `bootstrap/argocd/argocd-rbac-cm.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
  labels:
    app.kubernetes.io/name: argocd-rbac-cm
    app.kubernetes.io/part-of: argocd
data:
  # Policy configuration
  policy.default: role:readonly
  
  policy.csv: |
    # Define roles
    p, role:admin, applications, *, */*, allow
    p, role:admin, clusters, get, *, allow
    p, role:admin, repositories, *, *, allow
    p, role:admin, projects, *, *, allow
    p, role:admin, accounts, *, *, allow
    p, role:admin, gpgkeys, *, *, allow
    p, role:admin, exec, create, */*, allow
    
    p, role:developer, applications, get, resilience-ai/*, allow
    p, role:developer, applications, sync, resilience-ai/*, allow
    p, role:developer, applications, action/*, resilience-ai/*, allow
    p, role:developer, logs, get, resilience-ai/*, allow
    p, role:developer, exec, create, resilience-ai/*, allow
    
    p, role:readonly, applications, get, resilience-ai/*, allow
    p, role:readonly, logs, get, resilience-ai/*, allow
    
    # Define groups
    g, resilience-ai:administrators, role:admin
    g, resilience-ai:developers, role:developer
    g, resilience-ai:viewers, role:readonly
```

### 4. ArgoCD Command Parameters

**File: `bootstrap/argocd/argocd-cmd-params-cm.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cmd-params-cm
  namespace: argocd
  labels:
    app.kubernetes.io/name: argocd-cmd-params-cm
    app.kubernetes.io/part-of: argocd
data:
  # Server settings
  server.insecure: "false"
  server.rootpath: ""
  server.basehref: "/"
  server.disable.auth: "false"
  server.enable.gzip: "true"
  server.x.frame.options: "sameorigin"
  
  # Controller settings
  controller.status.processors: "20"
  controller.operation.processors: "10"
  controller.repo.server.timeout.seconds: "60"
  
  # Repo server settings
  reposerver.parallelism.limit: "0"
  reposerver.disable.tls: "false"
  
  # Application controller settings
  application.namespaces: ""
```

### 5. ArgoCD Server Deployment Patches

**File: `bootstrap/argocd/argocd-server-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-server
  namespace: argocd
spec:
  template:
    spec:
      containers:
        - name: argocd-server
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          env:
            - name: ARGOCD_SERVER_INSECURE
              valueFrom:
                configMapKeyRef:
                  name: argocd-cmd-params-cm
                  key: server.insecure
                  optional: true
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            seccompProfile:
              type: RuntimeDefault
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: argocd-server
                topologyKey: kubernetes.io/hostname
```

### 6. ArgoCD Ingress Configuration

**File: `bootstrap/argocd/ingress.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
    - hosts:
        - argocd.resilience-ai.io
      secretName: argocd-server-tls
  rules:
    - host: argocd.resilience-ai.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  name: https
```

---

## Application Definitions

### 1. ArgoCD Project Definition

**File: `bootstrap/projects/resilience-ai.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: resilience-ai
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  description: ResilienceAI Application Project
  
  # Source repositories allowed
  sourceRepos:
    - https://github.com/resilience-ai/gitops.git
    - https://charts.bitnami.com/bitnami
    - https://prometheus-community.github.io/helm-charts
    - https://grafana.github.io/helm-charts
  
  # Destination clusters and namespaces
  destinations:
    - namespace: resilience-ai-dev
      server: https://kubernetes.default.svc
    - namespace: resilience-ai-staging
      server: https://kubernetes.default.svc
    - namespace: resilience-ai-prod
      server: https://kubernetes.default.svc
    - namespace: monitoring
      server: https://kubernetes.default.svc
    - namespace: data-platform
      server: https://kubernetes.default.svc
  
  # Allowed cluster-scoped resources
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: rbac.authorization.k8s.io
      kind: ClusterRole
    - group: rbac.authorization.k8s.io
      kind: ClusterRoleBinding
    - group: apiextensions.k8s.io
      kind: CustomResourceDefinition
    - group: scheduling.k8s.io
      kind: PriorityClass
  
  # Allowed namespace-scoped resources
  namespaceResourceWhitelist:
    - group: 'apps'
      kind: Deployment
    - group: 'apps'
      kind: StatefulSet
    - group: 'apps'
      kind: DaemonSet
    - group: ''
      kind: Service
    - group: ''
      kind: ConfigMap
    - group: ''
      kind: Secret
    - group: ''
      kind: ServiceAccount
    - group: networking.k8s.io
      kind: Ingress
    - group: networking.k8s.io
      kind: NetworkPolicy
    - group: autoscaling
      kind: HorizontalPodAutoscaler
    - group: policy
      kind: PodDisruptionBudget
    - group: rbac.authorization.k8s.io
      kind: Role
    - group: rbac.authorization.k8s.io
      kind: RoleBinding
  
  # Denied resources
  namespaceResourceBlacklist:
    - group: ''
      kind: ResourceQuota
  
  # Sync windows for production
  syncWindows:
    - kind: allow
      schedule: '0 2 * * *'
      duration: 4h
      applications:
        - 'resilience-ai-prod-*'
      namespaces:
        - 'resilience-ai-prod'
      timeZone: 'UTC'
    - kind: deny
      schedule: '0 0 * * 0'
      duration: 24h
      manualSync: true
      applications:
        - 'resilience-ai-prod-*'
  
  # Orphaned resource monitoring
  orphanedResources:
    warn: true
  
  # Source namespace restriction
  sourceNamespaces:
    - argocd
```

### 2. Root Application (App of Apps Pattern)

**File: `bootstrap/root-application.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilience-ai-root
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  labels:
    app.kubernetes.io/name: resilience-ai-root
    app.kubernetes.io/part-of: resilience-ai
    environment: all
spec:
  project: default
  source:
    repoURL: https://github.com/resilience-ai/gitops.git
    targetRevision: main
    path: apps/overlays
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - RespectIgnoreDifferences=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
```

### 3. Environment-Specific Application Set

**File: `apps/applicationset.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: resilience-ai-apps
  namespace: argocd
  labels:
    app.kubernetes.io/name: resilience-ai-apps
    app.kubernetes.io/part-of: resilience-ai
spec:
  generators:
    - matrix:
        generators:
          - list:
              elements:
                - environment: dev
                  namespace: resilience-ai-dev
                  cluster: https://kubernetes.default.svc
                  autoSync: true
                  prune: true
                - environment: staging
                  namespace: resilience-ai-staging
                  cluster: https://kubernetes.default.svc
                  autoSync: true
                  prune: true
                - environment: production
                  namespace: resilience-ai-prod
                  cluster: https://kubernetes.default.svc
                  autoSync: false
                  prune: false
          - list:
              elements:
                - component: core-api
                  path: apps/base/core-api
                - component: ml-pipeline
                  path: apps/base/ml-pipeline
                - component: monitoring
                  path: apps/base/monitoring
                - component: data-platform
                  path: apps/base/data-platform
  
  template:
    metadata:
      name: '{{environment}}-{{component}}'
      namespace: argocd
      finalizers:
        - resources-finalizer.argocd.argoproj.io
      labels:
        app.kubernetes.io/name: '{{component}}'
        app.kubernetes.io/part-of: resilience-ai
        environment: '{{environment}}'
    spec:
      project: resilience-ai
      source:
        repoURL: https://github.com/resilience-ai/gitops.git
        targetRevision: main
        path: '{{path}}'
        kustomize:
          namePrefix: '{{environment}}-'
          commonLabels:
            environment: '{{environment}}'
      destination:
        server: '{{cluster}}'
        namespace: '{{namespace}}'
      syncPolicy:
        automated:
          prune: '{{prune}}'
          selfHeal: '{{autoSync}}'
          allowEmpty: false
        syncOptions:
          - CreateNamespace=true
          - PrunePropagationPolicy=foreground
          - PruneLast=true
        retry:
          limit: 3
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
      ignoreDifferences:
        - group: apps
          kind: Deployment
          jsonPointers:
            - /spec/replicas
```

### 4. Core API Application Definition

**File: `apps/base/core-api/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: resilience-ai

resources:
  - serviceaccount.yaml
  - configmap.yaml
  - secret.yaml
  - deployment.yaml
  - service.yaml
  - hpa.yaml
  - pdb.yaml
  - networkpolicy.yaml
  - servicemonitor.yaml

commonLabels:
  app.kubernetes.io/name: core-api
  app.kubernetes.io/part-of: resilience-ai
  app.kubernetes.io/component: api
  app.kubernetes.io/managed-by: argocd

images:
  - name: core-api
    newName: ghcr.io/resilience-ai/core-api
    newTag: v1.2.3

configMapGenerator:
  - name: core-api-config
    behavior: create
    literals:
      - LOG_LEVEL=info
      - METRICS_ENABLED=true
      - TRACING_ENABLED=true
```

**File: `apps/base/core-api/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
  labels:
    app.kubernetes.io/name: core-api
    app.kubernetes.io/component: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: core-api
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
      labels:
        app.kubernetes.io/name: core-api
        app.kubernetes.io/component: api
    spec:
      serviceAccountName: core-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: core-api
          image: core-api
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
          envFrom:
            - configMapRef:
                name: core-api-config
            - secretRef:
                name: core-api-secrets
                optional: true
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /health/startup
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 30
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /cache
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir:
            sizeLimit: 1Gi
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
                        - core-api
                topologyKey: kubernetes.io/hostname
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: core-api
```

**File: `apps/base/core-api/hpa.yaml`**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-api
  labels:
    app.kubernetes.io/name: core-api
    app.kubernetes.io/component: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: core-api
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
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
        - type: Pods
          value: 4
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Min
```

**File: `apps/base/core-api/pdb.yaml`**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: core-api
  labels:
    app.kubernetes.io/name: core-api
    app.kubernetes.io/component: api
spec:
  minAvailable: 51%
  selector:
    matchLabels:
      app.kubernetes.io/name: core-api
```

**File: `apps/base/core-api/networkpolicy.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: core-api
  labels:
    app.kubernetes.io/name: core-api
    app.kubernetes.io/component: api
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: core-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9090
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: data-platform
      ports:
        - protocol: TCP
          port: 5432
        - protocol: TCP
          port: 9092
        - protocol: TCP
          port: 9000
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

---

## Sync Policies & Automation

### 1. Automated Sync Configuration

**File: `policies/sync-policies.yaml`**

```yaml
# Development Environment - Auto-sync enabled
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilience-ai-dev
  namespace: argocd
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - RespectIgnoreDifferences=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

---
# Staging Environment - Auto-sync with approval
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilience-ai-staging
  namespace: argocd
spec:
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
      limit: 3
      backoff:
        duration: 10s
        factor: 2
        maxDuration: 5m

---
# Production Environment - Manual sync required
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilience-ai-prod
  namespace: argocd
spec:
  syncPolicy:
    automated:
      prune: false
      selfHeal: false
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - Validate=true
    retry:
      limit: 2
      backoff:
        duration: 30s
        factor: 2
        maxDuration: 10m
```

### 2. Health Checks and Resource Hooks

**File: `apps/base/core-api/resource-hooks.yaml`**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: core-api-migration
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  template:
    spec:
      containers:
        - name: migration
          image: ghcr.io/resilience-ai/core-api-migrations:latest
          command: ["migrate", "up"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: core-api-secrets
                  key: database-url
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
      restartPolicy: OnFailure
      activeDeadlineSeconds: 300

---
apiVersion: batch/v1
kind: Job
metadata:
  name: core-api-smoke-test
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: smoke-test
          image: ghcr.io/resilience-ai/smoke-tests:latest
          command: ["pytest", "tests/smoke/", "-v"]
          env:
            - name: API_ENDPOINT
              value: http://core-api:8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
      restartPolicy: Never
      activeDeadlineSeconds: 600
```

### 3. Notification Configuration

**File: `bootstrap/argocd/notifications/notifications.yaml`**

```yaml
templates:
  - name: app-sync-succeeded
    notification:
      slack:
        method: POST
        body: |
          {
            "attachments": [{
              "title": "{{.app.metadata.name}}",
              "title_link": "{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
              "color": "#18be52",
              "fields": [{
                "title": "Sync Status",
                "value": "{{.app.status.sync.status}}",
                "short": true
              }, {
                "title": "Repository",
                "value": "{{.app.spec.source.repoURL}}",
                "short": true
              }, {
                "title": "Revision",
                "value": "{{.app.status.sync.revision}}",
                "short": true
              }]
            }]
          }
  
  - name: app-sync-failed
    notification:
      slack:
        method: POST
        body: |
          {
            "attachments": [{
              "title": "{{.app.metadata.name}}",
              "title_link": "{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
              "color": "#f4c030",
              "fields": [{
                "title": "Sync Status",
                "value": "{{.app.status.sync.status}}",
                "short": true
              }, {
                "title": "Error",
                "value": "{{.app.status.operationState.message}}",
                "short": false
              }]
            }]
          }
  
  - name: app-health-degraded
    notification:
      slack:
        method: POST
        body: |
          {
            "attachments": [{
              "title": "{{.app.metadata.name}}",
              "title_link": "{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
              "color": "#d64113",
              "fields": [{
                "title": "Health Status",
                "value": "{{.app.status.health.status}}",
                "short": true
              }, {
                "title": "Message",
                "value": "{{.app.status.health.message}}",
                "short": false
              }]
            }]
          }

triggers:
  - name: on-sync-succeeded
    condition: app.status.sync.status == 'Synced' && app.status.operationState.phase == 'Succeeded'
    template: app-sync-succeeded
  
  - name: on-sync-failed
    condition: app.status.operationState.phase == 'Failed' || app.status.operationState.phase == 'Error'
    template: app-sync-failed
  
  - name: on-health-degraded
    condition: app.status.health.status == 'Degraded'
    template: app-health-degraded
  
  - name: on-deployed
    condition: app.status.operationState.phase in ['Succeeded'] && app.status.health.status == 'Healthy'
    template: app-sync-succeeded

services:
  slack:
    token: $slack-token
```

---

## Multi-Environment Management

### 1. Kustomize Overlay Structure

**File: `apps/overlays/dev/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: resilience-ai-dev

resources:
  - ../../base/core-api
  - ../../base/ml-pipeline
  - ../../base/monitoring

namePrefix: dev-

commonLabels:
  environment: dev
  tier: development

commonAnnotations:
  environment.description: "Development environment for ResilienceAI"
  contact.team: "platform-team@resilience-ai.io"

images:
  - name: core-api
    newTag: latest
  - name: ml-pipeline
    newTag: latest

replicas:
  - name: core-api
    count: 1
  - name: ml-pipeline
    count: 1

patchesStrategicMerge:
  - deployment-patch.yaml
  - hpa-patch.yaml
  - configmap-patch.yaml

configMapGenerator:
  - name: environment-config
    behavior: merge
    literals:
      - ENVIRONMENT=dev
      - DEBUG=true
      - LOG_LEVEL=debug
      - FEATURE_FLAGS=experimental-features=true
```

**File: `apps/overlays/dev/deployment-patch.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
spec:
  template:
    spec:
      containers:
        - name: core-api
          resources:
            requests:
              cpu: 50m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          env:
            - name: DEBUG
              value: "true"
            - name: LOG_LEVEL
              value: "debug"
```

**File: `apps/overlays/dev/hpa-patch.yaml`**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-api
spec:
  minReplicas: 1
  maxReplicas: 3
```

### 2. Staging Environment

**File: `apps/overlays/staging/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: resilience-ai-staging

resources:
  - ../../base/core-api
  - ../../base/ml-pipeline
  - ../../base/monitoring

namePrefix: staging-

commonLabels:
  environment: staging
  tier: staging

images:
  - name: core-api
    newTag: v1.2.3-rc.1
  - name: ml-pipeline
    newTag: v1.2.3-rc.1

replicas:
  - name: core-api
    count: 2
  - name: ml-pipeline
    count: 2

configMapGenerator:
  - name: environment-config
    behavior: merge
    literals:
      - ENVIRONMENT=staging
      - DEBUG=false
      - LOG_LEVEL=info
```

### 3. Production Environment

**File: `apps/overlays/production/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: resilience-ai-prod

resources:
  - ../../base/core-api
  - ../../base/ml-pipeline
  - ../../base/monitoring
  - ../../base/data-platform

namePrefix: prod-

commonLabels:
  environment: production
  tier: production

images:
  - name: core-api
    newTag: v1.2.3
  - name: ml-pipeline
    newTag: v1.2.3

replicas:
  - name: core-api
    count: 5
  - name: ml-pipeline
    count: 3

configMapGenerator:
  - name: environment-config
    behavior: merge
    literals:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=warn
      - METRICS_ENABLED=true
      - TRACING_ENABLED=true

patchesStrategicMerge:
  - deployment-patch.yaml
  - hpa-patch.yaml
  - pdb-patch.yaml
```

**File: `apps/overlays/production/deployment-patch.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
spec:
  template:
    spec:
      containers:
        - name: core-api
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          env:
            - name: LOG_LEVEL
              value: "warn"
            - name: METRICS_ENABLED
              value: "true"
            - name: TRACING_ENABLED
              value: "true"
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app.kubernetes.io/name: core-api
              topologyKey: kubernetes.io/hostname
```

**File: `apps/overlays/production/hpa-patch.yaml`**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: core-api
spec:
  minReplicas: 5
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 600
      policies:
        - type: Percent
          value: 5
          periodSeconds: 60
```

**File: `apps/overlays/production/pdb-patch.yaml`**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: core-api
spec:
  minAvailable: 66%
```

---

## Secret Management

### 1. Sealed Secrets Setup

**File: `secrets/sealed-secrets/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: kube-system

resources:
  - https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

patchesStrategicMerge:
  - controller-patch.yaml
```

**File: `secrets/sealed-secrets/controller-patch.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sealed-secrets-controller
  namespace: kube-system
spec:
  template:
    spec:
      containers:
        - name: sealed-secrets-controller
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            seccompProfile:
              type: RuntimeDefault
```

### 2. Creating Sealed Secrets

```bash
# Install kubeseal CLI
brew install kubeseal

# Create a regular secret
cat <<EOF > secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: core-api-secrets
  namespace: resilience-ai-prod
type: Opaque
stringData:
  database-url: "postgresql://user:pass@db:5432/resilience"
  api-key: "sk-prod-123456789"
  jwt-secret: "super-secret-jwt-key"
EOF

# Seal the secret for production
kubeseal --format=yaml --scope=namespace-wide < secret.yaml > sealed-secret-prod.yaml

# Move to appropriate location
mv sealed-secret-prod.yaml secrets/sealed/production/

# Clean up unencrypted secret
rm secret.yaml
```

### 3. External Secrets Operator

**File: `secrets/external-secrets/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: external-secrets

resources:
  - namespace.yaml
  - https://github.com/external-secrets/external-secrets/releases/download/v0.9.9/external-secrets.yaml
  - secretstore.yaml
  - externalsecret.yaml
```

**File: `secrets/external-secrets/secretstore.yaml`**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
```

**File: `secrets/external-secrets/externalsecret.yaml`**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: core-api-secrets
  namespace: resilience-ai-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: core-api-secrets
    creationPolicy: Owner
    deletionPolicy: Retain
    template:
      type: Opaque
      data:
        database-url: "{{ .database_url }}"
        api-key: "{{ .api_key }}"
        jwt-secret: "{{ .jwt_secret }}"
  data:
    - secretKey: database_url
      remoteRef:
        key: resilience-ai/prod/core-api
        property: database_url
    - secretKey: api_key
      remoteRef:
        key: resilience-ai/prod/core-api
        property: api_key
    - secretKey: jwt_secret
      remoteRef:
        key: resilience-ai/prod/core-api
        property: jwt_secret
```

### 4. SOPS with Age Encryption

**File: `.sops.yaml`**

```yaml
# Creation rules
creation_rules:
  # Production secrets
  - path_regex: secrets/.*production.*\.yaml$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
  
  # Staging secrets
  - path_regex: secrets/.*staging.*\.yaml$
    age: age1xyz...
  
  # Development secrets
  - path_regex: secrets/.*dev.*\.yaml$
    age: age1abc...
```

**File: `secrets/sops/production/core-api-secrets.enc.yaml`**

```yaml
apiVersion: v1
kind: Secret
metadata:
    name: core-api-secrets
    namespace: resilience-ai-prod
type: Opaque
stringData:
    database-url: ENC[AES256_GCM,data:...,iv:...,tag:...,type:str]
    api-key: ENC[AES256_GCM,data:...,iv:...,tag:...,type:str]
sops:
    age:
        - recipient: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
          enc: ...
    lastmodified: "2024-01-15T10:00:00Z"
    version: 3.8.1
```

---

## Rollback Strategies

### 1. Git-Based Rollback

```bash
# View deployment history
git log --oneline --all

# Rollback to previous version
git revert HEAD --no-edit
git push origin main

# Or checkout specific version
git checkout <commit-hash> -- apps/overlays/production/kustomization.yaml
git commit -m "Rollback to version v1.2.2"
git push origin main
```

### 2. ArgoCD Rollback via UI/CLI

```bash
# List application history
argocd app history resilience-ai-prod-core-api

# Rollback to specific revision
argocd app rollback resilience-ai-prod-core-api 3

# Or sync to specific commit
argocd app sync resilience-ai-prod-core-api --revision v1.2.2
```

### 3. Automated Rollback on Failure

**File: `policies/rollback-policy.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: resilience-ai-prod-core-api
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "1"
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  # Rollback configuration
  revisionHistoryLimit: 10
```

### 4. Canary Rollback with Flagger

**File: `apps/base/core-api/canary.yaml`**

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: core-api
  namespace: resilience-ai-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: core-api
  service:
    port: 8080
    targetPort: 8080
    gateways:
      - istio-gateway
    hosts:
      - api.resilience-ai.io
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
        url: http://flagger-loadtester.test/
        timeout: 5s
        metadata:
          cmd: "hey -z 1m -q 10 -c 2 http://core-api-canary:8080/health"
      - name: conformance-test
        type: pre-rollout
        url: http://flagger-loadtester.test/
        timeout: 30s
        metadata:
          type: bash
          cmd: "curl -sf http://core-api-canary:8080/health/ready"
  # Automated rollback on failure
  revertOnDeletion: true
```

---

## Monitoring & Alerting

### 1. ArgoCD Metrics

**File: `monitoring/argocd-servicemonitor.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: argocd-metrics
  namespace: monitoring
  labels:
    app.kubernetes.io/name: argocd
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: argocd
  namespaceSelector:
    matchNames:
      - argocd
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

### 2. Prometheus Rules for ArgoCD

**File: `monitoring/prometheus-rules.yaml`**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: argocd-alerts
  namespace: monitoring
  labels:
    app.kubernetes.io/name: argocd
spec:
  groups:
    - name: argocd
      rules:
        - alert: ArgoCDApplicationOutOfSync
          expr: |
            argocd_app_info{sync_status!="Synced"} == 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "ArgoCD Application {{ $labels.name }} is out of sync"
            description: "Application {{ $labels.name }} in namespace {{ $labels.namespace }} has been out of sync for more than 5 minutes"
        
        - alert: ArgoCDApplicationDegraded
          expr: |
            argocd_app_info{health_status="Degraded"} == 1
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "ArgoCD Application {{ $labels.name }} is degraded"
            description: "Application {{ $labels.name }} health status is degraded"
        
        - alert: ArgoCDApplicationSyncFailed
          expr: |
            increase(argocd_app_sync_total{phase="Error"}[1h]) > 0
          for: 0m
          labels:
            severity: critical
          annotations:
            summary: "ArgoCD Application {{ $labels.name }} sync failed"
            description: "Application {{ $labels.name }} sync failed with error"
        
        - alert: ArgoCDRepoServerHighMemory
          expr: |
            container_memory_usage_bytes{container="argocd-repo-server"} / container_spec_memory_limit_bytes{container="argocd-repo-server"} > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "ArgoCD Repo Server high memory usage"
            description: "Repo Server memory usage is above 80%"
        
        - alert: ArgoCDServerDown
          expr: |
            up{job="argocd-server-metrics"} == 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "ArgoCD Server is down"
            description: "ArgoCD Server has been down for more than 1 minute"
```

### 3. Grafana Dashboard

**File: `monitoring/grafana-dashboard-argocd.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-argocd
  namespace: monitoring
  labels:
    grafana_dashboard: "true"
data:
  argocd-dashboard.json: |
    {
      "dashboard": {
        "title": "ArgoCD Overview",
        "tags": ["argocd", "gitops"],
        "timezone": "utc",
        "panels": [
          {
            "title": "Application Status",
            "type": "stat",
            "targets": [
              {
                "expr": "count by (sync_status) (argocd_app_info)",
                "legendFormat": "{{ sync_status }}"
              }
            ],
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
          },
          {
            "title": "Application Health",
            "type": "stat",
            "targets": [
              {
                "expr": "count by (health_status) (argocd_app_info)",
                "legendFormat": "{{ health_status }}"
              }
            ],
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
          },
          {
            "title": "Sync Duration",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum(rate(argocd_app_sync_duration_seconds_bucket[5m])) by (le))",
                "legendFormat": "p95"
              },
              {
                "expr": "histogram_quantile(0.50, sum(rate(argocd_app_sync_duration_seconds_bucket[5m])) by (le))",
                "legendFormat": "p50"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
          },
          {
            "title": "Sync Operations",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(argocd_app_sync_total[5m])) by (phase)",
                "legendFormat": "{{ phase }}"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
          }
        ]
      }
    }
```

### 4. ArgoCD Notifications Integration

**File: `monitoring/argocd-notifications-config.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.webhook.prometheus: |
    url: http://prometheus-alertmanager.monitoring.svc:9093/webhook/argocd
    headers:
    - name: Content-Type
      value: application/json
  
  template.app-prometheus: |
    webhook:
      prometheus:
        method: POST
        body: |
          {
            "alerts": [{
              "status": "firing",
              "labels": {
                "alertname": "ArgoCDApplicationChange",
                "app": "{{.app.metadata.name}}",
                "sync_status": "{{.app.status.sync.status}}",
                "health_status": "{{.app.status.health.status}}"
              },
              "annotations": {
                "message": "Application {{.app.metadata.name}} status changed"
              }
            }]
          }
  
  trigger.on-sync-status-change: |
    - description: Application sync status changed
      send:
      - app-prometheus
      when: app.status.sync.status in ['Synced', 'OutOfSync']
```

---

## Security Best Practices

### 1. RBAC Configuration

**File: `security/rbac.yaml`**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: argocd-application-controller
rules:
  - apiGroups:
      - '*'
    resources:
      - '*'
    verbs:
      - '*'
  - nonResourceURLs:
      - '*'
    verbs:
      - '*'

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: argocd-application-controller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: argocd-application-controller
subjects:
  - kind: ServiceAccount
    name: argocd-application-controller
    namespace: argocd
```

### 2. Network Policies

**File: `security/network-policies.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: argocd-server
  namespace: argocd
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: argocd-server
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
        - protocol: TCP
          port: 8083
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: argocd-repo-server
      ports:
        - protocol: TCP
          port: 8081
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: argocd-application-controller
      ports:
        - protocol: TCP
          port: 8082
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

### 3. Pod Security Standards

**File: `security/pod-security.yaml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: resilience-ai-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 4. OPA/Gatekeeper Policies

**File: `policies/constraints/required-labels.yaml`**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: required-labels
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet", "DaemonSet"]
      - apiGroups: [""]
        kinds: ["Service", "ConfigMap", "Secret"]
    excludedNamespaces:
      - kube-system
      - kube-public
  parameters:
    labels:
      - key: app.kubernetes.io/name
        allowedRegex: "^[a-z0-9-]+$"
      - key: app.kubernetes.io/part-of
        allowedRegex: "^[a-z0-9-]+$"
      - key: app.kubernetes.io/component
        allowedRegex: "^[a-z0-9-]+$"
      - key: app.kubernetes.io/managed-by
        allowedRegex: "^[a-z0-9-]+$"
```

**File: `policies/constraints/restricted-images.yaml`**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: allowed-image-repositories
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "resilience-ai-*"
  parameters:
    repos:
      - "ghcr.io/resilience-ai/"
      - "docker.io/bitnami/"
      - "registry.k8s.io/"
      - "quay.io/prometheus/"
      - "quay.io/kiwigrid/"
```

**File: `policies/constraints/resource-limits.yaml`**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredResources
metadata:
  name: required-resources
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet"]
    namespaces:
      - "resilience-ai-*"
  parameters:
    limits:
      - cpu
      - memory
    requests:
      - cpu
      - memory
```

### 5. Audit Logging

**File: `security/audit-policy.yaml`**

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log ArgoCD application changes
  - level: RequestResponse
    resources:
      - group: argoproj.io
        resources: ["applications", "applicationsets", "appprojects"]
    omitStages:
      - RequestReceived
  
  # Log secret access
  - level: Metadata
    resources:
      - group: ""
        resources: ["secrets"]
    omitStages:
      - RequestReceived
  
  # Log all other resources at Metadata level
  - level: Metadata
    omitStages:
      - RequestReceived
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Set up Git repository structure | High | 1 day | Platform Team |
| Install ArgoCD | High | 1 day | Platform Team |
| Configure ArgoCD projects | High | 1 day | Platform Team |
| Set up basic RBAC | High | 2 days | Security Team |
| Configure notifications | Medium | 1 day | Platform Team |

### Phase 2: Application Onboarding (Week 3-4)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Create base application manifests | High | 3 days | App Teams |
| Set up environment overlays | High | 2 days | Platform Team |
| Configure sync policies | High | 1 day | Platform Team |
| Test dev environment | High | 2 days | App Teams |
| Document onboarding process | Medium | 1 day | Platform Team |

### Phase 3: Security & Secrets (Week 5-6)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Deploy Sealed Secrets | High | 1 day | Security Team |
| Set up External Secrets Operator | High | 2 days | Security Team |
| Configure secret rotation | High | 2 days | Security Team |
| Implement OPA policies | Medium | 3 days | Security Team |
| Security audit | Medium | 2 days | Security Team |

### Phase 4: Production Readiness (Week 7-8)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Production environment setup | High | 3 days | Platform Team |
| Configure sync windows | High | 1 day | Platform Team |
| Set up monitoring & alerting | High | 2 days | Observability Team |
| Implement rollback procedures | High | 2 days | Platform Team |
| Load testing | High | 2 days | App Teams |

### Phase 5: Advanced Features (Week 9-10)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Implement canary deployments | Medium | 3 days | Platform Team |
| Set up multi-cluster | Medium | 3 days | Platform Team |
| Configure disaster recovery | Medium | 2 days | Platform Team |
| Optimize performance | Low | 2 days | Platform Team |
| Documentation & training | Medium | 2 days | Platform Team |

---

## Quick Start Guide

### 1. Bootstrap ArgoCD

```bash
# Clone the repository
git clone https://github.com/resilience-ai/gitops.git
cd gitops

# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -k bootstrap/argocd/

# Wait for ArgoCD to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get initial password
argocd admin initial-password -n argocd

# Port forward for initial access
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### 2. Configure CLI Access

```bash
# Login to ArgoCD
argocd login argocd.resilience-ai.io --username admin --password <initial-password>

# Change password
argocd account update-password

# Add repository
argocd repo add https://github.com/resilience-ai/gitops.git \
  --username <github-username> \
  --password <github-token>
```

### 3. Deploy Root Application

```bash
# Apply root application
kubectl apply -f bootstrap/root-application.yaml

# Verify applications
argocd app list

# Sync all applications
argocd app sync -l app.kubernetes.io/part-of=resilience-ai
```

### 4. Verify Deployment

```bash
# Check application status
argocd app get resilience-ai-dev-core-api

# View application resources
kubectl get all -n resilience-ai-dev

# Check logs
kubectl logs -n resilience-ai-dev -l app.kubernetes.io/name=core-api
```

---

## Troubleshooting Guide

### Common Issues

#### Application Out of Sync

```bash
# Check sync status
argocd app get <app-name>

# View diff
argocd app diff <app-name>

# Force sync
argocd app sync <app-name> --force

# Check for resource conflicts
kubectl get events -n <namespace> --field-selector type=Warning
```

#### Sync Failures

```bash
# Check operation logs
argocd app logs <app-name>

# Check ArgoCD controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

# Check repo server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server
```

#### Permission Issues

```bash
# Check RBAC
kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<sa-name>

# Check ArgoCD RBAC
argocd account can-i <action> <resource> <sub-resource>
```

---

## Appendix

### A. File Structure Summary

```
resilience-ai-gitops/
├── bootstrap/
│   ├── argocd/              # ArgoCD installation
│   └── projects/            # ArgoCD projects
├── apps/
│   ├── base/                # Base application manifests
│   └── overlays/            # Environment-specific overlays
├── infrastructure/          # Infrastructure components
├── secrets/                 # Secret management
├── policies/                # OPA/Gatekeeper policies
├── monitoring/              # Monitoring configuration
└── docs/                    # Documentation
```

### B. Key Commands Reference

```bash
# Application management
argocd app list
argocd app get <app-name>
argocd app sync <app-name>
argocd app delete <app-name>
argocd app rollback <app-name> <revision>

# Project management
argocd proj list
argocd proj get <project-name>

# Repository management
argocd repo list
argocd repo add <url>
argocd repo rm <url>

# Account management
argocd account list
argocd account get <username>
argocd account update-password
```

### C. Useful Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kustomize Documentation](https://kustomize.io/)
- [GitOps Best Practices](https://www.weave.works/blog/gitops-best-practices)
- [CNCF GitOps Working Group](https://github.com/cncf/tag-app-delivery/tree/main/gitops-wg)

---

*Document Version: 1.0*
*Last Updated: January 2024*
*Maintained by: ResilienceAI Platform Team*
