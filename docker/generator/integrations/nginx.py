"""
NGINX log generators.

Generates realistic NGINX access and error logs following ECS schema.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Tuple

from .base import BaseGenerator


# Sample data pools
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "curl/7.88.1",
    "python-requests/2.31.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "PostmanRuntime/7.35.0"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HTTP_METHODS_WEIGHTED = ["GET"] * 70 + ["POST"] * 20 + ["PUT"] * 5 + ["DELETE"] * 3 + ["HEAD"] * 2

URL_PATHS = [
    "/",
    "/index.html",
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/orders",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v2/graphql",
    "/static/js/main.js",
    "/static/css/style.css",
    "/static/images/logo.png",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/admin/dashboard",
    "/admin/users",
    "/docs/api",
    "/search",
    "/products/123",
    "/products/456/reviews"
]

REFERRERS = [
    "-",
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://example.com/",
    "https://internal.example.com/dashboard",
    "https://api-docs.example.com/"
]

STATUS_CODES_WEIGHTED = (
    [200] * 70 +
    [201] * 5 +
    [204] * 3 +
    [301] * 2 +
    [302] * 3 +
    [304] * 5 +
    [400] * 3 +
    [401] * 2 +
    [403] * 2 +
    [404] * 3 +
    [500] * 1 +
    [502] * 1
)

HOSTNAMES = [
    "web-server-01",
    "web-server-02",
    "nginx-lb-01",
    "api-gateway-01"
]


class NginxAccessGenerator(BaseGenerator):
    """Generator for NGINX access logs."""

    DATA_STREAM = "logs-nginx.access-default"

    def generate(self) -> Tuple[Dict, str]:
        """Generate an NGINX access log event."""
        timestamp = self._get_timestamp()
        client_ip = self._random_ip(private=False)
        method = random.choice(HTTP_METHODS_WEIGHTED)
        path = random.choice(URL_PATHS)
        status = random.choice(STATUS_CODES_WEIGHTED)
        user_agent = random.choice(USER_AGENTS)
        referrer = random.choice(REFERRERS)
        hostname = random.choice(HOSTNAMES)

        # Generate realistic response sizes based on path and status
        if status >= 400:
            body_bytes = random.randint(200, 1000)
        elif path.endswith(('.js', '.css')):
            body_bytes = random.randint(10000, 500000)
        elif path.endswith(('.png', '.jpg', '.ico')):
            body_bytes = random.randint(5000, 2000000)
        elif '/api/' in path:
            body_bytes = random.randint(100, 50000)
        else:
            body_bytes = random.randint(500, 20000)

        # Response time in seconds
        response_time = random.uniform(0.001, 2.0)
        if status >= 500:
            response_time = random.uniform(1.0, 30.0)

        event = self._base_event("nginx.access", "nginx")

        event.update({
            "host": {
                "name": hostname,
                "hostname": hostname
            },
            "source": {
                "ip": client_ip,
                "address": client_ip
            },
            "url": {
                "path": path,
                "original": path
            },
            "http": {
                "request": {
                    "method": method,
                    "referrer": referrer if referrer != "-" else None
                },
                "response": {
                    "status_code": status,
                    "body": {
                        "bytes": body_bytes
                    }
                },
                "version": "1.1"
            },
            "user_agent": {
                "original": user_agent
            },
            "event": {
                **event["event"],
                "category": ["web"],
                "type": ["access"],
                "outcome": "success" if status < 400 else "failure",
                "duration": int(response_time * 1e9)  # nanoseconds
            },
            "nginx": {
                "access": {
                    "remote_ip_list": [client_ip]
                }
            }
        })

        # Build log message in combined format
        event["message"] = (
            f'{client_ip} - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")}] '
            f'"{method} {path} HTTP/1.1" {status} {body_bytes} '
            f'"{referrer}" "{user_agent}"'
        )

        return event, self.DATA_STREAM


class NginxErrorGenerator(BaseGenerator):
    """Generator for NGINX error logs."""

    DATA_STREAM = "logs-nginx.error-default"

    ERROR_TYPES = [
        {
            "level": "error",
            "message": "connect() failed (111: Connection refused) while connecting to upstream",
            "weight": 25
        },
        {
            "level": "error",
            "message": "upstream timed out (110: Connection timed out) while reading response header from upstream",
            "weight": 20
        },
        {
            "level": "warn",
            "message": "client intended to send too large body",
            "weight": 15
        },
        {
            "level": "error",
            "message": "open() \"/var/www/html/favicon.ico\" failed (2: No such file or directory)",
            "weight": 20
        },
        {
            "level": "crit",
            "message": "SSL_do_handshake() failed (SSL: error:14094412:SSL routines:ssl3_read_bytes:sslv3 alert bad certificate)",
            "weight": 5
        },
        {
            "level": "error",
            "message": "limiting requests, excess: 10.520 by zone \"api_limit\"",
            "weight": 10
        },
        {
            "level": "warn",
            "message": "upstream server temporarily disabled while connecting to upstream",
            "weight": 5
        }
    ]

    def generate(self) -> Tuple[Dict, str]:
        """Generate an NGINX error log event."""
        timestamp = self._get_timestamp()
        hostname = random.choice(HOSTNAMES)
        client_ip = self._random_ip(private=False)

        # Weighted selection of error type
        weights = [e["weight"] for e in self.ERROR_TYPES]
        error = random.choices(self.ERROR_TYPES, weights=weights)[0]

        pid = random.randint(1000, 65000)
        tid = random.randint(1, 100)
        connection = random.randint(100000, 999999)
        request_path = random.choice(URL_PATHS)

        event = self._base_event("nginx.error", "nginx")

        event.update({
            "host": {
                "name": hostname,
                "hostname": hostname
            },
            "source": {
                "ip": client_ip,
                "address": client_ip
            },
            "process": {
                "pid": pid,
                "thread": {
                    "id": tid
                }
            },
            "log": {
                "level": error["level"]
            },
            "event": {
                **event["event"],
                "category": ["web"],
                "type": ["error"],
                "outcome": "failure"
            },
            "nginx": {
                "error": {
                    "connection_id": connection
                }
            },
            "url": {
                "path": request_path
            }
        })

        # Format error message
        event["message"] = (
            f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")} [{error["level"]}] '
            f'{pid}#{tid}: *{connection} {error["message"]}, '
            f'client: {client_ip}, request: "GET {request_path} HTTP/1.1"'
        )

        return event, self.DATA_STREAM
