# Public API contract — `v1`

> This document is the **public interface** of openbrain-ros. The
> `openkinematics/openbrain-dashboard` repo builds against it and treats
> field-name drift as breakage. Do not change shapes here without bumping
> the version and coordinating the swap in both repos.

## ROS topics

### Publishers (subscribe to these from any client)

| Topic | Type | Notes |
|---|---|---|
| `/camera/front/color/image_raw` | `sensor_msgs/Image` | RGB |
| `/camera/front/color/camera_info` | `sensor_msgs/CameraInfo` | intrinsics |
| `/camera/front/depth/image_rect_raw` | `sensor_msgs/Image` | depth |
| `/camera/front/imu` | `sensor_msgs/Imu` | onboard BMI085 |
| `/camera/back/color/image_raw` | `sensor_msgs/Image` | |
| `/camera/back/color/camera_info` | `sensor_msgs/CameraInfo` | |
| `/camera/back/depth/image_rect_raw` | `sensor_msgs/Image` | |
| `/camera/back/imu` | `sensor_msgs/Imu` | |
| `/scan` | `sensor_msgs/LaserScan` | LiDAR or projected from depth |
| `/odom` | `nav_msgs/Odometry` | |
| `/map` | `nav_msgs/OccupancyGrid` | from RTAB-Map |
| `/robot_description` | `std_msgs/String` | latched URDF |
| `/system/health` | `openbrain_msgs/SystemHealth` | 1 Hz |
| `/missions/status` | `openbrain_msgs/MissionStatus` | 2 Hz |

### Subscribers (publish to these to control the robot)

| Topic | Type | Notes |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | clamped by active speed profile |
| `/goal_pose` | `geometry_msgs/PoseStamped` | feeds Nav2 |

## ROS services

| Service | Request | Response | What |
|---|---|---|---|
| `/missions/load` | `openbrain_msgs/srv/LoadMission` | `{success, message}` | Load N waypoints + `loop` flag |
| `/missions/start` | `std_srvs/Trigger` | `{success, message}` | Start the loaded mission |
| `/missions/stop` | `std_srvs/Trigger` | `{success, message}` | Cancel current navigation goal |
| `/teleop/set_speed_profile` | `openbrain_msgs/srv/SetSpeedProfile` | `{success, message, max_linear_velocity, max_angular_velocity}` | profile ∈ `beginner` ‖ `normal` ‖ `insane` |

## Custom message shapes (`openbrain_msgs/`)

```
SystemHealth.msg:
  Header   header
  float32[] cpu_per_core           # 0..100
  float32  cpu_temp_c              # NaN if unavailable
  float32  gpu_percent             # 0..100
  float32  gpu_temp_c              # NaN if unavailable
  uint64   ram_used_bytes
  uint64   ram_total_bytes
  ThermalZone[] thermal_zones      # {name, temp_c}
  PowerRail[]   power_rails        # {name, voltage_v, current_a}
  uint64   uptime_s
  string[] node_names_running

MissionStatus.msg:
  Header   header
  uint8    state                   # IDLE | LOADED | RUNNING | PAUSED |
                                    # SUCCEEDED | FAILED | CANCELED
  string   mission_id
  int32    current_waypoint_index  # -1 if none
  uint32   total_waypoints
  string   message

Waypoint.msg:
  float32 x
  float32 y
  float32 yaw
  string  label
  float32 dwell_seconds

LoadMission.srv:
  Waypoint[] waypoints
  bool       loop
  string     mission_id
  ---
  bool       success
  string     message

SetSpeedProfile.srv:
  string profile               # "beginner" | "normal" | "insane"
  ---
  bool   success
  string message
  float32 max_linear_velocity
  float32 max_angular_velocity
```

## Network interfaces

| Endpoint | Protocol | Purpose |
|---|---|---|
| `:9090` | WebSocket (rosbridge) | Topic/service bridge |
| `:8080/stream/{name}/offer` | WebRTC SDP exchange (POST JSON) | Live video |
| `:8080/stream/{name}.mjpeg` | `multipart/x-mixed-replace` | MJPEG fallback |
| `:8080/stream/{name}/snapshot` | `image/jpeg` | Single still (poster) |
| `:8080/healthz` | `text/plain` | Liveness probe |

Default stream names: `front`, `back`. Add more in
[`openbrain_teleop/config/streams.yaml`](../src/openbrain_teleop/config/streams.yaml).

## Versioning policy

This contract is **`v1`**. Any breaking shape change requires:

1. PR labeled `breaking-change`.
2. Notification to `openkinematics/openbrain-dashboard` maintainers (and a
   companion PR there before the bump merges).
3. Bump to `v2` with a deprecation notice on `v1` for ≥ 2 minor versions.

Adding new fields to existing messages is **not** breaking and does not
require the dance above — rosbridge serializes JSON and the dashboard
ignores unknown keys.
