"""Pure-Python tests for the fleet aggregator."""

from __future__ import annotations

import json

from openbrain_demos_fleet_control.aggregator import Aggregator


class _Clock:
    """Deterministic clock for time-sensitive assertions."""

    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _aggr(timeout: float = 5.0):
    clk = _Clock()
    return Aggregator(heartbeat_timeout_s=timeout, clock=clk), clk


def test_initial_snapshot_is_empty():
    a, _ = _aggr()
    snap = a.snapshot()
    assert snap.total_count == 0
    assert snap.online_count == 0
    assert snap.robots == []


def test_health_update_creates_robot_marked_online():
    a, _ = _aggr()
    a.update_health(
        "r01",
        cpu_per_core=[10.0, 20.0, 30.0],
        cpu_temp_c=55.0,
        gpu_percent=70.0,
        gpu_temp_c=60.0,
        ram_used_bytes=2_000_000_000,
        ram_total_bytes=8_000_000_000,
    )
    snap = a.snapshot()
    assert snap.total_count == 1
    assert snap.online_count == 1
    r = snap.robots[0]
    assert r.robot_id == "r01"
    assert r.cpu_percent_avg == 20.0  # mean
    assert r.online


def test_robot_goes_offline_after_timeout():
    a, clk = _aggr(timeout=5.0)
    a.update_health(
        "r01",
        cpu_per_core=[10.0],
        cpu_temp_c=55.0,
        gpu_percent=70.0,
        gpu_temp_c=60.0,
        ram_used_bytes=1,
        ram_total_bytes=2,
    )
    clk.advance(6.0)
    a.tick()
    snap = a.snapshot()
    assert snap.total_count == 1
    assert snap.online_count == 0
    assert not snap.robots[0].online


def test_robot_returns_to_online_when_heartbeat_resumes():
    a, clk = _aggr(timeout=5.0)
    a.update_health(
        "r01",
        cpu_per_core=[10.0],
        cpu_temp_c=55.0,
        gpu_percent=70.0,
        gpu_temp_c=60.0,
        ram_used_bytes=1,
        ram_total_bytes=2,
    )
    clk.advance(6.0)
    a.tick()
    assert not a.snapshot().robots[0].online
    a.update_health(
        "r01",
        cpu_per_core=[20.0],
        cpu_temp_c=55.0,
        gpu_percent=70.0,
        gpu_temp_c=60.0,
        ram_used_bytes=1,
        ram_total_bytes=2,
    )
    a.tick()
    assert a.snapshot().robots[0].online


def test_mission_update_records_state_and_progress():
    a, _ = _aggr()
    a.update_mission(
        "r02", state=2, mission_id="patrol-1", current_waypoint_index=3, total_waypoints=10
    )
    snap = a.snapshot()
    r = snap.robots[0]
    assert r.mission_state == 2
    assert r.mission_id == "patrol-1"
    assert r.mission_progress == (3, 10)


def test_snapshot_robots_sorted_by_id():
    a, _ = _aggr()
    for rid in ("r03", "r01", "r02"):
        a.update_health(
            rid,
            cpu_per_core=[10.0],
            cpu_temp_c=55.0,
            gpu_percent=70.0,
            gpu_temp_c=60.0,
            ram_used_bytes=1,
            ram_total_bytes=2,
        )
    ids = [r.robot_id for r in a.snapshot().robots]
    assert ids == ["r01", "r02", "r03"]


def test_to_json_replaces_nan_with_null():
    a, _ = _aggr()
    a.update_health(
        "r01",
        cpu_per_core=[10.0],
        cpu_temp_c=float("nan"),
        gpu_percent=0.0,
        gpu_temp_c=float("nan"),
        ram_used_bytes=1,
        ram_total_bytes=2,
    )
    payload = json.loads(a.snapshot().to_json())
    assert payload["robots"][0]["cpu_temp_c"] is None
    assert payload["robots"][0]["gpu_temp_c"] is None


def test_empty_cpu_per_core_handled():
    """Missing telemetry shouldn't divide-by-zero the CPU average."""
    a, _ = _aggr()
    a.update_health(
        "r01",
        cpu_per_core=[],
        cpu_temp_c=50.0,
        gpu_percent=0.0,
        gpu_temp_c=50.0,
        ram_used_bytes=1,
        ram_total_bytes=2,
    )
    assert a.snapshot().robots[0].cpu_percent_avg == 0.0
