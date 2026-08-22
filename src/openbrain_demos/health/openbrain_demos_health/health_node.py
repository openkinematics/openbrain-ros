"""Publishes Jetson telemetry on /system/health.

Sources telemetry from two backends:

  * **Jetson path**: prefers `jetson_stats` (the `jtop` library) when running
    on a real Jetson — it surfaces tegrastats-quality CPU/GPU/RAM/thermal/power.
  * **Generic path**: falls back to `psutil` so the node still runs (and the
    dashboard still gets a populated message) on a developer laptop in CI.

The published message shape is the v1 contract documented in
`openbrain_msgs/SystemHealth.msg`, which mirrors the dashboard's
`SystemHealthMsg` TypeScript interface — drift here breaks the dashboard.
"""

from __future__ import annotations

import math
import sys
import time

import psutil
import rclpy
from openbrain_msgs.msg import PowerRail, SystemHealth, ThermalZone
from rclpy.node import Node


class HealthNode(Node):
    PUBLISH_PERIOD_SEC = 1.0

    def __init__(self) -> None:
        super().__init__("openbrain_health")
        self._pub = self.create_publisher(SystemHealth, "/system/health", 10)
        self._jtop = self._try_jtop()
        self._t0 = time.monotonic()
        self.create_timer(self.PUBLISH_PERIOD_SEC, self._tick)
        self.get_logger().info(
            f"publishing /system/health from {'jtop' if self._jtop else 'psutil'} backend"
        )

    def _tick(self) -> None:
        msg = SystemHealth()
        msg.header.stamp = self.get_clock().now().to_msg()

        if self._jtop is not None and self._jtop.ok():
            self._fill_from_jtop(msg)
        else:
            self._fill_from_psutil(msg)

        msg.uptime_s = int(time.monotonic() - self._t0)
        msg.node_names_running = [n[0] for n in self.get_node_names_and_namespaces()]
        self._pub.publish(msg)

    # ---- backends -----------------------------------------------------

    def _fill_from_jtop(self, msg: SystemHealth) -> None:  # pragma: no cover - hardware path
        cpu = self._jtop.cpu
        gpu = self._jtop.gpu
        mem = self._jtop.memory
        power = self._jtop.power
        temps = self._jtop.temperature

        msg.cpu_per_core = [float(c.get("val", 0.0)) for c in cpu.get("cpu", [])]
        msg.cpu_temp_c = float(temps.get("CPU", {}).get("temp", float("nan")))
        msg.gpu_percent = float(gpu.get("ga10b", {}).get("status", {}).get("load", 0.0))
        msg.gpu_temp_c = float(temps.get("GPU", {}).get("temp", float("nan")))
        msg.ram_used_bytes = int(mem.get("RAM", {}).get("used", 0)) * 1024
        msg.ram_total_bytes = int(mem.get("RAM", {}).get("total", 0)) * 1024
        msg.thermal_zones = [
            ThermalZone(name=name, temp_c=float(zone.get("temp", float("nan"))))
            for name, zone in temps.items()
        ]
        msg.power_rails = [
            PowerRail(
                name=name,
                voltage_v=float(rail.get("volt", 0)) / 1000.0,
                current_a=float(rail.get("cur", 0)) / 1000.0,
            )
            for name, rail in power.get("rail", {}).items()
        ]

    def _fill_from_psutil(self, msg: SystemHealth) -> None:
        msg.cpu_per_core = [float(p) for p in psutil.cpu_percent(interval=None, percpu=True)]
        msg.cpu_temp_c = _first_temp(["coretemp", "cpu_thermal", "k10temp"])
        msg.gpu_percent = 0.0  # unknown without jtop / nvidia-smi
        msg.gpu_temp_c = float("nan")
        vmem = psutil.virtual_memory()
        msg.ram_used_bytes = int(vmem.used)
        msg.ram_total_bytes = int(vmem.total)
        msg.thermal_zones = _all_temps()
        msg.power_rails = []  # not available outside Jetson

    def _try_jtop(self):
        try:
            from jtop import jtop  # type: ignore
        except ImportError:
            return None
        try:
            j = jtop()
            j.start()
            return j
        except Exception:  # pragma: no cover - hardware path
            return None


def _first_temp(prefixes: list[str]) -> float:
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    for prefix in prefixes:
        for label, entries in temps.items():
            if not label.startswith(prefix):
                continue
            for entry in entries:
                if entry.current is not None:
                    return float(entry.current)
    return float("nan")


def _all_temps() -> list[ThermalZone]:
    zones: list[ThermalZone] = []
    if not hasattr(psutil, "sensors_temperatures"):
        return zones
    for label, entries in psutil.sensors_temperatures().items():
        for entry in entries:
            value = entry.current
            if value is None:
                continue
            zones.append(
                ThermalZone(
                    name=f"{label}/{entry.label}" if entry.label else label,
                    temp_c=float(value),
                )
            )
    return zones


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = HealthNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


# Keep math import live for the NaN constants above.
_ = math.nan


if __name__ == "__main__":
    main()
