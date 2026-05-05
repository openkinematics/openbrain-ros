"""Phase-3 stub for the Quectel RM520N 5G modem manager."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg="[openbrain_drivers_quectel_5g] TODO: Phase 3 — talk to Quectel RM520N over QMI/MBIM via ModemManager."
            ),
        ]
    )
