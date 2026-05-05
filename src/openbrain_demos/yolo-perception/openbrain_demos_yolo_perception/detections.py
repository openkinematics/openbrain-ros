"""Pure-Python detection helpers — testable without rclpy / ultralytics.

Splits the data-processing concerns (NMS-derived boxes → ROS messages)
from the inference loop in :mod:`yolo_node`. Lets us unit-test the
post-processing path on a developer laptop.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """One detection in pixel coordinates."""

    label_id: int
    label: str
    score: float  # 0..1
    cx: float  # center x, pixels
    cy: float  # center y, pixels
    w: float  # bounding-box width, pixels
    h: float  # bounding-box height, pixels


def postprocess(
    boxes_xywh,
    scores,
    class_ids,
    names: dict[int, str],
    *,
    score_threshold: float,
    max_results: int = 100,
) -> list[Detection]:
    """Filter + sort raw model output into :class:`Detection` records.

    ``boxes_xywh`` is an iterable of (cx, cy, w, h) tuples (pixels).
    ``scores`` is the parallel iterable of confidence values.
    ``class_ids`` is the parallel iterable of integer class ids.
    """
    out: list[Detection] = []
    for box, score, cls in zip(boxes_xywh, scores, class_ids, strict=False):
        s = float(score)
        if s < score_threshold:
            continue
        cls_int = int(cls)
        out.append(
            Detection(
                label_id=cls_int,
                label=names.get(cls_int, str(cls_int)),
                score=s,
                cx=float(box[0]),
                cy=float(box[1]),
                w=float(box[2]),
                h=float(box[3]),
            )
        )
    out.sort(key=lambda d: d.score, reverse=True)
    return out[:max_results]


def color_for_class(cls_int: int) -> tuple[int, int, int]:
    """Deterministic BGR color per class id — used by the overlay drawer."""
    # Cheap hash → stable color. We pick from a wider gamut than evenly-spaced
    # HSV because adjacent classes (cat=15, dog=16) want distinguishable hues.
    h = (cls_int * 1103515245 + 12345) & 0x7FFFFFFF
    return (h & 0xFF, (h >> 8) & 0xFF, (h >> 16) & 0xFF)
