"""Launch the mission state-machine."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_demos_missions",
                executable="missions_node",
                name="openbrain_missions",
                output="screen",
            ),
        ]
    )
