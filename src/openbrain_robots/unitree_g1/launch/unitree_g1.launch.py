"""Launch the Unitree G1 adapter scaffold."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_robots_unitree_g1",
                executable="unitree_g1_adapter",
                name="unitree_g1_adapter",
                output="screen",
            ),
        ]
    )
