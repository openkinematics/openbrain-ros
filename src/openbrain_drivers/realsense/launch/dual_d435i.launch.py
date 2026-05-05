"""Bring up two RealSense D435i cameras as the front/back pair.

Reads serial numbers from launch arguments (provided by the bringup layer
from `config/{mini,max}.yaml`). Each camera is namespaced so its topics land
under `/camera/front/*` and `/camera/back/*` per the v1 API contract. A
camera with an empty serial argument is silently skipped so partial-hardware
boxes still launch.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def _camera_group(name: str, serial_arg: str) -> GroupAction:
    config = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_drivers_realsense"),
            "config",
            "d435i.yaml",
        ]
    )

    serial = LaunchConfiguration(serial_arg)
    has_serial = PythonExpression(["'", serial, "' != ''"])

    return GroupAction(
        condition=IfCondition(has_serial),
        actions=[
            PushRosNamespace(["camera/", name]),
            Node(
                package="realsense2_camera",
                executable="realsense2_camera_node",
                name=f"{name}_realsense",
                output="screen",
                parameters=[config, {"serial_no": serial, "camera_name": name}],
            ),
        ],
    )


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "front_serial", default_value="", description="USB serial of the front D435i."
            ),
            DeclareLaunchArgument(
                "back_serial", default_value="", description="USB serial of the back D435i."
            ),
            _camera_group("front", "front_serial"),
            _camera_group("back", "back_serial"),
        ]
    )
