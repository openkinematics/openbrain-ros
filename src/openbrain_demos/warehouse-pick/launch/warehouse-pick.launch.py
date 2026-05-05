"""Stub launch for the 'warehouse-pick' demo. Phase-2/3 implementation lands later."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_demos_warehouse_pick] TODO: Warehouse pick-and-pack reference cell with a mobile manipulator."
            ),
        ]
    )
