"""
Cisco ASA firewall log generator.

Generates realistic Cisco ASA syslog events following ECS schema.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Tuple

from .base import BaseGenerator


# Common Cisco ASA message IDs and their meanings
ASA_MESSAGES = [
    {
        "id": "106001",
        "severity": 2,
        "weight": 5,
        "type": "Inbound TCP connection denied",
        "action": "denied"
    },
    {
        "id": "106006",
        "severity": 2,
        "weight": 5,
        "type": "Deny inbound UDP",
        "action": "denied"
    },
    {
        "id": "106007",
        "severity": 2,
        "weight": 3,
        "type": "Deny inbound UDP due to DNS",
        "action": "denied"
    },
    {
        "id": "106014",
        "severity": 3,
        "weight": 5,
        "type": "Deny inbound icmp",
        "action": "denied"
    },
    {
        "id": "106015",
        "severity": 6,
        "weight": 3,
        "type": "Deny TCP (no connection)",
        "action": "denied"
    },
    {
        "id": "106023",
        "severity": 4,
        "weight": 8,
        "type": "Deny by access-group",
        "action": "denied"
    },
    {
        "id": "106100",
        "severity": 6,
        "weight": 15,
        "type": "access-list permitted/denied",
        "action": "allowed"
    },
    {
        "id": "302013",
        "severity": 6,
        "weight": 20,
        "type": "Built inbound TCP connection",
        "action": "allowed"
    },
    {
        "id": "302014",
        "severity": 6,
        "weight": 10,
        "type": "Teardown TCP connection",
        "action": "allowed"
    },
    {
        "id": "302015",
        "severity": 6,
        "weight": 15,
        "type": "Built inbound UDP connection",
        "action": "allowed"
    },
    {
        "id": "302016",
        "severity": 6,
        "weight": 8,
        "type": "Teardown UDP connection",
        "action": "allowed"
    },
    {
        "id": "302020",
        "severity": 6,
        "weight": 3,
        "type": "Built inbound ICMP connection",
        "action": "allowed"
    },
    {
        "id": "302021",
        "severity": 6,
        "weight": 2,
        "type": "Teardown ICMP connection",
        "action": "allowed"
    },
    {
        "id": "305011",
        "severity": 6,
        "weight": 10,
        "type": "Built dynamic translation",
        "action": "allowed"
    },
    {
        "id": "305012",
        "severity": 6,
        "weight": 5,
        "type": "Teardown dynamic translation",
        "action": "allowed"
    },
    {
        "id": "313001",
        "severity": 3,
        "weight": 3,
        "type": "Denied ICMP type",
        "action": "denied"
    },
    {
        "id": "710003",
        "severity": 6,
        "weight": 5,
        "type": "TCP access permitted",
        "action": "allowed"
    },
    {
        "id": "733100",
        "severity": 4,
        "weight": 2,
        "type": "Threat detection rate exceeded",
        "action": "alert"
    }
]

INTERFACES = ["outside", "inside", "dmz", "management", "guest"]

PROTOCOLS = ["TCP", "UDP", "ICMP", "GRE", "ESP"]

FIREWALL_NAMES = ["ASA-FW-01", "ASA-FW-02", "ASA-EDGE-01", "ASA-CORE-01"]

ACCESS_LISTS = ["outside_access_in", "inside_access_out", "dmz_access_in", "global_policy"]

# Common ports for more realistic traffic
COMMON_PORTS = {
    "web": [80, 443, 8080, 8443],
    "mail": [25, 110, 143, 465, 587, 993, 995],
    "dns": [53],
    "ssh": [22],
    "rdp": [3389],
    "database": [1433, 1521, 3306, 5432, 27017],
    "other": [21, 23, 135, 139, 445, 389, 636, 88]
}


class CiscoASAGenerator(BaseGenerator):
    """Generator for Cisco ASA syslog events."""

    DATA_STREAM = "logs-cisco_asa.log-default"

    SEVERITY_NAMES = {
        0: "emergencies",
        1: "alerts",
        2: "critical",
        3: "errors",
        4: "warnings",
        5: "notifications",
        6: "informational",
        7: "debugging"
    }

    def generate(self) -> Tuple[Dict, str]:
        """Generate a Cisco ASA syslog event."""
        # Weighted selection of message type
        weights = [m["weight"] for m in ASA_MESSAGES]
        msg = random.choices(ASA_MESSAGES, weights=weights)[0]

        return self._generate_asa_event(msg), self.DATA_STREAM

    def _get_port_pair(self) -> Tuple[int, int]:
        """Generate realistic source and destination ports."""
        # Pick a category
        category = random.choice(list(COMMON_PORTS.keys()))
        dst_port = random.choice(COMMON_PORTS[category])
        src_port = random.randint(1024, 65535)
        return src_port, dst_port

    def _generate_asa_event(self, msg: Dict) -> Dict:
        """Generate a Cisco ASA event based on message type."""
        timestamp = self._get_timestamp()
        firewall = random.choice(FIREWALL_NAMES)

        # Generate IPs
        src_ip = self._random_ip(private=False)
        dst_ip = self._random_ip(private=True)

        # Sometimes reverse for outbound
        if random.random() < 0.3:
            src_ip, dst_ip = dst_ip, src_ip

        src_port, dst_port = self._get_port_pair()
        protocol = random.choice(["TCP", "UDP"]) if msg["id"].startswith("302") else random.choice(PROTOCOLS)

        src_interface = random.choice(INTERFACES)
        dst_interface = random.choice([i for i in INTERFACES if i != src_interface])

        event = self._base_event("cisco_asa.log", "cisco_asa")

        event.update({
            "host": {
                "name": firewall,
                "hostname": firewall
            },
            "observer": {
                "name": firewall,
                "product": "ASA",
                "vendor": "Cisco",
                "type": "firewall"
            },
            "source": {
                "ip": src_ip,
                "port": src_port,
                "address": src_ip
            },
            "destination": {
                "ip": dst_ip,
                "port": dst_port,
                "address": dst_ip
            },
            "network": {
                "protocol": protocol.lower(),
                "transport": protocol.lower() if protocol in ["TCP", "UDP"] else "ip",
                "direction": "inbound" if src_interface == "outside" else "outbound"
            },
            "event": {
                **event["event"],
                "code": msg["id"],
                "action": msg["action"],
                "category": ["network"],
                "type": ["connection", "allowed" if msg["action"] == "allowed" else "denied"],
                "outcome": "success" if msg["action"] == "allowed" else "failure",
                "severity": msg["severity"]
            },
            "log": {
                "level": self.SEVERITY_NAMES.get(msg["severity"], "informational"),
                "syslog": {
                    "severity": {
                        "code": msg["severity"],
                        "name": self.SEVERITY_NAMES.get(msg["severity"], "informational")
                    },
                    "facility": {
                        "code": 20,
                        "name": "local4"
                    }
                }
            },
            "cisco": {
                "asa": {
                    "message_id": msg["id"],
                    "source_interface": src_interface,
                    "destination_interface": dst_interface
                }
            }
        })

        # Generate message based on type
        event["message"] = self._build_message(msg, event)

        return event

    def _build_message(self, msg: Dict, event: Dict) -> str:
        """Build the syslog message string."""
        src = event["source"]
        dst = event["destination"]
        cisco = event["cisco"]["asa"]
        protocol = event["network"]["protocol"].upper()

        msg_id = msg["id"]

        if msg_id in ["302013", "302015", "302020"]:
            # Built connection
            conn_id = random.randint(100000, 9999999)
            return (
                f'%ASA-6-{msg_id}: Built {"inbound" if cisco["source_interface"] == "outside" else "outbound"} '
                f'{protocol} connection {conn_id} for {cisco["source_interface"]}:{src["ip"]}/{src["port"]} '
                f'to {cisco["destination_interface"]}:{dst["ip"]}/{dst["port"]}'
            )

        elif msg_id in ["302014", "302016", "302021"]:
            # Teardown connection
            conn_id = random.randint(100000, 9999999)
            duration = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
            bytes_sent = random.randint(100, 1000000)
            return (
                f'%ASA-6-{msg_id}: Teardown {protocol} connection {conn_id} for '
                f'{cisco["source_interface"]}:{src["ip"]}/{src["port"]} to '
                f'{cisco["destination_interface"]}:{dst["ip"]}/{dst["port"]} duration {duration} bytes {bytes_sent}'
            )

        elif msg_id == "106023":
            # Deny by access-group
            acl = random.choice(ACCESS_LISTS)
            return (
                f'%ASA-4-{msg_id}: Deny {protocol} src {cisco["source_interface"]}:{src["ip"]}/{src["port"]} '
                f'dst {cisco["destination_interface"]}:{dst["ip"]}/{dst["port"]} by access-group "{acl}"'
            )

        elif msg_id == "106100":
            # access-list permitted/denied
            acl = random.choice(ACCESS_LISTS)
            action = "permitted" if msg["action"] == "allowed" else "denied"
            hit_cnt = random.randint(1, 1000)
            return (
                f'%ASA-6-{msg_id}: access-list {acl} {action} {protocol} '
                f'{cisco["source_interface"]}/{src["ip"]}({src["port"]}) -> '
                f'{cisco["destination_interface"]}/{dst["ip"]}({dst["port"]}) hit-cnt {hit_cnt}'
            )

        elif msg_id in ["305011", "305012"]:
            # NAT translation
            action = "Built" if msg_id == "305011" else "Teardown"
            global_ip = self._random_ip(private=False)
            return (
                f'%ASA-6-{msg_id}: {action} dynamic {protocol} translation from '
                f'{cisco["source_interface"]}:{src["ip"]}/{src["port"]} to '
                f'{cisco["destination_interface"]}:{global_ip}/{random.randint(1024, 65535)}'
            )

        elif msg_id == "733100":
            # Threat detection
            rate = random.randint(100, 5000)
            return (
                f'%ASA-4-{msg_id}: [{msg["type"]}] drop rate exceeded. '
                f'Current rate: {rate}/sec, trigger rate: 100/sec'
            )

        elif msg_id == "710003":
            # TCP access permitted
            return (
                f'%ASA-6-{msg_id}: {protocol} access permitted from {src["ip"]}/{src["port"]} '
                f'to {cisco["destination_interface"]}:{dst["ip"]}/{dst["port"]}'
            )

        else:
            # Generic deny messages
            return (
                f'%ASA-{msg["severity"]}-{msg_id}: {msg["type"]} from {src["ip"]} to {dst["ip"]} on interface '
                f'{cisco["source_interface"]}'
            )
