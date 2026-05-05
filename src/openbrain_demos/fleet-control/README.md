# fleet-control

> Multi-robot fleet aggregator. Subscribes to `/system/health` and
> `/missions/status` for each robot in the fleet (over a shared DDS
> domain) and publishes one consolidated `/fleet/snapshot` JSON the
> dashboard's Fleet page renders as a live table.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Runs on any host that can reach the robots' DDS multicast — typically a
Kinematics Max (the fleet operator console) or a workstation in the same
LAN as the fleet. Mini works too if the fleet is small.

## Category

Fleet.

## How it works

Each robot in the fleet publishes its standard topics under a unique
namespace on a shared DDS domain:

```
/r01/system/health      /r01/missions/status
/r02/system/health      /r02/missions/status
/r03/system/health      /r03/missions/status
```

The fleet node reads its `robots:` list from the YAML config, wires up
one subscription per namespace, and republishes a consolidated
snapshot every second:

| Direction | Topic | Type |
|---|---|---|
| pub | `/fleet/snapshot` | `std_msgs/String` (JSON, latched) |
| pub | `/fleet/online_count` | `std_msgs/UInt32` |
| pub | `/fleet/total_count` | `std_msgs/UInt32` |
| sub | `/<robot_id>/system/health` | `openbrain_msgs/SystemHealth` |
| sub | `/<robot_id>/missions/status` | `openbrain_msgs/MissionStatus` |

A robot is marked **offline** if it hasn't published a fresh
`/system/health` within `heartbeat_timeout_s` (default 5 s). When it
publishes again it flips back to online — the dashboard's table updates
in place.

## Snapshot JSON shape

```json
{
  "generated_unix": 1746409600.123,
  "online_count": 2,
  "total_count": 3,
  "robots": [
    {
      "robot_id": "r01",
      "last_seen_unix": 1746409599.880,
      "online": true,
      "cpu_percent_avg": 18.4,
      "cpu_temp_c": 56.0,
      "gpu_percent": 72.0,
      "gpu_temp_c": 61.0,
      "ram_used_bytes": 2147483648,
      "ram_total_bytes": 8589934592,
      "mission_state": 2,
      "mission_id": "patrol-1",
      "mission_progress": [3, 10]
    },
    ...
  ]
}
```

NaN values (typical for `cpu_temp_c` on hosts without thermal sensors)
are coerced to JSON `null` so the dashboard's parser doesn't choke.

## Run

Edit [`config/default.yaml`](config/default.yaml) to list your robot
namespaces, then:

```bash
ros2 launch openbrain_demos_fleet_control fleet.launch.py
ros2 topic echo /fleet/snapshot --once
```

For a single-robot test (subscribes to bare `/system/health`):

```bash
ros2 launch openbrain_demos_fleet_control fleet.launch.py \
    --ros-args -p robots:='[""]'
```

## Tests

[`test/test_aggregator.py`](test/test_aggregator.py) covers heartbeat
freshness logic (online → offline → online), CPU-mean computation,
sorted snapshot output, NaN scrubbing for JSON, and the empty-CPU
edge case. The clock is injected for deterministic time-based tests.

## Phase-2 plans

`/fleet/dispatch` will broadcast a `LoadMission` to a selected subset
of the fleet (by tag, by role, or all). Today the dashboard fans out
per-robot service calls instead — workable but slower for large
fleets.

## Related demos

- [`missions`](../missions) — what each robot in the fleet runs
- [`health`](../health) — what each robot publishes for the aggregator to read
- [`profile`](../profile) — fleet operator's own preferences
