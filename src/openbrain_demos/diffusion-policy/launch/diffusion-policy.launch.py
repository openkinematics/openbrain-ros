"""Stub launch for the 'diffusion-policy' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_diffusion_policy] TODO: Diffusion-policy imitation learning rollout on the robot."
            ),
        ]
    )
