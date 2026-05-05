"""Unit tests for the SDK-free helpers in the Go2 adapter.

These exercise the pure-Python paths that don't touch ``unitree_sdk2py``:
yaw → quaternion conversion and the URDF env-var loader. The SDK bridge
itself is excluded from coverage on purpose — it's hardware-only code.
"""

from __future__ import annotations

import math
import os
import tempfile

from openbrain_robots_unitree_go2.unitree_go2_adapter import _load_urdf, _yaw_to_quat


def test_yaw_to_quat_zero():
    q = _yaw_to_quat(0.0)
    assert q.x == 0.0 and q.y == 0.0
    assert q.z == 0.0
    assert q.w == 1.0


def test_yaw_to_quat_quarter_turn():
    q = _yaw_to_quat(math.pi / 2)
    assert math.isclose(q.z, math.sin(math.pi / 4), rel_tol=1e-6)
    assert math.isclose(q.w, math.cos(math.pi / 4), rel_tol=1e-6)


def test_yaw_to_quat_negative():
    q = _yaw_to_quat(-math.pi / 2)
    assert math.isclose(q.z, -math.sin(math.pi / 4), rel_tol=1e-6)


def test_load_urdf_returns_none_when_unset():
    assert _load_urdf(None) is None
    assert _load_urdf("") is None


def test_load_urdf_reads_file():
    with tempfile.NamedTemporaryFile("w", suffix=".urdf", delete=False) as f:
        f.write("<robot name='go2'/>")
        path = f.name
    try:
        assert _load_urdf(path) == "<robot name='go2'/>"
    finally:
        os.unlink(path)


def test_load_urdf_missing_file_returns_none():
    assert _load_urdf("/nonexistent/path/does-not-exist.urdf") is None
