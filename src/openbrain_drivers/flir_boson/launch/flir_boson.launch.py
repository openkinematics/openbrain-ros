"""Phase-3 stub for the FLIR Boson 640 thermal camera."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_drivers_flir_boson] TODO: Phase 3 — wrap FLIR Boson SDK over USB UVC."
            ),
        ]
    )
