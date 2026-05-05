"""Launch rosbridge_server WebSocket on :9090 (dashboard contract)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    port = LaunchConfiguration("port")
    address = LaunchConfiguration("address")

    return LaunchDescription(
        [
            DeclareLaunchArgument("port", default_value="9090"),
            DeclareLaunchArgument("address", default_value="0.0.0.0"),
            Node(
                package="rosbridge_server",
                executable="rosbridge_websocket",
                name="rosbridge_websocket",
                output="screen",
                parameters=[
                    {
                        "port": port,
                        "address": address,
                        "call_services_in_new_thread": True,
                        "max_message_size": 10_000_000,  # 10 MB to fit large /robot_description URDFs
                    }
                ],
            ),
        ]
    )
