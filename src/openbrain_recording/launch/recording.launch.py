"""Launch the recording controller node."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="openbrain_recording",
                executable="recording_node",
                name="openbrain_recording",
                output="screen",
            ),
        ]
    )
