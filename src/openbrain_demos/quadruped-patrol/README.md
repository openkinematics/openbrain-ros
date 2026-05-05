# quadruped-patrol

> Quadruped patrol around a learned waypoint loop with battery-aware
> return-to-charger. Composes
> [`openbrain_demos_missions`](../missions) with a battery monitor that
> interrupts the loop when the cell drops below threshold and dispatches
> a single-waypoint return mission to the charger pose.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max. Designed for a Unitree Go2 / Go2-W (the
robot that has a battery `power_supply_status` of `CHARGING` when on
its dock), but works on any robot publishing
`sensor_msgs/BatteryState` on `/battery/state`.

## Category

Navigation.

## Topics & services

| Direction | Topic / service | Type |
|---|---|---|
| sub | `/battery/state` | `sensor_msgs/BatteryState` |
| sub | `/missions/status` | `openbrain_msgs/MissionStatus` |
| call | `/missions/load` | `openbrain_msgs/srv/LoadMission` |
| call | `/missions/start` | `std_srvs/srv/Trigger` |
| call | `/missions/stop` | `std_srvs/srv/Trigger` |

This demo is a **client** of the missions node — it doesn't expose new
services itself. The dashboard already controls patrol via the existing
mission API.

## Recharge state machine

```
                    ┌─ battery > resume_threshold ──┐
                    │  AND on_charger               │
                    │                                ▼
              ┌────────────┐                ┌──────────────┐
              │  PATROL    │ ──────────────▶│ ON CHARGER   │
              │  (looped)  │  battery <=    │              │
              │            │  low_threshold │              │
              └────────────┘                └──────────────┘
                    ▲                              │
                    │  RESUME (battery >= resume)  │
                    └──────────────────────────────┘
```

Hysteresis matters: `resume_threshold` (default 75%) is far above
`low_threshold` (default 25%) so the robot doesn't bounce between
patrol and dock as it crosses the boundary. There's also a
`critical_threshold` (default 10%) below which the robot returns even
if it wasn't patrolling (operator parked it somewhere awkward).

## Run

```bash
# Bring up the bringup stack first (cockpit / mini.launch.py).
ros2 launch openbrain_demos_quadruped_patrol patrol.launch.py \
    loop_file:=/etc/openbrain/patrol_loop.json \
    low_threshold_pct:=25 \
    resume_threshold_pct:=75
```

Loop-file schema (see [`config/example_loop.json`](config/example_loop.json)):

```json
{
  "loop": [
    {"x": 1.0, "y": 0.0,  "yaw": 0.0, "label": "kitchen", "dwell_seconds": 2.0},
    {"x": 1.0, "y": 1.5,  "yaw": 1.57},
    {"x": 0.0, "y": 0.0,  "yaw": 3.14, "label": "home"}
  ],
  "charger": {"x": -0.5, "y": 0.0, "yaw": 0.0, "label": "charger"}
}
```

## Parameters

| Name | Default | Description |
|---|---|---|
| `loop_file` | `""` | Path to the patrol loop JSON; node is idle if empty |
| `low_threshold_pct` | `25.0` | Below this, abort patrol and return to charger |
| `resume_threshold_pct` | `75.0` | Once on charger and above this, resume patrol |
| `critical_threshold_pct` | `10.0` | Below this, return-to-charger overrides everything |

## Tests

[`test/test_policy.py`](test/test_policy.py) covers the full
state-machine truth table (charged, low, critical, on-charger above /
below resume), the hysteresis guard, and the invalid-threshold
validation that the dataclass enforces.

## Related demos

- [`missions`](../missions) — the underlying state machine this
  composes
- [`vslam-gps-denied`](../vslam-gps-denied) — pairs nicely for indoor
  patrols where GPS isn't available
- [`fleet-control`](../fleet-control) — monitor a fleet of patrolling
  robots from one dashboard
