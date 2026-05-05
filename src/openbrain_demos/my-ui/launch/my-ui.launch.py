"""Stub launch for the 'my-ui' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_my_ui] TODO: Build a custom dashboard panel from scratch."
            ),
        ]
    )
