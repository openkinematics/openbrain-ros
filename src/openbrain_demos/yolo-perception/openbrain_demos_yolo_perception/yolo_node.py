"""YOLO object detector node.

Subscribes to a camera image topic, runs Ultralytics inference, publishes
``vision_msgs/Detection2DArray`` and (optionally) an annotated overlay
image that the dashboard's CockPit page can subscribe to as a second
camera tile.

The Ultralytics weight file is loaded from ``model_path``. If the file
doesn't exist on disk, Ultralytics will download the standard COCO
weights (``yolo11n.pt`` by default) into the same path on first run —
so a fresh install just works on any host with internet.

Inference backend is auto-selected (CUDA / CPU). On Jetson the
``imgsz`` parameter trades latency for accuracy: 640×640 sustains
~30 fps on Orin Nano, ~120 fps on T5000. On the AGX Orin the optional
``half`` parameter switches to FP16.

Topics
------
sub  ``/camera/<source>/color/image_raw``   ``sensor_msgs/Image``
pub  ``/perception/yolo/detections``        ``vision_msgs/Detection2DArray``
pub  ``/perception/yolo/overlay``           ``sensor_msgs/Image`` (optional)

Parameters
----------
``model_path``       (str)   path to a Ultralytics .pt or .engine file.
``source``           (str)   camera namespace (default ``front``).
``score_threshold``  (float) drop detections below this confidence.
``imgsz``            (int)   inference resolution (default 640).
``half``             (bool)  FP16 inference (T5000 / AGX Orin).
``publish_overlay``  (bool)  publish the annotated image alongside detections.
``device``           (str)   ``cpu`` ‖ ``cuda:0`` ‖ ``""`` for auto-select.
"""

from __future__ import annotations

import sys
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

from openbrain_demos_yolo_perception.detections import Detection, color_for_class, postprocess


