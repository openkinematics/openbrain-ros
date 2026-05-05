"""Validate the RTAB-Map params YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "rtabmap.yaml"


def test_yaml_parses():
    yaml.safe_load(CONFIG.read_text())


def test_planar_robot_constraint():
    """Indoor mobile robots should run in 3DOF mode — saves CPU and avoids
    drift in pitch/roll that confuses the costmap layer."""
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["Reg/Force3DoF"] == "true"


def test_publishes_occupancy_grid():
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["RGBD/CreateOccupancyGrid"] == "true"
    assert params["Grid/FromDepth"] == "true"


def test_persistent_db_path_under_maps():
    data = yaml.safe_load(CONFIG.read_text())
    params = data["/**"]["ros__parameters"]
    assert params["database_path"].startswith("/maps/"), (
        "RTAB-Map DB must live under /maps so the volume mount in docker-compose persists it"
    )
