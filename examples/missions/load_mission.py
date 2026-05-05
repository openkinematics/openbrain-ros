#!/usr/bin/env python3
"""Load + start a mission from a JSON file via rclpy.

Usage:
    python3 examples/missions/load_mission.py patrol.json [--loop]

The script loads waypoints from the JSON file, calls /missions/load,
then /missions/start, and prints /missions/status updates until the
mission terminates. Demonstrates the dashboard contract end-to-end.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

from openbrain_msgs.msg import MissionStatus, Waypoint
from openbrain_msgs.srv import LoadMission

TERMINAL = {
    MissionStatus.STATE_SUCCEEDED,
    MissionStatus.STATE_FAILED,
    MissionStatus.STATE_CANCELED,
}


class MissionDriver(Node):
    def __init__(self, waypoints: list[dict], loop: bool, mission_id: str) -> None:
        super().__init__("openbrain_example_mission_driver")
        self._load_cli = self.create_client(LoadMission, "/missions/load")
        self._start_cli = self.create_client(Trigger, "/missions/start")
        self._status_sub = self.create_subscription(
            MissionStatus, "/missions/status", self._on_status, 10
        )
        self._waypoints = waypoints
        self._loop = loop
        self._mission_id = mission_id
        self._terminated = False

    async def run(self) -> int:
        if not self._load_cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("/missions/load is not advertised — is the missions node up?")
            return 2
        if not self._start_cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("/missions/start is not advertised")
            return 2

        req = LoadMission.Request()
        req.mission_id = self._mission_id
        req.loop = self._loop
        for entry in self._waypoints:
            wp = Waypoint()
            wp.x = float(entry["x"])
            wp.y = float(entry["y"])
            wp.yaw = float(entry.get("yaw", 0.0))
            wp.label = str(entry.get("label", ""))
            wp.dwell_seconds = float(entry.get("dwell_seconds", 0.0))
            req.waypoints.append(wp)

        load = await self._load_cli.call_async(req)
        if not load.success:
            self.get_logger().error(f"load failed: {load.message}")
            return 2
        self.get_logger().info(f"loaded: {load.message}")

        start = await self._start_cli.call_async(Trigger.Request())
        if not start.success:
            self.get_logger().error(f"start failed: {start.message}")
            return 2
        self.get_logger().info("started — watching /missions/status")
        return 0

    def _on_status(self, msg: MissionStatus) -> None:
        self.get_logger().info(
            f"  state={msg.state} wp={msg.current_waypoint_index}/{msg.total_waypoints} "
            f"msg={msg.message!r}"
        )
        if msg.state in TERMINAL:
            self._terminated = True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="path to a mission JSON")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--mission-id", default="example-mission")
    args = parser.parse_args(argv)

    waypoints = json.loads(args.file.read_text())
    rclpy.init()
    driver = MissionDriver(waypoints, args.loop, args.mission_id)

    # Drive the async load/start, then spin until we see a terminal state.
    import asyncio

    rc = asyncio.get_event_loop().run_until_complete(driver.run())
    if rc != 0:
        driver.destroy_node()
        rclpy.shutdown()
        return rc

    while rclpy.ok() and not driver._terminated:
        rclpy.spin_once(driver, timeout_sec=0.5)

    driver.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
