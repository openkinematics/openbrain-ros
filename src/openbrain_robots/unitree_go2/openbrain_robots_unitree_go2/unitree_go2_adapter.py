"""Unitree Go2 / Go2-W adapter.

Translates /cmd_vel into Unitree's high-level locomotion API and forwards
robot odometry onto /odom. The Unitree SDK ships as a closed-source binary
that the user installs out-of-band; we import it lazily so the package still
builds and lints on a developer laptop without it.

Channels we expose to the SDK:

* ``Move`` (high-level): vx, vy, omega in m/s and rad/s, identical to ROS Twist
  semantics, so the translation is a direct copy.
* ``HighState`` -> ``/odom``: the SDK publishes filtered odometry from foot-IMU
  fusion at ~500 Hz; we downsample to 20 Hz to match the rest of the stack.

The adapter declares two parameters:

* ``network_interface`` (string, default ``"eth0"``) — interface that talks to
  the dog over Ethernet (CycloneDDS xml is templated on this).
* ``urdf_path`` (string, default ``""``) — optional URDF to publish on
  /robot_description; falls back to env var ``OPENBRAIN_URDF_PATH``.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import rclpy
from geometry_msgs.msg import Quaternion, Twist
from nav_msgs.msg import Odometry
from openbrain_robots_generic.robot_adapter import RobotAdapter


class UnitreeGo2Adapter(RobotAdapter):
    """Adapter for Unitree Go2 / Go2-W.

    The Unitree SDK is loaded lazily so we can lint and unit-test without it.
    """

    def __init__(self) -> None:
        urdf = _load_urdf(os.environ.get("OPENBRAIN_URDF_PATH"))
        super().__init__("unitree_go2_adapter", urdf=urdf)

        self.declare_parameter("network_interface", "eth0")
        self.declare_parameter("urdf_path", "")

        self._sdk = self._try_load_sdk()
        if self._sdk is None:
            self.get_logger().warn(
                "unitree_sdk2py not importable — running in dry-run mode. "
                "Install the SDK and set CYCLONEDDS_URI on the robot to enable."
            )

    def send_velocity(self, twist: Twist) -> None:
        if self._sdk is None:
            return
        # Unitree's high-level Move expects (vx, vy, omega).
        self._sdk.publish_move(
            float(twist.linear.x),
            float(twist.linear.y),
            float(twist.angular.z),
        )

    def read_odometry(self) -> Odometry | None:
        if self._sdk is None:
            return None
        sample = self._sdk.latest_high_state()
        if sample is None:
            return None
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.x = float(sample.position[0])
        odom.pose.pose.position.y = float(sample.position[1])
        odom.pose.pose.position.z = float(sample.position[2])
        odom.pose.pose.orientation = _yaw_to_quat(float(sample.yaw))
        odom.twist.twist.linear.x = float(sample.velocity[0])
        odom.twist.twist.linear.y = float(sample.velocity[1])
        odom.twist.twist.angular.z = float(sample.yaw_rate)
        return odom

    def _try_load_sdk(self):  # pragma: no cover - SDK not available in CI
        try:
            from unitree_sdk2py.go2 import sport as _sport  # type: ignore
        except ImportError:
            return None

        iface = self.get_parameter("network_interface").get_parameter_value().string_value
        return _Go2SdkBridge(iface, _sport)


def _yaw_to_quat(yaw: float) -> Quaternion:
    half = 0.5 * yaw
    q = Quaternion()
    q.z = math.sin(half)
    q.w = math.cos(half)
    return q


def _load_urdf(path_str: str | None) -> str | None:
    if not path_str:
        return None
    try:
        return Path(path_str).read_text()
    except OSError:
        return None


class _Go2SdkBridge:  # pragma: no cover - SDK-only path
    """Thin shim over Unitree's Python SDK so the adapter logic stays testable."""

    def __init__(self, iface: str, sport_module) -> None:
        self._client = sport_module.SportClient()
        self._client.SetNetworkInterface(iface)
        self._client.Init()

    def publish_move(self, vx: float, vy: float, omega: float) -> None:
        self._client.Move(vx, vy, omega)

    def latest_high_state(self):
        return self._client.GetHighState() if hasattr(self._client, "GetHighState") else None


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = UnitreeGo2Adapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