class YoloNode(Node):
    DEFAULT_MODEL = "yolo11n.pt"

    def __init__(self) -> None:
        super().__init__("openbrain_yolo")

        self.declare_parameter("model_path", self.DEFAULT_MODEL)
        self.declare_parameter("source", "front")
        self.declare_parameter("score_threshold", 0.25)
        self.declare_parameter("imgsz", 640)
        self.declare_parameter("half", False)
        self.declare_parameter("publish_overlay", True)
        self.declare_parameter("device", "")

        self._bridge = CvBridge()
        self._model = None  # lazy: we only need ultralytics on the inference path

        # Best-effort QoS to keep up with the camera without backpressuring it.
        qos = QoSProfile(depth=1, reliability=QoSReliabilityPolicy.BEST_EFFORT)

        source = self.get_parameter("source").get_parameter_value().string_value
        in_topic = f"/camera/{source}/color/image_raw"
        self._sub = self.create_subscription(Image, in_topic, self._on_frame, qos)

        self._det_pub = self.create_publisher(Detection2DArray, "/perception/yolo/detections", 10)
        self._overlay_pub = (
            self.create_publisher(Image, "/perception/yolo/overlay", 10)
            if self._p_bool("publish_overlay")
            else None
        )

        self._infer_count = 0
        self._infer_total_ms = 0.0
        self.create_timer(5.0, self._log_stats)

        self.get_logger().info(
            f"yolo_node ready — subscribing {in_topic}, "
            f"model={self._p_str('model_path')!r}, imgsz={self._p_int('imgsz')}"
        )

    # ---- inference path ----------------------------------------------

    def _on_frame(self, msg: Image) -> None:
        try:
            bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # pragma: no cover - defensive
            self.get_logger().warn(f"bridge failed: {exc}")
            return

        model = self._ensure_model()
        if model is None:
            return

        t0 = time.monotonic()
        try:
            results = model.predict(
                source=bgr,
                imgsz=self._p_int("imgsz"),
                conf=self._p_float("score_threshold"),
                half=self._p_bool("half"),
                device=self._p_str("device") or None,
                verbose=False,
            )
        except Exception as exc:  # pragma: no cover - inference path
            self.get_logger().error(f"inference failed: {exc}")
            return
        ms = (time.monotonic() - t0) * 1000.0
        self._infer_count += 1
        self._infer_total_ms += ms

        if not results:
            return
        result = results[0]
        names = getattr(model, "names", {}) or {}
        boxes_xywh = result.boxes.xywh.cpu().numpy() if hasattr(result.boxes, "xywh") else []
        scores = result.boxes.conf.cpu().numpy() if hasattr(result.boxes, "conf") else []
        class_ids = result.boxes.cls.cpu().numpy() if hasattr(result.boxes, "cls") else []

        dets = postprocess(
            boxes_xywh,
            scores,
            class_ids,
            names if isinstance(names, dict) else dict(enumerate(names)),
            score_threshold=self._p_float("score_threshold"),
        )
        self._publish_detections(dets, msg.header.frame_id, msg.header.stamp)
        if self._overlay_pub is not None:
            self._publish_overlay(bgr, dets, msg.header)

    def _publish_detections(self, dets: list[Detection], frame_id: str, stamp) -> None:
        out = Detection2DArray()
        out.header.stamp = stamp
        out.header.frame_id = frame_id
        for d in dets:
            det = Detection2D()
            det.header = out.header
            det.bbox.center.position.x = d.cx
            det.bbox.center.position.y = d.cy
            det.bbox.size_x = d.w
            det.bbox.size_y = d.h
            hyp = ObjectHypothesisWithPose()
            hyp.hypothesis.class_id = d.label
            hyp.hypothesis.score = d.score
            det.results.append(hyp)
            out.detections.append(det)
        self._det_pub.publish(out)

    def _publish_overlay(self, bgr, dets: list[Detection], header) -> None:
        canvas = bgr.copy()
        for d in dets:
            x = int(d.cx - d.w / 2)
            y = int(d.cy - d.h / 2)
            x2 = int(d.cx + d.w / 2)
            y2 = int(d.cy + d.h / 2)
            color = color_for_class(d.label_id)
            cv2.rectangle(canvas, (x, y), (x2, y2), color, 2)
            label = f"{d.label} {d.score:.2f}"
            cv2.putText(canvas, label, (x, max(15, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        out = self._bridge.cv2_to_imgmsg(canvas, encoding="bgr8")
        out.header = header
        self._overlay_pub.publish(out)

    # ---- model loading -----------------------------------------------

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        try:
            from ultralytics import YOLO
        except ImportError:
            self.get_logger().error(
                "ultralytics not installed — install with `pip install ultralytics`. "
                "Detector is idle until then."
            )
            self._model = False
            return None
        path = self._p_str("model_path") or self.DEFAULT_MODEL
        try:
            self._model = YOLO(path)
            self.get_logger().info(f"loaded model {path}")
        except Exception as exc:  # pragma: no cover - load path
            self.get_logger().error(f"failed to load model {path!r}: {exc}")
            self._model = False
            return None
        return self._model

    # ---- diagnostics --------------------------------------------------

    def _log_stats(self) -> None:
        if not self._infer_count:
            return
        avg_ms = self._infer_total_ms / self._infer_count
        fps = 1000.0 / avg_ms if avg_ms > 0 else 0.0
        self.get_logger().info(
            f"yolo: {self._infer_count} frames, avg {avg_ms:.1f} ms ({fps:.1f} fps)"
        )
        self._infer_count = 0
        self._infer_total_ms = 0.0

    # ---- param helpers -----------------------------------------------

    def _p_str(self, name: str) -> str:
        return self.get_parameter(name).get_parameter_value().string_value

    def _p_int(self, name: str) -> int:
        return self.get_parameter(name).get_parameter_value().integer_value

    def _p_float(self, name: str) -> float:
        return self.get_parameter(name).get_parameter_value().double_value

    def _p_bool(self, name: str) -> bool:
        return self.get_parameter(name).get_parameter_value().bool_value


def main(argv: list[str] | None = None) -> None:
    rclpy.init(args=argv if argv is not None else sys.argv)
    node = YoloNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
