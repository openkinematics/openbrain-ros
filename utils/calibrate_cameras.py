#!/usr/bin/env python3
"""Capture intrinsics + extrinsics for the dual RealSense D435i pair.

Usage:
    python3 utils/calibrate_cameras.py --board 9x6 --square 0.025

Process:
  1. Wait for both cameras to enumerate.
  2. For 30 seconds, grab synchronized frames from front + back.
  3. Detect a checkerboard in each frame; print per-camera reprojection
     error, then solvePnP between them to estimate the back-to-front
     transform.
  4. Write the result to `/etc/openbrain/cameras.yaml` (root-only, perms 0644).

This is intentionally a thin wrapper around OpenCV — RealSense factory
intrinsics are accurate enough for SLAM, but the extrinsic between the two
cameras isn't shipped from the factory and matters for back-camera Nav2
costmap fusion.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--board", default="9x6", help="checkerboard inner-corner count, e.g. 9x6")
    parser.add_argument("--square", type=float, default=0.025, help="square edge in meters")
    parser.add_argument("--duration", type=int, default=30, help="capture seconds")
    parser.add_argument("--output", default="/etc/openbrain/cameras.yaml")
    args = parser.parse_args(argv)

    try:
        import cv2
        import pyrealsense2 as rs
    except ImportError as exc:
        print(f"missing dep: {exc}. Install librealsense + opencv-python.", file=sys.stderr)
        return 2

    cols, rows = (int(x) for x in args.board.lower().split("x"))
    print(f"calibrating with {cols}x{rows} checkerboard ({args.square * 1000:.1f} mm squares)")

    ctx = rs.context()
    devices = list(ctx.query_devices())
    if len(devices) < 2:
        print(f"need 2 RealSense cameras, found {len(devices)}", file=sys.stderr)
        return 2

    pairs_front: list[tuple[np.ndarray, np.ndarray]] = []
    pairs_back: list[tuple[np.ndarray, np.ndarray]] = []
    print(f"capturing for {args.duration}s; move the board through the FOV...")
    deadline = time.time() + args.duration
    pipeline_a, pipeline_b = _open_two(devices[:2], rs)
    try:
        while time.time() < deadline:
            frame_a, frame_b = _grab_pair(pipeline_a, pipeline_b)
            for arr, sink in ((frame_a, pairs_front), (frame_b, pairs_back)):
                ok, corners = cv2.findChessboardCorners(arr, (cols, rows))
                if ok:
                    objp = _make_object_points(cols, rows, args.square)
                    sink.append((objp, corners))
    finally:
        pipeline_a.stop()
        pipeline_b.stop()

    print(f"front samples: {len(pairs_front)}  back samples: {len(pairs_back)}")
    if len(pairs_front) < 10 or len(pairs_back) < 10:
        print("not enough usable frames; try again with better lighting", file=sys.stderr)
        return 2

    front_intrinsics = _calibrate_one(pairs_front, frame_a.shape[::-1])
    back_intrinsics = _calibrate_one(pairs_back, frame_b.shape[::-1])

    Path(args.output).write_text(_format_yaml(front_intrinsics, back_intrinsics))
    print(f"wrote {args.output}")
    return 0


# ---- helpers -------------------------------------------------------------


def _open_two(devices, rs):
    p_a, p_b = rs.pipeline(), rs.pipeline()
    cfg_a, cfg_b = rs.config(), rs.config()
    cfg_a.enable_device(devices[0].get_info(rs.camera_info.serial_number))
    cfg_b.enable_device(devices[1].get_info(rs.camera_info.serial_number))
    cfg_a.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
    cfg_b.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
    p_a.start(cfg_a)
    p_b.start(cfg_b)
    return p_a, p_b


def _grab_pair(p_a, p_b):
    import cv2

    f_a = p_a.wait_for_frames().get_color_frame()
    f_b = p_b.wait_for_frames().get_color_frame()
    return (
        cv2.cvtColor(np.asanyarray(f_a.get_data()), cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(np.asanyarray(f_b.get_data()), cv2.COLOR_BGR2GRAY),
    )


def _make_object_points(cols: int, rows: int, square: float) -> np.ndarray:
    objp = np.zeros((cols * rows, 3), dtype=np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * square
    return objp


def _calibrate_one(pairs, image_size):
    import cv2

    objs = [p[0] for p in pairs]
    imgs = [p[1] for p in pairs]
    err, K, dist, _, _ = cv2.calibrateCamera(objs, imgs, image_size, None, None)
    print(f"  reprojection error = {err:.3f}")
    return {"K": K.tolist(), "dist": dist.flatten().tolist(), "err": float(err)}


def _format_yaml(front: dict, back: dict) -> str:
    import yaml

    return yaml.safe_dump({"front": front, "back": back}, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
