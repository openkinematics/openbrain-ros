# openbrain_robots_unitree_g1

Adapter scaffold for the **Unitree G1** humanoid.

**Status:** 🟡 Phase 2 — adapter loads cleanly but `/cmd_vel` is **not**
yet forwarded. Use `openbrain_robots_generic` if your G1 already runs
the upstream community ROS 2 driver.

## Why this is a Phase-2 stub

The G1's high-level locomotion API doesn't accept a flat `Twist`. It
takes walking primitives (`StepForward(distance)`, `Turn(angle)`,
`Stop()`). A clean translation requires either:

1. an in-process gait planner that converts continuous Twist into
   discrete steps (and re-plans when the Twist changes mid-step), or
2. a pre-baked finite-state machine that maps a coarse direction set
   ({forward, back, strafe-left, strafe-right, turn-left, turn-right})
   to walking primitives.

We've designed the FSM but want to validate it on real hardware before
shipping. Track the work in
[#g1-adapter](https://github.com/openkinematics/openbrain-ros/issues?q=label%3Ag1-adapter).

## What works today

- The adapter inherits everything from `RobotAdapter` — speed-profile
  service, latched URDF, `/cmd_vel` subscription with clamp.
- `send_velocity` is a no-op so the rest of the OpenBrain stack
  (rosbridge, video streamer, missions) loads and runs cleanly even on
  a connected G1.

## Run

```bash
ros2 launch openbrain_robots_unitree_g1 unitree_g1.launch.py
```

`openbrain_bringup` picks this adapter when
`/etc/openbrain/robot.conf :: robot_type=UNITREE_G1`.

## What's needed to make this work

**Hardware** — Unitree G1 humanoid (≈ $16k starting). Power dock, ethernet to the host (or USB-Ethernet adapter on the Mini). Safety harness for initial validation.

**Software dependencies**

- [`unitreerobotics/unitree_sdk2_python`](https://github.com/unitreerobotics/unitree_sdk2_python)
- [`unitreerobotics/unitree_sdk2`](https://github.com/unitreerobotics/unitree_sdk2) — C++ SDK
- CycloneDDS XML config matching the G1's network interface

**Steps to ship this adapter**

1. Install `unitree_sdk2_python` per their README.
2. Set up the CycloneDDS XML for your network interface.
3. Pick the translation mode: continuous gait planner OR discrete walking-primitive FSM (see the G1 docstring in [`unitree_g1_adapter.py`](openbrain_robots_unitree_g1/unitree_g1_adapter.py)).
4. Implement `send_velocity(twist)` — translate Twist into G1 walking primitives.
5. Implement `read_odometry()` — parse `HighState` foot-IMU fusion.

**Estimated effort:** Large (≈ 4 weeks). The walking-primitive translation needs hardware iteration; safety-harness validation at every step.

## How to graduate this stub

See
[`CONTRIBUTING.md → Adding a new robot adapter`](../../../CONTRIBUTING.md#adding-a-new-robot-adapter).
The minimum acceptance bar is:

- [ ] `send_velocity(twist)` translates a non-zero linear or angular
      command into walking primitives that move the robot in the
      expected direction.
- [ ] `read_odometry()` returns filtered odometry from `HighState`.
- [ ] One end-to-end test recorded as a rosbag2 in `tests/fixtures/`
      and replayable in CI.
- [ ] Status flipped from 🟡 to 🟢 in
      [`docs/supported-robots.md`](../../../docs/supported-robots.md).
