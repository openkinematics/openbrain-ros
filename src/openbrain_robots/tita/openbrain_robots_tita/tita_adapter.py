"""DirectDrive Tita adapter (Phase 2 scaffold).

Tita's vendor SDK is C++-only and exposes a CAN-bus joint command stream;
wiring it into a clean /cmd_vel translation needs a body-balance controller
that is out of scope for v0.1. Pass-through scaffold for now.
"""

from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Twist
from openbrain_robots_generic.robot_adapter import RobotAdapter


class TitaAdapter(RobotAdapter):
    def __init__(self) -> None:
        super().__init__("tita_adapter")
        self.get_logger().warn("Tita adapter is a Phase-2 scaffold; /cmd_vel is not forwarded.")

    def send_velocity(self, twist: Twist) -> None:  # noqa: ARG002
        return  # TODO(phase-2): wire to Tita SDK + balance controller.


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = TitaAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
