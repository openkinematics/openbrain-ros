"""Launch RTAB-Map in RGB-D + odom mode against the front camera.

Defaults match the v1 contract:
  - subscribes /camera/front/color/image_raw + /camera/front/depth/image_rect_raw + /odom
  - publishes /map (nav_msgs/OccupancyGrid) and /map -> /odom TF
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    config = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_slam"),
            "config",
            "rtabmap.yaml",
        ]
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    localization = LaunchConfiguration("localization")

    rtabmap = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[
            config,
            {
                "use_sim_time": use_sim_time,
                "Mem/IncrementalMemory": ["false" if localization == "true" else "true"][0],
            },
        ],
        remappings=[
            ("rgb/image", "/camera/front/color/image_raw"),
            ("rgb/camera_info", "/camera/front/color/camera_info"),
            ("depth/image", "/camera/front/depth/image_rect_raw"),
            ("odom", "/odom"),
        ],
        arguments=["--delete_db_on_start" if localization == "false" else ""],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument(
                "localization",
                default_value="false",
                description="If true, RTAB-Map runs read-only against an existing map.",
            ),
            rtabmap,
        ]
    )
