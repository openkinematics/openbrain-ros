"""Launch the HTTP video streamer (WebRTC + MJPEG) on :8080."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    config = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_teleop"),
            "config",
            "streams.yaml",
        ]
    )

    port = LaunchConfiguration("port")

    return LaunchDescription(
        [
            DeclareLaunchArgument("port", default_value="8080"),
            Node(
                package="openbrain_teleop",
                executable="video_streamer",
                name="video_streamer",
                output="screen",
                arguments=["--config", config, "--port", port],
            ),
        ]
    )
