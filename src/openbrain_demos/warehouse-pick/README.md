# warehouse-pick

> Warehouse pick-and-pack reference cell. Mobile manipulator drives to a shelf, identifies the target SKU via YOLO, plans and executes the grasp with diffusion-policy, drops in a tote.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Max.

## Category

Manipulation.

## ROS topics & services (target shape)

/perception/yolo/detections (sub) ; /control/joints (pub) ; /missions/status (pub)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/warehouse_pick/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

builds on yolo-perception + diffusion-policy + missions.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_warehouse_pick warehouse-pick.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — Mobile manipulator: Kinematics-compatible mobile base + 6-DoF arm + tote/bin + a YOLO-trained set of SKUs. Optional ATI Mini45 F/T wrist sensor for closed-loop force feedback.

**Software dependencies**

- This demo **composes** [`yolo-perception`](../yolo-perception) (already 🟢) + [`diffusion-policy`](../diffusion-policy) (🟡) + [`missions`](../missions) (already 🟢)
- A YOLO model fine-tuned on the SKUs you want to pick
- A diffusion policy trained on cluttered-bin grasps in your specific bin geometry

**Steps to graduate this stub**

1. Bring up the existing demos (yolo, missions) on your robot.
2. Graduate `diffusion-policy` first (this depends on it).
3. Capture demos of cluttered-bin picks, train the policy.
4. Write the orchestrator: drive to bin (missions), detect SKU (yolo), grasp (diffusion-policy), drop in tote, repeat

**Estimated effort:** Very Large (≈ 6+ weeks). Composition is the easy part; the data collection + per-bin tuning is the long pole. Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `warehouse-pick/` (Python module or C++ src).
- [ ] `launch/warehouse-pick.launch.py` brings up every node the demo needs.
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
