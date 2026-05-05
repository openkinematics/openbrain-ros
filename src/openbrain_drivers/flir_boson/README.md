# openbrain_drivers_flir_boson

Wraps the FLIR Boson SDK to expose the **Boson 640** thermal camera as
a ROS 2 topic.

**Status:** 🔴 Phase 3.

## Will publish

| Topic | Type |
|---|---|
| `/camera/thermal/image_raw` | `sensor_msgs/Image` (mono16, radiometric) |
| `/camera/thermal/camera_info` | `sensor_msgs/CameraInfo` |

## What's needed to make this work

**Hardware** — FLIR Boson 640 thermal camera (industrial; ≈ $4k). USB-C cable. The camera enumerates as a v4l2 device on Linux.

**Software dependencies**

- FLIR Boson SDK (vendor binary distribution; free download with EULA acceptance from flir.com)
- `v4l-utils` for fallback raw capture
- Optional: GStreamer for hardware-accelerated MJPEG

**Steps to ship this driver**

1. Download the FLIR Boson SDK + EULA.
2. Install the SDK to `/opt/flir-boson-sdk/`.
3. Set the udev rule so the camera is owned by the `video` group.
4. Write a node that opens the v4l2 device, applies radiometric calibration, and publishes `mono16` on `/camera/thermal/image_raw`

**Estimated effort:** Medium (≈ 2 weeks). Radiometric calibration + OpenCV palette mapping is the bulk of the work.
## Upstream

[FLIR Boson SDK](https://www.flir.com/products/boson/) (vendor EULA, free
binary distribution).

