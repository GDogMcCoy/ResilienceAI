#!/bin/bash
# Phase 2 Implementation Script
# Observability Stack

set -e

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

# 7. Verify installation
echo "Verifying observability stack..."
echo "Prometheus pods:"
kubectl get pods -n monitoring -l app=prometheus

echo ""
echo "Grafana pods:"
kubectl get pods -n monitoring -l app=grafana

echo ""
echo "Jaeger pods:"
kubectl get pods -n observability -l app=jaeger

echo ""
echo "Kiali pods:"
kubectl get pods -n istio-system -l app=kiali

echo ""
echo "Phase 2 complete!"
