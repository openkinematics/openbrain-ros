# openbrain_recording

rosbag2 controller exposed over ROS services. Lets the dashboard (or the
`openbrain` CLI) start and stop session recordings without shelling in.

## Services

| Service | Type | What |
|---|---|---|
| `/recording/start` | `std_srvs/Trigger` | Start a new bag at `/recordings/<UTC-timestamp>/` |
| `/recording/stop` | `std_srvs/Trigger` | Cleanly stop the current bag |

## Topics recorded (default)

`/cmd_vel`, `/odom`, `/map`, `/system/health`, `/missions/status`,
`/camera/front/color/image_raw`, `/camera/back/color/image_raw`.

Override at launch time:

```bash
ros2 launch openbrain_recording recording.launch.py
ros2 param set /openbrain_recording topics "['/foo','/bar']"
```

## Run

```bash
ros2 launch openbrain_recording recording.launch.py
ros2 service call /recording/start std_srvs/srv/Trigger
# ... drive around ...
ros2 service call /recording/stop  std_srvs/srv/Trigger
```

Bags land in `/recordings/`. Mount that path as a Docker volume so they
survive container restarts (the default compose file does this).

## Playback

```bash
ros2 bag play /recordings/<timestamp>
```

Or use the CLI shortcut:

```bash
openbrain play <timestamp>
```
