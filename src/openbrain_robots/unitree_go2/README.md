# openbrain_robots_unitree_go2

Adapter for **Unitree Go2 / Go2-W**. Translates `/cmd_vel` (already
clamped by `openbrain_safety/twist_mux`) into Unitree's high-level
locomotion API and forwards the dog's filtered odometry onto `/odom`.

**Status:** ✅ v0.1 (validated on Go2 EDU).

## What you need

| | |
|---|---|
| Robot | Unitree Go2 or Go2-W |
| Network | Direct ethernet (or USB-Ethernet adapter on the Mini) to the dog's onboard CycloneDDS interface |
| SDK | [`unitree_sdk2py`](https://github.com/unitreerobotics/unitree_sdk2_python) installed on the edge box |
| Edge box | Kinematics Mini, Max, or any Jetson with JetPack 6.2 |

If `unitree_sdk2py` isn't importable the adapter still loads, just in
**dry-run mode** — `/cmd_vel` is read and clamped but not forwarded.
Useful for dashboard development.

## Topics

| Direction | Topic | Type | Notes |
|---|---|---|---|
| sub | `/cmd_vel` | `geometry_msgs/Twist` | clamped by `openbrain_safety` first |
| pub | `/odom` | `nav_msgs/Odometry` | filtered foot-IMU fusion downsampled to 20 Hz |
| pub | `/robot_description` | `std_msgs/String` | latched URDF (set `OPENBRAIN_URDF_PATH`) |

## Services (inherited from `RobotAdapter`)

| Service | Type |
|---|---|
| `/teleop/set_speed_profile` | `openbrain_msgs/srv/SetSpeedProfile` |

## Run

```bash
ros2 launch openbrain_robots_unitree_go2 unitree_go2.launch.py \
    network_interface:=eth0
```

`openbrain_bringup` picks this adapter when
`/etc/openbrain/robot.conf :: robot_type=UNITREE_GO2`.

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `network_interface` | `eth0` | Ethernet interface that talks to the dog's CycloneDDS bus |
| `urdf_path` | `""` | Optional URDF; falls back to `$OPENBRAIN_URDF_PATH` |

## Velocity mapping

Unitree's high-level `Move(vx, vy, omega)` has identical semantics to a
ROS `Twist` (m/s and rad/s in the body frame), so the translation is a
direct copy. The adapter does not touch low-level joint commands.

## Wiring caveats

The Unitree SDK assumes a specific CycloneDDS XML config. The Mini /
Max install scripts already template that file with the right
`network_interface` value. If you're running native, set
`CYCLONEDDS_URI=file:///etc/openbrain/cyclonedds.xml` before launching.

## Status reporting

Battery, mode, and gait status are surfaced through the standard ROS 2
`/diagnostics` topic by `openbrain_diagnostics` — no custom topics here.
