"""HTTP video streamer for the OpenBrain dashboard.

Exposes two endpoints per camera, matching the contract consumed by the
dashboard's `lib/video.ts`:

    POST /stream/{name}/offer    -> WebRTC SDP exchange (application/json)
    GET  /stream/{name}.mjpeg    -> multipart/x-mixed-replace MJPEG fallback
    GET  /stream/{name}/snapshot -> single JPEG (still frame, for SEO/poster)

The streamer subscribes to `/camera/{name}/color/image_raw` for each
configured camera and keeps the latest frame in a thread-safe slot.
WebRTC uses aiortc with a custom :class:`RosVideoTrack` that pulls from
that slot at the negotiated frame rate. MJPEG re-encodes frames on demand.

Configuration is a YAML file with one entry per stream:

    streams:
      front:
        topic: /camera/front/color/image_raw
        framerate: 15
      back:
        topic: /camera/back/color/image_raw
        framerate: 15
"""

from __future__ import annotations

import argparse
import asyncio
import fractions
import logging
import threading
import time
from dataclasses import dataclass, field

import cv2
import numpy as np
import rclpy
import yaml
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image

LOG = logging.getLogger("openbrain.video_streamer")


# ---------------------------------------------------------------------------
# Frame slot — single-producer (ROS thread), multi-consumer (asyncio handlers)
# ---------------------------------------------------------------------------


@dataclass
class FrameSlot:
    """Holds the latest camera frame as BGR numpy array."""

    framerate: float
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _bgr: np.ndarray | None = None
    _stamp: float = 0.0

    def put(self, bgr: np.ndarray) -> None:
        with self._lock:
            self._bgr = bgr
            self._stamp = time.time()

    def get(self) -> np.ndarray | None:
        with self._lock:
            return None if self._bgr is None else self._bgr.copy()

    @property
    def stamp(self) -> float:
        with self._lock:
            return self._stamp


# ---------------------------------------------------------------------------
# ROS bridge — runs in its own thread so we don't block the event loop
# ---------------------------------------------------------------------------


class CameraBridge(Node):
    def __init__(self, slots: dict[str, FrameSlot], topics: dict[str, str]) -> None:
        super().__init__("openbrain_video_streamer")
        self._bridge = CvBridge()
        # Best-effort QoS to keep up with high-rate camera streams without
        # backpressuring the publisher.
        qos = QoSProfile(depth=1, reliability=QoSReliabilityPolicy.BEST_EFFORT)
        for name, topic in topics.items():
            slot = slots[name]
            self.create_subscription(Image, topic, _make_callback(slot, self._bridge), qos)
            self.get_logger().info(f"streaming {topic} as /stream/{name}")


