"""Launch the Unitree Go2 adapter."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    network_interface = LaunchConfiguration("network_interface")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "network_interface",
                default_value="eth0",
                description="Ethernet interface that talks to the Go2 over CycloneDDS.",
            ),
            Node(
                package="openbrain_robots_unitree_go2",
                executable="unitree_go2_adapter",
                name="unitree_go2_adapter",
                output="screen",
                parameters=[{"network_interface": network_interface}],
            ),
        ]
    )
