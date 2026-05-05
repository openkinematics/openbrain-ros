"""Helpers for detecting which robot adapter to load.

Resolution order (highest priority first):
  1. ``robot_type`` LaunchConfiguration explicitly passed at the CLI.
  2. ``ROBOT_TYPE`` environment variable.
  3. ``robot_type`` key in ``/etc/openbrain/robot.conf``  (KEY=VALUE format).
  4. Fallback: ``GENERIC``.

Recognized values: ``UNITREE_GO2``, ``UNITREE_G1``, ``TITA``, ``GENERIC``.
"""

from __future__ import annotations

import os
from pathlib import Path

VALID = {"UNITREE_GO2", "UNITREE_G1", "TITA", "GENERIC"}
CONF_PATH = Path("/etc/openbrain/robot.conf")

ADAPTER_PACKAGES = {
    "UNITREE_GO2": ("openbrain_robots_unitree_go2", "unitree_go2.launch.py"),
    "UNITREE_G1": ("openbrain_robots_unitree_g1", "unitree_g1.launch.py"),
    "TITA": ("openbrain_robots_tita", "tita.launch.py"),
    "GENERIC": ("openbrain_robots_generic", "generic.launch.py"),
}


def detect_robot_type(cli_value: str | None = None) -> str:
    if cli_value and cli_value.upper() in VALID:
        return cli_value.upper()
    env_value = os.environ.get("ROBOT_TYPE")
    if env_value and env_value.upper() in VALID:
        return env_value.upper()
    if CONF_PATH.exists():
        for line in CONF_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip().lower() == "robot_type":
                value = value.strip().strip('"').strip("'").upper()
                if value in VALID:
                    return value
    return "GENERIC"


def adapter_for(robot_type: str) -> tuple[str, str]:
    """Return (package, launch_file) for the named robot type."""
    return ADAPTER_PACKAGES[robot_type.upper()]
