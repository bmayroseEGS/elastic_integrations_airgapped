#!/bin/bash

# Build elastic-data container image
# Run this on an internet-connected machine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="${IMAGE_NAME:-elastic-data}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-localhost:5000}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Build elastic-data Container${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd "$SCRIPT_DIR"

# Build the image
echo -e "${YELLOW}Building image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}${NC}"
docker build -t "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Build successful!${NC}"
    echo ""
    echo "Image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    echo "To save for air-gapped transfer:"
    echo "  docker save ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -o elastic-data.tar"
    echo ""
    echo "To push to local registry:"
    echo "  docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
