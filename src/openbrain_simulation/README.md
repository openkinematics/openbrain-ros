# openbrain_simulation

Gazebo (Ignition) bringup with a sim differential-drive robot. Runs the
**full OpenBrain stack** without any physical hardware — useful for
dashboard development, demo recording, and CI smoke-tests.

## What ships

- **World:** `worlds/openbrain_lab.sdf` — a 10×10 m room with two boxes.
- **Robot:** `urdf/sim_robot.urdf.xacro` — diff-drive base with a 2D lidar
  and a front RGBD camera.
- **Bridge:** `config/sim_bridge.yaml` — ros_gz_bridge topic mappings to
  hit the v1 contract (`/cmd_vel`, `/odom`, `/scan`, `/camera/front/*`).

## Run

```bash
make sim
# or:
ros2 launch openbrain_simulation sim.launch.py
```

Open the dashboard at `ws://localhost:9090`. You should see:

- the sim robot's front camera streaming on `/stream/front`,
- a live map building from the lidar,
- joystick / WASD control driving the robot in Gazebo.

## Why simulate?

- Iterate on the dashboard without owning a robot.
- Record reproducible bags via `openbrain record sim-demo`.
- Run the full `make test` profile in CI (Phase 2 — currently sim is
  manual-only, with a headless smoke-test planned).

## Upstream

[`ros_gz`](https://github.com/gazebosim/ros_gz) (Apache-2.0) and
[Gazebo](https://gazebosim.org) (Apache-2.0).
