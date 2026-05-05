"""Phase-2 stub for the NVBlox 3D-mapping bridge.

The rich "what's needed" instructions live in the
[`nvblox-mapping`](../../openbrain_demos/nvblox-mapping) demo's README —
hardware list, exact apt packages, Nav2 wiring steps, estimated effort.

When the demo graduates, replace this LogInfo with an
``IncludeLaunchDescription`` of the demo's launch (same pattern as
``yolo.launch.py``).
"""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "[openbrain_perception/nvblox] TODO: Phase 2 — see "
                    "src/openbrain_demos/nvblox-mapping/README.md for the full "
                    "'What's needed to make this work' checklist."
                )
            ),
        ]
    )
