# edge-nerf

> On-edge NeRF capture from the robot's cameras. Operator drives the robot through a scene; the demo captures synchronized RGB + pose, trains a small NeRF on the T5000's GPU in ~5 min, exports a .glb mesh.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Perception.

## ROS topics & services (target shape)

/camera/front/color/image_raw (sub) ; /odom (sub) ; /perception/nerf/mesh (pub, file path)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/edge_nerf/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

nerfstudio ; gaussian-splatting.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_edge_nerf edge-nerf.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — Robot with a forward camera (RealSense ✓). **Kinematics Max** with **T5000 128 GB** — NeRF training needs ≈ 16 GB VRAM and takes 3–10 minutes per scene.

**Software dependencies**

- [`nerfstudio-project/nerfstudio`](https://github.com/nerfstudio-project/nerfstudio) — `pip install nerfstudio`
- [`COLMAP`](https://github.com/colmap/colmap) for structure-from-motion (camera pose estimation)
- Optional: [`gsplat`](https://github.com/nerfstudio-project/gsplat) for Gaussian splatting
- ≈ 50 GB free on `/opt/openbrain/captures/` per scene

**Steps to graduate this stub**

1. Install nerfstudio + COLMAP on the box.
2. Drive the robot through the scene; record a synchronized RGB + odom bag.
3. Convert bag → nerfstudio dataset (`ns-process-data`).
4. Train: `ns-train nerfacto`. Export: `ns-export poisson` or `gaussian-splat`.
5. Wire the export step into a ROS service so the dashboard can trigger it

**Estimated effort:** Medium-Large (≈ 3 weeks). Single-pass training is well-trodden; making it operator-friendly is the work. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `edge-nerf/` (Python module or C++ src).
- [ ] `launch/edge-nerf.launch.py` brings up every node the demo needs.
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
