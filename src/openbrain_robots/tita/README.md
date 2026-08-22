# openbrain_robots_tita

Adapter scaffold for the **DirectDrive Tita** wheel-legged robot.

**Status:** 🟡 Phase 2 — adapter loads cleanly but `/cmd_vel` is **not**
yet forwarded.

## Why this is a Phase-2 stub

Tita's vendor SDK is C++-only and exposes a CAN-bus joint command
stream. Translating a flat `Twist` into safe joint commands requires a
body-balance controller (the wheel-legged form factor needs continuous
torso-angle correction or it tips). Building that controller well is
out of scope for v0.1.

For v0.2 we plan to wrap the manufacturer's reference balance
controller as an external process and pipe the OpenBrain `Twist`
through it. Track the work in
[#tita-adapter](https://github.com/openkinematics/openbrain-ros/issues?q=label%3Atita-adapter).

## Hardware notes

The proposed Tita integration uses a custom DB25 connection for ethernet and
power. No validated cable pinout or schematic has been released. Electrical
documents will be published in
[`kinematics-mini-hw`](https://github.com/openkinematics/kinematics-mini-hw)
only after continuity, polarity, current, and protection checks are complete.

## What works today

- Adapter inherits everything from `RobotAdapter` — speed-profile
  service, latched URDF, `/cmd_vel` subscription with clamp.
- `send_velocity` is a no-op so the rest of the OpenBrain stack still
  loads cleanly when the robot is connected.

## Run

```bash
ros2 launch openbrain_robots_tita tita.launch.py
```

`openbrain_bringup` picks this adapter when
`/etc/openbrain/robot.conf :: robot_type=TITA`.

## What's needed to make this work

**Hardware** — DirectDrive Tita wheel-legged robot. A custom edge-compute cable is planned but no validated pinout is public yet; track the hardware work in [`kinematics-mini-hw`](https://github.com/openkinematics/kinematics-mini-hw). Workshop space is required because Tita can self-balance but is harder to recover from a fall than a wheeled base.

**Software dependencies**

- DirectDrive's vendor SDK (C++; request access via their dev portal)
- A body-balance controller — either DirectDrive's reference implementation or a custom one
- CAN-bus tooling for low-level joint debug

**Steps to ship this adapter**

1. Acquire DirectDrive's SDK + the reference balance controller.
2. Wire the CAN-bus joint commands through the balance controller (it owns torso-angle correction).
3. Implement `send_velocity(twist)` — feed the Twist into the balance controller's high-level input.
4. Implement `read_odometry()` — wheel-encoder odometry fused with the torso IMU.
5. Validate that a steady-state Twist actually reaches the commanded velocity.

**Estimated effort:** Large (≈ 4 weeks). The body-balance integration is the long pole; budget extra time for hardware iteration.

## How to graduate this stub

See
[`CONTRIBUTING.md → Adding a new robot adapter`](../../../CONTRIBUTING.md#adding-a-new-robot-adapter).
The minimum acceptance bar is:

- [ ] `send_velocity(twist)` drives the body-balance controller and
      reaches commanded velocities under steady-state Twist input.
- [ ] `read_odometry()` returns wheel-encoder odometry fused with the
      torso IMU.
- [ ] Documented CAN-bus configuration so a fresh install just works.
- [ ] Status flipped from 🟡 to 🟢 in
      [`docs/supported-robots.md`](../../../docs/supported-robots.md).
