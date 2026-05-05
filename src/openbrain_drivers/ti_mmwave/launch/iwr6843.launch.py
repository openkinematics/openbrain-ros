"""Phase-3 stub for TI IWR6843 mmWave radar."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_drivers_ti_mmwave] TODO: Phase 3 — wrap TI mmWave ROS 2 toolbox for IWR6843."
            ),
        ]
    )
