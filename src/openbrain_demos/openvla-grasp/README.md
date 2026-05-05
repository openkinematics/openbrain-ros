# openvla-grasp

> OpenVLA-7B grasp policy. Same shape as GR00T but with the open-weights OpenVLA model. Runs FP16 on T5000, INT8 on T4000.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

VLA.

## ROS topics & services (target shape)

/camera/front/color/image_raw (sub) ; /control/eef_delta (pub) ; /perception/openvla/diagnostics (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/openvla_grasp/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

openvla/openvla-7b on huggingface ; openvla.github.io.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_openvla_grasp openvla-grasp.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — 6-DoF arm with parallel-jaw gripper. **Kinematics Max** — T5000 ideal (FP16, 8 fps), AGX Orin / T4000 OK with INT8 quantization.

**Software dependencies**

- [`openvla/openvla-7b`](https://huggingface.co/openvla/openvla-7b) on HuggingFace (open weights, ≈ 14 GB)
- `transformers`, `torch >= 2.4`, `accelerate`
- Optional: `bitsandbytes` for INT4 quantization on Orin Nano

**Steps to graduate this stub**

1. `huggingface-cli login`, then `huggingface-cli download openvla/openvla-7b --local-dir /opt/openbrain/models/openvla-7b`.
2. Install Python deps (`pip install transformers accelerate`).
3. Write the inference node — load the model, subscribe to camera, publish `/control/eef_delta`.
4. Wire your arm's joint controller to consume `/control/eef_delta`

**Estimated effort:** Medium (≈ 2 weeks). Mostly model loading + arm wiring. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `openvla-grasp/` (Python module or C++ src).
- [ ] `launch/openvla-grasp.launch.py` brings up every node the demo needs.
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
