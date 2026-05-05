# openbrain_drivers_xsens

Wraps the Xsens MTi ROS 2 driver for the **MTi-630** (industrial AHRS) and
**MTi-680G** (RTK GNSS/INS) IMUs available as Max payloads.

**Status:** 🔴 Phase 3.

## Will publish

| Topic | Type |
|---|---|
| `/imu/xsens/data` | `sensor_msgs/Imu` |
| `/imu/xsens/mag` | `sensor_msgs/MagneticField` |
| `/imu/xsens/gnss` | `sensor_msgs/NavSatFix` *(680G only)* |

## What's needed to make this work

**Hardware** — Xsens MTi-630 (industrial AHRS, ≈ $1.5k) or MTi-680G (RTK GNSS/INS, ≈ $4k). USB or RS-232 serial.

**Software dependencies**

- [`xsens/xsens_mti_ros2_driver`](https://github.com/xsens/xsens_mti_ros2_driver) — vendor BSD
- udev rule for `/dev/ttyUSB_xsens` (template in upstream README)

**Steps to ship this driver**

1. Plug in the IMU; verify enumeration with `ls /dev/ttyUSB*`.
2. Install the udev rule (`sudo cp 99-xsens.rules /etc/udev/rules.d/`).
3. Build the driver in this workspace.
4. Replace the TODO launch with the driver's `xsens_mti_node` launch, configured for your model (MTi-630 vs 680G changes the topic set)

**Estimated effort:** Small (≈ 2 days). Vendor driver is well-maintained.
## Upstream

[Xsens MTi ROS 2 driver](https://github.com/xsens/xsens_mti_ros2_driver) (vendor BSD).

