"""Validate the dual D435i config."""

from __future__ import annotations

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "d435i.yaml"


def test_yaml_parses():
    yaml.safe_load(CONFIG.read_text())


def test_imu_is_unified():
    """unite_imu_method=2 produces a single clean /imu topic; without it
    we'd publish raw gyro+accel separately and the dashboard would have to
    fuse them."""
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["unite_imu_method"] == 2


def test_align_depth_enabled():
    """Aligned depth is what RTAB-Map and Nav2's depth costmap layer want."""
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["align_depth.enable"] is True


def test_pointcloud_disabled():
    """Generated pointclouds are heavy on USB bandwidth; downstream nodes
    (RTAB-Map, NVBlox) build their own from the depth image."""
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["pointcloud.enable"] is False
