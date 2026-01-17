"""
Integrations module for Elastic Data Generator.

All sample data is embedded - no network access required.
"""

from .base import BaseGenerator
from .windows import (
    WindowsSecurityGenerator,
    WindowsSystemGenerator,
    WindowsApplicationGenerator
)
from .nginx import NginxAccessGenerator, NginxErrorGenerator
from .cisco_asa import CiscoASAGenerator


# Registry of all available integrations
# Each integration has datasets, each dataset has a generator class
AVAILABLE_INTEGRATIONS = {
    "windows": {
        "description": "Windows Event Log data (Security, System, Application)",
        "icon": "🪟",
        "datasets": {
            "security": {
                "description": "Security events (logon, process, privilege)",
                "data_stream": "logs-windows.security-default",
                "generator": WindowsSecurityGenerator
            },
            "system": {
                "description": "System events (service, startup, shutdown)",
                "data_stream": "logs-windows.system-default",
                "generator": WindowsSystemGenerator
            },
            "application": {
                "description": "Application events (errors, warnings)",
                "data_stream": "logs-windows.application-default",
                "generator": WindowsApplicationGenerator
            }
        }
    },
    "nginx": {
        "description": "NGINX web server logs",
        "icon": "🌐",
        "datasets": {
            "access": {
                "description": "HTTP access logs",
                "data_stream": "logs-nginx.access-default",
                "generator": NginxAccessGenerator
            },
            "error": {
                "description": "Error logs",
                "data_stream": "logs-nginx.error-default",
                "generator": NginxErrorGenerator
            }
        }
    },
    "cisco_asa": {
        "description": "Cisco ASA firewall logs",
        "icon": "🔥",
        "datasets": {
            "log": {
                "description": "ASA syslog events",
                "data_stream": "logs-cisco_asa.log-default",
                "generator": CiscoASAGenerator
            }
        }
    }
}


__all__ = [
    'AVAILABLE_INTEGRATIONS',
    'BaseGenerator',
    'WindowsSecurityGenerator',
    'WindowsSystemGenerator',
    'WindowsApplicationGenerator',
    'NginxAccessGenerator',
    'NginxErrorGenerator',
    'CiscoASAGenerator'
]
