#!/bin/bash
# Phase 1 Implementation Script
# Service Mesh Foundation

set -e

echo "=== Phase 1: Service Mesh Foundation ==="

# 1. Install Istio
echo "Installing Istio..."
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.20.0
export PATH=$PWD/bin:$PATH

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
echo "Istio pods:"
kubectl get pods -n istio-system

echo ""
echo "Gateways:"
kubectl get gateway -n resilience-ai

echo ""
echo "VirtualServices:"
kubectl get virtualservice -n resilience-ai

echo ""
echo "DestinationRules:"
kubectl get destinationrule -n resilience-ai

echo ""
echo "Phase 1 complete!"
