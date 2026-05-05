"""Self-test checks. Pure-Python so they're testable without rclpy.

Each check returns a :class:`CheckResult`. The doctor CLI prints them in a
human-friendly table; the diagnostics ROS node maps them onto
``diagnostic_msgs/DiagnosticArray`` so the dashboard can show them in its
Diagnostics tab.

Add new checks by appending to :data:`CHECKS` — each entry is
``(name, callable)``. The callable takes no arguments and returns a
``CheckResult``.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


class Severity(IntEnum):
    OK = 0
    WARN = 1
    ERROR = 2
    UNKNOWN = 3


@dataclass
class CheckResult:
    name: str
    severity: Severity
    message: str
    details: dict = field(default_factory=dict)


CheckFn = Callable[[], CheckResult]


# ---- individual checks -----------------------------------------------------


def check_disk_space() -> CheckResult:
    """At least 5 GB free on the partition holding /maps and /recordings."""
    target = "/" if not Path("/maps").exists() else "/maps"
    try:
        usage = shutil.disk_usage(target)
    except OSError as exc:
        return CheckResult("disk", Severity.ERROR, f"disk_usage failed: {exc}")
    free_gb = usage.free / 1e9
    sev = Severity.OK if free_gb > 5.0 else Severity.WARN if free_gb > 1.0 else Severity.ERROR
    return CheckResult(
        "disk",
        sev,
        f"{free_gb:.1f} GB free on {target}",
        {"free_bytes": usage.free, "total_bytes": usage.total, "path": target},
    )


def check_thermal() -> CheckResult:
    """Highest thermal-zone reading must be under 85 °C."""
    zones: list[tuple[str, float]] = []
    base = Path("/sys/class/thermal")
    if not base.exists():
        return CheckResult("thermal", Severity.UNKNOWN, "no /sys/class/thermal")
    for zone in sorted(base.glob("thermal_zone*")):
        try:
            value = int((zone / "temp").read_text().strip()) / 1000.0
            label = (zone / "type").read_text().strip()
            zones.append((label, value))
        except OSError:
            continue
    if not zones:
        return CheckResult("thermal", Severity.UNKNOWN, "no thermal zones readable")
    label, hottest = max(zones, key=lambda z: z[1])
    sev = Severity.OK if hottest < 75 else Severity.WARN if hottest < 85 else Severity.ERROR
    return CheckResult(
        "thermal",
        sev,
        f"hottest zone: {label} @ {hottest:.1f} °C",
        {"zones": [{"name": n, "temp_c": t} for n, t in zones]},
    )


def check_gpu() -> CheckResult:
    """Detect an NVIDIA GPU via tegrastats (Jetson) or nvidia-smi (desktop)."""
    if Path("/etc/nv_tegra_release").exists():
        return CheckResult("gpu", Severity.OK, "Jetson (tegra) detected", {"backend": "tegra"})
    if shutil.which("nvidia-smi"):
        try:
            out = (
                subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                    text=True,
                    timeout=5,
                )
                .strip()
                .splitlines()
            )
            return CheckResult("gpu", Severity.OK, f"{len(out)} GPU(s): {out[0]}", {"gpus": out})
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            return CheckResult("gpu", Severity.WARN, f"nvidia-smi failed: {exc}")
    return CheckResult("gpu", Severity.WARN, "no NVIDIA GPU detected (sim/dev mode OK)")


def check_realsense() -> CheckResult:
    """rs-enumerate-devices must list at least one camera."""
    if not shutil.which("rs-enumerate-devices"):
        return CheckResult(
            "realsense",
            Severity.UNKNOWN,
            "librealsense not installed (skip if not using RealSense)",
        )
    try:
        out = subprocess.check_output(
            ["rs-enumerate-devices", "--short"],
            text=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return CheckResult("realsense", Severity.ERROR, f"enumerate failed: {exc}")
    serials = [
        line.split()[-1]
        for line in out.splitlines()
        if line.strip().startswith("0") or line.strip().startswith("1")
    ]
    sev = Severity.OK if serials else Severity.WARN
    msg = f"{len(serials)} camera(s)" + (f" — serials {serials}" if serials else "")
    return CheckResult("realsense", sev, msg, {"serials": serials})


def check_network_route() -> CheckResult:
    """A default route must exist (otherwise rosbridge will be unreachable)."""
    try:
        out = subprocess.check_output(["ip", "route", "show", "default"], text=True, timeout=3)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return CheckResult("network", Severity.ERROR, f"ip route failed: {exc}")
    if not out.strip():
        return CheckResult("network", Severity.ERROR, "no default route")
    return CheckResult("network", Severity.OK, out.splitlines()[0].strip())


def check_rosbridge_port() -> CheckResult:
    """TCP :9090 should be listening (rosbridge running)."""
    return _check_local_port("rosbridge", 9090)


def check_streamer_port() -> CheckResult:
    """TCP :8080 should be listening (video streamer running)."""
    return _check_local_port("streamer", 8080)


def check_etc_robot_conf() -> CheckResult:
    """``/etc/openbrain/robot.conf`` must exist and declare a robot_type."""
    path = Path("/etc/openbrain/robot.conf")
    if not path.exists():
        return CheckResult("robot.conf", Severity.WARN, "missing — run `sudo ./install.sh`")
    body = path.read_text()
    for line in body.splitlines():
        if line.strip().startswith("robot_type="):
            return CheckResult(
                "robot.conf",
                Severity.OK,
                line.strip(),
                {"path": str(path)},
            )
    return CheckResult("robot.conf", Severity.WARN, "robot_type= line missing")


def check_ros_env() -> CheckResult:
    """ROS_DISTRO should be set to humble."""
    distro = os.environ.get("ROS_DISTRO", "")
    if distro == "humble":
        return CheckResult("ros_env", Severity.OK, "ROS_DISTRO=humble")
    if distro:
        return CheckResult("ros_env", Severity.WARN, f"ROS_DISTRO={distro!r} (expected humble)")
    return CheckResult(
        "ros_env", Severity.WARN, "ROS_DISTRO unset — source /opt/ros/humble/setup.bash"
    )


CHECKS: list[CheckFn] = [
    check_ros_env,
    check_etc_robot_conf,
    check_disk_space,
    check_thermal,
    check_gpu,
    check_realsense,
    check_network_route,
    check_rosbridge_port,
    check_streamer_port,
]


def run_all_checks() -> list[CheckResult]:
    return [fn() for fn in CHECKS]


# ---- helpers ---------------------------------------------------------------


def _check_local_port(name: str, port: int) -> CheckResult:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect(("127.0.0.1", port))
    except (TimeoutError, OSError):
        return CheckResult(name, Severity.WARN, f":{port} not listening")
    finally:
        sock.close()
    return CheckResult(name, Severity.OK, f":{port} accepting connections")


def to_json(results: list[CheckResult]) -> str:
    return json.dumps(
        [
            {
                "name": r.name,
                "severity": r.severity.name,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ],
        indent=2,
    )
