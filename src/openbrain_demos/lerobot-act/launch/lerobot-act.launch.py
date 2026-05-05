"""Stub launch for the 'lerobot-act' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_lerobot_act] TODO: Action-chunking policy from the LeRobot stack."
            ),
        ]
    )
