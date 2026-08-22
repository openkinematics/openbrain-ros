"""RobotAdapter base class.

Vendor-specific adapters (Unitree Go2, Unitree G1, DirectDrive Tita, ...)
extend this class. The adapter is responsible for:

  * translating geometry_msgs/Twist on /cmd_vel into the vendor SDK's
    velocity command,
  * publishing nav_msgs/Odometry on /odom (if the vendor SDK exposes it),
  * publishing the robot's URDF on /robot_description (latched).

The base class wires up the standard subscriptions and applies the speed
profile cap requested via /teleop/set_speed_profile. Subclasses only need
to override `send_velocity` and (optionally) `read_odometry`.
"""

from __future__ import annotations

from dataclasses import dataclass

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from openbrain_msgs.srv import SetSpeedProfile
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String


@dataclass(frozen=True)
class SpeedProfile:
    name: str
    max_linear: float  # m/s
    max_angular: float  # rad/s


SPEED_PROFILES: dict[str, SpeedProfile] = {
    "beginner": SpeedProfile("beginner", max_linear=0.3, max_angular=0.5),
    "normal": SpeedProfile("normal", max_linear=1.0, max_angular=1.5),
    "insane": SpeedProfile("insane", max_linear=2.5, max_angular=3.0),
}

DEFAULT_PROFILE = "normal"


class RobotAdapter(Node):
    """Base class for robot adapters.

    Subclasses must override :meth:`send_velocity`. They may also override
    :meth:`read_odometry` to publish odometry at every tick.
    """

    def __init__(self, node_name: str, *, urdf: str | None = None) -> None:
        super().__init__(node_name)

        self._profile = SPEED_PROFILES[DEFAULT_PROFILE]

        self._cmd_sub = self.create_subscription(
            Twist, "/cmd_vel", self._on_cmd_vel, qos_profile=10
        )
        self._odom_pub = self.create_publisher(Odometry, "/odom", qos_profile=10)

        latched = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._urdf_pub = self.create_publisher(String, "/robot_description", latched)
        if urdf is not None:
            self._urdf_pub.publish(String(data=urdf))

        self._set_profile_srv = self.create_service(
            SetSpeedProfile, "/teleop/set_speed_profile", self._on_set_profile
        )

        self._odom_timer = self.create_timer(0.05, self._tick_odometry)
        self.get_logger().info(f"{node_name} ready (profile={self._profile.name})")

    # ---- velocity path -------------------------------------------------

    def _on_cmd_vel(self, msg: Twist) -> None:
        capped = Twist()
        capped.linear.x = _clamp(msg.linear.x, self._profile.max_linear)
        capped.linear.y = _clamp(msg.linear.y, self._profile.max_linear)
        capped.angular.z = _clamp(msg.angular.z, self._profile.max_angular)
        try:
            self.send_velocity(capped)
        except Exception as exc:  # pragma: no cover - defensive
            self.get_logger().error(f"send_velocity failed: {exc}")

    def send_velocity(self, twist: Twist) -> None:
        """Translate a (capped) Twist into a vendor SDK call.

        Subclasses must override.
        """
        raise NotImplementedError

    # ---- odometry path -------------------------------------------------

    def _tick_odometry(self) -> None:
        odom = self.read_odometry()
        if odom is not None:
            self._odom_pub.publish(odom)

    def read_odometry(self) -> Odometry | None:
        """Return the latest odometry sample, or None if unavailable.

        Subclasses may override. The default returns None (no odom published).
        """
        return None

    # ---- speed profile -------------------------------------------------

    def _on_set_profile(
        self,
        request: SetSpeedProfile.Request,
        response: SetSpeedProfile.Response,
    ) -> SetSpeedProfile.Response:
        profile = SPEED_PROFILES.get(request.profile)
        if profile is None:
            response.success = False
            response.message = (
                f"unknown profile {request.profile!r}; expected one of {sorted(SPEED_PROFILES)}"
            )
            return response
        self._profile = profile
        response.success = True
        response.message = f"speed profile set to {profile.name}"
        response.max_linear_velocity = profile.max_linear
        response.max_angular_velocity = profile.max_angular
        self.get_logger().info(f"speed profile -> {profile.name}")
        return response


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))
