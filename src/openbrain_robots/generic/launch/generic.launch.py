"""Launch the generic pass-through robot adapter."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_robots_generic",
                executable="generic_adapter",
                name="generic_adapter",
                output="screen",
            ),
        ]
    )
