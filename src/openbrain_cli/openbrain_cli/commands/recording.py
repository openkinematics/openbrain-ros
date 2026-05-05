"""`openbrain record / stop / play` — thin wrappers."""

from __future__ import annotations

import os
import subprocess
import sys


def start() -> int:
    return _trigger("/recording/start")


def stop() -> int:
    return _trigger("/recording/stop")


def play(name: str, *, rate: float) -> int:
    target = f"/recordings/{name}"
    if not os.path.isdir(target):
        print(f"no such bag: {target}", file=sys.stderr)
        return 2
    cmd = ["ros2", "bag", "play", target, "--rate", str(rate)]
    print(" ".join(cmd))
    return subprocess.call(cmd)


# ---- helpers -------------------------------------------------------------


def _trigger(service: str) -> int:
    cmd = ["ros2", "service", "call", service, "std_srvs/srv/Trigger"]
    print(" ".join(cmd))
    return subprocess.call(cmd)
