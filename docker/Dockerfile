# elastic-data container for air-gapped Kubernetes deployment
FROM alpine:3.19

ARG TARGETARCH
ARG VERSION=latest

# Install dependencies
RUN apk add --no-cache ca-certificates curl bash

# Download elastic-data binary
RUN ARCH=$([ "$TARGETARCH" = "amd64" ] && echo "x86_64" || echo "arm64") && \
    if [ "$VERSION" = "latest" ]; then \
        VERSION=$(curl -s https://api.github.com/repos/tehbooom/elastic-data/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/'); \
    fi && \
    curl -L -o /tmp/elastic-data.tar.gz \
        "https://github.com/tehbooom/elastic-data/releases/download/${VERSION}/elastic-data_Linux_${ARCH}.tar.gz" && \
    tar -xzf /tmp/elastic-data.tar.gz -C /usr/local/bin && \
    rm /tmp/elastic-data.tar.gz && \
    chmod +x /usr/local/bin/elastic-data

# Create config directory
RUN mkdir -p /root/.config/elastic-data

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
