# rosa-voice-control

> Voice-driven control. A small on-device wake-word model (~3M params) listens continuously; on wake it streams to whisper-tiny, then to a function-calling LLM that emits a structured action JSON, then executed against the standard service surface.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Teleop.

## ROS topics & services (target shape)

/audio/mic (sub, audio_common_msgs/AudioData) ; /missions/load (call) ; /cmd_vel (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/rosa_voice_control/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

openai-whisper ; openWakeWord ; llama.cpp for the LLM.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_rosa_voice_control rosa-voice-control.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — USB microphone (any UVC-compatible). Speaker for confirmation TTS optional. **Kinematics Max** — ideally T5000 if running a 7B-class LLM on-device; Mini works with whisper-tiny + a 1B-class model.

**Software dependencies**

- [`whisper.cpp`](https://github.com/ggerganov/whisper.cpp) — wake-word + STT
- [`openWakeWord`](https://github.com/dscripka/openWakeWord) — small wake-word model
- [`llama.cpp`](https://github.com/ggerganov/llama.cpp) — function-calling LLM (Phi-3.5-mini-instruct, Llama-3.2-3B-Instruct, etc.)
- `audio_common` ROS package for mic capture

**Steps to graduate this stub**

1. Install audio capture: `apt install ros-humble-audio-common-msgs ros-humble-audio-capture`.
2. Build whisper.cpp + llama.cpp on the box, download chosen models.
3. Configure openWakeWord with a wake phrase.
4. Write the dispatcher: wake → STT → LLM with function-calling schema for our service surface (`/missions/load`, `/cmd_vel`, `/teleop/set_speed_profile`) → execute

**Estimated effort:** Medium-Large (≈ 3 weeks). The hardest part is the LLM function-call prompt + safety guardrails. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `rosa-voice-control/` (Python module or C++ src).
- [ ] `launch/rosa-voice-control.launch.py` brings up every node the demo needs.
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
