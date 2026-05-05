#!/usr/bin/env python3
"""Drive a 30-second circle at 0.3 m/s + 0.5 rad/s.

Useful as a SLAM smoke test: the robot trajectory is closed-loop and
returns to the start, so RTAB-Map should detect a loop closure.

Publishes to /safety/cmd_vel/dashboard (priority 80) — the safety mux
arbitrates. If the mux is offline the robot stays still.
"""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CircleDriver(Node):
    def __init__(self, *, linear: float, angular: float, duration_s: float) -> None:
        super().__init__("openbrain_example_circle_driver")
        self._pub = self.create_publisher(Twist, "/safety/cmd_vel/dashboard", 10)
        self._linear = linear
        self._angular = angular
        self._deadline = self.get_clock().now().nanoseconds / 1e9 + duration_s
        self.create_timer(0.05, self._tick)

    def _tick(self) -> None:
        now = self.get_clock().now().nanoseconds / 1e9
        twist = Twist()
        if now < self._deadline:
            twist.linear.x = self._linear
            twist.angular.z = self._angular
        # else publish zero — let the safety mux time us out
        self._pub.publish(twist)


def main() -> None:
    rclpy.init()
    node = CircleDriver(linear=0.3, angular=0.5, duration_s=30.0)
    try:
        # Spin a hair longer than the duration so the final zero lands.
        end = time.time() + 32.0
        while rclpy.ok() and time.time() < end:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
