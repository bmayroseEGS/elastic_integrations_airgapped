#!/bin/bash

# Download elastic-data binary for air-gapped transfer
# Run this on an internet-connected machine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/../bin"
REPO="tehbooom/elastic-data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Download elastic-data Binary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$ARCH" in
    x86_64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

echo -e "${YELLOW}Detected: ${OS}/${ARCH}${NC}"

# Get latest release
echo -e "${YELLOW}Fetching latest release...${NC}"
LATEST_RELEASE=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_RELEASE" ]; then
    echo -e "${RED}Failed to get latest release${NC}"
    exit 1
fi

echo -e "${GREEN}Latest release: ${LATEST_RELEASE}${NC}"

# Construct download URL
# Format: elastic-data_Linux_x86_64.tar.gz or elastic-data_Darwin_arm64.tar.gz
case "$OS" in
    linux)
        OS_NAME="Linux"
        ;;
    darwin)
        OS_NAME="Darwin"
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

case "$ARCH" in
    amd64)
        ARCH_NAME="x86_64"
        ;;
    arm64)
        ARCH_NAME="arm64"
        ;;
esac

FILENAME="elastic-data_${OS_NAME}_${ARCH_NAME}.tar.gz"
DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LATEST_RELEASE}/${FILENAME}"

echo -e "${YELLOW}Downloading: ${DOWNLOAD_URL}${NC}"

# Create bin directory
mkdir -p "$BIN_DIR"

# Download and extract
cd "$BIN_DIR"
curl -L -o "$FILENAME" "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    echo -e "${RED}Download failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Extracting...${NC}"
tar -xzf "$FILENAME"
rm "$FILENAME"

# Make executable
chmod +x elastic-data

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Download Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Binary location: ${BIN_DIR}/elastic-data"
echo ""
echo "For air-gapped transfer, copy the entire repository:"
echo "  tar -czf elastic_integrations_airgapped.tar.gz elastic_integrations_airgapped/"
echo ""

# Also download Linux version if on Mac (for air-gapped Linux deployment)
if [ "$OS" = "darwin" ]; then
    echo -e "${YELLOW}Also downloading Linux version for air-gapped deployment...${NC}"
    LINUX_FILENAME="elastic-data_Linux_x86_64.tar.gz"
    LINUX_URL="https://github.com/${REPO}/releases/download/${LATEST_RELEASE}/${LINUX_FILENAME}"

    curl -L -o "$LINUX_FILENAME" "$LINUX_URL"
    tar -xzf "$LINUX_FILENAME"
    mv elastic-data elastic-data-linux
    rm "$LINUX_FILENAME"

    echo -e "${GREEN}Linux binary: ${BIN_DIR}/elastic-data-linux${NC}"
fi
