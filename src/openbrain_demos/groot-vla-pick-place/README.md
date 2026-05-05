# groot-vla-pick-place

> Run NVIDIA GR00T (a 2B-parameter Vision-Language-Action transformer) on the edge for tabletop pick-and-place. The model takes an RGB observation + a natural-language instruction and emits 7-DoF end-effector deltas at 10 Hz.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

VLA.

## ROS topics & services (target shape)

/camera/front/color/image_raw (sub) ; /perception/groot/instruction (sub, std_msgs/String) ; /control/eef_delta (pub, geometry_msgs/Twist)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/groot_vla_pick_place/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

GR00T model card on huggingface ; nvidia/Isaac-GR00T repo.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_groot_vla_pick_place groot-vla-pick-place.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — 6-DoF arm with parallel-jaw gripper (Franka Panda, UR5e, or SO-101 dual-arm verified). Kinematics Max with **T5000 128 GB** strongly recommended (GR00T 2B at FP16 needs ≈ 14 GB VRAM).

**Software dependencies**

- [`nvidia/Isaac-GR00T`](https://github.com/NVIDIA/Isaac-GR00T) (NVIDIA-gated; sign EULA)
- GR00T-N1 model weights from NGC (≈ 5 GB)
- `transformers >= 4.45`, `torch >= 2.4`, `accelerate`
- Vendor SDK for your arm (libfranka, ur_rtde, lerobot)

**Steps to graduate this stub**

1. Get NVIDIA NGC API key, download GR00T checkpoint to `/opt/openbrain/models/groot-n1/`.
2. Install Isaac-GR00T per their README (`pip install -e .`).
3. Wire your arm's joint controller into `/control/eef_delta`.
4. Replace the TODO launch with a node that loads the model, subscribes to camera + instruction, runs inference at 10 Hz, and publishes EEF deltas

**Estimated effort:** Large (≈ 3–4 weeks). Adapter + tokenizer + control loop tuning. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `groot-vla-pick-place/` (Python module or C++ src).
- [ ] `launch/groot-vla-pick-place.launch.py` brings up every node the demo needs.
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
