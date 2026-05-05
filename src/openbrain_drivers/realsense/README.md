# openbrain_drivers_realsense

Launch + config for the Intel RealSense D435i (and D456) used as the
front/back depth camera pair on the Kinematics Mini and Max boxes.

## Topics produced

Per-camera namespace `/camera/{front,back}/`:

| Topic | Type |
|---|---|
| `color/image_raw` | `sensor_msgs/Image` |
| `depth/image_rect_raw` | `sensor_msgs/Image` |
| `imu` | `sensor_msgs/Imu` |
| `color/camera_info` | `sensor_msgs/CameraInfo` |
| `depth/camera_info` | `sensor_msgs/CameraInfo` |

Frames published: `{name}_link`, `{name}_color_optical_frame`,
`{name}_depth_optical_frame`.

## Usage

```bash
ros2 launch openbrain_drivers_realsense dual_d435i.launch.py \
    front_serial:=123456789 back_serial:=987654321
```

Serials live in `config/mini.yaml` / `config/max.yaml` at the workspace root —
the bringup layer reads them and forwards.

## Upstream

Wraps [`realsense2_camera`](https://github.com/IntelRealSense/realsense-ros)
(Apache-2.0). Requires Intel RealSense SDK 2.55+ on the host.
