"""Mission recording / playback over ROS services.

Wraps ``ros2 bag record`` and ``ros2 bag play`` as long-lived subprocesses,
controllable from rosbridge. Bags land in ``/recordings/<name>/``.

Services
--------
``/recording/start``  ``std_srvs/Trigger``  start the default-named recording
``/recording/stop``   ``std_srvs/Trigger``  stop the active recording

Topics recorded by default (override with the ``topics`` parameter):
  /cmd_vel /odom /map /system/health /missions/status
  /camera/front/color/image_raw /camera/back/color/image_raw

Why subprocess instead of rosbag2_py?
  rosbag2_py has CPython API drift between Humble patches and Iron — the
  CLI is the stable interface and exits cleanly on SIGINT.
"""

from __future__ import annotations

import os
import shlex
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

DEFAULT_TOPICS = [
    "/cmd_vel",
    "/odom",
    "/map",
    "/system/health",
    "/missions/status",
    "/camera/front/color/image_raw",
    "/camera/back/color/image_raw",
]


class RecordingNode(Node):
    def __init__(self) -> None:
        super().__init__("openbrain_recording")

        self.declare_parameter("output_dir", "/recordings")
        self.declare_parameter("topics", DEFAULT_TOPICS)
        self.declare_parameter("compress", True)

        self._proc: subprocess.Popen | None = None
        self._current: Path | None = None

        self.create_service(Trigger, "/recording/start", self._on_start)
        self.create_service(Trigger, "/recording/stop", self._on_stop)

        Path(self._output_dir()).mkdir(parents=True, exist_ok=True)
        self.get_logger().info(f"recording_node ready (output_dir={self._output_dir()})")

    # ---- helpers -----------------------------------------------------

    def _output_dir(self) -> str:
        return self.get_parameter("output_dir").get_parameter_value().string_value

    def _topics(self) -> list[str]:
        raw = self.get_parameter("topics").get_parameter_value().string_array_value
        return list(raw) if raw else DEFAULT_TOPICS

    def _compress(self) -> bool:
        return bool(self.get_parameter("compress").get_parameter_value().bool_value)

    # ---- service handlers --------------------------------------------

    def _on_start(self, _req, resp: Trigger.Response) -> Trigger.Response:
        if self._proc is not None and self._proc.poll() is None:
            resp.success = False
            resp.message = f"recording already in progress at {self._current}"
            return resp

        name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        target = Path(self._output_dir()) / name
        topics = self._topics()
        cmd = ["ros2", "bag", "record", "-o", str(target), *topics]
        if self._compress():
            cmd.extend(["--compression-mode", "file", "--compression-format", "zstd"])
        self.get_logger().info(f"starting recording: {shlex.join(cmd)}")
        try:
            self._proc = subprocess.Popen(cmd, preexec_fn=os.setsid)
            self._current = target
            resp.success = True
            resp.message = str(target)
        except OSError as exc:
            self._proc = None
            resp.success = False
            resp.message = f"failed to spawn ros2 bag record: {exc}"
        return resp

    def _on_stop(self, _req, resp: Trigger.Response) -> Trigger.Response:
        if self._proc is None or self._proc.poll() is not None:
            resp.success = False
            resp.message = "no recording active"
            return resp
        self.get_logger().info(f"stopping recording at {self._current}")
        try:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGINT)
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)
            self._proc.wait()
        finished = self._current
        self._proc = None
        self._current = None
        resp.success = True
        resp.message = str(finished) if finished else ""
        return resp

    # ---- shutdown ----------------------------------------------------

    def destroy_node(self):
        if self._proc is not None and self._proc.poll() is None:
            try:
                os.killpg(os.getpgid(self._proc.pid), signal.SIGINT)
                self._proc.wait(timeout=5)
            except Exception:  # pragma: no cover - best effort
                pass
        return super().destroy_node()


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = RecordingNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
