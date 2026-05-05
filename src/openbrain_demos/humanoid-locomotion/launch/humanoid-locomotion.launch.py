"""Stub launch for the 'humanoid-locomotion' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_humanoid_locomotion] TODO: RL humanoid locomotion controller running on the edge."
            ),
        ]
    )
