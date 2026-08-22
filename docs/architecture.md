# Architecture

> A guided tour of how data flows through OpenBrain. Read this once when
> you join the project; refer back when adding a new package or
> debugging an issue that crosses package boundaries.

## 30-second mental model

```
   dashboard / CLI / SDK
            │
   rosbridge :9090   video :8080   read-only connector :8090
            │                       │
   ──────── ROS 2 graph ────────────┴────
   safety mux  ◀──  joystick / dashboard / nav / AI
       │
       ▼
   robot adapter ──▶ vendor SDK ──▶ motors
```

Every velocity producer publishes to a **namespaced** topic
(`/safety/cmd_vel/{joystick,dashboard,nav,ai}`). The safety mux
arbitrates by priority + freshness and produces the canonical
`/cmd_vel`. The robot adapter clamps to the active speed profile and
forwards to the vendor SDK.

For learned manipulator skills, `openbrain_connector` is a separate
observability plane. SkillOps exports a lineage-pinned descriptor, the
robot-side edge host combines it with its fail-closed hardware profile, and the
Dashboard reads `GET /v1/status`. The inference server receives observations
and returns action proposals only; it never receives a servo device. Connector
v1 has no command surface, so adding it cannot bypass the existing ROS safety
path.

## Layered package map

```
                ┌─────────────── operator surfaces ───────────────┐
                │  openbrain_cli   │  openbrain-dashboard repo    │
                └──────────┬───────┴──────────────┬───────────────┘
                           │                      │
                  ws :9090 (rosbridge)    HTTP :8080 (video streamer)
                           │                      │
       ┌───────────────────┴──────────────────────┴──────────────────────┐
       │                       openbrain_teleop                          │
       └──────────────────────────────┬──────────────────────────────────┘
                                      │
   ┌──────────────────┬───────────────┼──────────────┬─────────────────┐
   │                  │               │              │                 │
   ▼                  ▼               ▼              ▼                 ▼
openbrain_demos  openbrain_safety  openbrain_nav  openbrain_slam  openbrain_diagnostics
(missions, ...)  (twist_mux,        (Nav2 + BT)   (RTAB-Map)        (/diagnostics)
                  estop,
                  watchdog)
                       │                  │              │
                       │                  ▼              ▼
                       │          /safety/cmd_vel/nav  /map
                       │                  │
                       ▼                  ▼
                 ┌────────────────────────────────┐
                 │        openbrain_robots        │  ◀── openbrain_msgs (contracts)
                 │  generic / go2 / g1 / tita     │
                 └────────────┬───────────────────┘
                              │
                              ▼
                       vendor SDK / robot
```

## Velocity flow

The most important data path. **Nothing should publish to `/cmd_vel`
directly** — every producer goes through the safety mux.

```
joystick (LB held)        dashboard joystick           Nav2 controller         AI policy
        │                        │                            │                     │
   /safety/cmd_vel/joystick  /safety/cmd_vel/dashboard  /safety/cmd_vel/nav   /safety/cmd_vel/ai
   prio 100, t/o 0.5s       prio 80, t/o 0.5s          prio 50, t/o 1.0s     prio 30, t/o 1.0s
        └────────────────────────┴────────────────────────────┴─────────────────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │   twist_mux     │  /safety/estop (Bool, latched)
                                        │   (50 Hz)       │  ────────────► hard zero
                                        └────────┬────────┘
                                                 │
                                            /cmd_vel
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  RobotAdapter   │  /teleop/set_speed_profile
                                        │  clamp + send   │  ◀── (beginner|normal|insane)
                                        └────────┬────────┘
                                                 │
                                            vendor SDK
```

**Priority rationale.** Joystick > dashboard > nav > AI. A physical
gamepad held by a human in the loop overrides anything coming over the
network. The dashboard joystick (operator at a distance) overrides
autonomy. Nav2 overrides AI policies because Nav2 has the costmap and
collision avoidance.

**Watchdog rationale.** A source that hasn't published within its
`timeout_s` is treated as silent. If every source goes silent, the mux
publishes zero — the robot stops. There is **no coast-on-disconnect**.

## Map flow

```
front camera (RealSense)
   /camera/front/color/image_raw
   /camera/front/depth/image_rect_raw
              │
              ▼
        openbrain_slam (RTAB-Map)
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
  /map     map→odom    /maps/openbrain.db
  (1 Hz)    (TF)       (persisted)
              │
              ▼
        openbrain_nav (Nav2)
              │
              ▼
   /safety/cmd_vel/nav  ──▶ twist_mux  ──▶ /cmd_vel
```

