"""Stub launch for the 'groot-vla-pick-place' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_groot_vla_pick_place] TODO: GR00T VLA model running on the edge for tabletop pick-and-place."
            ),
        ]
    )
