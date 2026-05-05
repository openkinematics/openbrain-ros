"""`openbrain status` and `openbrain ip` implementations."""

from __future__ import annotations

import socket
import subprocess
from pathlib import Path


def run() -> int:
    print(_box("OpenBrain status"))
    print(f"  robot.conf : {_robot_conf_summary()}")
    print(f"  hostname   : {socket.gethostname()}")
    print(f"  ips        : {', '.join(_local_ips()) or '(none)'}")
    print(f"  rosbridge  : {_port_status(9090)}")
    print(f"  streamer   : {_port_status(8080)}")
    print(f"  systemd    : {_systemd_unit_status('openbrain.service')}")
    print()
    print("Recent journalctl (last 20 lines):")
    print(_recent_journal())
    return 0


def print_ips() -> int:
    for ip in _local_ips():
        print(ip)
    return 0


# ---- helpers -------------------------------------------------------------


def _robot_conf_summary() -> str:
    path = Path("/etc/openbrain/robot.conf")
    if not path.exists():
        return "missing — run `sudo ./install.sh`"
    parts = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        parts.append(line)
    return "; ".join(parts) or "(empty)"


def _local_ips() -> list[str]:
    try:
        out = subprocess.check_output(["hostname", "-I"], text=True, timeout=2)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return []
    return [ip for ip in out.split() if ip and not ip.startswith("127.")]


def _port_status(port: int) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect(("127.0.0.1", port))
        return f"listening on :{port}"
    except OSError:
        return f"NOT listening on :{port}"
    finally:
        sock.close()


def _systemd_unit_status(unit: str) -> str:
    try:
        out = subprocess.check_output(
            ["systemctl", "is-active", unit],
            text=True,
            timeout=2,
            stderr=subprocess.STDOUT,
        ).strip()
        return out
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return f"unknown ({exc})"


def _recent_journal() -> str:
    try:
        return subprocess.check_output(
            ["journalctl", "-u", "openbrain.service", "-n", "20", "--no-pager"],
            text=True,
            timeout=3,
            stderr=subprocess.STDOUT,
        ).rstrip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "(journalctl unavailable)"


def _box(title: str) -> str:
    bar = "─" * (len(title) + 2)
    return f"┌{bar}┐\n│ {title} │\n└{bar}┘"
