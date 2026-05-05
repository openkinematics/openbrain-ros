"""Twist multiplexer with priority arbitration + watchdog.

Subscribes to N input topics each tagged with a priority and a timeout.
Republishes the highest-priority input that has produced a fresh sample
within its timeout to ``/cmd_vel``. If no input is fresh, publishes a zero
velocity (so the robot stops, never coasts).

Honors a software e-stop latched on ``/safety/estop`` (Bool); while latched,
the output is unconditionally zero regardless of input.

Configured by YAML — see ``config/twist_mux.yaml`` for the canonical layout.
"""

from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool

from openbrain_safety.sources import _Source

ZERO = Twist()


class TwistMux(Node):
    PUBLISH_RATE_HZ = 50.0

    def __init__(self) -> None:
        super().__init__("twist_mux")

        # Parameters: each input is a triple (topic, priority, timeout_s).
        # Default mirrors the v1 contract: dashboard cmd_vel beats nav, nav
        # beats AI policies, joystick (when enabled) wins everything.
        self.declare_parameter("output_topic", "/cmd_vel")
        self.declare_parameter("inputs.joystick.topic", "/safety/cmd_vel/joystick")
        self.declare_parameter("inputs.joystick.priority", 100)
        self.declare_parameter("inputs.joystick.timeout_s", 0.5)
        self.declare_parameter("inputs.dashboard.topic", "/safety/cmd_vel/dashboard")
        self.declare_parameter("inputs.dashboard.priority", 80)
        self.declare_parameter("inputs.dashboard.timeout_s", 0.5)
        self.declare_parameter("inputs.nav.topic", "/safety/cmd_vel/nav")
        self.declare_parameter("inputs.nav.priority", 50)
        self.declare_parameter("inputs.nav.timeout_s", 1.0)
        self.declare_parameter("inputs.ai.topic", "/safety/cmd_vel/ai")
        self.declare_parameter("inputs.ai.priority", 30)
        self.declare_parameter("inputs.ai.timeout_s", 1.0)

        self._sources: list[_Source] = []
        for name in ("joystick", "dashboard", "nav", "ai"):
            topic = self.get_parameter(f"inputs.{name}.topic").get_parameter_value().string_value
            priority = (
                self.get_parameter(f"inputs.{name}.priority").get_parameter_value().integer_value
            )
            timeout = (
                self.get_parameter(f"inputs.{name}.timeout_s").get_parameter_value().double_value
            )
            src = _Source(name=name, topic=topic, priority=priority, timeout_s=timeout)
            self.create_subscription(Twist, topic, _make_cb(self, src), 10)
            self._sources.append(src)

        self._estop = False
        self.create_subscription(Bool, "/safety/estop", self._on_estop, 10)

        out_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        self._pub = self.create_publisher(Twist, out_topic, 10)

        self.create_timer(1.0 / self.PUBLISH_RATE_HZ, self._tick)
        self.get_logger().info(f"twist_mux ready — {len(self._sources)} inputs, output {out_topic}")

    def _on_estop(self, msg: Bool) -> None:
        if msg.data and not self._estop:
            self.get_logger().warn("e-stop LATCHED — publishing zero velocity")
        elif not msg.data and self._estop:
            self.get_logger().info("e-stop CLEARED")
        self._estop = bool(msg.data)

    def _tick(self) -> None:
        if self._estop:
            self._pub.publish(ZERO)
            return

        now = self.get_clock().now()
        winner: _Source | None = None
        for src in self._sources:
            if src.last_stamp is None or src.last_msg is None:
                continue
            age = (now - src.last_stamp).nanoseconds / 1e9
            if age > src.timeout_s:
                continue
            if winner is None or src.priority > winner.priority:
                winner = src

        if winner is None:
            # No fresh input: publish zero so the robot stops (don't coast).
            self._pub.publish(ZERO)
            return
        self._pub.publish(winner.last_msg)


def _make_cb(node: TwistMux, src: _Source):
    def cb(msg: Twist) -> None:
        src.last_msg = msg
        src.last_stamp = node.get_clock().now()

    return cb


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = TwistMux()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
