"""`openbrain logs` — tail journalctl + ROS logs."""

from __future__ import annotations

import subprocess


def run() -> int:
    cmd = ["journalctl", "-u", "openbrain.service", "-f", "--no-pager"]
    return subprocess.call(cmd)
