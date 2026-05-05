"""Constants exported from the recording node, isolated so tests can
import them without dragging ``rclpy`` in. Same pattern as
``openbrain_safety.sources``.
"""

from __future__ import annotations

DEFAULT_TOPICS: list[str] = [
    "/cmd_vel",
    "/odom",
    "/map",
    "/system/health",
    "/missions/status",
    "/camera/front/color/image_raw",
    "/camera/back/color/image_raw",
]
