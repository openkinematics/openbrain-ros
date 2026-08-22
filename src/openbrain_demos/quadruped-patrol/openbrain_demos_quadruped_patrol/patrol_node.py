"""Patrol orchestrator.

Loads a waypoint loop from JSON, calls ``/missions/load`` + ``/missions/start``,
then watches ``/battery/state`` and ``/missions/status``. When the battery
drops below ``low_threshold``, calls ``/missions/stop`` and dispatches a
single-waypoint return-to-charger mission. When the battery climbs back
above ``resume_threshold``, resumes the original patrol loop.

The patrol loop and charger pose live in the same JSON file so an
operator can edit one place. See ``config/example_loop.json`` for the
expected schema.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import rclpy
from openbrain_msgs.msg import MissionStatus, Waypoint
from openbrain_msgs.srv import LoadMission
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_srvs.srv import Trigger

from openbrain_demos_quadruped_patrol.policy import (
    BatteryDecision,
    PatrolPolicy,
    decide,
)


class PatrolNode(Node):
    POLL_PERIOD_SEC = 1.0

    def __init__(self) -> None:
        super().__init__("openbrain_quadruped_patrol")

        self.declare_parameter("loop_file", "")
        self.declare_parameter("low_threshold_pct", 25.0)
        self.declare_parameter("resume_threshold_pct", 75.0)
        self.declare_parameter("critical_threshold_pct", 10.0)

        self._policy = PatrolPolicy(
            low_threshold=self._p_float("low_threshold_pct"),
            resume_threshold=self._p_float("resume_threshold_pct"),
            critical_threshold=self._p_float("critical_threshold_pct"),
        )

        self._loop_waypoints: list[dict] = []
        self._charger_waypoint: dict | None = None
        self._load_loop_file()

        self._battery_pct: float = 100.0
        self._on_charger: bool = False
        self._mission_state: int = MissionStatus.STATE_IDLE
        self._patrolling = False  # we initiated the active mission

        # Service clients.
        self._load_cli = self.create_client(LoadMission, "/missions/load")
        self._start_cli = self.create_client(Trigger, "/missions/start")
        self._stop_cli = self.create_client(Trigger, "/missions/stop")

        # Subscriptions.
        self.create_subscription(BatteryState, "/battery/state", self._on_battery, 10)
        self.create_subscription(MissionStatus, "/missions/status", self._on_mission, 10)

        self.create_timer(self.POLL_PERIOD_SEC, self._tick)
        self.get_logger().info(
            f"patrol_node ready — {len(self._loop_waypoints)} waypoint(s), "
            f"low={self._policy.low_threshold}% resume={self._policy.resume_threshold}%"
        )

    # ---- subs --------------------------------------------------------

    def _on_battery(self, msg: BatteryState) -> None:
        # `percentage` is in [0.0, 1.0] per REP 134, but real driver code
        # often emits 0..100. Accept either.
        raw = float(msg.percentage)
        self._battery_pct = raw * 100.0 if raw <= 1.0 else raw
        self._on_charger = bool(
            getattr(msg, "power_supply_status", 0) == BatteryState.POWER_SUPPLY_STATUS_CHARGING
        )

    def _on_mission(self, msg: MissionStatus) -> None:
        self._mission_state = int(msg.state)

    # ---- main loop ---------------------------------------------------

    def _tick(self) -> None:
        decision = decide(
            battery_pct=self._battery_pct,
            on_charger=self._on_charger,
            currently_patrolling=self._patrolling,
            policy=self._policy,
        )

        if decision is BatteryDecision.KEEP_PATROLLING:
            if not self._patrolling and self._loop_waypoints:
                self._dispatch(self._loop_waypoints, mission_id="patrol", loop=True)
                self._patrolling = True
            return

        if decision is BatteryDecision.GO_TO_CHARGER:
            if self._charger_waypoint is None:
                self.get_logger().warn("battery low but no charger waypoint configured — stopping")
                self._fire(self._stop_cli)
                self._patrolling = False
                return
            self.get_logger().warn(f"battery {self._battery_pct:.1f}% — returning to charger")
            self._fire(self._stop_cli)
            self._dispatch([self._charger_waypoint], mission_id="return-to-charger", loop=False)
            self._patrolling = False
            return

        if decision is BatteryDecision.STAY_AT_CHARGER:
            return  # no-op

        if decision is BatteryDecision.RESUME_PATROL:
            self.get_logger().info(f"battery {self._battery_pct:.1f}% — resuming patrol")
            if self._loop_waypoints:
                self._dispatch(self._loop_waypoints, mission_id="patrol", loop=True)
                self._patrolling = True

    # ---- helpers -----------------------------------------------------

    def _load_loop_file(self) -> None:
        path_str = self._p_str("loop_file").strip()
        if not path_str:
            self.get_logger().warn("no loop_file parameter set; patrol idle until configured")
            return
        try:
            payload = json.loads(Path(path_str).read_text())
        except OSError as exc:
            self.get_logger().error(f"can't read loop_file {path_str}: {exc}")
            return
        except json.JSONDecodeError as exc:
            self.get_logger().error(f"loop_file is not valid JSON: {exc}")
            return
        self._loop_waypoints = list(payload.get("loop", []))
        self._charger_waypoint = payload.get("charger")
        self.get_logger().info(
            f"loaded loop with {len(self._loop_waypoints)} waypoint(s) "
            f"+ charger={'yes' if self._charger_waypoint else 'no'} from {path_str}"
        )

    def _dispatch(self, wps: list[dict], *, mission_id: str, loop: bool) -> None:
        if not self._load_cli.wait_for_service(timeout_sec=2.0):
            self.get_logger().error("/missions/load not available; missions node down?")
            return
        req = LoadMission.Request(mission_id=mission_id, loop=loop)
        for entry in wps:
            wp = Waypoint()
            wp.x = float(entry["x"])
            wp.y = float(entry["y"])
            wp.yaw = float(entry.get("yaw", 0.0))
            wp.label = str(entry.get("label", ""))
            wp.dwell_seconds = float(entry.get("dwell_seconds", 0.0))
            req.waypoints.append(wp)
        self._load_cli.call_async(req)
        # Fire-and-forget start (the missions node is ours; we trust it).
        self.create_timer(0.5, self._fire_start_once)

    def _fire_start_once(self) -> None:
        if not self._start_cli.wait_for_service(timeout_sec=0.5):
            return
        self._start_cli.call_async(Trigger.Request())
        # Self-cancel: this is a one-shot.
        for t in self.timers:
            if t.callback is self._fire_start_once:
                t.cancel()

    def _fire(self, cli) -> None:
        if not cli.wait_for_service(timeout_sec=0.5):
            return
        cli.call_async(Trigger.Request())

    # ---- param helpers -----------------------------------------------

    def _p_str(self, name: str) -> str:
        return self.get_parameter(name).get_parameter_value().string_value

    def _p_float(self, name: str) -> float:
        return self.get_parameter(name).get_parameter_value().double_value


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
