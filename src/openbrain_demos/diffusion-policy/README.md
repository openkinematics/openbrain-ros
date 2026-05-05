# diffusion-policy

> Diffusion-policy imitation-learning rollout on the robot. Loads a .ckpt trained off-board, samples action chunks of 16 steps via DDIM, executes the first 8.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Manipulation.

## ROS topics & services (target shape)

/perception/state (sub, custom) ; /control/joints (pub, sensor_msgs/JointState)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/diffusion_policy/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

columbia-ai-robotics/diffusion_policy ; arxiv.org/abs/2303.04137.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_diffusion_policy diffusion-policy.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — 6-DoF arm + tabletop work area. Optional ATI Mini45 F/T wrist sensor (cluttered-bin variant). Kinematics Max recommended.

**Software dependencies**

- [`columbia-ai-robotics/diffusion_policy`](https://github.com/columbia-ai-robotics/diffusion_policy)
- A trained `.ckpt` for your task (60–200 demos via teleop, then 4–8 GPU-hours on a workstation)
- `torch >= 2.0`, `diffusers`, `hydra-core`

**Steps to graduate this stub**

1. Capture demonstrations: drive the arm via teleop, record with `openbrain record` (or LeRobot's recorder).
2. Train off-board using the upstream repo's training scripts.
3. Drop the `.ckpt` at `/opt/openbrain/models/diffusion-policy/<task>.ckpt`.
4. Write the rollout node — load policy, sample 16-step DDIM action chunks, execute the first 8

**Estimated effort:** Medium (≈ 2 weeks of integration; training time depends on task complexity). Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `diffusion-policy/` (Python module or C++ src).
- [ ] `launch/diffusion-policy.launch.py` brings up every node the demo needs.
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
