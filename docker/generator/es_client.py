"""
Elasticsearch client for bulk indexing.
Uses urllib to avoid external dependencies.
"""

import json
import ssl
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from base64 import b64encode
from typing import List, Dict, Optional


class ElasticsearchClient:
    """Simple Elasticsearch client using urllib (no external deps)."""

    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        self.host = host.rstrip('/')
        self.auth_header = 'Basic ' + b64encode(f"{username}:{password}".encode()).decode()
        self.verify_ssl = verify_ssl
        self._ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context."""
        context = ssl.create_default_context()
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return context

    def bulk_index(self, actions: List[Dict]) -> Dict:
        """Send bulk indexing request to Elasticsearch."""
        url = f"{self.host}/_bulk"

        # Build NDJSON body
        body = ""
        for action in actions:
            body += json.dumps(action["action"]) + "\n"
            body += json.dumps(action["doc"]) + "\n"

        headers = {
            "Content-Type": "application/x-ndjson",
            "Authorization": self.auth_header
        }

        request = Request(url, data=body.encode('utf-8'), headers=headers, method='POST')

        try:
            with urlopen(request, context=self._ssl_context, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            raise Exception(f"HTTP Error {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"URL Error: {e.reason}")

    def check_connection(self) -> bool:
        """Check if Elasticsearch is reachable."""
        url = f"{self.host}/"
        headers = {"Authorization": self.auth_header}
        request = Request(url, headers=headers)

        try:
            with urlopen(request, context=self._ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return True
        except Exception:
            return False

    def get_cluster_info(self) -> Optional[Dict]:
        """Get cluster information."""
        url = f"{self.host}/"
        headers = {"Authorization": self.auth_header}
        request = Request(url, headers=headers)

        try:
            with urlopen(request, context=self._ssl_context, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            return None
