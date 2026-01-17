# elastic-data - Air-Gapped Integration Data Generator

A TUI-based tool for generating sample data for Elastic integrations in air-gapped environments.
All sample data is embedded - **no network access required**.

Inspired by [tehbooom/elastic-data](https://github.com/tehbooom/elastic-data) but designed for fully offline use.

## Features

- **Interactive TUI**: Navigate with keyboard, select integrations, configure EPS
- **Air-Gapped**: All sample data embedded - works without internet
- **Multiple Integrations**: Windows, NGINX, Cisco ASA (more coming)
- **Real-time Status**: Monitor running generators and event counts
- **ECS Compliant**: Events follow Elastic Common Schema

## Supported Integrations

| Integration | Datasets | Data Streams |
|------------|----------|--------------|
| Windows | security, system, application | logs-windows.security-default, logs-windows.system-default, logs-windows.application-default |
| NGINX | access, error | logs-nginx.access-default, logs-nginx.error-default |
| Cisco ASA | log | logs-cisco_asa.log-default |

## Prerequisites

This repository is designed to work with the [helm-fleet-deployment-airgapped](https://github.com/bmayroseEGS/helm-fleet-deployment-airgapped) stack.

1. Deploy the Elastic Stack using helm-fleet-deployment-airgapped
2. When running `collect-all.sh`, you will be prompted to clone additional repos - select this one
3. The script will download required images for air-gapped transfer

## Quick Start

### 1. Build the Image

```bash
./build.sh
docker push localhost:5000/elastic-data:latest
```

### 2. Deploy to Kubernetes

```bash
# Using defaults (ES at http://elasticsearch-master:9200)
./deploy.sh

# Or with custom ES settings
ES_HOST="https://my-es:9200" ES_USER="elastic" ES_PASS="secret" ./deploy.sh
```

### 3. Start the TUI

```bash
# Get pod name and exec into it
POD=$(kubectl get pods -n elastic -l app.kubernetes.io/name=elastic-data -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n elastic -- python /app/main.py
```

## TUI Navigation

| Key | Action |
|-----|--------|
| ↑/↓ | Navigate list / Adjust EPS |
| Enter | Select / Start generator |
| Esc | Go back |
| I | Go to Integrations view |
| S | Go to Status view |
| Q | Quit |

## TUI Views

1. **Integrations**: List of available integrations
2. **Datasets**: Datasets within selected integration
3. **Config**: Configure EPS before starting
4. **Status**: Monitor running generators

## Configuration

### Helm Values

```yaml
# values.yaml
elasticsearch:
  host: "http://elasticsearch-master:9200"
  username: "elastic"
  password: "elastic"
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ELASTICSEARCH_HOST | http://elasticsearch-master:9200 | ES endpoint |
| ELASTICSEARCH_USERNAME | elastic | ES username |
| ELASTICSEARCH_PASSWORD | elastic | ES password |

## Project Structure

```
elastic_integrations_airgapped/
├── docker/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── generator/          # Python generator code
│       ├── main.py         # Main orchestrator
│       ├── es_client.py    # ES bulk client
│       ├── ui/
│       │   └── tui.py      # Curses TUI
│       └── integrations/   # Data generators
│           ├── base.py     # Base generator class
│           ├── windows.py  # Windows events
│           ├── nginx.py    # NGINX logs
│           └── cisco_asa.py # Cisco ASA logs
├── helm_charts/
│   └── elastic-data/       # Helm chart
├── generator/              # Source (copied to docker/)
├── build.sh               # Build script
├── deploy.sh              # Deploy script
└── README.md
```

## Adding New Integrations

1. Create a new file in `generator/integrations/` (e.g., `myintegration.py`)
2. Extend `BaseGenerator` class and implement `generate()` method
3. Register in `generator/integrations/__init__.py` under `AVAILABLE_INTEGRATIONS`
4. Copy to docker/generator/: `cp -r generator/* docker/generator/`
5. Rebuild and redeploy

Example:

```python
from .base import BaseGenerator

class MyIntegrationGenerator(BaseGenerator):
    DATA_STREAM = "logs-myintegration.log-default"

    def generate(self):
        event = self._base_event("myintegration.log", "myintegration")
        event["message"] = "Sample event"
        return event, self.DATA_STREAM
```

## Verifying Data in Kibana

1. Go to **Discover**
2. Create data view for `logs-*`
3. Filter by `labels.synthetic: true` to see generated events
4. Check for integration-specific fields like `winlog.*`, `nginx.*`, `cisco.*`

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -n elastic -l app.kubernetes.io/name=elastic-data
kubectl logs -n elastic -l app.kubernetes.io/name=elastic-data
```

### Cannot connect to Elasticsearch
Verify the Elasticsearch host is correct and accessible:
```bash
kubectl exec -it <pod-name> -n elastic -- curl -u elastic:elastic http://elasticsearch-master:9200
```

### TUI not displaying correctly
Ensure you have a proper TTY:
```bash
kubectl exec -it <pod-name> -n elastic -- /bin/bash
# Then run manually
python /app/main.py
```

## Related Repositories

- [helm-fleet-deployment-airgapped](https://github.com/bmayroseEGS/helm-fleet-deployment-airgapped) - Main Elastic Stack deployment
- [agent_deployment_airgapped](https://github.com/bmayroseEGS/agent_deployment_airgapped) - Elastic Agent and synthetic data generators

## License

Apache 2.0
