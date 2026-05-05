"""Unit tests for FrameSlot and config loading."""

import os
import tempfile

import numpy as np
from openbrain_teleop.video_streamer import FrameSlot, _load_streams, _no_signal_frame


def test_frame_slot_round_trip():
    slot = FrameSlot(framerate=15)
    assert slot.get() is None
    bgr = np.zeros((10, 10, 3), dtype=np.uint8)
    slot.put(bgr)
    out = slot.get()
    assert out is not None and out.shape == bgr.shape


def test_no_signal_frame_dimensions():
    img = _no_signal_frame()
    assert img.shape[2] == 3
    assert img.dtype.name == "uint8"


def test_load_streams_minimal():
    payload = """
streams:
  front:
    topic: /camera/front/color/image_raw
    framerate: 10
"""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(payload)
        path = f.name
    try:
        slots, topics = _load_streams(path)
        assert "front" in slots
        assert slots["front"].framerate == 10
        assert topics["front"] == "/camera/front/color/image_raw"
    finally:
        os.unlink(path)
