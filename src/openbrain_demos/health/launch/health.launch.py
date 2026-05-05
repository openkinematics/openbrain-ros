"""Launch the system health publisher."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_demos_health",
                executable="health_node",
                name="openbrain_health",
                output="screen",
            ),
        ]
    )
