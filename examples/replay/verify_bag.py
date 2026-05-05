#!/usr/bin/env python3
"""Replay a rosbag2 and assert that the contract topics show up.

Spawns ``ros2 bag play`` and counts incoming messages on /system/health
and /cmd_vel for 30 seconds. Exits non-zero if either rate drops below
threshold — useful in CI as a regression guard.

Usage:
    python3 examples/replay/verify_bag.py /recordings/<bag-name>
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

from openbrain_msgs.msg import SystemHealth


class Counter(Node):
    def __init__(self) -> None:
        super().__init__("openbrain_example_bag_verifier")
        self.health_count = 0
        self.cmd_vel_count = 0
        self.create_subscription(SystemHealth, "/system/health", self._h, 10)
        self.create_subscription(Twist, "/cmd_vel", self._c, 10)

    def _h(self, _msg: SystemHealth) -> None:
        self.health_count += 1

    def _c(self, _msg: Twist) -> None:
        self.cmd_vel_count += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag")
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--min-health-hz", type=float, default=0.5)
    parser.add_argument("--min-cmd-vel-hz", type=float, default=1.0)
    args = parser.parse_args()

    rclpy.init()
    counter = Counter()

    proc = subprocess.Popen(
        ["ros2", "bag", "play", args.bag, "--clock", "200"],
        preexec_fn=os.setsid,
    )

    deadline = time.time() + args.duration
    try:
        while rclpy.ok() and time.time() < deadline:
            rclpy.spin_once(counter, timeout_sec=0.1)
    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        proc.wait(timeout=5)
        counter.destroy_node()
        rclpy.shutdown()

    health_hz = counter.health_count / args.duration
    cmd_vel_hz = counter.cmd_vel_count / args.duration
    print(f"/system/health  rx={counter.health_count}  ({health_hz:.2f} Hz)")
    print(f"/cmd_vel        rx={counter.cmd_vel_count}  ({cmd_vel_hz:.2f} Hz)")

    rc = 0
    if health_hz < args.min_health_hz:
        print(f"FAIL: /system/health below {args.min_health_hz} Hz", file=sys.stderr)
        rc = 1
    if cmd_vel_hz < args.min_cmd_vel_hz:
        print(f"FAIL: /cmd_vel below {args.min_cmd_vel_hz} Hz", file=sys.stderr)
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
