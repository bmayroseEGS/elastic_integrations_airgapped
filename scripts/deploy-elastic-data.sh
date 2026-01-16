#!/bin/bash

# Deploy and run elastic-data on air-gapped machine
# This script helps configure and run the elastic-data tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/../bin"
CONFIG_DIR="${HOME}/.config/elastic-data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Elastic Data Generator Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for binary
BINARY=""
if [ -f "${BIN_DIR}/elastic-data-linux" ]; then
    BINARY="${BIN_DIR}/elastic-data-linux"
elif [ -f "${BIN_DIR}/elastic-data" ]; then
    BINARY="${BIN_DIR}/elastic-data"
else
    echo -e "${RED}Error: elastic-data binary not found in ${BIN_DIR}${NC}"
    echo "Please run download-elastic-data.sh first on an internet-connected machine"
    exit 1
fi

echo -e "${GREEN}Found binary: ${BINARY}${NC}"

# Check if config exists
if [ ! -f "${CONFIG_DIR}/config.yaml" ]; then
    echo ""
    echo -e "${YELLOW}No configuration found. Creating config...${NC}"
    mkdir -p "$CONFIG_DIR"

    # Prompt for Elasticsearch settings
    read -p "Elasticsearch host [http://elasticsearch-master:9200]: " ES_HOST
    ES_HOST=${ES_HOST:-http://elasticsearch-master:9200}

    read -p "Elasticsearch username [elastic]: " ES_USER
    ES_USER=${ES_USER:-elastic}

    read -sp "Elasticsearch password [elastic]: " ES_PASS
    ES_PASS=${ES_PASS:-elastic}
    echo ""

    # Create config
    cat > "${CONFIG_DIR}/config.yaml" << EOF
elasticsearch:
  host: "${ES_HOST}"
  username: "${ES_USER}"
  password: "${ES_PASS}"

# Optional: Kibana for dashboard installation
# kibana:
#   host: "http://kibana:5601"

# Data replacement rules (customize generated data)
# replacements:
#   domains:
#     - "example.com"
#     - "test.local"
#   ips:
#     - "192.168.1.100"
#     - "10.0.0.50"
#   usernames:
#     - "testuser"
#     - "admin"
#   hostnames:
#     - "server01"
#     - "workstation01"
EOF

    echo -e "${GREEN}Configuration saved to ${CONFIG_DIR}/config.yaml${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Running elastic-data${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "The interactive TUI will start."
echo ""
echo "Usage tips:"
echo "  - Use arrow keys to navigate"
echo "  - Press Enter to select"
echo "  - Choose an integration (e.g., nginx, windows, cisco_asa)"
echo "  - Select a dataset"
echo "  - Configure event rate (events per second)"
echo "  - Press Enter to start ingestion"
echo ""
echo -e "${YELLOW}Press Enter to continue...${NC}"
read

# Run the binary
exec "$BINARY"
