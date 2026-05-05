"""Stub launch for the 'openvla-grasp' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_openvla_grasp] TODO: OpenVLA grasping policy on a 6-DoF arm."
            ),
        ]
    )
