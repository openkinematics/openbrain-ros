"""The ros_gz bridge config must cover every contract topic the rest of
the stack expects from a sim robot.

If a topic isn't bridged, SLAM / Nav2 / the streamer go quiet without an
obvious error. Locking the bridge config in tests prevents that.
"""

from __future__ import annotations

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "sim_bridge.yaml"

REQUIRED_ROS_TOPICS = {
    "/clock",
    "/cmd_vel",
    "/odom",
    "/scan",
    "/camera/front/color/image_raw",
    "/camera/front/depth/image_rect_raw",
    "/camera/front/color/camera_info",
    "/joint_states",
}


def _load() -> list[dict]:
    return yaml.safe_load(CONFIG.read_text())


def test_yaml_parses_as_list_of_mappings():
    data = _load()
    assert isinstance(data, list)
    assert all(isinstance(entry, dict) for entry in data)


def test_every_required_topic_is_bridged():
    bridged = {entry["ros_topic_name"] for entry in _load()}
    missing = REQUIRED_ROS_TOPICS - bridged
    assert not missing, f"sim_bridge.yaml missing topics: {sorted(missing)}"


def test_each_entry_has_required_keys():
    required = {"ros_topic_name", "gz_topic_name", "ros_type_name", "gz_type_name", "direction"}
    for entry in _load():
        missing = required - entry.keys()
        assert not missing, f"entry {entry.get('ros_topic_name')!r} missing keys: {missing}"


def test_directions_are_valid():
    valid = {"GZ_TO_ROS", "ROS_TO_GZ", "BIDIRECTIONAL"}
    for entry in _load():
        assert entry["direction"] in valid, (
            f"{entry['ros_topic_name']}: invalid direction {entry['direction']!r}"
        )


def test_cmd_vel_flows_into_sim():
    by_topic = {e["ros_topic_name"]: e for e in _load()}
    assert by_topic["/cmd_vel"]["direction"] == "ROS_TO_GZ"


def test_odom_flows_out_of_sim():
    by_topic = {e["ros_topic_name"]: e for e in _load()}
    assert by_topic["/odom"]["direction"] == "GZ_TO_ROS"
