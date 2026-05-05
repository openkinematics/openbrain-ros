"""Validate the VIO-tuned RTAB-Map params."""

from __future__ import annotations

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "rtabmap_vio.yaml"


def test_yaml_parses():
    yaml.safe_load(CONFIG.read_text())


def test_imu_subscribed():
    """The whole point of this profile — RTAB-Map must consume the IMU."""
    params = yaml.safe_load(CONFIG.read_text())["/**"]["ros__parameters"]
    assert params["subscribe_imu"] is True


def test_internal_vio_enabled():
    """odom_info must be subscribed so RTAB-Map produces its own odometry."""
    params = yaml.safe_load(CONFIG.read_text())["/**"]["ros__parameters"]
    assert params["subscribe_odom_info"] is True


def test_visual_plus_icp_strategy():
    """Reg/Strategy=2 = Vis+ICP. Vis-only (0) drifts; ICP-only (1)
    fails on textureless surfaces."""
    params = yaml.safe_load(CONFIG.read_text())["/**"]["ros__parameters"]
    assert params["Reg/Strategy"] == "2"


def test_separate_db_path():
    """Don't clobber the default openbrain_slam DB."""
    params = yaml.safe_load(CONFIG.read_text())["/**"]["ros__parameters"]
    assert params["database_path"] == "/maps/openbrain_vslam.db"
