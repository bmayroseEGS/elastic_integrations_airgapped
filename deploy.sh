#!/bin/bash
# Deploy elastic-data to Kubernetes
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
NAMESPACE="${NAMESPACE:-elastic}"
RELEASE_NAME="${RELEASE_NAME:-elastic-data}"
REGISTRY="${REGISTRY:-localhost:5000}"
ES_HOST="${ES_HOST:-http://elasticsearch-master:9200}"
ES_USER="${ES_USER:-elastic}"
ES_PASS="${ES_PASS:-elastic}"

echo "==========================================="
echo "  Deploying elastic-data"
echo "==========================================="
echo ""
echo "Namespace: ${NAMESPACE}"
echo "Elasticsearch: ${ES_HOST}"
echo ""

# Check if Helm chart exists
if [ ! -d "helm_charts/elastic-data" ]; then
    echo "ERROR: Helm chart not found at helm_charts/elastic-data"
    exit 1
fi

# Create namespace if needed
kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1 || \
    kubectl create namespace "${NAMESPACE}"

# Deploy with Helm
echo "Deploying with Helm..."
helm upgrade --install "${RELEASE_NAME}" ./helm_charts/elastic-data \
    --namespace "${NAMESPACE}" \
    --set image.registry="${REGISTRY}" \
    --set elasticsearch.host="${ES_HOST}" \
    --set elasticsearch.username="${ES_USER}" \
    --set elasticsearch.password="${ES_PASS}"

echo ""
echo "==========================================="
echo "  Deployment Complete!"
echo "==========================================="
echo ""
echo "To start the interactive TUI:"
echo ""
echo "  POD=\$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=elastic-data -o jsonpath='{.items[0].metadata.name}')"
echo "  kubectl exec -it \$POD -n ${NAMESPACE} -- python /app/main.py"
echo ""
echo "Or in one command:"
echo ""
echo "  kubectl exec -it \$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=elastic-data -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} -- python /app/main.py"
echo ""
