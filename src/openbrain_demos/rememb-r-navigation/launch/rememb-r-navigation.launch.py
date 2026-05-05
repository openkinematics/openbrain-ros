"""Stub launch for the 'rememb-r-navigation' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_rememb_r_navigation] TODO: Memory-augmented topological navigation that remembers landmarks."
            ),
        ]
    )
