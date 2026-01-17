#!/usr/bin/env python3
"""
Elastic Integration Data Generator

A TUI-based tool for generating sample data for Elastic integrations.
All sample data is embedded - works completely offline in air-gapped environments.

Inspired by tehbooom/elastic-data but designed for offline use.
"""

import os
import sys
import json
import time
import signal
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.tui import IntegrationTUI
from integrations import AVAILABLE_INTEGRATIONS
from es_client import ElasticsearchClient


@dataclass
class GeneratorConfig:
    """Configuration for data generation."""
    elasticsearch_host: str = "http://elasticsearch-master:9200"
    elasticsearch_username: str = "elastic"
    elasticsearch_password: str = "elastic"


@dataclass
class IntegrationState:
    """State for a running integration."""
    name: str
    dataset: str
    enabled: bool = False
    events_per_second: float = 1.0
    total_events: int = 0
    running: bool = False
    thread: Optional[threading.Thread] = None
    stop_event: Optional[threading.Event] = None


class DataGenerator:
    """Main data generator orchestrator."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.es_client = ElasticsearchClient(
            host=config.elasticsearch_host,
            username=config.elasticsearch_username,
            password=config.elasticsearch_password
        )
        self.integrations: Dict[str, IntegrationState] = {}
        self.running = False
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)

    def get_available_integrations(self) -> Dict:
        """Get all available integrations with their datasets."""
        return AVAILABLE_INTEGRATIONS

    def start_integration(self, integration_name: str, dataset: str, eps: float = 1.0):
        """Start generating data for an integration."""
        key = f"{integration_name}:{dataset}"

        if key in self.integrations and self.integrations[key].running:
            return False

        # Get the generator class
        if integration_name not in AVAILABLE_INTEGRATIONS:
            return False

        integration_info = AVAILABLE_INTEGRATIONS[integration_name]
        if dataset not in integration_info["datasets"]:
            return False

        generator_class = integration_info["datasets"][dataset]["generator"]

        # Create state
        stop_event = threading.Event()
        state = IntegrationState(
            name=integration_name,
            dataset=dataset,
            enabled=True,
            events_per_second=eps,
            running=True,
            stop_event=stop_event
        )

        # Start generator thread
        thread = threading.Thread(
            target=self._run_generator,
            args=(generator_class, state, stop_event),
            daemon=True
        )
        state.thread = thread
        self.integrations[key] = state
        thread.start()

        return True

    def _run_generator(self, generator_class, state: IntegrationState, stop_event: threading.Event):
        """Run a generator in a thread."""
        generator = generator_class()
        sleep_interval = 1.0 / state.events_per_second if state.events_per_second > 0 else 1.0
        batch_size = 10
        pending_events = []

        while not stop_event.is_set():
            try:
                # Generate event
                event, data_stream = generator.generate()
                pending_events.append({
                    "action": {"create": {"_index": data_stream}},
                    "doc": event
                })

                # Send batch
                if len(pending_events) >= batch_size:
                    try:
                        self.es_client.bulk_index(pending_events)
                        state.total_events += len(pending_events)
                    except Exception as e:
                        pass  # Log error but continue
                    pending_events = []

                time.sleep(sleep_interval)

            except Exception as e:
                time.sleep(1)

        # Send remaining events
        if pending_events:
            try:
                self.es_client.bulk_index(pending_events)
                state.total_events += len(pending_events)
            except:
                pass

        state.running = False

    def stop_integration(self, integration_name: str, dataset: str):
        """Stop generating data for an integration."""
        key = f"{integration_name}:{dataset}"

        if key not in self.integrations:
            return False

        state = self.integrations[key]
        if state.stop_event:
            state.stop_event.set()

        state.enabled = False
        return True

    def stop_all(self):
        """Stop all running integrations."""
        for key, state in self.integrations.items():
            if state.stop_event:
                state.stop_event.set()

        # Wait for threads to finish
        for key, state in self.integrations.items():
            if state.thread and state.thread.is_alive():
                state.thread.join(timeout=2)

    def get_status(self) -> Dict[str, Dict]:
        """Get status of all integrations."""
        status = {}
        for key, state in self.integrations.items():
            status[key] = {
                "name": state.name,
                "dataset": state.dataset,
                "enabled": state.enabled,
                "running": state.running,
                "eps": state.events_per_second,
                "total_events": state.total_events
            }
        return status


def main():
    """Main entry point."""
    # Load config from environment
    config = GeneratorConfig(
        elasticsearch_host=os.environ.get("ELASTICSEARCH_HOST", "http://elasticsearch-master:9200"),
        elasticsearch_username=os.environ.get("ELASTICSEARCH_USERNAME", "elastic"),
        elasticsearch_password=os.environ.get("ELASTICSEARCH_PASSWORD", "elastic")
    )

    # Create generator
    generator = DataGenerator(config)

    # Check ES connection
    if not generator.es_client.check_connection():
        print("Warning: Could not connect to Elasticsearch")
        print(f"Host: {config.elasticsearch_host}")
        print("Will retry when generating data...")
        print()

    # Start TUI
    tui = IntegrationTUI(generator)
    tui.run()


if __name__ == "__main__":
    main()
