"""Pure-Python fleet-state aggregator. Tested without rclpy.

Each robot in the fleet publishes its `/system/health` and (optionally)
`/missions/status` under a unique namespace — e.g. ``/r01/system/health``
on a shared DDS domain. The aggregator collects the latest snapshot per
robot, marks robots offline if their stamp is older than a heartbeat
threshold, and exposes a single :class:`FleetSnapshot` that the dashboard
renders.

This module owns only the data structures + freshness logic. The ROS
glue lives in :mod:`fleet_node`.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field


@dataclass
class RobotSnapshot:
    robot_id: str
    last_seen_unix: float
    online: bool
    cpu_percent_avg: float = 0.0  # mean across cpu_per_core, 0..100
    cpu_temp_c: float = float("nan")
    gpu_percent: float = 0.0
    gpu_temp_c: float = float("nan")
    ram_used_bytes: int = 0
    ram_total_bytes: int = 0
    mission_state: int = 0  # MissionStatus.STATE_IDLE
    mission_id: str = ""
    mission_progress: tuple[int, int] = (0, 0)  # (current_index, total)


@dataclass
class FleetSnapshot:
    generated_unix: float
    robots: list[RobotSnapshot] = field(default_factory=list)

    @property
    def online_count(self) -> int:
        return sum(1 for r in self.robots if r.online)

    @property
    def total_count(self) -> int:
        return len(self.robots)

    def to_json(self) -> str:
        import json

        def _scrub(d: dict) -> dict:
            # JSON doesn't tolerate NaN; coerce to null.
            for k, v in list(d.items()):
                if isinstance(v, float) and (v != v):  # NaN
                    d[k] = None
            return d

        return json.dumps(
            {
                "generated_unix": self.generated_unix,
                "online_count": self.online_count,
                "total_count": self.total_count,
                "robots": [_scrub(asdict(r)) for r in self.robots],
            }
        )


class Aggregator:
    """Holds the latest snapshot per robot, with heartbeat-based offline marking."""

    def __init__(self, *, heartbeat_timeout_s: float = 5.0, clock=time.time) -> None:
        self._timeout_s = heartbeat_timeout_s
        self._clock = clock
        self._robots: dict[str, RobotSnapshot] = {}

    def update_health(
        self,
        robot_id: str,
        *,
        cpu_per_core,
        cpu_temp_c,
        gpu_percent,
        gpu_temp_c,
        ram_used_bytes,
        ram_total_bytes,
    ) -> None:
        now = self._clock()
        snap = self._robots.get(robot_id) or RobotSnapshot(
            robot_id=robot_id,
            last_seen_unix=now,
            online=True,
        )
        cpu_avg = sum(float(c) for c in cpu_per_core) / len(cpu_per_core) if cpu_per_core else 0.0
        snap.last_seen_unix = now
        snap.online = True
        snap.cpu_percent_avg = cpu_avg
        snap.cpu_temp_c = float(cpu_temp_c)
        snap.gpu_percent = float(gpu_percent)
        snap.gpu_temp_c = float(gpu_temp_c)
        snap.ram_used_bytes = int(ram_used_bytes)
        snap.ram_total_bytes = int(ram_total_bytes)
        self._robots[robot_id] = snap

    def update_mission(
        self,
        robot_id: str,
        *,
        state: int,
        mission_id: str,
        current_waypoint_index: int,
        total_waypoints: int,
    ) -> None:
        now = self._clock()
        snap = self._robots.get(robot_id) or RobotSnapshot(
            robot_id=robot_id,
            last_seen_unix=now,
            online=True,
        )
        snap.last_seen_unix = now
        snap.online = True
        snap.mission_state = int(state)
        snap.mission_id = mission_id
        snap.mission_progress = (int(current_waypoint_index), int(total_waypoints))
        self._robots[robot_id] = snap

    def tick(self) -> None:
        """Mark stale robots offline. Call from a periodic timer."""
        now = self._clock()
        for snap in self._robots.values():
            snap.online = (now - snap.last_seen_unix) <= self._timeout_s

    def snapshot(self) -> FleetSnapshot:
        return FleetSnapshot(
            generated_unix=self._clock(),
            robots=sorted(self._robots.values(), key=lambda r: r.robot_id),
        )

    def __len__(self) -> int:
        return len(self._robots)
