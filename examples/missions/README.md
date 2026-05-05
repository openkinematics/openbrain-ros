# examples/missions

Mission JSON files. Load them with the CLI:

```bash
ros2 service call /missions/load openbrain_msgs/srv/LoadMission \
    "$(jq -c '{waypoints: ., loop: false, mission_id: \"patrol-1\"}' \
       examples/missions/patrol.json)"

ros2 service call /missions/start std_srvs/srv/Trigger
```

Or from a Python client — see [`load_mission.py`](./load_mission.py).

## Index

| File | Description |
|---|---|
| [`patrol.json`](./patrol.json) | Three-waypoint loop around the OpenBrain demo lab — kitchen → loading → home |
| [`square.json`](./square.json) | 1 m × 1 m square at origin, useful for a quick Nav2 sanity check |
| [`load_mission.py`](./load_mission.py) | Python client that calls `/missions/load` then `/missions/start` |

## Mission JSON schema

```json
[
  {
    "x": 1.0,                    // meters in /map frame
    "y": 0.0,
    "yaw": 0.0,                  // radians, CCW from +X
    "label": "kitchen",          // optional, free text
    "dwell_seconds": 2.0         // optional, default 0
  }
]
```

Fields not in the schema are ignored. The waypoint count is bounded
only by what Nav2's BT can plan through (we have not seen a problem
under 100 waypoints).
