"""Stub launch for the 'nvblox-mapping' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_nvblox_mapping] TODO: NVIDIA NVBlox 3D voxel + ESDF mapping from the depth pair."
            ),
        ]
    )
