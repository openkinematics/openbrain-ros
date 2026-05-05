"""Unit tests for the speed-profile clamp logic."""

from openbrain_robots_generic.robot_adapter import SPEED_PROFILES, _clamp


def test_clamp_within_bounds():
    assert _clamp(0.5, 1.0) == 0.5
    assert _clamp(-0.5, 1.0) == -0.5


def test_clamp_at_bounds():
    assert _clamp(1.5, 1.0) == 1.0
    assert _clamp(-1.5, 1.0) == -1.0


def test_known_profiles():
    assert "beginner" in SPEED_PROFILES
    assert "normal" in SPEED_PROFILES
    assert "insane" in SPEED_PROFILES
    assert SPEED_PROFILES["beginner"].max_linear < SPEED_PROFILES["normal"].max_linear
    assert SPEED_PROFILES["normal"].max_linear < SPEED_PROFILES["insane"].max_linear
