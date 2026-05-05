# openbrain_perception

> Top-level perception entry points. YOLO has a real implementation
> (delegated to [`openbrain_demos_yolo_perception`](../openbrain_demos/yolo-perception));
> NVBlox is scaffolded for Phase 2.

## Components

| Component | Status | Purpose |
|---|---|---|
| `yolo` | 🟢 v0.1 | YOLOv11/Ultralytics object detector. Publishes `vision_msgs/Detection2DArray` on `/perception/yolo/detections` and an annotated overlay on `/perception/yolo/overlay`. Real implementation lives in [`openbrain_demos_yolo_perception`](../openbrain_demos/yolo-perception); this launch is a thin include. |
| `nvblox` | 🟡 Phase 2 | NVBlox 3D-mapping bridge. Will publish TSDF/ESDF/mesh on `/perception/nvblox/*`. **What's needed to graduate it** — see [`nvblox-mapping`](../openbrain_demos/nvblox-mapping/README.md#whats-needed-to-make-this-work) for the hardware list, exact apt packages, and Nav2 wiring steps. |

## Run

```bash
ros2 launch openbrain_perception yolo.launch.py
ros2 launch openbrain_perception nvblox.launch.py        # phase-2 stub
```

The YOLO launch forwards every parameter the demo accepts (`model_path`,
`source`, `score_threshold`, `imgsz`, `half`, `publish_overlay`,
`device`) — see
[`openbrain_demos_yolo_perception`'s README](../openbrain_demos/yolo-perception/README.md)
for the full list and Jetson-class FPS reference points.

## Upstream

* [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics) (AGPL-3.0)
* [NVIDIA Isaac ROS NVBlox](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox) (Apache-2.0)
