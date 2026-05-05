"""`openbrain update` — pull the latest image and restart the unit.

Reads the image tag from `/etc/openbrain/robot.conf` (`image=` line) so an
operator can pin a specific version by editing one file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONF = Path("/etc/openbrain/robot.conf")
DEFAULT_IMAGE = "ghcr.io/openkinematics/openbrain-ros:latest"


def run() -> int:
    image = _image_from_conf() or DEFAULT_IMAGE
    print(f"pulling {image}")
    rc = subprocess.call(["docker", "pull", image])
    if rc != 0:
        print(f"docker pull failed (rc={rc})", file=sys.stderr)
        return rc
    print("restarting openbrain.service")
    return subprocess.call(["systemctl", "restart", "openbrain.service"])


def _image_from_conf() -> str | None:
    if not CONF.exists():
        return None
    for line in CONF.read_text().splitlines():
        line = line.strip()
        if line.startswith("image="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None
