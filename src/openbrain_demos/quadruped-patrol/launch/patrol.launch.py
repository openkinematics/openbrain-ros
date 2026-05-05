"""Launch the quadruped patrol orchestrator.

Assumes the missions node + Nav2 + a robot adapter are already running
(typically via ``openbrain_bringup/mini.launch.py``). This launch only
adds the patrol orchestrator on top.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_demos_quadruped_patrol"),
            "config",
            "default.yaml",
        ]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("loop_file", default_value=""),
            DeclareLaunchArgument("low_threshold_pct", default_value="25.0"),
            DeclareLaunchArgument("resume_threshold_pct", default_value="75.0"),
            DeclareLaunchArgument("critical_threshold_pct", default_value="10.0"),
            Node(
                package="openbrain_demos_quadruped_patrol",
                executable="patrol_node",
                name="openbrain_quadruped_patrol",
                output="screen",
                parameters=[
                    cfg,
                    {
                        "loop_file": LaunchConfiguration("loop_file"),
                        "low_threshold_pct": LaunchConfiguration("low_threshold_pct"),
                        "resume_threshold_pct": LaunchConfiguration("resume_threshold_pct"),
                        "critical_threshold_pct": LaunchConfiguration("critical_threshold_pct"),
                    },
                ],
            ),
        ]
    )
