# profile

> Per-operator profile loader: theme, accent color, default speed
> profile, default camera, joystick mapping, language, and the saved
> CockPit layout. Persists to `/opt/openbrain/profiles/<user>.yaml` and
> exposes a service surface the dashboard's Profile page consumes.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max — really, any host. No special sensors.

## Category

System.

## Topics & services

| Direction | Topic | Type | Notes |
|---|---|---|---|
| pub | `/profile/active` | `std_msgs/String` | latched JSON of the active profile |
| sub | `/profile/set_json` | `std_msgs/String` | JSON payload to merge + persist |

| Service | Type | What |
|---|---|---|
| `/profile/list` | `std_srvs/Trigger` | `response.message` = JSON `{"users": [...]}` |
| `/profile/get` | `std_srvs/Trigger` | `response.message` = active profile JSON |
| `/profile/set` | `std_srvs/Trigger` | persist the in-memory active profile |

## Run

```bash
ros2 launch openbrain_demos_profile profile.launch.py active_user:=alex
```

Then verify:

```bash
ros2 topic echo /profile/active --once
ros2 service call /profile/list std_srvs/srv/Trigger
```

## Schema (locked)

| Field | Type | Choices / shape |
|---|---|---|
| `user` | string | filename-safe; `/`, `.` etc. are sanitized |
| `display_name` | string | free text |
| `theme` | string | `light` ‖ `dark` ‖ `system` |
| `accent_color` | string | hex `#rgb` or `#rrggbb` (clamped to default if not hex) |
| `language` | string | `en` ‖ `pt` ‖ `es` ‖ `fr` ‖ `zh-CN` ‖ `de` |
| `default_speed_profile` | string | `beginner` ‖ `normal` ‖ `insane` |
| `default_camera` | string | free text (e.g. `front`, `back`, `thermal`) |
| `pad_layout` | string | `xbox` ‖ `ps5` ‖ `generic` |
| `cockpit_layout` | dict | opaque widget grid blob; the dashboard owns the schema |
| `custom_keybinds` | dict | opaque keybind blob; dashboard owns it |

Unknown keys in any incoming payload are **dropped** (security: a
malformed dashboard payload can't inject arbitrary state). Out-of-range
values are clamped to defaults — see `coerce()` in
[`store.py`](openbrain_demos_profile/store.py).

## Persistence

Each user lands at `/opt/openbrain/profiles/<user>.yaml`. Writes are
atomic (`*.tmp` then `os.replace`). The path is mounted as a Docker
volume in [`docker/docker-compose.yml`](../../../docker/docker-compose.yml)
so profiles survive container restarts.

## Tests

[`test/test_store.py`](test/test_store.py) covers schema clamping,
filename safety (path-traversal guard), corrupt-YAML fallback, list /
load / save round-trips, and on-disk field order.

## Related demos

- [`my-ui`](../my-ui) — saved cockpit layouts live in `cockpit_layout`
- [`fleet-control`](../fleet-control) — fleet operators each have a profile
