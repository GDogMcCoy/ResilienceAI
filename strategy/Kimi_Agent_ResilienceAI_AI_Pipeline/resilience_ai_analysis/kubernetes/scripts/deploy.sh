#!/bin/bash
# ============================================================================
# ResilienceAI - Kubernetes Deployment Script
# ============================================================================
# Usage: ./deploy.sh [environment] [action]
#   environment: dev|staging|prod (default: dev)
#   action: install|upgrade|uninstall|status (default: install)
# ============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-dev}"
ACTION="${2:-install}"
NAMESPACE="resilience-ai-${ENVIRONMENT}"
RELEASE_NAME="resilience-ai"
CHART_PATH="${PROJECT_ROOT}/helm/resilience-ai"
VALUES_FILE="${PROJECT_ROOT}/helm/resilience-ai/values-${ENVIRONMENT}.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
print_banner() {
    echo "======================================================================"
    echo "  ResilienceAI Kubernetes Deployment"
    echo "  Environment: ${ENVIRONMENT}"
    echo "  Action: ${ACTION}"
    echo "======================================================================"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if values file exists
    if [[ ! -f "$VALUES_FILE" ]]; then
        log_warning "Values file not found: $VALUES_FILE"
        log_info "Using default values.yaml"
        VALUES_FILE="${PROJECT_ROOT}/helm/resilience-ai/values.yaml"
    fi
    
    log_success "Prerequisites check passed"
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace: ${NAMESPACE}"
    
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        kubectl create namespace "$NAMESPACE"
        
        # Add Istio injection label
        kubectl label namespace "$NAMESPACE" istio-injection=enabled --overwrite
        
        log_success "Namespace created: ${NAMESPACE}"
    else
        log_info "Namespace already exists: ${NAMESPACE}"
    fi
}

# Create secrets
create_secrets() {
    log_info "Creating secrets..."
    
    # Check if secrets already exist
    if kubectl get secret resilience-ai-secrets -n "$NAMESPACE" &> /dev/null; then
        log_info "Secrets already exist"
        return
    fi
    
    # Create secrets from environment variables or files
    if [[ -f "${PROJECT_ROOT}/secrets/${ENVIRONMENT}.env" ]]; then
        kubectl create secret generic resilience-ai-secrets \
            --from-env-file="${PROJECT_ROOT}/secrets/${ENVIRONMENT}.env" \
            -n "$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
        log_success "Secrets created from environment file"
    else
        log_warning "Secrets file not found. Please create secrets manually."
        log_info "Example: kubectl create secret generic resilience-ai-secrets \\"
        log_info "  --from-literal=DB_PASSWORD=your-password \\"
        log_info "  --from-literal=JWT_SECRET=your-secret \\"
        log_info "  -n ${NAMESPACE}"
    fi
}

# Install/Upgrade Helm chart
install_helm_chart() {
    log_info "Installing/Upgrading Helm chart..."
    
    # Add required Helm repositories
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
    helm repo add istio https://istio-release.storage.googleapis.com/charts
    helm repo update
    
    # Build dependencies
    log_info "Building Helm dependencies..."
    helm dependency build "$CHART_PATH"
    
    case "$ACTION" in
        install)
            log_info "Installing Helm chart..."
            helm install "$RELEASE_NAME" "$CHART_PATH" \
                --namespace "$NAMESPACE" \
                --values "$VALUES_FILE" \
                --wait \
                --timeout 600s
            log_success "Helm chart installed successfully"
            ;;
        
        upgrade)
            log_info "Upgrading Helm chart..."
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
                --namespace "$NAMESPACE" \
                --values "$VALUES_FILE" \
                --wait \
                --timeout 600s \
                --atomic
            log_success "Helm chart upgraded successfully"
            ;;
        
        rollback)
            REVISION="${3:-0}"
            log_info "Rolling back to revision: ${REVISION}"
            helm rollback "$RELEASE_NAME" "$REVISION" \
                --namespace "$NAMESPACE" \
                --wait \
                --timeout 600s
            log_success "Rollback completed"
            ;;
        
        uninstall)
            log_info "Uninstalling Helm chart..."
            helm uninstall "$RELEASE_NAME" \
                --namespace "$NAMESPACE" \
                --wait \
                --timeout 300s
            log_success "Helm chart uninstalled"
            ;;
        
        status)
            log_info "Checking deployment status..."
            helm status "$RELEASE_NAME" -n "$NAMESPACE"
            kubectl get all -n "$NAMESPACE"
            ;;
        
        *)
            log_error "Unknown action: $ACTION"
            echo "Usage: $0 [environment] [install|upgrade|rollback|uninstall|status]"
            exit 1
            ;;
    esac
}

