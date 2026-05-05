# openbrain_diagnostics

Hardware self-test. Two surfaces:

1. **`doctor` CLI** — synchronous, prints a colorized table, exits with
   status 0 / 1 / 2 (OK / WARN / ERROR). Wired into `openbrain doctor`.
2. **`/diagnostics` topic** — `diagnostic_msgs/DiagnosticArray` published
   every 5 s by `diagnostics_node`. Consumed by the dashboard's Diagnostics
   tab and by `rqt_robot_monitor`.

## Checks

| Check | What it verifies |
|---|---|
| `ros_env` | `ROS_DISTRO=humble` |
| `robot.conf` | `/etc/openbrain/robot.conf` exists and declares `robot_type=` |
| `disk` | ≥ 5 GB free on the partition holding `/maps` |
| `thermal` | Hottest thermal zone < 85 °C |
| `gpu` | NVIDIA GPU detected (Jetson tegra or `nvidia-smi`) |
| `realsense` | At least one RealSense enumerated |
| `network` | A default route exists |
| `rosbridge` | TCP `:9090` accepts connections |
| `streamer` | TCP `:8080` accepts connections |

Add a check by appending `(name, callable)` to `CHECKS` in
`openbrain_diagnostics/checks.py` — the table renderer, JSON output, and
ROS publisher all pick it up automatically.

## CLI

```bash
openbrain doctor             # human-friendly table
openbrain doctor --json      # machine-readable
openbrain doctor --no-color  # for log capture / CI
```

## Topic

```bash
ros2 topic echo /diagnostics --once
```

Or open the dashboard's Diagnostics tab.
