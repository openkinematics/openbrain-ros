"""Stub launch for the 'edge-nerf' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_edge_nerf] TODO: On-edge NeRF capture from the robot's cameras."
            ),
        ]
    )
