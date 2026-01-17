# elastic-data - Air-gapped data generator for Elastic integrations
# All sample data is embedded - no network access required
FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install minimal dependencies (curses is included in python:3.11-slim)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy generator code
COPY generator/ /app/

# Create config directory
RUN mkdir -p /root/.config/elastic-data

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create symlink for easy CLI access
RUN ln -s /app/main.py /usr/local/bin/elastic-data && \
    chmod +x /app/main.py

ENTRYPOINT ["/entrypoint.sh"]
