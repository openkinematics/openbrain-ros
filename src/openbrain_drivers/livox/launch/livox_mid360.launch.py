"""Phase-3 stub for the Livox Mid-360 driver."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_drivers_livox] TODO: Phase 3 — wrap Livox SDK 2 driver for Mid-360."
            ),
        ]
    )
