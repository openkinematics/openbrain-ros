"""Pass-through adapter for ROS 2-native robots.

Use when the robot's own driver already subscribes to /cmd_vel and publishes
/odom. The adapter is a no-op on the velocity path (the vendor driver hears
/cmd_vel directly), but still owns /robot_description and the speed profile
service so the dashboard contract is satisfied.
"""

from __future__ import annotations

import sys
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist

from openbrain_robots_generic.robot_adapter import RobotAdapter


class GenericAdapter(RobotAdapter):
    def __init__(self) -> None:
        urdf = _load_urdf_param()
        super().__init__("generic_adapter", urdf=urdf)

    def send_velocity(self, twist: Twist) -> None:
        # Pass-through: assume the robot's native driver is already listening
        # to /cmd_vel. Nothing to do.
        return


def _load_urdf_param() -> str | None:
    # A real deployment would declare a `urdf_path` parameter and read it
    # here. For the skeleton we simply check $OPENBRAIN_URDF_PATH.
    import os

    path = os.environ.get("OPENBRAIN_URDF_PATH")
    if not path:
        return None
    try:
        return Path(path).read_text()
    except OSError:
        return None


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = GenericAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
