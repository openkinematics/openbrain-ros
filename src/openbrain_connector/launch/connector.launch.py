"""Launch the optional read-only OpenBrain edge-status service."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    hardware_profile = LaunchConfiguration("hardware_profile")
    skill_descriptor = LaunchConfiguration("skill_descriptor")
    runtime_state = LaunchConfiguration("runtime_state")
    bind = LaunchConfiguration("bind")
    port = LaunchConfiguration("port")
    allowed_origin = LaunchConfiguration("allowed_origin")

    connector = Node(
        package="openbrain_connector",
        executable="openbrain_connector",
        name="edge_status",
        arguments=[
            "--hardware-profile",
            hardware_profile,
            "--skill-descriptor",
            skill_descriptor,
            "--runtime-state",
            runtime_state,
            "--bind",
            bind,
            "--port",
            port,
            "--allow-origin",
            allowed_origin,
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "hardware_profile",
                default_value="/etc/openbrain/hardware-profile.json",
                description="Fail-closed robot hardware profile JSON",
            ),
            DeclareLaunchArgument(
                "skill_descriptor",
                default_value="/etc/openbrain/active-skill.json",
                description="Lineage-pinned openkinematics.edge-skill.v1 JSON",
            ),
            DeclareLaunchArgument(
                "runtime_state",
                default_value="/run/openbrain/skill-runtime.json",
                description="Optional atomically replaced runtime telemetry JSON",
            ),
            DeclareLaunchArgument("bind", default_value="127.0.0.1"),
            DeclareLaunchArgument("port", default_value="8090"),
            DeclareLaunchArgument(
                "allowed_origin",
                default_value="http://localhost:3000",
                description="Exact Dashboard origin allowed by CORS",
            ),
            connector,
        ]
    )
