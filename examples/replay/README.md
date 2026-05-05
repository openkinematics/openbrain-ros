# examples/replay

Record and replay sessions with rosbag2.

## Record from the CLI

```bash
openbrain record    # starts a bag in /recordings/<UTC-timestamp>/
# ... drive around ...
openbrain stop      # stops the active bag
```

## Record from rosbridge / dashboard

The same `openbrain_recording` services that the CLI calls:

```bash
ros2 service call /recording/start std_srvs/srv/Trigger
ros2 service call /recording/stop  std_srvs/srv/Trigger
```

## Replay

```bash
ros2 bag play /recordings/<UTC-timestamp>
# or:
openbrain play <UTC-timestamp> --rate 0.5
```

When replaying for SLAM / Nav2 testing, set `use_sim_time:=true` on
the consumers so they trust the bag's stamped time:

```bash
ros2 launch openbrain_slam rtabmap.launch.py use_sim_time:=true
ros2 bag play /recordings/<...>  --clock 200
```

## Scripted replay+verify

[`verify_bag.py`](./verify_bag.py) replays a bag and asserts that
`/system/health` and `/cmd_vel` show up at the expected rates. Useful
for catching regressions in topic plumbing.
