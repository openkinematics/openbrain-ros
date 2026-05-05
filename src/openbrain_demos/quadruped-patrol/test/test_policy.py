"""Unit tests for the patrol-vs-recharge policy."""

from __future__ import annotations

import pytest
from openbrain_demos_quadruped_patrol.policy import (
    BatteryDecision,
    PatrolPolicy,
    decide,
)

P = PatrolPolicy(low_threshold=25.0, resume_threshold=75.0, critical_threshold=10.0)


def _decide(*, battery, on_charger=False, patrolling=True):
    return decide(
        battery_pct=battery,
        on_charger=on_charger,
        currently_patrolling=patrolling,
        policy=P,
    )


def test_full_battery_keeps_patrolling():
    assert _decide(battery=90.0) == BatteryDecision.KEEP_PATROLLING


def test_low_battery_returns_to_charger():
    assert _decide(battery=20.0) == BatteryDecision.GO_TO_CHARGER


def test_just_above_low_threshold_keeps_patrolling():
    assert _decide(battery=26.0) == BatteryDecision.KEEP_PATROLLING


def test_critical_battery_always_returns():
    """Below critical threshold, even an idle robot (not patrolling) returns."""
    assert _decide(battery=5.0, patrolling=False) == BatteryDecision.GO_TO_CHARGER


def test_on_charger_below_resume_threshold_stays():
    assert _decide(battery=50.0, on_charger=True) == BatteryDecision.STAY_AT_CHARGER


def test_on_charger_above_resume_threshold_resumes():
    assert _decide(battery=80.0, on_charger=True) == BatteryDecision.RESUME_PATROL


def test_hysteresis_prevents_oscillation():
    """A robot at 30% battery should keep patrolling; if it dips to 24% it
    returns; on the charger at 30% it stays — the gap between low (25)
    and resume (75) prevents a flip-flop in either direction."""
    assert _decide(battery=30.0) == BatteryDecision.KEEP_PATROLLING
    assert _decide(battery=24.0) == BatteryDecision.GO_TO_CHARGER
    assert _decide(battery=30.0, on_charger=True) == BatteryDecision.STAY_AT_CHARGER
    assert _decide(battery=80.0, on_charger=True) == BatteryDecision.RESUME_PATROL


def test_invalid_thresholds_raise():
    with pytest.raises(ValueError):
        PatrolPolicy(low_threshold=50.0, resume_threshold=40.0)
    with pytest.raises(ValueError):
        PatrolPolicy(low_threshold=25.0, resume_threshold=75.0, critical_threshold=30.0)


def test_negative_critical_rejected():
    with pytest.raises(ValueError):
        PatrolPolicy(critical_threshold=-1.0)


def test_idle_robot_not_on_charger_waits():
    """A robot that isn't currently patrolling AND isn't on the charger
    AND is above critical: don't auto-start anything. The operator
    explicitly starts patrol via the dashboard."""
    assert (
        _decide(battery=80.0, on_charger=False, patrolling=False) == BatteryDecision.KEEP_PATROLLING
    )
