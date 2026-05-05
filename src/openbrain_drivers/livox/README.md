# openbrain_drivers_livox

Wraps the Livox SDK 2 driver for the **Livox Mid-360** spinning solid-state
LiDAR shipped on the Kinematics Max payload bay.

**Status:** 🔴 Phase 3 (`launch/livox_mid360.launch.py` is a stub).

## Will publish

| Topic | Type |
|---|---|
| `/lidar/livox/points` | `sensor_msgs/PointCloud2` |
| `/lidar/livox/imu` | `sensor_msgs/Imu` |

## What's needed to make this work

**Hardware** — Livox Mid-360 LiDAR (≈ $850), 24V DC supply, gigabit ethernet to the host. Mount per the Mid-360 datasheet (rotation axis vertical, no metal within 50 mm of the dome).

**Software dependencies**

- [`Livox-SDK/Livox-SDK2`](https://github.com/Livox-SDK/Livox-SDK2) — C++ SDK (BSD-3)
- [`Livox-SDK/livox_ros_driver2`](https://github.com/Livox-SDK/livox_ros_driver2) — ROS 2 wrapper
- A static IP for the LiDAR (default 192.168.1.1xx); the host needs a NIC on the same /24

**Steps to ship this driver**

1. Build Livox-SDK2 from source: `cmake .. && make && sudo make install`.
2. Build livox_ros_driver2 in this workspace (clone into `src/livox_ros_driver2`, then `colcon build`).
3. Edit `MID360_config.json` with the LiDAR's IP + your NIC's IP.
4. Replace the TODO launch with `IncludeLaunchDescription` of `livox_ros_driver2`'s `msg_MID360_launch.py`, remapped to `/lidar/livox/{points,imu}`

**Estimated effort:** Small (≈ 3–5 days). Mostly NIC config + launch composition.
## Upstream

[`Livox-SDK/livox_ros_driver2`](https://github.com/Livox-SDK/livox_ros_driver2) (BSD-3).

