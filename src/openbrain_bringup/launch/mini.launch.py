"""Bring up everything needed on a Kinematics Mini box.

Mini = Jetson Orin Nano 8 GB + 2× Intel RealSense D435i.

Stack:
  - dual D435i cameras                (openbrain_drivers_realsense)
  - RTAB-Map SLAM (front camera + odom)  (openbrain_slam)
  - Nav2 stack                        (openbrain_nav)
  - rosbridge :9090 + WebRTC :8080    (openbrain_teleop)
  - robot adapter (auto-detected)     (openbrain_robots_*)
"""

import os
import sys

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# Local helper lives next to this file; add ourselves to sys.path so it imports.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _robot_type import adapter_for, detect_robot_type  # noqa: E402


def generate_launch_description() -> LaunchDescription:
    front_serial = LaunchConfiguration("front_serial")
    back_serial = LaunchConfiguration("back_serial")
    enable_nav = LaunchConfiguration("enable_nav")
    enable_slam = LaunchConfiguration("enable_slam")
    enable_edge_status = LaunchConfiguration("enable_edge_status")
    edge_hardware_profile = LaunchConfiguration("edge_hardware_profile")
    edge_skill_descriptor = LaunchConfiguration("edge_skill_descriptor")
    edge_runtime_state = LaunchConfiguration("edge_runtime_state")
    edge_status_allowed_origin = LaunchConfiguration("edge_status_allowed_origin")
    # `robot_type` is declared below as a launch arg so the user can
    # override it from the CLI; the current process picks the adapter
    # from `detect_robot_type()` (env / robot.conf / fallback) directly.

    detected = detect_robot_type(os.environ.get("ROBOT_TYPE_OVERRIDE"))
    adapter_pkg, adapter_launch = adapter_for(detected)

    realsense = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("openbrain_drivers_realsense"),
                    "launch",
                    "dual_d435i.launch.py",
                ]
            )
        ),
        launch_arguments={"front_serial": front_serial, "back_serial": back_serial}.items(),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("openbrain_slam"),
                    "launch",
                    "rtabmap.launch.py",
                ]
            )
        ),
        condition=_if(enable_slam),
    )

    nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("openbrain_nav"),
                    "launch",
                    "nav2.launch.py",
                ]
            )
        ),
        condition=_if(enable_nav),
    )

    teleop = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("openbrain_teleop"),
                    "launch",
                    "teleop.launch.py",
                ]
            )
        ),
    )

    adapter = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare(adapter_pkg),
                    "launch",
                    adapter_launch,
                ]
            )
        ),
    )

    edge_status = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("openbrain_connector"), "launch", "connector.launch.py"]
            )
        ),
        condition=_if(enable_edge_status),
        launch_arguments={
            "hardware_profile": edge_hardware_profile,
            "skill_descriptor": edge_skill_descriptor,
            "runtime_state": edge_runtime_state,
            "allowed_origin": edge_status_allowed_origin,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_type",
                default_value=detected,
                description="UNITREE_GO2 | UNITREE_G1 | TITA | GENERIC",
            ),
            DeclareLaunchArgument(
                "front_serial", default_value=os.environ.get("OPENBRAIN_FRONT_SERIAL", "")
            ),
            DeclareLaunchArgument(
                "back_serial", default_value=os.environ.get("OPENBRAIN_BACK_SERIAL", "")
            ),
            DeclareLaunchArgument("enable_slam", default_value="true"),
            DeclareLaunchArgument("enable_nav", default_value="true"),
            DeclareLaunchArgument("enable_edge_status", default_value="false"),
            DeclareLaunchArgument(
                "edge_hardware_profile",
                default_value=os.environ.get(
                    "OPENBRAIN_EDGE_HARDWARE_PROFILE",
                    "/etc/openbrain/hardware-profile.json",
                ),
            ),
            DeclareLaunchArgument(
                "edge_skill_descriptor",
                default_value=os.environ.get(
                    "OPENBRAIN_EDGE_SKILL_DESCRIPTOR",
                    "/etc/openbrain/active-skill.json",
                ),
            ),
            DeclareLaunchArgument(
                "edge_runtime_state",
                default_value=os.environ.get(
                    "OPENBRAIN_EDGE_RUNTIME_STATE",
                    "/run/openbrain/skill-runtime.json",
                ),
            ),
            DeclareLaunchArgument(
                "edge_status_allowed_origin",
                default_value=os.environ.get(
                    "OPENBRAIN_DASHBOARD_ORIGIN",
                    "http://localhost:3000",
                ),
            ),
            LogInfo(
                msg=[f"[openbrain_bringup] mini box, robot_type={detected}, adapter={adapter_pkg}"]
            ),
            realsense,
            slam,
            nav,
            teleop,
            edge_status,
            adapter,
        ]
    )


def _if(cfg):
    """Tiny IfCondition wrapper that takes a LaunchConfiguration directly."""
    from launch.conditions import IfCondition

    return IfCondition(cfg)
