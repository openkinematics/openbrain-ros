"""Publish self-test results to /diagnostics every 5 s.

Wraps :mod:`openbrain_diagnostics.checks` into the standard
``diagnostic_msgs/DiagnosticArray`` topic so the dashboard's Diagnostics
tab and ROS-side rqt_robot_monitor both consume it for free.
"""

from __future__ import annotations

import sys

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.node import Node

from openbrain_diagnostics.checks import Severity, run_all_checks

_LEVEL = {
    Severity.OK: DiagnosticStatus.OK,
    Severity.WARN: DiagnosticStatus.WARN,
    Severity.ERROR: DiagnosticStatus.ERROR,
    Severity.UNKNOWN: DiagnosticStatus.STALE,
}


class DiagnosticsNode(Node):
    PUBLISH_PERIOD_SEC = 5.0

    def __init__(self) -> None:
        super().__init__("openbrain_diagnostics")
        self._pub = self.create_publisher(DiagnosticArray, "/diagnostics", 10)
        self.create_timer(self.PUBLISH_PERIOD_SEC, self._tick)
        self.get_logger().info("diagnostics_node ready (publishing /diagnostics every 5 s)")

    def _tick(self) -> None:
        results = run_all_checks()
        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        for r in results:
            status = DiagnosticStatus()
            status.level = _LEVEL[r.severity]
            status.name = f"openbrain/{r.name}"
            status.message = r.message
            status.hardware_id = "openbrain"
            status.values = [KeyValue(key=str(k), value=str(v)) for k, v in r.details.items()]
            msg.status.append(status)
        self._pub.publish(msg)


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = DiagnosticsNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
