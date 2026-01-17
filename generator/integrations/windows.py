"""
Windows Event Log generators.

Generates realistic Windows Security, System, and Application events
following ECS schema with winlog.* fields.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Tuple

from .base import BaseGenerator


# Sample data pools
USERNAMES = [
    "admin", "jsmith", "mwilson", "agarcia", "lchen",
    "kpatel", "rjohnson", "slee", "dkim", "SYSTEM",
    "LOCAL SERVICE", "NETWORK SERVICE", "Administrator"
]

COMPUTER_NAMES = [
    "DESKTOP-ABC123", "WORKSTATION-01", "SERVER-DC01",
    "LAPTOP-USER1", "PC-FINANCE-02", "SRV-APP-01"
]

DOMAINS = ["CORP", "CONTOSO", "WORKGROUP", "NT AUTHORITY"]

PROCESSES = [
    {"name": "chrome.exe", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"},
    {"name": "explorer.exe", "path": "C:\\Windows\\explorer.exe"},
    {"name": "svchost.exe", "path": "C:\\Windows\\System32\\svchost.exe"},
    {"name": "powershell.exe", "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"},
    {"name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe"},
    {"name": "notepad.exe", "path": "C:\\Windows\\System32\\notepad.exe"},
    {"name": "taskmgr.exe", "path": "C:\\Windows\\System32\\taskmgr.exe"},
    {"name": "msiexec.exe", "path": "C:\\Windows\\System32\\msiexec.exe"},
    {"name": "outlook.exe", "path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"},
    {"name": "excel.exe", "path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"}
]

SERVICES = [
    {"name": "wuauserv", "display": "Windows Update"},
    {"name": "BITS", "display": "Background Intelligent Transfer Service"},
    {"name": "Dnscache", "display": "DNS Client"},
    {"name": "EventLog", "display": "Windows Event Log"},
    {"name": "Spooler", "display": "Print Spooler"},
    {"name": "W32Time", "display": "Windows Time"},
    {"name": "WinDefend", "display": "Windows Defender Antivirus Service"}
]

APPLICATIONS = [
    {"name": "Application Error", "source": "Application Error"},
    {"name": "Windows Error Reporting", "source": "Windows Error Reporting"},
    {"name": ".NET Runtime", "source": ".NET Runtime"},
    {"name": "VSS", "source": "VSS"},
    {"name": "MsiInstaller", "source": "MsiInstaller"},
    {"name": "SecurityCenter", "source": "SecurityCenter"}
]

LOGON_TYPES = {
    2: "Interactive",
    3: "Network",
    4: "Batch",
    5: "Service",
    7: "Unlock",
    10: "RemoteInteractive",
    11: "CachedInteractive"
}


class WindowsSecurityGenerator(BaseGenerator):
    """Generator for Windows Security events."""

    DATA_STREAM = "logs-windows.security-default"

    # Event configurations with weights
    EVENT_TYPES = [
        {"id": 4624, "weight": 40, "name": "An account was successfully logged on"},
        {"id": 4625, "weight": 10, "name": "An account failed to log on"},
        {"id": 4688, "weight": 30, "name": "A new process has been created"},
        {"id": 4689, "weight": 15, "name": "A process has exited"},
        {"id": 4672, "weight": 5, "name": "Special privileges assigned to new logon"}
    ]

    def generate(self) -> Tuple[Dict, str]:
        """Generate a Windows Security event."""
        # Weighted random selection
        weights = [e["weight"] for e in self.EVENT_TYPES]
        event_type = random.choices(self.EVENT_TYPES, weights=weights)[0]

        if event_type["id"] == 4624:
            return self._generate_logon_success(), self.DATA_STREAM
        elif event_type["id"] == 4625:
            return self._generate_logon_failure(), self.DATA_STREAM
        elif event_type["id"] == 4688:
            return self._generate_process_create(), self.DATA_STREAM
        elif event_type["id"] == 4689:
            return self._generate_process_exit(), self.DATA_STREAM
        elif event_type["id"] == 4672:
            return self._generate_special_privilege(), self.DATA_STREAM

    def _base_security_event(self, event_id: int, event_name: str) -> Dict:
        """Create base security event structure."""
        computer = random.choice(COMPUTER_NAMES)
        event = self._base_event("windows.security", "windows")

        event.update({
            "host": {
                "name": computer,
                "hostname": computer,
                "os": {
                    "family": "windows",
                    "name": "Windows Server 2019",
                    "platform": "windows"
                }
            },
            "winlog": {
                "channel": "Security",
                "event_id": str(event_id),
                "provider_name": "Microsoft-Windows-Security-Auditing",
                "computer_name": computer,
                "record_id": random.randint(100000, 999999),
                "task": "Logon" if event_id in [4624, 4625, 4672] else "Process Creation",
                "keywords": ["Audit Success"] if event_id != 4625 else ["Audit Failure"],
                "opcode": "Info"
            },
            "event": {
                **event["event"],
                "code": str(event_id),
                "action": event_name,
                "category": ["authentication"] if event_id in [4624, 4625] else ["process"],
                "type": ["start"] if event_id in [4624, 4688] else ["end"],
                "outcome": "success" if event_id != 4625 else "failure"
            },
            "log": {
                "level": "information"
            }
        })

        return event

    def _generate_logon_success(self) -> Dict:
        """Generate Event ID 4624 - Successful logon."""
        username = random.choice(USERNAMES)
        domain = random.choice(DOMAINS)
        logon_type = random.choice(list(LOGON_TYPES.keys()))

        event = self._base_security_event(4624, "An account was successfully logged on")

        event["user"] = {
            "name": username,
            "domain": domain,
            "id": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}"
        }

        event["source"] = {
            "ip": self._random_ip(),
            "port": self._random_port()
        }

        event["winlog"]["logon"] = {
            "id": hex(random.randint(0x10000, 0xFFFFF)),
            "type": LOGON_TYPES[logon_type]
        }

        event["winlog"]["event_data"] = {
            "TargetUserName": username,
            "TargetDomainName": domain,
            "LogonType": str(logon_type),
            "IpAddress": event["source"]["ip"],
            "IpPort": str(event["source"]["port"]),
            "WorkstationName": event["host"]["name"],
            "LogonProcessName": random.choice(["User32", "Advapi", "NtLmSsp"]),
            "AuthenticationPackageName": random.choice(["NTLM", "Kerberos", "Negotiate"])
        }

        event["message"] = f"An account was successfully logged on. Subject: {domain}\\{username}"

        return event

    def _generate_logon_failure(self) -> Dict:
        """Generate Event ID 4625 - Failed logon."""
        username = random.choice(USERNAMES)
        domain = random.choice(DOMAINS)
        logon_type = random.choice(list(LOGON_TYPES.keys()))

        # Common failure reasons
        failure_reasons = [
            {"status": "0xc000006d", "sub": "0xc000006a", "reason": "Unknown user name or bad password"},
            {"status": "0xc000006d", "sub": "0xc0000064", "reason": "User name does not exist"},
            {"status": "0xc0000234", "sub": "0x0", "reason": "Account locked out"},
            {"status": "0xc0000072", "sub": "0x0", "reason": "Account disabled"}
        ]
        failure = random.choice(failure_reasons)

        event = self._base_security_event(4625, "An account failed to log on")

        event["user"] = {
            "name": username,
            "domain": domain
        }

        event["source"] = {
            "ip": self._random_ip(private=False),
            "port": self._random_port()
        }

        event["winlog"]["event_data"] = {
            "TargetUserName": username,
            "TargetDomainName": domain,
            "LogonType": str(logon_type),
            "IpAddress": event["source"]["ip"],
            "IpPort": str(event["source"]["port"]),
            "Status": failure["status"],
            "SubStatus": failure["sub"],
            "FailureReason": failure["reason"]
        }

        event["message"] = f"An account failed to log on. Subject: {domain}\\{username}. Reason: {failure['reason']}"

        return event

    def _generate_process_create(self) -> Dict:
        """Generate Event ID 4688 - Process creation."""
        process = random.choice(PROCESSES)
        parent = random.choice(PROCESSES)
        username = random.choice(USERNAMES)
        domain = random.choice(DOMAINS)

        event = self._base_security_event(4688, "A new process has been created")

        event["process"] = {
            "name": process["name"],
            "executable": process["path"],
            "pid": random.randint(1000, 65000),
            "parent": {
                "name": parent["name"],
                "executable": parent["path"],
                "pid": random.randint(1000, 65000)
            }
        }

        event["user"] = {
            "name": username,
            "domain": domain
        }

        event["winlog"]["event_data"] = {
            "NewProcessId": hex(event["process"]["pid"]),
            "NewProcessName": process["path"],
            "ProcessId": hex(event["process"]["parent"]["pid"]),
            "ParentProcessName": parent["path"],
            "SubjectUserName": username,
            "SubjectDomainName": domain,
            "TokenElevationType": random.choice(["%%1936", "%%1937", "%%1938"])
        }

        event["message"] = f"A new process has been created. Process: {process['name']} by {domain}\\{username}"

        return event

    def _generate_process_exit(self) -> Dict:
        """Generate Event ID 4689 - Process termination."""
        process = random.choice(PROCESSES)
        username = random.choice(USERNAMES)
        domain = random.choice(DOMAINS)

        event = self._base_security_event(4689, "A process has exited")

        event["process"] = {
            "name": process["name"],
            "executable": process["path"],
            "pid": random.randint(1000, 65000),
            "exit_code": random.choice([0, 1, -1])
        }

        event["user"] = {
            "name": username,
            "domain": domain
        }

        event["winlog"]["event_data"] = {
            "ProcessId": hex(event["process"]["pid"]),
            "ProcessName": process["path"],
            "SubjectUserName": username,
            "SubjectDomainName": domain,
            "Status": hex(event["process"]["exit_code"])
        }

        event["message"] = f"A process has exited. Process: {process['name']}"

        return event

    def _generate_special_privilege(self) -> Dict:
        """Generate Event ID 4672 - Special privileges assigned."""
        username = random.choice(USERNAMES)
        domain = random.choice(DOMAINS)

        privileges = [
            "SeSecurityPrivilege", "SeTakeOwnershipPrivilege",
            "SeLoadDriverPrivilege", "SeBackupPrivilege",
            "SeRestorePrivilege", "SeDebugPrivilege",
            "SeSystemEnvironmentPrivilege", "SeImpersonatePrivilege"
        ]

        assigned = random.sample(privileges, random.randint(1, 4))

        event = self._base_security_event(4672, "Special privileges assigned to new logon")

        event["user"] = {
            "name": username,
            "domain": domain
        }

        event["winlog"]["event_data"] = {
            "SubjectUserName": username,
            "SubjectDomainName": domain,
            "PrivilegeList": "\n\t\t\t".join(assigned)
        }

        event["message"] = f"Special privileges assigned to new logon. User: {domain}\\{username}"

        return event


class WindowsSystemGenerator(BaseGenerator):
    """Generator for Windows System events."""

    DATA_STREAM = "logs-windows.system-default"

    EVENT_TYPES = [
        {"id": 7036, "weight": 40, "name": "Service state change"},
        {"id": 7040, "weight": 20, "name": "Service start type changed"},
        {"id": 6005, "weight": 15, "name": "Event Log service started"},
        {"id": 6006, "weight": 10, "name": "Event Log service stopped"},
        {"id": 1, "weight": 15, "name": "System time synchronized"}
    ]

    def generate(self) -> Tuple[Dict, str]:
        """Generate a Windows System event."""
        weights = [e["weight"] for e in self.EVENT_TYPES]
        event_type = random.choices(self.EVENT_TYPES, weights=weights)[0]

        return self._generate_system_event(event_type), self.DATA_STREAM

    def _generate_system_event(self, event_type: Dict) -> Dict:
        """Generate a system event."""
        computer = random.choice(COMPUTER_NAMES)
        event = self._base_event("windows.system", "windows")

        event.update({
            "host": {
                "name": computer,
                "hostname": computer,
                "os": {
                    "family": "windows",
                    "name": "Windows Server 2019",
                    "platform": "windows"
                }
            },
            "winlog": {
                "channel": "System",
                "event_id": str(event_type["id"]),
                "provider_name": "Service Control Manager" if event_type["id"] in [7036, 7040] else "EventLog",
                "computer_name": computer,
                "record_id": random.randint(100000, 999999),
                "keywords": ["Classic"],
                "opcode": "Info"
            },
            "event": {
                **event["event"],
                "code": str(event_type["id"]),
                "action": event_type["name"],
                "category": ["configuration"],
                "type": ["change"]
            },
            "log": {
                "level": "information"
            }
        })

        if event_type["id"] in [7036, 7040]:
            service = random.choice(SERVICES)
            state = random.choice(["running", "stopped"])

            event["winlog"]["event_data"] = {
                "param1": service["display"],
                "param2": state
            }
            event["message"] = f"The {service['display']} service entered the {state} state."
        elif event_type["id"] == 6005:
            event["message"] = "The Event log service was started."
        elif event_type["id"] == 6006:
            event["message"] = "The Event log service was stopped."
        else:
            event["message"] = "The system time has been synchronized."

        return event


class WindowsApplicationGenerator(BaseGenerator):
    """Generator for Windows Application events."""

    DATA_STREAM = "logs-windows.application-default"

    EVENT_TYPES = [
        {"id": 1000, "weight": 30, "name": "Application error", "level": "error"},
        {"id": 1001, "weight": 25, "name": "Windows Error Reporting", "level": "information"},
        {"id": 1002, "weight": 20, "name": "Application hang", "level": "error"},
        {"id": 11707, "weight": 15, "name": "Installation completed successfully", "level": "information"},
        {"id": 11724, "weight": 10, "name": "Product removal completed", "level": "information"}
    ]

    def generate(self) -> Tuple[Dict, str]:
        """Generate a Windows Application event."""
        weights = [e["weight"] for e in self.EVENT_TYPES]
        event_type = random.choices(self.EVENT_TYPES, weights=weights)[0]

        return self._generate_app_event(event_type), self.DATA_STREAM

    def _generate_app_event(self, event_type: Dict) -> Dict:
        """Generate an application event."""
        computer = random.choice(COMPUTER_NAMES)
        app = random.choice(APPLICATIONS)
        process = random.choice(PROCESSES)

        event = self._base_event("windows.application", "windows")

        event.update({
            "host": {
                "name": computer,
                "hostname": computer,
                "os": {
                    "family": "windows",
                    "name": "Windows Server 2019",
                    "platform": "windows"
                }
            },
            "winlog": {
                "channel": "Application",
                "event_id": str(event_type["id"]),
                "provider_name": app["source"],
                "computer_name": computer,
                "record_id": random.randint(100000, 999999),
                "keywords": ["Classic"],
                "opcode": "Info"
            },
            "event": {
                **event["event"],
                "code": str(event_type["id"]),
                "action": event_type["name"],
                "category": ["process"],
                "type": ["error"] if event_type["level"] == "error" else ["info"]
            },
            "log": {
                "level": event_type["level"]
            }
        })

        if event_type["id"] == 1000:
            event["winlog"]["event_data"] = {
                "param1": process["name"],
                "param2": "10.0.19041.1",
                "param3": random.choice(["c0000005", "c0000094", "c0000374"]),
                "param4": hex(random.randint(0x10000, 0xFFFFF))
            }
            event["message"] = f"Faulting application name: {process['name']}, Faulting module: ntdll.dll"
        elif event_type["id"] == 1002:
            event["winlog"]["event_data"] = {
                "param1": process["name"],
                "param2": "10.0.19041.1"
            }
            event["message"] = f"The program {process['name']} stopped interacting with Windows."
        elif event_type["id"] == 11707:
            event["message"] = "Product: Microsoft Visual C++ 2019 -- Installation completed successfully."
        elif event_type["id"] == 11724:
            event["message"] = "Product: Microsoft Visual C++ 2019 -- Removal completed successfully."
        else:
            event["message"] = f"Windows Error Reporting: Fault bucket, type 0"

        return event
