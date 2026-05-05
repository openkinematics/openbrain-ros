# vlm-isaac-sim

> VLM-in-the-loop closed-loop policy evaluation against NVIDIA Isaac Sim. The same Vision-Language-Action policy that runs on the robot is evaluated in sim against a procedurally-generated scene; deltas drive the next round of fine-tuning.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

VLA.

## ROS topics & services (target shape)

sim/* (Isaac Sim's ROS 2 bridge) ; /control/eef_delta (pub) ; /eval/score (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/vlm_isaac_sim/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

NVIDIA Isaac Sim ; NVIDIA Isaac Lab.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_vlm_isaac_sim vlm-isaac-sim.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — x86 workstation with **NVIDIA Isaac Sim 4.x** (does NOT run on Jetson directly — VLM-in-the-loop is for off-board policy eval). NVIDIA RTX 4090 or A6000 for sim performance.

**Software dependencies**

- [NVIDIA Isaac Sim 4.x](https://developer.nvidia.com/isaac/sim) (free for individuals; commercial license required for orgs)
- A vision-language model: GPT-4V via API, Llama-3.2-Vision via local, or Claude via Anthropic API
- [`isaac_ros_msgs`](https://github.com/NVIDIA-ISAAC-ROS) for the Isaac Sim ROS 2 bridge
- Python: `omni.isaac.kit`, `anthropic` or `openai` SDK depending on VLM

**Steps to graduate this stub**

1. Install Isaac Sim 4.x on a Linux workstation (Jetson is NOT supported).
2. Set up the eval scene (procgen warehouse aisle, spilled bottle, etc.).
3. Bridge sim → ROS via Isaac Sim's ROS 2 publisher.
4. Write the VLM loop: capture sim screenshot → send to VLM → parse response → publish skill command → execute → repeat

**Estimated effort:** Large (≈ 4 weeks). Isaac Sim's API has a learning curve; VLM prompting + JSON schema for skills is iterative. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `vlm-isaac-sim/` (Python module or C++ src).
- [ ] `launch/vlm-isaac-sim.launch.py` brings up every node the demo needs.
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
