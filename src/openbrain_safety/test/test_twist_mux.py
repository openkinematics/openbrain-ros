"""Unit tests for the twist_mux _Source dataclass + import surface."""

from openbrain_safety.sources import _Source


def test_source_construction():
    s = _Source(name="joy", topic="/foo", priority=10, timeout_s=0.5)
    assert s.priority == 10
    assert s.last_msg is None
    assert s.last_stamp is None


def test_sources_module_is_rclpy_free():
    """The shared dataclass module must not transitively import rclpy —
    we keep test importability on non-ROS hosts (CI, dev laptops without
    ROS yet)."""
    import openbrain_safety.sources as mod

    assert "rclpy" not in (getattr(mod, "_imports", "") or "")
    # Constructing a _Source must not raise.
    src = mod._Source(name="x", topic="/x", priority=1, timeout_s=0.5)
    assert src.priority == 1
