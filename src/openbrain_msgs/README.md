# openbrain_msgs

Custom messages and services. **This is the dashboard contract.** Field
shapes here must match the TypeScript declarations in
[`openbrain-dashboard/lib/types.ts`](https://github.com/openkinematics/openbrain-dashboard/blob/main/lib/types.ts);
drift breaks the UI silently because rosbridge passes through unknown
keys as `undefined`.

For the human-friendly version of every shape, see
[`docs/api.md`](../../docs/api.md).

## Messages

| File | Used by | Direction |
|---|---|---|
| [`SystemHealth.msg`](msg/SystemHealth.msg) | `openbrain_demos_health` → dashboard | publish |
| [`MissionStatus.msg`](msg/MissionStatus.msg) | `openbrain_demos_missions` → dashboard | publish |
| [`Waypoint.msg`](msg/Waypoint.msg) | embedded inside `LoadMission.srv` | request |
| [`ThermalZone.msg`](msg/ThermalZone.msg) | embedded inside `SystemHealth.msg` | publish |
| [`PowerRail.msg`](msg/PowerRail.msg) | embedded inside `SystemHealth.msg` | publish |

## Services

| File | Server | Caller |
|---|---|---|
| [`LoadMission.srv`](srv/LoadMission.srv) | `openbrain_demos_missions` | dashboard |
| [`SetSpeedProfile.srv`](srv/SetSpeedProfile.srv) | every `RobotAdapter` subclass | dashboard |

## Versioning

This contract is **`v1`**. Adding new fields to existing messages is
non-breaking (rosbridge JSON ignores unknowns) and may land in any
release. Removing or renaming fields requires a `v2` package alongside
`v1` and a coordinated dashboard PR — see
[`docs/api.md#versioning-policy`](../../docs/api.md#versioning-policy).

## Build + verify

```bash
colcon build --packages-select openbrain_msgs
colcon test  --packages-select openbrain_msgs   # rosidl schema + lint
ros2 interface show openbrain_msgs/msg/SystemHealth
```

## Adding a new message

1. Drop the file under `msg/` (or `srv/` / `action/`).
2. Add it to the `set(msg_files ...)` list in [`CMakeLists.txt`](CMakeLists.txt).
3. If it embeds another type from this package, prefix with the package
   name: `openbrain_msgs/Waypoint` (the rosidl generator needs the explicit
   reference even for same-package nesting).
4. Document the shape in [`docs/api.md`](../../docs/api.md). The dashboard
   maintainer should sign off on the PR if the new type is consumed there.
