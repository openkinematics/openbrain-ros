# health

> Publishes Jetson system telemetry on `/system/health` at 1 Hz. The
> dashboard's Health page subscribes here for CPU/GPU/RAM/thermal/power
> tiles and historical charts.

**Status:** 🟢 Phase 1 — full implementation.

## Hardware

Either Kinematics Mini or Max — really, any Linux box. On Jetson the
node uses [`jetson-stats`](https://github.com/rbonghi/jetson_stats) for
tegrastats-quality telemetry; everywhere else it falls back to
[`psutil`](https://github.com/giampaolo/psutil) so a developer laptop
still publishes a populated message.

## Category

System.

## ROS topics

| Direction | Topic | Type | Rate |
|---|---|---|---|
| pub | `/system/health` | `openbrain_msgs/SystemHealth` | 1 Hz |

The message shape is locked to v1 — see
[`openbrain_msgs/msg/SystemHealth.msg`](../../openbrain_msgs/msg/SystemHealth.msg)
and the
[`docs/api.md` contract](../../../docs/api.md#systemhealthmsg-shape-from-dashboard-libtypests).

## Run

```bash
ros2 launch openbrain_demos_health health.launch.py
```

Verify:
```bash
ros2 topic echo /system/health --once
```

## Backends

| Backend | When | Source |
|---|---|---|
| `jtop` | On a Jetson with `jetson-stats` installed | tegrastats |
| `psutil` | Everywhere else (laptop, CI) | `/sys/class/thermal`, kernel meminfo |

The node logs which backend it picked at startup. If you see `jtop`
but the message is empty, the user running ROS may not be in the `jtop`
group — `sudo usermod -aG jtop "$USER"` and re-login.

## Tests

[`test/test_psutil_path.py`](test/test_psutil_path.py) exercises the
fallback path so CI catches regressions without needing a Jetson.

## Related demos

- [`profile`](../profile) — operator profile that picks default thermal alarms
- [`fleet-control`](../fleet-control) — aggregates `/system/health` across robots
