# Service Mesh Operational Runbooks

## Table of Contents
1. [Check Service Mesh Health](#check-service-mesh-health)
2. [Debug Traffic Issues](#debug-traffic-issues)
3. [Handle Circuit Breaker Events](#handle-circuit-breaker-events)
4. [Rollback Deployments](#rollback-deployments)
5. [Performance Tuning](#performance-tuning)
6. [Security Incident Response](#security-incident-response)

---

## Check Service Mesh Health

### Check Istio Control Plane
```bash
# Check Istio control plane pods
kubectl get pods -n istio-system

# Check Istio control plane services
kubectl get svc -n istio-system

# Check Istio ingress gateway
kubectl get pods -n istio-system -l app=istio-ingressgateway
```

### Check Proxy Status
```bash
# Check proxy status for all pods
istioctl proxy-status

# Check proxy status for specific namespace
istioctl proxy-status --namespace resilience-ai

# Check proxy config for a specific pod
istioctl proxy-config cluster <pod-name> -n resilience-ai
istioctl proxy-config listener <pod-name> -n resilience-ai
istioctl proxy-config route <pod-name> -n resilience-ai
istioctl proxy-config endpoint <pod-name> -n resilience-ai
```

### Check Sidecar Injection
```bash
# Check if namespace has sidecar injection enabled
kubectl get namespace resilience-ai -o yaml | grep istio-injection

# Check sidecar status for a pod
kubectl get pod <pod-name> -n resilience-ai -o jsonpath='{.spec.containers[*].name}'
```

---

## Debug Traffic Issues

### Check Virtual Services
```bash
# List all virtual services
kubectl get virtualservice -n resilience-ai

# Get detailed virtual service configuration
kubectl get virtualservice <virtualservice-name> -n resilience-ai -o yaml

# Check virtual service routing
istioctl proxy-config route <pod-name> -n resilience-ai
```

### Check Destination Rules
```bash
# List all destination rules
kubectl get destinationrule -n resilience-ai

# Get detailed destination rule configuration
kubectl get destinationrule <destinationrule-name> -n resilience-ai -o yaml
```

### Test Traffic Routing
```bash
# Test traffic from source pod to destination
kubectl exec -it <source-pod> -n resilience-ai -- curl -v http://<destination-service>/path

# Test with specific headers
kubectl exec -it <source-pod> -n resilience-ai -- curl -v -H "x-user-segment: beta" http://<destination-service>/path

# Test with canary header
kubectl exec -it <source-pod> -n resilience-ai -- curl -v -H "canary: true" http://<destination-service>/path
```

### Check Gateway Configuration
```bash
# List all gateways
kubectl get gateway -n resilience-ai

# Get detailed gateway configuration
kubectl get gateway <gateway-name> -n resilience-ai -o yaml

# Check ingress gateway configuration
kubectl get svc istio-ingressgateway -n istio-system
```

---

## Handle Circuit Breaker Events

### Check Circuit Breaker Status
```bash
# Check circuit breaker status via Envoy stats
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/stats | grep outlier

# Check circuit breaker ejections
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/stats | grep eject

# Check cluster health
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/clusters | grep health
```

### Reset Circuit Breaker
```bash
# Restart pod to reset circuit breaker
kubectl rollout restart deployment/<deployment-name> -n resilience-ai

# Scale deployment to reset connections
kubectl scale deployment/<deployment-name> --replicas=0 -n resilience-ai
kubectl scale deployment/<deployment-name> --replicas=<original-count> -n resilience-ai
```

### Adjust Circuit Breaker Settings
```bash
# Edit destination rule to adjust circuit breaker settings
kubectl edit destinationrule <destinationrule-name> -n resilience-ai

# Apply new circuit breaker configuration
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: <destinationrule-name>
  namespace: resilience-ai
spec:
  host: <service-name>
  trafficPolicy:
    outlierDetection:
      consecutive5xxErrors: 10  # Increase threshold
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
EOF
```

---

## Rollback Deployments

### Rollback Canary Deployment
```bash
# Rollback canary to stable
kubectl patch virtualservice ml-engine-canary -n resilience-ai --type='merge' -p '{
  "spec": {
    "http": [{
      "route": [{
        "destination": {
          "host": "ml-engine",
          "subset": "stable"
        },
        "weight": 100
      }]
    }]
  }
}'

# Scale down canary deployment
kubectl patch deployment ml-engine-canary -n resilience-ai --type='merge' -p '{"spec":{"replicas":0}}'

# Check rollback status
kubectl get virtualservice ml-engine-canary -n resilience-ai -o yaml
```

### Rollback Standard Deployment
```bash
# Rollback deployment
kubectl rollout undo deployment/<deployment-name> -n resilience-ai

# Check rollout history
kubectl rollout history deployment/<deployment-name> -n resilience-ai

# Rollback to specific revision
kubectl rollout undo deployment/<deployment-name> -n resilience-ai --to-revision=<revision-number>
```

---

## Performance Tuning

### Check Performance Metrics
```bash
# Check request rate
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/stats | grep request

# Check connection pool stats
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/stats | grep connection_pool

# Check latency metrics
kubectl exec -it <pod> -c istio-proxy -n resilience-ai -- curl localhost:15000/stats | grep latency
```

### Adjust Connection Pool Settings
```bash
# Edit destination rule to adjust connection pool
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: <destinationrule-name>
  namespace: resilience-ai
spec:
  host: <service-name>
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 200  # Increase max connections
        connectTimeout: 30ms
      http:
        http1MaxPendingRequests: 200
        http2MaxRequests: 2000
        maxRequestsPerConnection: 200
EOF
```

### Adjust Load Balancing
```bash
# Change load balancer algorithm
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: <destinationrule-name>
  namespace: resilience-ai
spec:
  host: <service-name>
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST  # or ROUND_ROBIN, RANDOM, etc.
EOF
```

---

## Security Incident Response

### Check mTLS Status
```bash
# Check mTLS configuration
kubectl get peerauthentication -n resilience-ai

# Check mTLS status for specific service
kubectl get peerauthentication <peerauthentication-name> -n resilience-ai -o yaml

# Check if mTLS is working
istioctl authn tls-check <pod-name>.<namespace>.svc.cluster.local
```

### Check Authorization Policies
```bash
# List all authorization policies
kubectl get authorizationpolicy -n resilience-ai

# Get detailed authorization policy
kubectl get authorizationpolicy <policy-name> -n resilience-ai -o yaml

# Check policy application
istioctl authz check <pod-name> -n resilience-ai
```

### Check JWT Authentication
```bash
# List request authentication policies
kubectl get requestauthentication -n resilience-ai

# Get detailed request authentication
kubectl get requestauthentication <policy-name> -n resilience-ai -o yaml

# Test JWT validation
kubectl exec -it <pod> -n resilience-ai -- curl -v -H "Authorization: Bearer <token>" http://<service>/path
```

### Emergency Security Response
```bash
# Enable strict mTLS immediately
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: resilience-ai
spec:
  mtls:
    mode: STRICT
EOF

# Deny all traffic
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: resilience-ai
spec:
  {}
EOF

# Allow only specific traffic
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: emergency-allow
  namespace: resilience-ai
spec:
  selector:
    matchLabels:
      app: <critical-service>
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account
EOF
```

---

## Common Commands Reference

### Istioctl Commands
```bash
# Analyze configuration
istioctl analyze -n resilience-ai

# Check proxy config
istioctl proxy-config <pod-name> -n resilience-ai

# Check authn/authz
istioctl authn tls-check <service>.<namespace>.svc.cluster.local
istioctl authz check <pod-name> -n resilience-ai

# Dashboard
istioctl dashboard kiali
istioctl dashboard grafana
istioctl dashboard jaeger
istioctl dashboard prometheus
```

### kubectl Commands
```bash
# Get all Istio resources
kubectl get gateway,virtualservice,destinationrule,serviceentry,envoyfilter -n resilience-ai

# Get all security resources
kubectl get peerauthentication,requestauthentication,authorizationpolicy -n resilience-ai

# Get events
kubectl get events -n resilience-ai --sort-by='.lastTimestamp'

# Get logs
kubectl logs -n resilience-ai -l app=<app-name> -c istio-proxy
```

---

*Document Version: 1.0*
*Last Updated: 2024*
