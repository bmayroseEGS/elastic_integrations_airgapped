# Elastic Integrations - Air-Gapped Deployment

Sample data generator for Elastic integrations in air-gapped environments. Uses [elastic-data](https://github.com/tehbooom/elastic-data) to generate realistic data for 400+ Elastic integrations.

## Overview

This repository provides tools to generate sample data for Elastic integrations (nginx, AWS, Cisco, Windows, Kubernetes, etc.) and ingest it directly into Elasticsearch. Designed for air-gapped environments where you need demo data without actual data sources.

## Prerequisites

This repository is designed to work with the [helm-fleet-deployment-airgapped](https://github.com/bmayroseEGS/helm-fleet-deployment-airgapped) stack.

1. Deploy the Elastic Stack using helm-fleet-deployment-airgapped
2. When running `collect-all.sh`, you will be prompted to clone additional repos - select this one
3. The script will download required binaries and images for air-gapped transfer

## Quick Start

### Option 1: Kubernetes Deployment (Recommended)

#### On Internet-Connected Machine

```bash
# Clone this repo
git clone https://github.com/bmayroseEGS/elastic_integrations_airgapped.git
cd elastic_integrations_airgapped

# Build the container image
cd docker
./build.sh

# Save for air-gapped transfer
docker save localhost:5000/elastic-data:latest -o elastic-data.tar
```

#### On Air-Gapped Machine

```bash
# Load and push the image
docker load -i elastic-data.tar
docker push localhost:5000/elastic-data:latest

# Deploy with Helm
cd helm_charts
helm install elastic-data ./elastic-data -n elastic

# Run the interactive TUI
kubectl exec -it $(kubectl get pods -n elastic -l app=elastic-data -o jsonpath='{.items[0].metadata.name}') -n elastic -- elastic-data
```

### Option 2: Run Binary Directly

#### On Internet-Connected Machine

```bash
# Download the elastic-data binary
./scripts/download-elastic-data.sh

# The binary will be saved to ./bin/elastic-data
```

#### On Air-Gapped Machine

```bash
# Run the data generator (requires port-forward to ES)
kubectl port-forward svc/elasticsearch-master 9200:9200 -n elastic &
./bin/elastic-data
```

## Using elastic-data

elastic-data is an interactive TUI (Terminal User Interface) application.

### Navigation

1. **Select Integration**: Use arrow keys to browse 400+ integrations
2. **Select Dataset**: Choose the specific dataset within the integration
3. **Configure**: Set events per second and other options
4. **Run**: Press Enter on the "run" tab to start ingestion

### Example Workflow

```bash
# Exec into the pod
kubectl exec -it <pod-name> -n elastic -- elastic-data

# In the TUI:
# 1. Navigate to "nginx" integration
# 2. Select "access" dataset
# 3. Set events per second (e.g., 10)
# 4. Press Enter to start generating data
```

## Supported Integrations

elastic-data supports 400+ integrations including:

- **Security**: Windows, Cisco ASA, Palo Alto, CrowdStrike, Microsoft Defender
- **Cloud**: AWS CloudTrail/VPC Flow/S3, Azure, GCP
- **Infrastructure**: Kubernetes, Docker, nginx, Apache, MySQL, PostgreSQL
- **Observability**: APM, Logs, Metrics
- And many more...

## Helm Chart Configuration

Key values in `helm_charts/elastic-data/values.yaml`:

```yaml
# Container image (build and push first)
image:
  registry: localhost:5000
  repository: elastic-data
  tag: "latest"

# Elasticsearch connection
elasticsearch:
  host: "http://elasticsearch-master:9200"
  username: "elastic"
  password: "elastic"

# Optional: Kibana for dashboard installation
kibana:
  host: "http://kibana:5601"
```

## Directory Structure

```
elastic_integrations_airgapped/
├── README.md
├── docker/
│   ├── Dockerfile              # Container image for elastic-data
│   ├── entrypoint.sh           # Container entrypoint
│   └── build.sh                # Build script
├── helm_charts/
│   └── elastic-data/           # Helm chart for Kubernetes deployment
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── scripts/
│   ├── download-elastic-data.sh   # Download binary for transfer
│   └── deploy-elastic-data.sh     # Deploy/run on air-gapped system
├── bin/                           # elastic-data binary (downloaded)
└── config/
    └── config.yaml.example        # Example configuration
```

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -n elastic -l app=elastic-data
kubectl logs -n elastic -l app=elastic-data
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
# Then run elastic-data manually
elastic-data
```

## Related Repositories

- [helm-fleet-deployment-airgapped](https://github.com/bmayroseEGS/helm-fleet-deployment-airgapped) - Main Elastic Stack deployment
- [agent_deployment_airgapped](https://github.com/bmayroseEGS/agent_deployment_airgapped) - Elastic Agent and synthetic data generators

## License

Apache 2.0
