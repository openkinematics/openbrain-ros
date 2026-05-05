"""Launch the fleet aggregator."""

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_demos_fleet_control"),
            "config",
            "default.yaml",
        ]
    )
    return LaunchDescription(
        [
            Node(
                package="openbrain_demos_fleet_control",
                executable="fleet_node",
                name="openbrain_fleet",
                output="screen",
                parameters=[cfg],
            ),
        ]
    )
