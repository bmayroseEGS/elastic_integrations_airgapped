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

### On Internet-Connected Machine

```bash
# Clone this repo (or let collect-all.sh do it)
git clone https://github.com/bmayroseEGS/elastic_integrations_airgapped.git

# Download the elastic-data binary
./scripts/download-elastic-data.sh

# The binary will be saved to ./bin/elastic-data
```

### On Air-Gapped Machine

```bash
# Run the data generator
./bin/elastic-data

# Or use the deployment script
./scripts/deploy-elastic-data.sh
```

## Supported Integrations

elastic-data supports 400+ integrations including:

- **Security**: Windows, Cisco ASA, Palo Alto, CrowdStrike, Microsoft Defender
- **Cloud**: AWS CloudTrail/VPC Flow/S3, Azure, GCP
- **Infrastructure**: Kubernetes, Docker, nginx, Apache, MySQL, PostgreSQL
- **Observability**: APM, Logs, Metrics
- And many more...

## Configuration

Create a config file at `~/.config/elastic-data/config.yaml`:

```yaml
elasticsearch:
  host: "http://elasticsearch-master:9200"
  username: "elastic"
  password: "elastic"

# Optional: data replacement rules
replacements:
  domains:
    - "example.com"
  ips:
    - "192.168.1.100"
  usernames:
    - "testuser"
```

## Directory Structure

```
elastic_integrations_airgapped/
├── README.md
├── bin/                    # elastic-data binary (downloaded)
├── scripts/
│   ├── download-elastic-data.sh   # Download binary for transfer
│   └── deploy-elastic-data.sh     # Deploy/run on air-gapped system
└── config/
    └── config.yaml.example        # Example configuration
```

## Related Repositories

- [helm-fleet-deployment-airgapped](https://github.com/bmayroseEGS/helm-fleet-deployment-airgapped) - Main Elastic Stack deployment
- [agent_deployment_airgapped](https://github.com/bmayroseEGS/agent_deployment_airgapped) - Elastic Agent and synthetic data generators

## License

Apache 2.0
