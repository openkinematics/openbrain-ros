"""Resolve which Max compute SKU we are running on, and load its overlay.

Resolution order (highest priority first):

  1. ``$OPENBRAIN_MAX_SKU`` env var (e.g. ``t5000_128gb``).
  2. ``compute=`` line in ``/etc/openbrain/robot.conf``.
  3. ``/proc/device-tree/model`` (Jetson exposes the platform name here).
  4. Fallback: ``t4000_64gb`` (the Max's base SKU).

Returns the path to the per-SKU YAML overlay under
``share/openbrain_bringup/config/`` (installed by the bringup CMakeLists)
or ``None`` if the overlay cannot be found.
"""

from __future__ import annotations

import os
from pathlib import Path

KNOWN_SKUS = {
    "jetson_t4000_64gb": "max_t4000_64gb.yaml",
    "jetson_t5000_128gb": "max_t5000_128gb.yaml",
    "jetson_agx_orin_64gb": "max_agx_orin_64gb.yaml",
    # short aliases the operator might type
    "t4000": "max_t4000_64gb.yaml",
    "t4000_64gb": "max_t4000_64gb.yaml",
    "t5000": "max_t5000_128gb.yaml",
    "t5000_128gb": "max_t5000_128gb.yaml",
    "agx_orin": "max_agx_orin_64gb.yaml",
    "agx_orin_64gb": "max_agx_orin_64gb.yaml",
}

DEFAULT = "max_t4000_64gb.yaml"

CONF_PATH = Path("/etc/openbrain/robot.conf")
DEVICE_TREE_MODEL = Path("/proc/device-tree/model")


def detect_sku() -> str:
    """Return the SKU file basename (e.g. ``max_t5000_128gb.yaml``)."""
    env = os.environ.get("OPENBRAIN_MAX_SKU", "").strip().lower()
    if env and env in KNOWN_SKUS:
        return KNOWN_SKUS[env]

    conf = _read_compute_from_conf()
    if conf and conf in KNOWN_SKUS:
        return KNOWN_SKUS[conf]

    auto = _autodetect_from_device_tree()
    if auto and auto in KNOWN_SKUS:
        return KNOWN_SKUS[auto]

    return DEFAULT


def _read_compute_from_conf() -> str | None:
    if not CONF_PATH.exists():
        return None
    for raw in CONF_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip().lower() == "compute":
            return value.strip().strip('"').strip("'").lower()
    return None


def _autodetect_from_device_tree() -> str | None:
    """Best-effort: map Jetson's /proc/device-tree/model string to a SKU."""
    if not DEVICE_TREE_MODEL.exists():
        return None
    try:
        # File ends with a NUL byte on Jetson.
        model = DEVICE_TREE_MODEL.read_bytes().decode("ascii", "replace").strip("\x00\n").lower()
    except OSError:
        return None
    if "t5000" in model or "thor" in model:
        return "t5000_128gb"
    if "t4000" in model:
        return "t4000_64gb"
    if "agx orin" in model or "agx-orin" in model:
        return "agx_orin_64gb"
    return None