# Apply Kubernetes manifests
apply_manifests() {
    log_info "Applying Kubernetes manifests..."
    
    # Apply base manifests
    kubectl apply -f "${PROJECT_ROOT}/base/00-namespace.yaml" || true
    
    # Apply Istio configurations if enabled
    if [[ -d "${PROJECT_ROOT}/istio" ]]; then
        log_info "Applying Istio configurations..."
        kubectl apply -f "${PROJECT_ROOT}/istio/" || true
    fi
    
    # Apply monitoring configurations
    if [[ -d "${PROJECT_ROOT}/monitoring" ]]; then
        log_info "Applying monitoring configurations..."
        kubectl apply -f "${PROJECT_ROOT}/monitoring/" || true
    fi
    
    log_success "Manifests applied"
}

# Wait for deployment to be ready
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    kubectl rollout status deployment/resilience-ai-app \
        -n "$NAMESPACE" \
        --timeout=600s
    
    log_success "Deployment is ready"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Get service endpoint
    SERVICE_URL=$(kubectl get ingress resilience-ai-ingress \
        -n "$NAMESPACE" \
        -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "")
    
    if [[ -n "$SERVICE_URL" ]]; then
        # Test health endpoint
        if curl -sf "http://${SERVICE_URL}/health/ready" > /dev/null 2>&1; then
            log_success "Health check passed"
        else
            log_warning "Health check failed or endpoint not accessible"
        fi
    else
        log_warning "Could not determine service URL"
    fi
}

# Print deployment info
print_deployment_info() {
    echo ""
    echo "======================================================================"
    echo "  Deployment Information"
    echo "======================================================================"
    echo ""
    echo "  Namespace: ${NAMESPACE}"
    echo "  Release: ${RELEASE_NAME}"
    echo "  Environment: ${ENVIRONMENT}"
    echo ""
    echo "  Services:"
    kubectl get svc -n "$NAMESPACE" -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,EXTERNAL-IP:.status.loadBalancer.ingress[0].hostname 2>/dev/null || true
    echo ""
    echo "  Pods:"
    kubectl get pods -n "$NAMESPACE" 2>/dev/null || true
    echo ""
    echo "  Ingress:"
    kubectl get ingress -n "$NAMESPACE" 2>/dev/null || true
    echo ""
    echo "======================================================================"
    echo ""
    echo "  Useful commands:"
    echo "    View logs:        kubectl logs -f deployment/resilience-ai-app -n ${NAMESPACE}"
    echo "    Shell access:     kubectl exec -it deployment/resilience-ai-app -n ${NAMESPACE} -- /bin/sh"
    echo "    Port forward:     kubectl port-forward svc/resilience-ai-app 8080:80 -n ${NAMESPACE}"
    echo "    Scale:            kubectl scale deployment resilience-ai-app --replicas=5 -n ${NAMESPACE}"
    echo ""
    echo "======================================================================"
}

# Main function
main() {
    print_banner
    check_prerequisites
    
    case "$ACTION" in
        install|upgrade)
            create_namespace
            create_secrets
            apply_manifests
            install_helm_chart
            wait_for_deployment
            run_smoke_tests
            print_deployment_info
            ;;
        
        rollback)
            install_helm_chart
            wait_for_deployment
            print_deployment_info
            ;;
        
        uninstall)
            install_helm_chart
            ;;
        
        status)
            install_helm_chart
            print_deployment_info
            ;;
    esac
}

# Run main function
main "$@"
