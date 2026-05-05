"""Launch the safety stack (twist_mux + estop_node)."""

from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_safety"),
            "config",
            "twist_mux.yaml",
        ]
    )
    return LaunchDescription(
        [
            Node(
                package="openbrain_safety",
                executable="twist_mux",
                name="twist_mux",
                output="screen",
                parameters=[cfg],
            ),
            Node(
                package="openbrain_safety",
                executable="estop_node",
                name="estop_node",
                output="screen",
            ),
        ]
    )
