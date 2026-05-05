"""Pure-Python policy for the patrol-vs-recharge decision.

Separated from the ROS node so it can be unit-tested without rclpy and
swapped out (e.g. with an RL policy) without touching the wiring layer.

Two state machines share this policy:

  * The **patrol** loop — drives the configured waypoints, looped, until
    the battery drops past ``low_threshold``.
  * The **return-to-charger** mission — a single-waypoint mission to
    ``charger_pose``. Resumes patrol once the battery climbs above
    ``resume_threshold`` (hysteresis: typically 5–10% above the low
    threshold to avoid bouncing).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BatteryDecision(Enum):
    KEEP_PATROLLING = "keep_patrolling"
    GO_TO_CHARGER = "go_to_charger"
    STAY_AT_CHARGER = "stay_at_charger"
    RESUME_PATROL = "resume_patrol"


@dataclass(frozen=True)
class PatrolPolicy:
    """Hysteresis thresholds for the recharge state machine.

    ``low_threshold`` and ``resume_threshold`` are battery percentages in
    [0, 100]. ``resume_threshold`` must be strictly greater than
    ``low_threshold`` or the patrol will oscillate.
    """

    low_threshold: float = 25.0
    resume_threshold: float = 75.0
    critical_threshold: float = 10.0  # below this, never resume even if asked

    def __post_init__(self) -> None:
        if self.resume_threshold <= self.low_threshold:
            raise ValueError("resume_threshold must be > low_threshold (hysteresis)")
        if not (0.0 <= self.critical_threshold <= self.low_threshold):
            raise ValueError("critical_threshold must be in [0, low_threshold]")


def decide(
    *,
    battery_pct: float,
    on_charger: bool,
    currently_patrolling: bool,
    policy: PatrolPolicy,
) -> BatteryDecision:
    """One-shot decision: given current state, what should the loop do?

    Caller is responsible for invoking the corresponding action
    (load + start a return mission, resume the patrol, etc.).
    """
    if on_charger:
        if battery_pct < policy.resume_threshold:
            return BatteryDecision.STAY_AT_CHARGER
        return BatteryDecision.RESUME_PATROL

    # Not on the charger.
    if battery_pct <= policy.critical_threshold:
        return BatteryDecision.GO_TO_CHARGER
    if currently_patrolling:
        if battery_pct <= policy.low_threshold:
            return BatteryDecision.GO_TO_CHARGER
        return BatteryDecision.KEEP_PATROLLING
    # Idle, not on charger — wait for explicit start.
    return BatteryDecision.KEEP_PATROLLING
