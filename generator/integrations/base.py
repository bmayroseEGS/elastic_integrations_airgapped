"""
Base generator class for all integrations.
"""

import random
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Tuple, List


class BaseGenerator(ABC):
    """Base class for all data generators."""

    def __init__(self):
        self.event_count = 0

    @abstractmethod
    def generate(self) -> Tuple[Dict, str]:
        """
        Generate a single event.

        Returns:
            Tuple of (event_dict, data_stream_name)
        """
        pass

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def _random_choice(self, items: List) -> any:
        """Choose a random item from a list."""
        return random.choice(items)

    def _random_ip(self, private: bool = True) -> str:
        """Generate a random IP address."""
        if private:
            # Private IP ranges
            ranges = [
                (10, random.randint(0, 255), random.randint(0, 255), random.randint(1, 254)),
                (172, random.randint(16, 31), random.randint(0, 255), random.randint(1, 254)),
                (192, 168, random.randint(0, 255), random.randint(1, 254))
            ]
            ip_parts = random.choice(ranges)
        else:
            # Public-looking IPs (avoiding reserved ranges)
            ip_parts = (
                random.randint(1, 223),
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(1, 254)
            )
        return ".".join(map(str, ip_parts))

    def _random_uuid(self) -> str:
        """Generate a random UUID."""
        return str(uuid.uuid4())

    def _random_port(self, well_known: bool = False) -> int:
        """Generate a random port number."""
        if well_known:
            return random.choice([22, 80, 443, 8080, 3389, 445, 135, 139])
        return random.randint(1024, 65535)

    def _base_event(self, dataset: str, module: str) -> Dict:
        """Create base event structure with common fields."""
        return {
            "@timestamp": self._get_timestamp(),
            "event": {
                "dataset": dataset,
                "module": module,
                "created": self._get_timestamp()
            },
            "ecs": {
                "version": "8.11.0"
            },
            "labels": {
                "synthetic": True
            },
            "tags": ["synthetic", "elastic-data-generator"]
        }
