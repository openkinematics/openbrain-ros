"""Unitree G1 humanoid adapter (Phase 2 scaffold).

The G1 has a different SDK than the Go2 (the high-level locomotion API takes
walking primitives rather than a flat Twist), so this adapter is a stub.
The pass-through behaviour from RobotAdapter is preserved so the rest of the
stack still loads.
"""

from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Twist
from openbrain_robots_generic.robot_adapter import RobotAdapter


class UnitreeG1Adapter(RobotAdapter):
    def __init__(self) -> None:
        super().__init__("unitree_g1_adapter")
        self.get_logger().warn(
            "Unitree G1 adapter is a Phase-2 scaffold; /cmd_vel is not forwarded."
        )

    def send_velocity(self, twist: Twist) -> None:  # noqa: ARG002
        return  # TODO(phase-2): translate to G1 walking primitives.


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = UnitreeG1Adapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
