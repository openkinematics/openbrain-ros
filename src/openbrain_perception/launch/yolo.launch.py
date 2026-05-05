"""YOLO detector launch — delegates to the real implementation in
``openbrain_demos_yolo_perception``.

The real inference loop, post-processing, overlay drawing, tests, and
parameter surface all live in
[`openbrain_demos/yolo-perception`](../../openbrain_demos/yolo-perception/)
so the demos catalog has a runnable entry. This launch is the
``openbrain_perception``-side entry point — same node, same outputs,
documented at the perception-package level.

If you want to wire a different detector (custom-trained YOLO, a
TensorRT engine, Isaac-ROS object_detection), replace this include
with your own launch composition.
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("openbrain_demos_yolo_perception"),
                            "launch",
                            "yolo.launch.py",
                        ]
                    )
                ),
            ),
        ]
    )
