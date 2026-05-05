"""Bring up the Nav2 stack with OpenBrain's default params + behavior tree.

Delegates the heavy lifting to nav2_bringup.bringup_launch.py, just feeding
our params file. The map server is intentionally NOT started here — RTAB-Map
already publishes /map. AMCL is also disabled by default; RTAB-Map provides
the map->odom transform.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    params = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_nav"),
            "config",
            "nav2.yaml",
        ]
    )

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("nav2_bringup"),
                    "launch",
                    "navigation_launch.py",
                ]
            )
        ),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "params_file": params,
            "autostart": "true",
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            nav2_bringup,
        ]
    )
