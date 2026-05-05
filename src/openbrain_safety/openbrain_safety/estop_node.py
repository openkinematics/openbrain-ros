"""Software emergency-stop node.

Latches a Bool on ``/safety/estop``. Two services flip it:

  /safety/estop_engage  -> std_srvs/Trigger
  /safety/estop_release -> std_srvs/Trigger

The dashboard's red e-stop button calls /safety/estop_engage; manual
reset (release) is intentionally a separate gesture so an e-stop cannot be
silently undone.

Latched value is republished at 5 Hz so late subscribers see it.
"""

from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import Bool
from std_srvs.srv import Trigger


class EstopNode(Node):
    REPUBLISH_HZ = 5.0

    def __init__(self) -> None:
        super().__init__("estop_node")
        latched = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._pub = self.create_publisher(Bool, "/safety/estop", latched)
        self._engaged = False
        self._publish()
        self.create_service(Trigger, "/safety/estop_engage", self._engage)
        self.create_service(Trigger, "/safety/estop_release", self._release)
        self.create_timer(1.0 / self.REPUBLISH_HZ, self._publish)
        self.get_logger().info("estop_node ready (clear)")

    def _engage(self, _req, resp: Trigger.Response) -> Trigger.Response:
        if not self._engaged:
            self.get_logger().warn("E-STOP ENGAGED via /safety/estop_engage")
        self._engaged = True
        self._publish()
        resp.success = True
        resp.message = "estop engaged"
        return resp

    def _release(self, _req, resp: Trigger.Response) -> Trigger.Response:
        if self._engaged:
            self.get_logger().info("E-stop released via /safety/estop_release")
        self._engaged = False
        self._publish()
        resp.success = True
        resp.message = "estop released"
        return resp

    def _publish(self) -> None:
        self._pub.publish(Bool(data=self._engaged))


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = EstopNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
