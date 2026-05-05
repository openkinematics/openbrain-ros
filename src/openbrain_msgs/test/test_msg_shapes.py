"""Schema-drift guard for the v1 contract.

If any of these tests fail, the dashboard's
`lib/types.ts :: SystemHealthMsg` (and friends) will silently break in
production — rosbridge serializes JSON and missing fields land as
``undefined`` on the client. So we lock the field names + types here and
require an explicit edit (with a coordinated dashboard PR) to change.

These tests are pure Python and read the .msg / .srv files as text — no
rclpy needed, so they run on every machine.
"""

from __future__ import annotations

import re
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent
MSG_DIR = PKG_ROOT / "msg"
SRV_DIR = PKG_ROOT / "srv"


def _fields(path: Path) -> list[tuple[str, str]]:
    """Return [(type, name), ...] for each declarative line in a msg/srv file."""
    out: list[tuple[str, str]] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line == "---":
            break_marker = line == "---"
            if break_marker:
                # Stop at the request/response separator for srv files.
                break
            continue
        # Drop default values and constants — we just want type + name.
        line = line.split("#", 1)[0].strip()
        if "=" in line and not line.startswith("string"):
            # Constant declarations like `uint8 STATE_IDLE = 0` — the type
            # and name still appear in the same shape as a normal field.
            line = line.split("=", 1)[0].strip()
        m = re.match(r"^([\w/\[\]]+)\s+(\w+)\s*$", line)
        if m:
            # (name, type) so callers can build `dict[name -> type]`.
            out.append((m.group(2), m.group(1)))
    return out


# ---- SystemHealth.msg ----------------------------------------------------


def test_system_health_field_names():
    """The dashboard's TypeScript shape uses these exact names."""
    fields = dict(_fields(MSG_DIR / "SystemHealth.msg"))
    expected = {
        "header": "std_msgs/Header",
        "cpu_per_core": "float32[]",
        "cpu_temp_c": "float32",
        "gpu_percent": "float32",
        "gpu_temp_c": "float32",
        "ram_used_bytes": "uint64",
        "ram_total_bytes": "uint64",
        "thermal_zones": "openbrain_msgs/ThermalZone[]",
        "power_rails": "openbrain_msgs/PowerRail[]",
        "uptime_s": "uint64",
        "node_names_running": "string[]",
    }
    for name, ros_type in expected.items():
        assert name in fields, f"SystemHealth.msg missing field {name!r}"
        assert fields[name] == ros_type, (
            f"SystemHealth.{name} type drift: expected {ros_type!r}, got {fields[name]!r}"
        )


def test_system_health_no_unexpected_required_fields():
    """Adding fields is fine; renaming or removing them isn't."""
    fields = dict(_fields(MSG_DIR / "SystemHealth.msg"))
    # If you intend to break the contract, edit the expected map above and
    # ship a companion PR in openbrain-dashboard.
    forbidden = {"gpu_utilization", "thermal_zones_celsius", "power_watts"}
    for name in forbidden:
        assert name not in fields, (
            f"SystemHealth.{name} reappeared — was renamed/removed in v1, "
            "do not bring it back without a v2 bump"
        )


# ---- Waypoint.msg --------------------------------------------------------


def test_waypoint_field_names():
    fields = dict(_fields(MSG_DIR / "Waypoint.msg"))
    assert fields.get("x") == "float32"
    assert fields.get("y") == "float32"
    assert fields.get("yaw") == "float32"
    assert fields.get("label") == "string"
    assert fields.get("dwell_seconds") == "float32"


# ---- LoadMission.srv -----------------------------------------------------


def test_load_mission_request_shape():
    """Dashboard sends {waypoints: [{x,y,yaw}], loop: bool}."""
    body = (SRV_DIR / "LoadMission.srv").read_text()
    request, _, response = body.partition("---")
    req_fields = dict(_fields_from_block(request))
    assert req_fields.get("waypoints") == "openbrain_msgs/Waypoint[]"
    assert req_fields.get("loop") == "bool"

    res_fields = dict(_fields_from_block(response))
    assert res_fields.get("success") == "bool"
    assert res_fields.get("message") == "string"


# ---- SetSpeedProfile.srv -------------------------------------------------


def test_set_speed_profile_shape():
    body = (SRV_DIR / "SetSpeedProfile.srv").read_text()
    request, _, response = body.partition("---")
    req_fields = dict(_fields_from_block(request))
    assert req_fields.get("profile") == "string"

    res_fields = dict(_fields_from_block(response))
    # Required by the dashboard.
    assert res_fields.get("success") == "bool"
    assert res_fields.get("message") == "string"


# ---- helpers -------------------------------------------------------------


def _fields_from_block(block: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#", 1)[0].strip()
        m = re.match(r"^([\w/\[\]]+)\s+(\w+)\s*$", line)
        if m:
            # (name, type) so callers can build `dict[name -> type]`.
            out.append((m.group(2), m.group(1)))
    return out
