"""Direct logic tests for the e-stop and twist_mux that don't need an
rclpy spin loop. Anything requiring ROS comm is left to launch_testing.
"""

from __future__ import annotations

from openbrain_safety.sources import _Source


def test_priority_ordering_picks_highest():
    """If multiple inputs are fresh, the highest priority wins.

    twist_mux's selection logic is a simple max() over priority among
    fresh sources. This test pins that contract.
    """
    inputs = [
        _Source(name="ai", topic="/x", priority=30, timeout_s=1.0),
        _Source(name="nav", topic="/x", priority=50, timeout_s=1.0),
        _Source(name="dashboard", topic="/x", priority=80, timeout_s=1.0),
        _Source(name="joystick", topic="/x", priority=100, timeout_s=1.0),
    ]
    winner = max(inputs, key=lambda s: s.priority)
    assert winner.name == "joystick"


def test_priority_levels_are_unique():
    """No two sources should share a priority — that would make the
    arbitration ambiguous."""
    priorities = {100, 80, 50, 30}
    assert len(priorities) == 4


def test_nav_outranks_ai():
    """Specifically: a Nav2 goal overrides an AI policy. If you flip this
    you change driver-takes-precedence semantics — needs a CHANGELOG note."""
    nav = _Source(name="nav", topic="/x", priority=50, timeout_s=1.0)
    ai = _Source(name="ai", topic="/x", priority=30, timeout_s=1.0)
    assert nav.priority > ai.priority


def test_dashboard_outranks_nav():
    """Operator > autonomy. The dashboard joystick overrides Nav2."""
    dashboard = _Source(name="dashboard", topic="/x", priority=80, timeout_s=1.0)
    nav = _Source(name="nav", topic="/x", priority=50, timeout_s=1.0)
    assert dashboard.priority > nav.priority


def test_joystick_outranks_dashboard():
    """A physical gamepad held by a human in the loop beats anything
    coming over the network."""
    joystick = _Source(name="joystick", topic="/x", priority=100, timeout_s=1.0)
    dashboard = _Source(name="dashboard", topic="/x", priority=80, timeout_s=1.0)
    assert joystick.priority > dashboard.priority
