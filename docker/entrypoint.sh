#!/bin/bash
set -e

CONFIG_DIR="/root/.config/elastic-data"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"

# Always create/update config from environment variables
mkdir -p "$CONFIG_DIR"

echo "Creating elastic-data config..."

cat > "$CONFIG_FILE" << EOF
elasticsearch:
  host: "${ELASTICSEARCH_HOST:-http://elasticsearch-master:9200}"
  username: "${ELASTICSEARCH_USERNAME:-elastic}"
  password: "${ELASTICSEARCH_PASSWORD:-elastic}"
EOF

# Add API key if provided
if [ -n "$ELASTICSEARCH_API_KEY" ]; then
    cat >> "$CONFIG_FILE" << EOF
  api_key: "${ELASTICSEARCH_API_KEY}"
EOF
fi

# Add Kibana if provided
if [ -n "$KIBANA_HOST" ]; then
    cat >> "$CONFIG_FILE" << EOF

kibana:
  host: "${KIBANA_HOST}"
EOF
fi

echo "Config written to $CONFIG_FILE"
echo ""
echo "Elasticsearch: ${ELASTICSEARCH_HOST:-http://elasticsearch-master:9200}"
echo ""
echo "=========================================="
echo "  elastic-data - Interactive TUI"
echo "=========================================="
echo ""
echo "This is an interactive application."
echo "Use: kubectl exec -it <pod-name> -n elastic -- /bin/bash"
echo "Then run: elastic-data"
echo ""

# Keep container running - user will exec into it
if [ "${KEEP_RUNNING:-true}" = "true" ]; then
    echo "Container is ready. Waiting for interactive session..."
    echo ""
    # Sleep forever to keep pod running
    exec tail -f /dev/null
else
    # Run elastic-data directly (requires TTY)
    exec /usr/local/bin/elastic-data "$@"
fi
