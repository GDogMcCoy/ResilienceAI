#!/bin/bash
# Phase 3 Implementation Script
# Resilience Patterns

set -e

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

# 4. Apply service entries
echo "Applying service entries..."
kubectl apply -f ../istio/serviceentries.yaml

# 5. Verify configuration
echo "Verifying resilience configuration..."
echo "Circuit breakers:"
kubectl get destinationrule -n resilience-ai | grep circuit-breaker

echo ""
echo "Retry policies:"
kubectl get virtualservice -n resilience-ai | grep retry

echo ""
echo "Timeout policies:"
kubectl get virtualservice -n resilience-ai | grep timeout

echo ""
echo "Phase 3 complete!"
