"""Pure-Python helpers shared by the twist_mux node.

Keeping these in their own module — separate from ``twist_mux.py`` —
means tests can import the dataclass without dragging in ``rclpy`` /
``geometry_msgs``. That matters for CI on hosts that don't have a ROS
install yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _Source:
    """One velocity input feeding the twist mux.

    Stamped with ``last_stamp`` (an opaque timestamp from the caller's
    clock) and ``last_msg`` (the most recent Twist). The mux compares
    ``last_stamp`` against ``timeout_s`` to decide whether the source
    counts as fresh.
    """

    name: str
    topic: str
    priority: int  # higher wins
    timeout_s: float
    # ``last_msg`` is geometry_msgs/Twist at runtime but we type it loosely
    # here to keep this module rclpy-free.
    last_msg: object | None = None
    last_stamp: object | None = None


# Default priority ladder. Higher number wins. Documented at length in
# ``openbrain_safety/README.md``.
DEFAULT_PRIORITIES = {
    "joystick": 100,
    "dashboard": 80,
    "nav": 50,
    "ai": 30,
}

# Default per-source timeout in seconds. Sources that go silent past their
# timeout are treated as if they'd never published.
DEFAULT_TIMEOUTS = {
    "joystick": 0.5,
    "dashboard": 0.5,
    "nav": 1.0,
    "ai": 1.0,
}
