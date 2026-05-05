"""Launch the diagnostics ROS node."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_diagnostics",
                executable="diagnostics_node",
                name="openbrain_diagnostics",
                output="screen",
            ),
        ]
    )
