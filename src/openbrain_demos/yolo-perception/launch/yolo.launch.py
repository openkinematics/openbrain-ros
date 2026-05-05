"""Launch the YOLO detector against the front camera by default."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    cfg = PathJoinSubstitution(
        [
            FindPackageShare("openbrain_demos_yolo_perception"),
            "config",
            "default.yaml",
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("model_path", default_value="yolo11n.pt"),
            DeclareLaunchArgument("source", default_value="front"),
            DeclareLaunchArgument("score_threshold", default_value="0.25"),
            DeclareLaunchArgument("imgsz", default_value="640"),
            DeclareLaunchArgument("half", default_value="false"),
            DeclareLaunchArgument("publish_overlay", default_value="true"),
            DeclareLaunchArgument("device", default_value=""),
            Node(
                package="openbrain_demos_yolo_perception",
                executable="yolo_node",
                name="openbrain_yolo",
                output="screen",
                parameters=[
                    cfg,
                    {
                        "model_path": LaunchConfiguration("model_path"),
                        "source": LaunchConfiguration("source"),
                        "score_threshold": LaunchConfiguration("score_threshold"),
                        "imgsz": LaunchConfiguration("imgsz"),
                        "half": LaunchConfiguration("half"),
                        "publish_overlay": LaunchConfiguration("publish_overlay"),
                        "device": LaunchConfiguration("device"),
                    },
                ],
            ),
        ]
    )
