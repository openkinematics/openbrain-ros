"""Stub launch for the 'rosa-voice-control' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_rosa_voice_control] TODO: ROSA voice-control: speak commands, the robot acts on them."
            ),
        ]
    )
