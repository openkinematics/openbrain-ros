# humanoid-locomotion

> RL humanoid locomotion controller running on the edge. Loads a policy trained in Isaac Lab, runs at 100 Hz against the robot's joint feedback, exposes a single /cmd_vel for high-level direction.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Locomotion.

## ROS topics & services (target shape)

/joint_states (sub) ; /imu (sub) ; /control/joints (pub at 100 Hz) ; /cmd_vel (sub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/humanoid_locomotion/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

Isaac Lab ; legged_gym ; HumanPlus.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_humanoid_locomotion humanoid-locomotion.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — Unitree G1, Unitree H1, or Stanley H1 — full safety harness required during initial validation. **Kinematics Max** with hard real-time isolation.

**Software dependencies**

- [Isaac Lab](https://github.com/isaac-sim/IsaacLab) for off-board policy training
- ONNX Runtime (with CUDA Execution Provider) for on-edge deployment
- A trained PPO policy exported to ONNX (≈ 10–30 MB)
- Vendor SDK for foot-IMU + joint-state feedback

**Steps to graduate this stub**

1. Train the policy in Isaac Lab using the humanoid-locomotion env (or use one of their pre-trained checkpoints).
2. Validate exhaustively in sim before any hardware run.
3. Export to ONNX: `python scripts/play.py --export onnx`.
4. Drop policy at `/opt/openbrain/models/humanoid_locomotion/<robot>.onnx`.
5. Write the 100 Hz control loop: subscribe to joint state + IMU, run policy, publish joint commands

**Estimated effort:** Very Large (≈ 6+ weeks). Safety-critical; needs in-sim validation, harnessed validation, then untethered. Plan for at least one PI-level review. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `humanoid-locomotion/` (Python module or C++ src).
- [ ] `launch/humanoid-locomotion.launch.py` brings up every node the demo needs.
- [ ] At least one unit test under `test/` exercising the non-trivial
      logic (parsing, conversion, state-machine transitions, …).
- [ ] README updated with: real run instructions, expected output,
      sample bag/screenshot, troubleshooting tips.
- [ ] Status flipped from 🟡 to 🟢 in
      [`src/openbrain_demos/README.md`](../README.md).

## Related demos

Browse the [demo index](../README.md) for adjacent slugs in the same
category — many demos cleanly compose (e.g. `quadruped-patrol` uses
`missions` and `yolo-perception`).
