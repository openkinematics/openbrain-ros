"""ROS node that aggregates per-robot health + mission status.

Each robot in the fleet publishes ``/system/health`` (and optionally
``/missions/status``) under its own namespace on a shared DDS domain —
typically ``/r01/...``, ``/r02/...``, ... The fleet node reads
``robots:`` from its YAML config and subscribes to each namespace.

Outputs (consumed by the dashboard's Fleet page):

  /fleet/snapshot           std_msgs/String   JSON of the full fleet
                                              state, latched, republished
                                              every 1 s.
  /fleet/online_count       std_msgs/UInt32   convenience scalar
  /fleet/total_count        std_msgs/UInt32   convenience scalar

Dispatch (Phase-2): /fleet/dispatch will broadcast a LoadMission to the
selected subset. The shape will follow openbrain_msgs/LoadMission with
an extra ``selector`` field. Not implemented in v0.1 — the dashboard
currently fans out a per-robot LoadMission call instead.
"""

from __future__ import annotations

import sys

import rclpy
from openbrain_msgs.msg import MissionStatus, SystemHealth
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String, UInt32

from openbrain_demos_fleet_control.aggregator import Aggregator


class FleetNode(Node):
    PUBLISH_PERIOD_SEC = 1.0

    def __init__(self) -> None:
        super().__init__("openbrain_fleet")

        # robots: list of namespaces (e.g. ["r01", "r02", "r03"]).
        # Empty default = subscribe to bare /system/health (single-robot mode).
        self.declare_parameter("robots", [""])
        self.declare_parameter("heartbeat_timeout_s", 5.0)

        timeout = self.get_parameter("heartbeat_timeout_s").get_parameter_value().double_value
        self._aggr = Aggregator(heartbeat_timeout_s=timeout)

        latched = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._snapshot_pub = self.create_publisher(String, "/fleet/snapshot", latched)
        self._online_pub = self.create_publisher(UInt32, "/fleet/online_count", 10)
        self._total_pub = self.create_publisher(UInt32, "/fleet/total_count", 10)

        robots = self.get_parameter("robots").get_parameter_value().string_array_value or [""]
        for ns in robots:
            self._wire_robot(ns)
        self.get_logger().info(f"fleet_node ready — tracking {len(robots)} robot(s)")

        self.create_timer(self.PUBLISH_PERIOD_SEC, self._tick)

    # ---- wiring ------------------------------------------------------

    def _wire_robot(self, ns: str) -> None:
        robot_id = ns.strip("/") or "default"
        prefix = f"/{ns.strip('/')}" if ns.strip("/") else ""

        def on_health(msg: SystemHealth, _id: str = robot_id) -> None:
            self._aggr.update_health(
                _id,
                cpu_per_core=list(msg.cpu_per_core),
                cpu_temp_c=msg.cpu_temp_c,
                gpu_percent=msg.gpu_percent,
                gpu_temp_c=msg.gpu_temp_c,
                ram_used_bytes=msg.ram_used_bytes,
                ram_total_bytes=msg.ram_total_bytes,
            )

        def on_mission(msg: MissionStatus, _id: str = robot_id) -> None:
            self._aggr.update_mission(
                _id,
                state=msg.state,
                mission_id=msg.mission_id,
                current_waypoint_index=msg.current_waypoint_index,
                total_waypoints=msg.total_waypoints,
            )

        self.create_subscription(SystemHealth, f"{prefix}/system/health", on_health, 10)
        self.create_subscription(MissionStatus, f"{prefix}/missions/status", on_mission, 10)
        self.get_logger().info(f"  wired {robot_id} on {prefix}/system/health + /missions/status")

    # ---- tick + publish ---------------------------------------------

    def _tick(self) -> None:
        self._aggr.tick()
        snap = self._aggr.snapshot()
        self._snapshot_pub.publish(String(data=snap.to_json()))
        self._online_pub.publish(UInt32(data=snap.online_count))
        self._total_pub.publish(UInt32(data=snap.total_count))


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = FleetNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
