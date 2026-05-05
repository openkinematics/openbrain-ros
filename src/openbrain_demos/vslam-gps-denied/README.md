# vslam-gps-denied

> RTAB-Map RGB-D + IMU configuration tuned for GPS-denied environments —
> warehouses, basements, indoor drone flight. The robot computes its
> own visual-inertial odometry from the front camera + its IMU, with
> tighter loop-closure thresholds for repetitive corridors.

**Status:** 🟢 Phase 1 — full implementation (configuration profile +
launch composition over `openbrain_slam`'s building blocks).

## Hardware

Either Kinematics Mini or Max. Requires the front RealSense D435i
(depth + IMU). The back camera is optional but the dashboard will be
quiet on `/camera/back/*` if it's not present.

## Category

Navigation.

## What's different

This isn't a fork of `openbrain_slam` — it's a config + launch overlay
on the same RTAB-Map binary. The differences vs. the default profile:

| Setting | Default profile | This profile | Why |
|---|---|---|---|
| `subscribe_imu` | false | **true** | The IMU is the input that makes VIO possible |
| `subscribe_odom_info` | false | **true** | RTAB-Map produces its own /odom; no wheel encoders required |
| `Reg/Strategy` | 1 (ICP) | **2 (Vis+ICP)** | Visual features anchor the alignment; ICP refines geometry |
| `Mem/STMSize` | 10 | **30** | Longer short-term memory → more loop-closure candidates on revisits |
| `Vis/MinInliers` | 20 | **25** | Stricter loop closures → fewer false positives in repetitive aisles |
| `Mem/UseOdomFeatures` | true | **false** | Don't bias the matcher with potentially-bad odom guesses |
| `Reg/Force3DoF` | true | **false** | Default supports 6DoF (drones); flip via launch arg for ground robots |
| `database_path` | `/maps/openbrain.db` | `/maps/openbrain_vslam.db` | Don't clobber the default-profile map |

The RTAB-Map binary is unchanged; only YAML and remappings differ.

## Topics

| Direction | Topic | Type |
|---|---|---|
| sub | `/camera/front/color/image_raw` | `sensor_msgs/Image` |
| sub | `/camera/front/color/camera_info` | `sensor_msgs/CameraInfo` |
| sub | `/camera/front/depth/image_rect_raw` | `sensor_msgs/Image` |
| sub | `/camera/front/imu` | `sensor_msgs/Imu` |
| pub | `/map` | `nav_msgs/OccupancyGrid` |
| pub | `/odom` | `nav_msgs/Odometry` (from VIO) |
| pub | `tf: map -> odom` | TF |

## Run

For an indoor mobile robot (3DoF, default):

```bash
ros2 launch openbrain_demos_vslam_gps_denied vslam.launch.py force_3dof:=true
```

For an indoor drone (6DoF):

```bash
ros2 launch openbrain_demos_vslam_gps_denied vslam.launch.py
```

The map persists at `/maps/openbrain_vslam.db` — mount that path as a
Docker volume so it survives container restarts (the default
`docker/docker-compose.yml` already does this for `/maps`).

## Tests

[`test/test_config.py`](test/test_config.py) pins the four key
divergences from the base profile (`subscribe_imu`,
`subscribe_odom_info`, `Reg/Strategy`, separate DB path). If any of
those drift, CI catches it before the demo ships broken.

## Reference

- [`introlab/rtabmap_ros`](https://github.com/introlab/rtabmap_ros) (BSD-3)
- RTAB-Map's [VIO tutorial](https://github.com/introlab/rtabmap/wiki/Visual-Inertial-Odometry-(VIO))
- Inspired by indoor-drone navigation patterns from the OpenVINO and
  ORB-SLAM3 communities.

## Related demos

- [`quadruped-patrol`](../quadruped-patrol) — pairs nicely on Go2 in
  warehouse / basement settings
- [`nvblox-mapping`](../nvblox-mapping) — when you want full 3D
  obstacle volumes instead of an occupancy grid