`/maps/openbrain.db` is the persistent SLAM database. The Docker
volume mount ensures it survives container restarts. Nav2's costmap
layer subscribes to `/map` and `/scan`; if you have a real LiDAR (Max
payload), `/scan` comes from `openbrain_drivers_livox` instead of the
RGB-D depth projection.

## Video flow

Dashboard expects video over HTTP, **not** ROS:

```
RealSense or sim
  /camera/{front,back}/color/image_raw   (sensor_msgs/Image)
              │
              ▼
   openbrain_teleop / video_streamer
   (subscribes to ROS topics, keeps a single-frame slot per camera)
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
WebRTC    MJPEG       single JPEG
POST      GET         GET
/stream/  /stream/    /stream/
{name}/   {name}      {name}/
offer    .mjpeg       snapshot
```

WebRTC is preferred — same bandwidth, lower latency. MJPEG is a
fallback for symmetric-NAT and older browsers. Snapshot is for the
dashboard's poster image and SEO previews.

## Mission flow

```
dashboard mission planner
   POST /missions/load (JSON: waypoints, loop)
              │
              ▼
   openbrain_demos_missions
   • parses + validates waypoints
   • holds the FSM (IDLE → LOADED → RUNNING → ...)
   • drives Nav2 via navigate_to_pose (action client)
              │
   ┌──────────┴──────────┐
   ▼                     ▼
 Nav2's NavigateToPose   /missions/status (2 Hz, every transition)
 action server           ◀── dashboard's mission planner subscribes here
              │
              ▼
       /safety/cmd_vel/nav
              │
              ▼
        twist_mux → /cmd_vel
```

The state machine is intentionally simple — Nav2 owns the hard part
(planning + replanning + recovery). The mission node is just the
orchestrator.

## Health flow

```
host (Jetson or laptop)
              │
              ▼
   openbrain_demos_health
   (polls jtop or psutil at 1 Hz)
              │
              ▼
   /system/health (openbrain_msgs/SystemHealth)
              │
              ▼
   dashboard's Health page
```

Plus a parallel `/diagnostics` channel from `openbrain_diagnostics`
(every 5 s, broader self-test: cameras, GPU, network, ROS env, …).
The dashboard's Diagnostics tab and `rqt_robot_monitor` both consume
the standard `diagnostic_msgs/DiagnosticArray` shape.

## Bringup composition

`openbrain_bringup/launch/mini.launch.py` is the conductor:

```
mini.launch.py
   ├── openbrain_drivers_realsense       (cameras)
   ├── openbrain_slam                    (RTAB-Map)
   ├── openbrain_nav                     (Nav2 + BT)
   ├── openbrain_safety                  (twist_mux + estop)
   ├── openbrain_teleop                  (rosbridge + streamer)
   └── robot adapter   ◀── chosen by _robot_type.detect_robot_type()
       ├── generic   (default)
       ├── unitree_go2
       ├── unitree_g1
       └── tita
```

`max.launch.py` is a superset — same as `mini.launch.py` plus
opt-in payload drivers (LiDAR, industrial IMU, thermal, mmWave, 5G).
Each payload is gated on a launch argument, so a Max box without the
payload still launches cleanly.

## Failure modes (and what catches them)

| Failure | What detects it | Reaction |
|---|---|---|
| Camera unplugged | `openbrain_drivers_realsense` IfCondition skip on empty serial | Launch continues; `/diagnostics` reports it |
| All velocity sources silent | `twist_mux` watchdog timeout | Publishes zero on `/cmd_vel` |
| Operator hits e-stop | `estop_node` latches `/safety/estop` | `twist_mux` publishes zero |
| Nav2 action server down | `missions_node._send_next_goal` `wait_for_server` timeout | Mission FSM transitions to `FAILED` with a clear `/missions/status.message` |
| GPU overheats | `openbrain_diagnostics.check_thermal` | `/diagnostics` WARN at 75 °C, ERROR at 85 °C |
| Disk full | `openbrain_diagnostics.check_disk_space` | WARN under 5 GB, ERROR under 1 GB |
| Connection lost mid-mission | dashboard reconnect logic + rosbridge auto-reconnect | Mission keeps running; status is replayed when client reconnects |

## Where to read next

- [`api.md`](api.md) — the public ROS contract (topics, services, message shapes)
- [`edge-runtime-status.md`](edge-runtime-status.md) — SkillOps, edge host, inference, and Dashboard integration
- [`installation.md`](installation.md) — install on Jetson, laptop, or from source
- [`supported-robots.md`](supported-robots.md) — adapter status matrix
- [`troubleshooting.md`](troubleshooting.md) — common pitfalls
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — adding demos, robots, drivers
