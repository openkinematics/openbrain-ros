"""Sanity checks on the default topic list."""

from openbrain_recording.defaults import DEFAULT_TOPICS


def test_default_topics_includes_critical():
    assert "/cmd_vel" in DEFAULT_TOPICS
    assert "/odom" in DEFAULT_TOPICS
    assert "/system/health" in DEFAULT_TOPICS
    assert any("camera/front" in t for t in DEFAULT_TOPICS)


def test_default_topics_unique():
    assert len(DEFAULT_TOPICS) == len(set(DEFAULT_TOPICS))
