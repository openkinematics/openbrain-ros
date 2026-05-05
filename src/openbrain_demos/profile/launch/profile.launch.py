"""Launch the operator-profile node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("active_user", default_value="default"),
            DeclareLaunchArgument("root", default_value="/opt/openbrain/profiles"),
            Node(
                package="openbrain_demos_profile",
                executable="profile_node",
                name="openbrain_profile",
                output="screen",
                parameters=[
                    {
                        "active_user": LaunchConfiguration("active_user"),
                        "root": LaunchConfiguration("root"),
                    }
                ],
            ),
        ]
    )