def _make_callback(slot: FrameSlot, bridge: CvBridge):
    def cb(msg: Image) -> None:
        try:
            slot.put(bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8"))
        except Exception as exc:  # pragma: no cover - defensive
            LOG.warning("frame conversion failed: %s", exc)

    return cb


def _spin_ros(node: CameraBridge) -> None:
    rclpy.spin(node)


# ---------------------------------------------------------------------------
# WebRTC video track
# ---------------------------------------------------------------------------


class RosVideoTrack(VideoStreamTrack):
    """A VideoStreamTrack that pulls frames from a FrameSlot."""

    kind = "video"

    def __init__(self, slot: FrameSlot) -> None:
        super().__init__()
        self._slot = slot
        self._frame_count = 0
        # Time-base 1/90000 is the WebRTC convention for video.
        self._time_base = fractions.Fraction(1, 90000)
        self._period = 1.0 / max(slot.framerate, 1.0)
        self._last_emit = 0.0

    async def recv(self) -> VideoFrame:
        # Pace the track; aiortc would otherwise drown the SFU.
        now = time.time()
        wait = self._period - (now - self._last_emit)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_emit = time.time()

        bgr = self._slot.get()
        if bgr is None:
            bgr = _no_signal_frame()

        frame = VideoFrame.from_ndarray(bgr, format="bgr24")
        # WebRTC wants timestamps in 90 kHz units.
        self._frame_count += 1
        frame.pts = int(self._frame_count * 90000 * self._period)
        frame.time_base = self._time_base
        return frame


def _no_signal_frame(width: int = 640, height: int = 480) -> np.ndarray:
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(
        img,
        "no signal",
        (width // 2 - 100, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (200, 200, 200),
        2,
    )
    return img


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------


class StreamerApp:
    def __init__(self, slots: dict[str, FrameSlot]) -> None:
        self._slots = slots
        self._peers: set[RTCPeerConnection] = set()

    async def offer(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        slot = self._slots.get(name)
        if slot is None:
            raise web.HTTPNotFound(text=f"unknown stream {name!r}")

        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        self._peers.add(pc)

        @pc.on("connectionstatechange")
        async def on_state_change():
            if pc.connectionState in ("failed", "closed"):
                await pc.close()
                self._peers.discard(pc)

        pc.addTrack(RosVideoTrack(slot))

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return web.json_response(
            {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
            }
        )

    async def mjpeg(self, request: web.Request) -> web.StreamResponse:
        name = request.match_info["name"]
        slot = self._slots.get(name)
        if slot is None:
            raise web.HTTPNotFound(text=f"unknown stream {name!r}")

        boundary = "openbrainmjpeg"
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": f"multipart/x-mixed-replace; boundary={boundary}",
                "Cache-Control": "no-cache, no-store, private",
                "Pragma": "no-cache",
            },
        )
        await response.prepare(request)

        period = 1.0 / max(slot.framerate, 1.0)
        try:
            while not request.transport.is_closing():
                bgr = slot.get()
                if bgr is None:
                    bgr = _no_signal_frame()
                ok, jpeg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ok:
                    await asyncio.sleep(period)
                    continue
                payload = jpeg.tobytes()
                chunk = (
                    (
                        f"--{boundary}\r\n"
                        f"Content-Type: image/jpeg\r\n"
                        f"Content-Length: {len(payload)}\r\n\r\n"
                    ).encode("ascii")
                    + payload
                    + b"\r\n"
                )
                await response.write(chunk)
                await asyncio.sleep(period)
        except (asyncio.CancelledError, ConnectionResetError):
            pass
        return response

    async def snapshot(self, request: web.Request) -> web.Response:
        name = request.match_info["name"]
        slot = self._slots.get(name)
        if slot is None:
            raise web.HTTPNotFound(text=f"unknown stream {name!r}")
        bgr = slot.get() or _no_signal_frame()
        ok, jpeg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            raise web.HTTPInternalServerError(text="encode failed")
        return web.Response(body=jpeg.tobytes(), content_type="image/jpeg")

    async def close(self) -> None:
        await asyncio.gather(*(pc.close() for pc in self._peers), return_exceptions=True)
        self._peers.clear()


def build_app(slots: dict[str, FrameSlot]) -> tuple[web.Application, StreamerApp]:
    streamer = StreamerApp(slots)
    app = web.Application()
    app.router.add_post("/stream/{name}/offer", streamer.offer)
    app.router.add_get("/stream/{name}.mjpeg", streamer.mjpeg)
    app.router.add_get("/stream/{name}/snapshot", streamer.snapshot)
    app.router.add_get("/healthz", lambda _r: web.Response(text="ok"))

    async def _on_shutdown(_app: web.Application) -> None:
        await streamer.close()

    app.on_shutdown.append(_on_shutdown)
    return app, streamer


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _load_streams(path: str) -> tuple[dict[str, FrameSlot], dict[str, str]]:
    with open(path) as fh:
        cfg = yaml.safe_load(fh) or {}
    streams = cfg.get("streams", {})
    slots: dict[str, FrameSlot] = {}
    topics: dict[str, str] = {}
    for name, entry in streams.items():
        framerate = float(entry.get("framerate", 15.0))
        slots[name] = FrameSlot(framerate=framerate)
        topics[name] = entry["topic"]
    return slots, topics


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to streams.yaml")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args, ros_args = parser.parse_known_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    slots, topics = _load_streams(args.config)

    rclpy.init(args=ros_args)
    bridge = CameraBridge(slots, topics)
    ros_thread = threading.Thread(target=_spin_ros, args=(bridge,), daemon=True)
    ros_thread.start()

    app, _ = build_app(slots)
    try:
        web.run_app(app, host=args.host, port=args.port)
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
