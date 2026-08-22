"""Sanity checks on waypoint -> PoseStamped conversion."""

import math

from builtin_interfaces.msg import Time
from openbrain_demos_missions.missions_node import _waypoint_to_pose_stamped
from openbrain_msgs.msg import Waypoint


def test_yaw_to_quaternion_zero():
    wp = Waypoint(x=1.0, y=2.0, yaw=0.0, label="", dwell_seconds=0.0)
    ps = _waypoint_to_pose_stamped(wp, Time())
    assert ps.pose.position.x == 1.0
    assert ps.pose.position.y == 2.0
    assert ps.pose.orientation.w == 1.0
    assert ps.pose.orientation.z == 0.0


def test_yaw_to_quaternion_quarter_turn():
    wp = Waypoint(x=0.0, y=0.0, yaw=math.pi / 2, label="", dwell_seconds=0.0)
    ps = _waypoint_to_pose_stamped(wp, Time())
    assert math.isclose(ps.pose.orientation.z, math.sin(math.pi / 4), rel_tol=1e-6)
    assert math.isclose(ps.pose.orientation.w, math.cos(math.pi / 4), rel_tol=1e-6)


def test_frame_is_map():
    wp = Waypoint(x=0.0, y=0.0, yaw=0.0, label="x", dwell_seconds=0.0)
    ps = _waypoint_to_pose_stamped(wp, Time())
    assert ps.header.frame_id == "map"
