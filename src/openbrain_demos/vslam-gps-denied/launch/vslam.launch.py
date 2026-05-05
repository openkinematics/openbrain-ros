"""GPS-denied SLAM bringup.

Replaces the default openbrain_slam config with a VIO-tuned variant —
RTAB-Map computes its own visual-inertial odometry from the front
camera + its IMU, no /odom dependency. Suitable for warehouses,
basements, and indoor drone flight where wheel-encoder / GNSS odometry
is unavailable or unreliable.

Pairs cleanly with the rest of the cockpit stack (Nav2 still consumes
/map and /odom, both produced by RTAB-Map here).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_demos_vslam_gps_denied"),
            "config",
            "rtabmap_vio.yaml",
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument(
                "force_3dof",
                default_value="false",
                description="Constrain SLAM to 3DoF (mobile robot). Set true for ground vehicles.",
            ),
            Node(
                package="rtabmap_slam",
                executable="rtabmap",
                name="rtabmap_vio",
                output="screen",
                parameters=[
                    cfg,
                    {
                        "use_sim_time": LaunchConfiguration("use_sim_time"),
                        "Reg/Force3DoF": LaunchConfiguration("force_3dof"),
                    },
                ],
                remappings=[
                    ("rgb/image", "/camera/front/color/image_raw"),
                    ("rgb/camera_info", "/camera/front/color/camera_info"),
                    ("depth/image", "/camera/front/depth/image_rect_raw"),
                    ("imu", "/camera/front/imu"),
                    # Note: no /odom remap — VIO produces its own.
                ],
                arguments=["--delete_db_on_start"],
            ),
        ]
    )
