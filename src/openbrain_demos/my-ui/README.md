# my-ui

> A drag-and-drop dashboard panel built from scratch. The user picks widgets (camera tile, joystick, mission planner, telemetry chart) from a palette, arranges them on a grid, and saves the layout to their profile.

**Status:** 🟡 stub — scaffolded package with a TODO launch.
The graduating PR turns this into a 🟢 demo.

## Hardware

Either.

## Category

Dashboard.

## ROS topics & services (target shape)

/system/health (sub) ; /cmd_vel (pub via dashboard) ; /missions/load (call)

(See [`docs/api.md`](../../../docs/api.md) for the conventions used by
the v1 contract. Demos are free to add new private topics under
`/perception/my_ui/*` or similar — keep public-API additions to
[`openbrain_msgs`](../../openbrain_msgs).)

## References

openbrain-dashboard /app/my-ui/* — this demo packages a worked example layout that lands as a default in the dashboard's "templates" gallery.

## How to run (placeholder)

```bash
ros2 launch openbrain_demos_my_ui my-ui.launch.py
```

The launch file currently logs a TODO. Once this stub graduates, it
will bring up the demo's nodes and document any extra parameters here.



## What's needed to make this work

**Hardware** — Either Mini or Max — no special hardware. Runs entirely in the dashboard.

**Software dependencies**

None on the ROS side. The widget grid is rendered by [openbrain-dashboard](https://github.com/openkinematics/openbrain-dashboard).

**Steps to graduate this stub**

1. Design the widget JSON schema (re-uses the `cockpit_layout` field from [`profile`](../profile)).
2. Add a layout-validator node here that publishes a layout template on `/my_ui/template`.
3. Land the matching dashboard PR that renders the layout.

**Estimated effort:** Small (≈ 1 week). Open the issue in [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues) before starting so we can coordinate scope + reviewers.

## How to graduate this stub

See [`CONTRIBUTING.md → Adding a new demo`](../../../CONTRIBUTING.md#adding-a-new-demo).
Minimum acceptance bar:

- [ ] Real implementation under `my-ui/` (Python module or C++ src).
- [ ] `launch/my-ui.launch.py` brings up every node the demo needs.
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
