"""Cockpit demo — bring up the default teleop stack on a Mini box.

Identical to mini.launch.py but with a different name so users can
``ros2 launch openbrain_demos_cockpit cockpit.launch.py`` straight from the
demo catalog.
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("openbrain_bringup"),
                            "launch",
                            "mini.launch.py",
                        ]
                    )
                ),
            ),
        ]
    )
