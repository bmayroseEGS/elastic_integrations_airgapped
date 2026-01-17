#!/bin/bash
set -e

echo "==========================================="
echo "  elastic-data - Integration Data Generator"
echo "  Air-Gapped Edition - All data embedded"
echo "==========================================="
echo ""
echo "Elasticsearch: ${ELASTICSEARCH_HOST:-http://elasticsearch-master:9200}"
echo ""

# Export environment variables for the Python script
export ELASTICSEARCH_HOST="${ELASTICSEARCH_HOST:-http://elasticsearch-master:9200}"
export ELASTICSEARCH_USERNAME="${ELASTICSEARCH_USERNAME:-elastic}"
export ELASTICSEARCH_PASSWORD="${ELASTICSEARCH_PASSWORD:-elastic}"

# Keep container running - user will exec into it
if [ "${KEEP_RUNNING:-true}" = "true" ]; then
    echo "Container is ready. Waiting for interactive session..."
    echo ""
    echo "To start the TUI, run:"
    echo "  kubectl exec -it <pod-name> -n elastic -- python /app/main.py"
    echo ""
    # Sleep forever to keep pod running
    exec tail -f /dev/null
else
    # Run elastic-data directly (requires TTY)
    exec python /app/main.py "$@"
fi
