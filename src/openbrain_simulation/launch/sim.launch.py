"""Bring up Gazebo + the sim robot + ros_gz bridge.

Pairs with `openbrain_bringup/mini.launch.py` (which contributes SLAM, Nav2,
teleop, the safety stack). End result: dashboard sees a virtual robot with
front-camera video and live map within ~30 seconds, no hardware required.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    pkg = FindPackageShare("openbrain_simulation")
    world = PathJoinSubstitution([pkg, "worlds", "openbrain_lab.sdf"])
    urdf = PathJoinSubstitution([pkg, "urdf", "sim_robot.urdf.xacro"])
    bridge_cfg = PathJoinSubstitution([pkg, "config", "sim_bridge.yaml"])

    use_sim_time = LaunchConfiguration("use_sim_time")

    # ros_gz_sim bringup is a separate launch shipped by ros_gz_sim itself.
    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("ros_gz_sim"),
                    "launch",
                    "gz_sim.launch.py",
                ]
            )
        ),
        launch_arguments={"gz_args": [world, " -r -v 3"]}.items(),
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            "openbrain_sim_robot",
            "-topic",
            "robot_description",
            "-x",
            "0",
            "-y",
            "0",
            "-z",
            "0.05",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[{"config_file": bridge_cfg, "use_sim_time": use_sim_time}],
    )

    robot_state = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "robot_description": ExecuteProcess(
                    cmd=["xacro", urdf],
                    output="screen",
                    shell=False,
                ),
            }
        ],
    )

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("openbrain_bringup"),
                    "launch",
                    "mini.launch.py",
                ]
            )
        ),
        launch_arguments={
            "front_serial": "",
            "back_serial": "",
            "robot_type": "GENERIC",
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            gz,
            spawn_robot,
            bridge,
            robot_state,
            bringup,
        ]
    )
