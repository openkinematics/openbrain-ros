# missions

> Mission state-machine. Loads an ordered list of waypoints, drives each
> one with Nav2's `navigate_to_pose` action, optionally loops, publishes
> live status. The dashboard's mission planner is the primary client.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max. Requires `openbrain_nav` (Nav2) to be
running so `navigate_to_pose` is reachable. Without Nav2 the node still
loads but `start` returns `success: false` with a clear message.

## Category

Navigation.

## ROS services

| Service | Type | What |
|---|---|---|
| `/missions/load` | `openbrain_msgs/srv/LoadMission` | Load N waypoints + `loop` flag |
| `/missions/start` | `std_srvs/srv/Trigger` | Begin executing |
| `/missions/stop` | `std_srvs/srv/Trigger` | Cancel current goal |

## ROS topics

| Direction | Topic | Type | Rate |
|---|---|---|---|
| pub | `/missions/status` | `openbrain_msgs/MissionStatus` | 2 Hz |

State enum on `MissionStatus.state`:
`IDLE | LOADED | RUNNING | PAUSED | SUCCEEDED | FAILED | CANCELED`.

## Run

```bash
ros2 launch openbrain_demos_missions missions.launch.py
```

The node depends on Nav2's `navigate_to_pose` action server, so make
sure `openbrain_nav` is up first (or use
[`cockpit.launch.py`](../cockpit/launch/cockpit.launch.py) which brings
up both).

## Mission JSON example

```json
[
  {"x": 1.0,  "y": 0.0, "yaw": 0.0,    "label": "kitchen", "dwell_seconds": 2.0},
  {"x": 1.0,  "y": 1.5, "yaw": 1.5708, "label": "loading", "dwell_seconds": 5.0},
  {"x": 0.0,  "y": 0.0, "yaw": 3.1416, "label": "home"}
]
```

A worked example lives at
[`examples/missions/patrol.json`](../../../examples/missions/patrol.json).

## Dashboard integration

The dashboard sends a `LoadMissionRequest` shaped exactly as the
service expects (`waypoints: [{x, y, yaw}], loop: bool`), so no
translation layer needed.

## Tests

[`test/test_waypoint_conversion.py`](test/test_waypoint_conversion.py)
exercises yaw → quaternion and frame_id handling. The state-machine
transitions are covered by the parts that don't need a live Nav2
action server (load + start-without-server).

## Related demos

- [`cockpit`](../cockpit) — brings up Nav2 + missions in one shot
- [`quadruped-patrol`](../quadruped-patrol) — extension with battery-aware return-to-charger
