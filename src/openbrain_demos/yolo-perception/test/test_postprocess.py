"""Tests for the pure-Python detection post-processing path."""

from __future__ import annotations

from openbrain_demos_yolo_perception.detections import (
    Detection,
    color_for_class,
    postprocess,
)


def test_threshold_drops_low_confidence():
    boxes = [(10, 10, 20, 20), (30, 30, 40, 40)]
    scores = [0.05, 0.9]
    cls_ids = [0, 0]
    out = postprocess(boxes, scores, cls_ids, {0: "person"}, score_threshold=0.25)
    assert len(out) == 1
    assert out[0].score == 0.9


def test_results_sorted_by_score_desc():
    boxes = [(0, 0, 10, 10)] * 3
    scores = [0.6, 0.9, 0.7]
    cls_ids = [0, 0, 0]
    out = postprocess(boxes, scores, cls_ids, {0: "person"}, score_threshold=0.0)
    assert [d.score for d in out] == [0.9, 0.7, 0.6]


def test_unknown_class_falls_back_to_id():
    boxes = [(0, 0, 10, 10)]
    out = postprocess(boxes, [0.9], [42], names={}, score_threshold=0.0)
    assert out[0].label == "42"


def test_max_results_caps_output():
    boxes = [(0, 0, 1, 1)] * 50
    scores = [0.5] * 50
    cls_ids = [0] * 50
    out = postprocess(boxes, scores, cls_ids, {0: "x"}, score_threshold=0.0, max_results=10)
    assert len(out) == 10


def test_color_is_deterministic():
    a = color_for_class(15)
    b = color_for_class(15)
    assert a == b
    # And different classes get different colors (statistically — pin a known case).
    assert color_for_class(15) != color_for_class(16)


def test_color_in_byte_range():
    for cls in range(0, 100, 7):
        c = color_for_class(cls)
        assert all(0 <= ch <= 255 for ch in c)


def test_detection_is_immutable():
    d = Detection(label_id=0, label="x", score=0.5, cx=1.0, cy=2.0, w=3.0, h=4.0)
    try:
        d.score = 0.9  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("Detection should be frozen")
