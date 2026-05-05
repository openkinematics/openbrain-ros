"""Stub launch for the 'vlm-isaac-sim' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_vlm_isaac_sim] TODO: VLM in the loop with NVIDIA Isaac Sim for closed-loop policy eval."
            ),
        ]
    )
