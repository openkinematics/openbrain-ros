"""Launch the Tita adapter scaffold."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_robots_tita",
                executable="tita_adapter",
                name="tita_adapter",
                output="screen",
            ),
        ]
    )
