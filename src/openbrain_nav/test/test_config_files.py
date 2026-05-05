"""Validate the Nav2 params YAML and behavior-tree XML at build time."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def test_nav2_yaml_parses():
    data = yaml.safe_load((CONFIG_DIR / "nav2.yaml").read_text())
    # Top-level keys are the Nav2 server names.
    expected_servers = {
        "amcl",
        "bt_navigator",
        "controller_server",
        "local_costmap",
        "global_costmap",
        "planner_server",
        "behavior_server",
    }
    assert expected_servers <= set(data.keys()), (
        f"missing Nav2 servers in config: {expected_servers - set(data.keys())}"
    )


def test_bt_xml_parses_and_has_main_tree():
    xml = (CONFIG_DIR / "nav_to_pose_bt.xml").read_text()
    root = ET.fromstring(xml)
    assert root.tag == "root"
    assert root.attrib.get("main_tree_to_execute") == "MainTree"
    main_tree = root.find("BehaviorTree[@ID='MainTree']")
    assert main_tree is not None, "behavior tree must define MainTree"


def test_controller_uses_regulated_pure_pursuit():
    data = yaml.safe_load((CONFIG_DIR / "nav2.yaml").read_text())
    plugin = data["controller_server"]["ros__parameters"]["FollowPath"]["plugin"]
    assert "RegulatedPurePursuitController" in plugin
