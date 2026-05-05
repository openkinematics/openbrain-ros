"""Phase-3 stub for the Hesai JT128 driver."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_drivers_hesai] TODO: Phase 3 — wrap HesaiLidar_SDK_2.0 for JT128 with ISO 13849-1 PLd safety layer."
            ),
        ]
    )
