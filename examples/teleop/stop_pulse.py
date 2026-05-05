#!/usr/bin/env python3
"""Engage e-stop, sleep 3 s, release. Smoke test for the safety surface."""

from __future__ import annotations

import time

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


def _call(node: Node, service: str) -> None:
    cli = node.create_client(Trigger, service)
    if not cli.wait_for_service(timeout_sec=2.0):
        node.get_logger().error(f"{service} not advertised")
        return
    fut = cli.call_async(Trigger.Request())
    rclpy.spin_until_future_complete(node, fut, timeout_sec=2.0)
    resp = fut.result()
    node.get_logger().info(f"{service} -> success={resp.success!r} msg={resp.message!r}")


def main() -> None:
    rclpy.init()
    node = rclpy.create_node("openbrain_example_estop_pulse")
    try:
        _call(node, "/safety/estop_engage")
        time.sleep(3)
        _call(node, "/safety/estop_release")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
