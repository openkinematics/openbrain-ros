"""Bring up everything needed on a Kinematics Max box.

Max = Jetson AGX Orin / T4000 / T5000 + RealSense pair + LiDAR + industrial
IMU + (optional) thermal / mmWave / 5G payloads.

This is a superset of mini.launch.py with payload drivers added behind
launch arguments. Drivers gracefully no-op when their hardware is missing.
"""

import os
import sys

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _max_sku import detect_sku  # noqa: E402
from _robot_type import adapter_for, detect_robot_type  # noqa: E402


def _include(pkg: str, launch_file: str, *, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare(pkg), "launch", launch_file])
        ),
        condition=condition,
    )


def generate_launch_description() -> LaunchDescription:
    detected = detect_robot_type(os.environ.get("ROBOT_TYPE_OVERRIDE"))
    adapter_pkg, adapter_launch = adapter_for(detected)
    sku_file = detect_sku()

    enable_lidar = LaunchConfiguration("enable_lidar")
    enable_industrial_imu = LaunchConfiguration("enable_industrial_imu")
    enable_thermal = LaunchConfiguration("enable_thermal")
    enable_mmwave = LaunchConfiguration("enable_mmwave")
    enable_5g = LaunchConfiguration("enable_5g")
    enable_edge_status = LaunchConfiguration("enable_edge_status")
    edge_hardware_profile = LaunchConfiguration("edge_hardware_profile")
    edge_skill_descriptor = LaunchConfiguration("edge_skill_descriptor")
    edge_runtime_state = LaunchConfiguration("edge_runtime_state")
    edge_status_allowed_origin = LaunchConfiguration("edge_status_allowed_origin")

    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_type", default_value=detected),
            DeclareLaunchArgument("enable_lidar", default_value="false"),
            DeclareLaunchArgument("enable_industrial_imu", default_value="false"),
            DeclareLaunchArgument("enable_thermal", default_value="false"),
            DeclareLaunchArgument("enable_mmwave", default_value="false"),
            DeclareLaunchArgument("enable_5g", default_value="false"),
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
                msg=[
                    f"[openbrain_bringup] max box, robot_type={detected}, "
                    f"adapter={adapter_pkg}, sku={sku_file}"
                ]
            ),
            # Mini stack as the foundation.
            _include("openbrain_drivers_realsense", "dual_d435i.launch.py"),
            _include("openbrain_slam", "rtabmap.launch.py"),
            _include("openbrain_nav", "nav2.launch.py"),
            _include("openbrain_teleop", "teleop.launch.py"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("openbrain_connector"),
                            "launch",
                            "connector.launch.py",
                        ]
                    )
                ),
                condition=IfCondition(enable_edge_status),
                launch_arguments={
                    "hardware_profile": edge_hardware_profile,
                    "skill_descriptor": edge_skill_descriptor,
                    "runtime_state": edge_runtime_state,
                    "allowed_origin": edge_status_allowed_origin,
                }.items(),
            ),
            # Industrial payload drivers (Phase 3 stubs today, real launches when
            # the wrappers land — they all currently no-op cleanly so this list is
            # safe to leave wired up).
            _include(
                "openbrain_drivers_livox",
                "livox_mid360.launch.py",
                condition=IfCondition(enable_lidar),
            ),
            _include(
                "openbrain_drivers_xsens",
                "xsens_mti.launch.py",
                condition=IfCondition(enable_industrial_imu),
            ),
            _include(
                "openbrain_drivers_flir_boson",
                "flir_boson.launch.py",
                condition=IfCondition(enable_thermal),
            ),
            _include(
                "openbrain_drivers_ti_mmwave",
                "iwr6843.launch.py",
                condition=IfCondition(enable_mmwave),
            ),
            _include(
                "openbrain_drivers_quectel_5g",
                "quectel_rm520n.launch.py",
                condition=IfCondition(enable_5g),
            ),
            _include(adapter_pkg, adapter_launch),
        ]
    )
