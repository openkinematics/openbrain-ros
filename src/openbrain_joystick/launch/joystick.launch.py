"""Launch joy_node + joystick_teleop with the configured pad mapping."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    pad = LaunchConfiguration("pad")  # one of: xbox, ps5, generic
    device = LaunchConfiguration("device")

    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_joystick"),
            "config",
            [pad, ".yaml"],
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "pad", default_value="xbox", description="Pad mapping: xbox | ps5 | generic"
            ),
            DeclareLaunchArgument(
                "device", default_value="/dev/input/js0", description="Linux joystick device path"
            ),
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                parameters=[
                    {
                        "device_id": 0,
                        "device_name": "",
                        "device_path": device,
                        "deadzone": 0.05,
                        "autorepeat_rate": 20.0,
                    }
                ],
            ),
            Node(
                package="openbrain_joystick",
                executable="joystick_teleop",
                name="joystick_teleop",
                output="screen",
                parameters=[cfg],
            ),
        ]
    )
