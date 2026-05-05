# yolo-perception

> YOLO object detector running against the front camera. Uses
> Ultralytics for inference (auto-selects CPU / CUDA / TensorRT) and
> publishes `vision_msgs/Detection2DArray` plus an annotated overlay
> image the dashboard's CockPit can render as a second camera tile.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max. Performance reference points (640×640,
INT8 where available):

| Box | FPS |
|---|---|
| Kinematics Mini (Orin Nano 8 GB) | ~25–30 |
| Kinematics Max — T4000 64 GB | ~55–70 |
| Kinematics Max — T5000 128 GB (FP16) | ~110–130 |
| Kinematics Max — AGX Orin 64 GB | ~35–45 |

Switch to a `.engine` (TensorRT) model file to get the upper end of
each range; `ultralytics` exports them with `yolo export format=engine`.

## Category

Perception.

## Topics

| Direction | Topic | Type |
|---|---|---|
| sub | `/camera/<source>/color/image_raw` | `sensor_msgs/Image` |
| pub | `/perception/yolo/detections` | `vision_msgs/Detection2DArray` |
| pub | `/perception/yolo/overlay` | `sensor_msgs/Image` (optional) |

`<source>` is the `source` parameter — defaults to `front`.

## Run

```bash
ros2 launch openbrain_demos_yolo_perception yolo.launch.py
```

First launch downloads `yolo11n.pt` (~5 MB COCO weights) into the
working directory. To use a custom model:

```bash
ros2 launch openbrain_demos_yolo_perception yolo.launch.py \
    model_path:=/opt/openbrain/models/my-custom.engine \
    half:=true device:=cuda:0
```

## Parameters

| Name | Default | Description |
|---|---|---|
| `model_path` | `yolo11n.pt` | Path to a `.pt` or `.engine` Ultralytics model |
| `source` | `front` | Camera namespace |
| `score_threshold` | `0.25` | Drop detections below this confidence |
| `imgsz` | `640` | Inference resolution (square) |
| `half` | `false` | FP16 inference (T5000 / AGX Orin) |
| `publish_overlay` | `true` | Publish the annotated image |
| `device` | `""` | `""` auto, `cpu`, or `cuda:0` |

## Tests

[`test/test_postprocess.py`](test/test_postprocess.py) covers the
threshold filter, score sort, label fallback, max-results clamp, and
the color-per-class hash. The inference loop itself is exercised on
hardware; the post-processing path that turns model output into
`Detection2DArray` is the part that drifts most often, so it gets
direct unit coverage.

## Upstream

- [`ultralytics/ultralytics`](https://github.com/ultralytics/ultralytics) (AGPL-3.0)
- [`vision_msgs`](https://github.com/ros-perception/vision_msgs) (Apache-2.0)

## Related demos

- [`nvblox-mapping`](../nvblox-mapping) — pairs detections with depth for 3D positions
- [`warehouse-pick`](../warehouse-pick) — uses these detections as the perception input
