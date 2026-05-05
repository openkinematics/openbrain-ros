# lerobot-act

> HuggingFace LeRobot ACT (Action-Chunking Transformer) policy. Runs on lower-end hardware than diffusion-policy because the action head is a transformer decoder, not a diffusion model.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Either.

## Category

Manipulation.

## ROS topics & services (target shape)

/camera/front/color/image_raw (sub) ; /control/joints (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/lerobot_act/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

huggingface/lerobot ; tonyzhaozh.github.io/aloha.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_lerobot_act lerobot-act.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — ALOHA bimanual setup, SO-101 dual-arm, or a single Koch arm. Either Mini or Max (ACT runs on Orin Nano at 20 Hz).

**Software dependencies**

- [`huggingface/lerobot`](https://github.com/huggingface/lerobot) — `pip install lerobot`
- A trained ACT policy (`.safetensors`) for your task
- `torch`, `transformers`

**Steps to graduate this stub**

1. Install LeRobot: `pip install "lerobot[all]"`.
2. Capture teleop demos via `openbrain record` (or LeRobot's `record.py`).
3. Train ACT off-board (≈ 30 min on a single GPU).
4. Push policy to HF Hub or save locally; load it in the rollout node

**Estimated effort:** Medium (≈ 2 weeks). LeRobot's API is stable; integration is wiring + arm controller. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `lerobot-act/` (Python module or C++ src).
- [ ] `launch/lerobot-act.launch.py` brings up every node the demo needs.
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
