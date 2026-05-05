# rememb-r-navigation

> Memory-augmented topological navigation: the robot builds a sparse graph of "places" tagged with VLM embeddings and re-localizes by similarity. Survives map drift and re-arrangements that break dense SLAM.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Navigation.

## ROS topics & services (target shape)

/camera/front/color/image_raw (sub) ; /memory/places (pub, custom) ; /goal_pose (pub when re-localized)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/rememb_r_navigation/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

RememBR papers ; openvla embedding ; sentence-transformers.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_rememb_r_navigation rememb-r-navigation.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — Any indoor mobile robot with a forward-facing camera. **Kinematics Max** — VLM embeddings + vector search benefit from GPU.

**Software dependencies**

- A vision-language embedding model: [SigLIP](https://huggingface.co/google/siglip-base-patch16-224) (≈ 1 GB) or [CLIP](https://huggingface.co/openai/clip-vit-base-patch32)
- A vector database: [ChromaDB](https://github.com/chroma-core/chroma) or `sqlite-vss`
- `transformers`, `torch`, `chromadb`

**Steps to graduate this stub**

1. Install deps (`pip install transformers chromadb sentence-transformers`).
2. Download an embedding model to `/opt/openbrain/models/siglip/`.
3. Design the place-tagging schema (suggested: timestamp + pose + image embedding + free-text label).
4. Write three nodes: capture (subscribe to camera + odom, embed, insert), query (subscribe to a query topic, retrieve k-nearest places), and goto (publish `/goal_pose` from a retrieved place)

**Estimated effort:** Large (≈ 4 weeks; research-grade). Lots of design choices around chunking, freshness, and forgetting. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `rememb-r-navigation/` (Python module or C++ src).
- [ ] `launch/rememb-r-navigation.launch.py` brings up every node the demo needs.
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
