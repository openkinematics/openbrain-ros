"""Mission state-machine.

Services (consumed by openbrain-dashboard):
  /missions/load  (openbrain_msgs/LoadMission)  — load N waypoints + loop flag
  /missions/start (std_srvs/Trigger)            — begin executing
  /missions/stop  (std_srvs/Trigger)            — cancel current goal

Topic:
  /missions/status (openbrain_msgs/MissionStatus) — published at 2 Hz

Driving is delegated to Nav2's ``navigate_to_pose`` action; the mission node
just walks the waypoint list and feeds them in sequence (with optional loop).
"""

from __future__ import annotations

import math
import sys
import threading
import uuid

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_srvs.srv import Trigger

from openbrain_msgs.msg import MissionStatus, Waypoint
from openbrain_msgs.srv import LoadMission

STATE_IDLE = MissionStatus.STATE_IDLE
STATE_LOADED = MissionStatus.STATE_LOADED
STATE_RUNNING = MissionStatus.STATE_RUNNING
STATE_SUCCEEDED = MissionStatus.STATE_SUCCEEDED
STATE_FAILED = MissionStatus.STATE_FAILED
STATE_CANCELED = MissionStatus.STATE_CANCELED


class MissionsNode(Node):
    def __init__(self) -> None:
        super().__init__("openbrain_missions")

        self._lock = threading.Lock()
        self._state = STATE_IDLE
        self._mission_id = ""
        self._waypoints: list[Waypoint] = []
        self._loop = False
        self._index = -1
        self._message = ""
        self._active_goal_handle = None

        self._nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        self.create_service(LoadMission, "/missions/load", self._on_load)
        self.create_service(Trigger, "/missions/start", self._on_start)
        self.create_service(Trigger, "/missions/stop", self._on_stop)

        self._status_pub = self.create_publisher(MissionStatus, "/missions/status", 10)
        self.create_timer(0.5, self._publish_status)

        self.get_logger().info("missions node ready")

    # ---- service handlers --------------------------------------------

    def _on_load(
        self, req: LoadMission.Request, resp: LoadMission.Response
    ) -> LoadMission.Response:
        with self._lock:
            if self._state == STATE_RUNNING:
                resp.success = False
                resp.message = "cannot load while a mission is running; call /missions/stop first"
                return resp
            if not req.waypoints:
                resp.success = False
                resp.message = "no waypoints provided"
                return resp
            self._waypoints = list(req.waypoints)
            self._loop = bool(req.loop)
            self._mission_id = req.mission_id or uuid.uuid4().hex[:12]
            self._index = -1
            self._state = STATE_LOADED
            self._message = f"{len(self._waypoints)} waypoints loaded"
        resp.success = True
        resp.message = self._message
        self.get_logger().info(f"loaded mission {self._mission_id}: {self._message}")
        return resp

    def _on_start(self, _req: Trigger.Request, resp: Trigger.Response) -> Trigger.Response:
        with self._lock:
            if self._state not in (STATE_LOADED, STATE_SUCCEEDED, STATE_CANCELED, STATE_FAILED):
                resp.success = False
                resp.message = f"cannot start from state {self._state}"
                return resp
            if not self._waypoints:
                resp.success = False
                resp.message = "no mission loaded"
                return resp
            self._index = 0
            self._state = STATE_RUNNING
            self._message = "starting"

        self._send_next_goal()
        resp.success = True
        resp.message = "mission started"
        return resp

    def _on_stop(self, _req: Trigger.Request, resp: Trigger.Response) -> Trigger.Response:
        with self._lock:
            handle = self._active_goal_handle
            self._state = STATE_CANCELED
            self._message = "stop requested"
        if handle is not None:
            handle.cancel_goal_async()
        resp.success = True
        resp.message = "stopping"
        return resp

    # ---- mission stepping --------------------------------------------

    def _send_next_goal(self) -> None:
        with self._lock:
            if self._state != STATE_RUNNING:
                return
            if self._index >= len(self._waypoints):
                if self._loop:
                    self._index = 0
                else:
                    self._state = STATE_SUCCEEDED
                    self._message = "mission complete"
                    return
            wp = self._waypoints[self._index]

        if not self._nav_client.wait_for_server(timeout_sec=2.0):
            with self._lock:
                self._state = STATE_FAILED
                self._message = "navigate_to_pose action server unavailable"
            return

        goal = NavigateToPose.Goal()
        goal.pose = _waypoint_to_pose_stamped(wp, self.get_clock().now().to_msg())
        send_future = self._nav_client.send_goal_async(goal)
        send_future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future) -> None:
        handle = future.result()
        if handle is None or not handle.accepted:
            with self._lock:
                self._state = STATE_FAILED
                self._message = "navigate_to_pose rejected goal"
            return
        with self._lock:
            self._active_goal_handle = handle
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._on_goal_result)

    def _on_goal_result(self, future) -> None:
        result = future.result()
        status = result.status if result is not None else GoalStatus.STATUS_UNKNOWN

        with self._lock:
            self._active_goal_handle = None
            if self._state == STATE_CANCELED:
                # Stop was requested mid-flight.
                return
            if status == GoalStatus.STATUS_SUCCEEDED:
                self._index += 1
                self._message = f"reached waypoint {self._index}/{len(self._waypoints)}"
            elif status == GoalStatus.STATUS_CANCELED:
                self._state = STATE_CANCELED
                self._message = "goal canceled"
                return
            else:
                self._state = STATE_FAILED
                self._message = f"navigation failed (status {status})"
                return
            still_running = self._state == STATE_RUNNING

        if still_running:
            self._send_next_goal()

    # ---- status publishing -------------------------------------------

    def _publish_status(self) -> None:
        msg = MissionStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        with self._lock:
            msg.state = self._state
            msg.mission_id = self._mission_id
            msg.current_waypoint_index = self._index
            msg.total_waypoints = len(self._waypoints)
            msg.message = self._message
        self._status_pub.publish(msg)


def _waypoint_to_pose_stamped(wp: Waypoint, stamp) -> PoseStamped:
    ps = PoseStamped()
    ps.header.frame_id = "map"
    ps.header.stamp = stamp
    ps.pose.position.x = float(wp.x)
    ps.pose.position.y = float(wp.y)
    ps.pose.position.z = 0.0
    half = 0.5 * float(wp.yaw)
    ps.pose.orientation.z = math.sin(half)
    ps.pose.orientation.w = math.cos(half)
    return ps


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = MissionsNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
