# cockpit

> Default teleop stack — what a fresh Kinematics Mini boots into. Brings up
> cameras, SLAM, Nav2, rosbridge, the WebRTC streamer, and the configured
> robot adapter so the dashboard can drive the robot immediately.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max. No payload sensors required. RealSense
D435i pair recommended for SLAM; the launch gracefully skips missing
cameras so a no-camera laptop dev session still works.

## Category

Teleop.

## What it brings up

`cockpit.launch.py` is a thin include over
[`openbrain_bringup/mini.launch.py`](../../openbrain_bringup/launch/mini.launch.py).
End result:

- 2× RealSense D435i (`openbrain_drivers_realsense`)
- RTAB-Map RGB-D SLAM (`openbrain_slam`)
- Nav2 stack with the OpenBrain behavior tree (`openbrain_nav`)
- Safety mux + dead-man + e-stop (`openbrain_safety`)
- rosbridge `:9090` + WebRTC/MJPEG streamer `:8080` (`openbrain_teleop`)
- Robot adapter — auto-selected from `/etc/openbrain/robot.conf`

## Run

```bash
ros2 launch openbrain_demos_cockpit cockpit.launch.py
```

Then open the dashboard pointing at `ws://<robot>:9090`. You should
see two camera tiles, a virtual joystick, the live map, and system
telemetry inside ~30 seconds.

## Troubleshooting

- **No camera frames.** Run `openbrain doctor` — the `realsense` check
  reports if `rs-enumerate-devices` finds your hardware.
- **Robot doesn't respond to the joystick.** Check `/safety/estop`
  is `false` and that your `robot_type` in `/etc/openbrain/robot.conf`
  matches the connected robot.

See [`docs/troubleshooting.md`](../../../docs/troubleshooting.md) for
the full list.

## Related demos

- [`health`](../health) — telemetry that the dashboard's status bar reads
- [`missions`](../missions) — multi-waypoint patrol over the same stack
