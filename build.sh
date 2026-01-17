#!/bin/bash
# Build elastic-data container image for air-gapped deployment
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
IMAGE_NAME="${IMAGE_NAME:-elastic-data}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-localhost:5000}"

echo "==========================================="
echo "  Building elastic-data Image"
echo "==========================================="
echo ""
echo "Image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Build the image
echo "Building Docker image..."
docker build -t "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" ./docker

echo ""
echo "Build complete!"
echo ""
echo "To push to local registry:"
echo "  docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "To deploy with Helm:"
echo "  ./deploy.sh"
