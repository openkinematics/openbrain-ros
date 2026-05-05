"""`openbrain estop / estop-release` — calls the e-stop services."""

from __future__ import annotations

import subprocess


def engage() -> int:
    return _trigger("/safety/estop_engage")


def release() -> int:
    return _trigger("/safety/estop_release")


def _trigger(service: str) -> int:
    cmd = ["ros2", "service", "call", service, "std_srvs/srv/Trigger"]
    print(" ".join(cmd))
    return subprocess.call(cmd)
