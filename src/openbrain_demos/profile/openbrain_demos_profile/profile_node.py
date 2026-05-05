"""ROS node that exposes the profile store over services + a latched topic.

Services
--------
``/profile/list``  ``std_srvs/Trigger``  → response.message = JSON ``{"users": [...]}``
``/profile/get``   ``std_srvs/Trigger``  → response.message = active profile JSON
``/profile/set``   ``std_srvs/Trigger``  Hack: takes the active profile snapshot.
                                         For arbitrary updates the dashboard
                                         calls ``/profile/set_json`` (a custom
                                         use of the ``LoadMission`` service
                                         shape with a JSON blob in
                                         ``mission_json``-style param). Pending
                                         a dedicated SetProfile.srv in v0.2.

Topic
-----
``/profile/active``  ``std_msgs/String`` (latched) — JSON of the active profile.
                     Republished on every successful set/load.

The dashboard reads ``/profile/active`` directly via rosbridge and renders
the Profile page from it. On user save it calls ``/profile/set`` with the
preferred-payload pattern.
"""

from __future__ import annotations

import json
import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String
from std_srvs.srv import Trigger

from openbrain_demos_profile.store import Profile, ProfileStore, coerce


class ProfileNode(Node):
    def __init__(self) -> None:
        super().__init__("openbrain_profile")

        self.declare_parameter("root", str(ProfileStore().root))
        self.declare_parameter("active_user", "default")

        self._store = ProfileStore(self.get_parameter("root").get_parameter_value().string_value)

        latched = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._active_pub = self.create_publisher(String, "/profile/active", latched)

        self.create_service(Trigger, "/profile/list", self._on_list)
        self.create_service(Trigger, "/profile/get", self._on_get)
        # /profile/set + /profile/set_json: see module docstring. The dashboard
        # writes JSON into the ``message`` field of a Trigger via rosbridge's
        # arbitrary-string passthrough.
        self.create_service(Trigger, "/profile/set", self._on_set_from_param)
        self.create_subscription(String, "/profile/set_json", self._on_set_json, 10)

        # Load + publish the active profile on startup.
        user = self.get_parameter("active_user").get_parameter_value().string_value or "default"
        profile = self._store.load(user)
        self._publish(profile)
        self.get_logger().info(
            f"profile_node ready (root={self._store.root}, active={profile.user})"
        )

    # ---- handlers ----------------------------------------------------

    def _on_list(self, _req, resp: Trigger.Response) -> Trigger.Response:
        resp.success = True
        resp.message = json.dumps({"users": self._store.list_users()})
        return resp

    def _on_get(self, _req, resp: Trigger.Response) -> Trigger.Response:
        resp.success = self._store.active() is not None
        resp.message = self._store.to_json()
        return resp

    def _on_set_from_param(self, _req, resp: Trigger.Response) -> Trigger.Response:
        # Re-saves the in-memory active profile. Useful for "make this current".
        active = self._store.active()
        if active is None:
            resp.success = False
            resp.message = "no active profile to save"
            return resp
        path = self._store.save(active)
        self._publish(active)
        resp.success = True
        resp.message = str(path)
        return resp

    def _on_set_json(self, msg: String) -> None:
        """Apply a JSON payload to the active profile and persist."""
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f"/profile/set_json: invalid JSON ({exc})")
            return
        if not isinstance(payload, dict):
            self.get_logger().warn(
                f"/profile/set_json: expected JSON object, got {type(payload).__name__}"
            )
            return
        # Keep current user identity unless explicitly switching.
        active = self._store.active() or Profile()
        merged = {**self._asdict(active), **payload}
        profile = coerce(merged)
        path = self._store.save(profile)
        self._publish(profile)
        self.get_logger().info(f"profile saved: {path}")

    # ---- helpers -----------------------------------------------------

    def _publish(self, profile: Profile) -> None:
        self._active_pub.publish(String(data=self._store.to_json(profile)))

    @staticmethod
    def _asdict(profile: Profile) -> dict:
        from dataclasses import asdict as _asdict

        return _asdict(profile)


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = ProfileNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
