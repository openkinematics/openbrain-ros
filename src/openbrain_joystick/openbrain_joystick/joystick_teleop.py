"""Translate ``sensor_msgs/Joy`` into ``geometry_msgs/Twist``.

Output topic: ``/safety/cmd_vel/joystick`` (consumed by ``twist_mux``).

The mapping is parameter-driven so we can support PS5, Xbox, and a generic
xpad layout from one node. Defaults to the Xbox layout (the most common
ROS-side mapping after ``joy_node``).

Hold the dead-man button for cmd_vel to flow. Releasing it stops publishing,
which lets ``twist_mux``'s timeout drop us to zero within ~0.5 s.

A dedicated **turbo** axis multiplies the linear/angular gain. A dedicated
**estop_button** call hits ``/safety/estop_engage`` so the operator can
emergency-stop without leaving the gamepad.
"""

from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_srvs.srv import Trigger


class JoystickTeleop(Node):
    def __init__(self) -> None:
        super().__init__("joystick_teleop")

        # Axis indices (Xbox / generic ROS joy_node defaults)
        self.declare_parameter("axis_linear_x", 1)  # left stick Y
        self.declare_parameter("axis_linear_y", 0)  # left stick X
        self.declare_parameter("axis_angular_z", 3)  # right stick X
        self.declare_parameter("scale_linear", 1.0)
        self.declare_parameter("scale_angular", 1.5)

        # Buttons
        self.declare_parameter("deadman_button", 4)  # LB / L1
        self.declare_parameter("turbo_button", 5)  # RB / R1 (×2)
        self.declare_parameter("estop_button", 1)  # B / Circle
        self.declare_parameter("estop_release_button", 3)  # Y / Triangle
        self.declare_parameter("turbo_factor", 2.0)

        self._cmd_pub = self.create_publisher(Twist, "/safety/cmd_vel/joystick", 10)
        self._estop_engage = self.create_client(Trigger, "/safety/estop_engage")
        self._estop_release = self.create_client(Trigger, "/safety/estop_release")

        self.create_subscription(Joy, "/joy", self._on_joy, 10)
        self._last_estop_pressed = False
        self._last_release_pressed = False
        self.get_logger().info("joystick_teleop ready (output /safety/cmd_vel/joystick)")

    def _p(self, name: str):
        return self.get_parameter(name).get_parameter_value()

    def _on_joy(self, msg: Joy) -> None:
        ax_lx = self._p("axis_linear_x").integer_value
        ax_ly = self._p("axis_linear_y").integer_value
        ax_az = self._p("axis_angular_z").integer_value
        deadman = self._p("deadman_button").integer_value
        turbo = self._p("turbo_button").integer_value
        estop = self._p("estop_button").integer_value
        release = self._p("estop_release_button").integer_value

        # E-stop edges (only fire on press, not while held).
        estop_pressed = _btn(msg, estop)
        if estop_pressed and not self._last_estop_pressed:
            self._call(self._estop_engage)
        self._last_estop_pressed = estop_pressed

        release_pressed = _btn(msg, release)
        if release_pressed and not self._last_release_pressed:
            self._call(self._estop_release)
        self._last_release_pressed = release_pressed

        # Velocity is gated by the dead-man.
        if not _btn(msg, deadman):
            return

        scale_lin = self._p("scale_linear").double_value
        scale_ang = self._p("scale_angular").double_value
        if _btn(msg, turbo):
            factor = self._p("turbo_factor").double_value
            scale_lin *= factor
            scale_ang *= factor

        twist = Twist()
        twist.linear.x = scale_lin * _axis(msg, ax_lx)
        twist.linear.y = scale_lin * _axis(msg, ax_ly)
        twist.angular.z = scale_ang * _axis(msg, ax_az)
        self._cmd_pub.publish(twist)

    def _call(self, client) -> None:
        if not client.service_is_ready():
            self.get_logger().warn(f"estop service {client.srv_name!r} not ready; skipping")
            return
        client.call_async(Trigger.Request())


def _axis(msg: Joy, idx: int) -> float:
    return float(msg.axes[idx]) if 0 <= idx < len(msg.axes) else 0.0


def _btn(msg: Joy, idx: int) -> bool:
    return bool(msg.buttons[idx]) if 0 <= idx < len(msg.buttons) else False


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = JoystickTeleop()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
