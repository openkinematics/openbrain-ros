# nvblox-mapping

> NVIDIA NVBlox volumetric 3D mapping from the depth pair. Publishes a TSDF and ESDF that Nav2 can consume for full-3D obstacle avoidance.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Navigation.

## ROS topics & services (target shape)

/camera/front/depth/image_rect_raw (sub) ; /odom (sub) ; /perception/nvblox/{tsdf,esdf,mesh} (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/nvblox_mapping/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

NVIDIA-ISAAC-ROS/isaac_ros_nvblox ; nvidia.com/en-us/on-demand/session/gtcfall22-a41063.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_nvblox_mapping nvblox-mapping.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — RealSense D435i / D455 (depth + camera_info topics already published by [`openbrain_drivers_realsense`](../../openbrain_drivers/realsense)). **Kinematics Max** — TSDF + ESDF integration is GPU-heavy.

**Software dependencies**

- [`NVIDIA-ISAAC-ROS/isaac_ros_nvblox`](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox) — apt or source build
- `ros-humble-isaac-ros-nvblox` if available; otherwise build from source
- CUDA + cuDNN (already on JetPack 6.2)

**Steps to graduate this stub**

1. Install nvblox: `apt install ros-humble-isaac-ros-nvblox` (or build from source per the upstream README).
2. Replace the TODO launch with `IncludeLaunchDescription` of `nvblox_examples_bringup`'s realsense launch, with our remappings.
3. Wire `/perception/nvblox/{tsdf,esdf,mesh}` outputs into Nav2's costmap as a static layer

**Estimated effort:** Small-Medium (≈ 1 week). Mostly launch composition + Nav2 integration. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `nvblox-mapping/` (Python module or C++ src).
- [ ] `launch/nvblox-mapping.launch.py` brings up every node the demo needs.
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
