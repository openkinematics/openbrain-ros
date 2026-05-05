"""Phase-3 stub for the Xsens MTi-630 / MTi-680G IMU."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(msg="[openbrain_drivers_xsens] TODO: Phase 3 — wrap Xsens MTi ROS 2 driver."),
        ]
    )
