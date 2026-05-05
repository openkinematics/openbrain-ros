# openbrain_cli

The single operator command. Installs as both `openbrain` and `ob`.

## Usage

```text
openbrain status              # robot type, IPs, ports, systemd state, recent logs
openbrain doctor              # hardware self-test (cameras, GPU, network, disk, ...)
openbrain doctor --json       # machine-readable
openbrain teleop              # interactive WASD teleop in this terminal
openbrain record              # start a rosbag2 recording
openbrain stop                # stop the active recording
openbrain play <bag-name>     # replay /recordings/<bag-name>
openbrain estop               # engage software e-stop
openbrain estop-release       # release it
openbrain ip                  # print LAN IPs (for dashboard URLs)
openbrain logs                # tail journalctl -u openbrain -f
openbrain update              # pull latest image and restart the unit
openbrain --version
```

## Why a CLI?

Most tasks an operator does on a Jetson — verify cameras, start a
recording, check logs, e-stop — should be a single short command, not a
chain of `ros2 ...` invocations. The CLI also gives the dashboard a stable
fallback when SSH is the only available channel.

## Implementation

Each sub-command is lazy-imported (`openbrain --version` doesn't need
rclpy). `doctor` is the same code as `ros2 run openbrain_diagnostics
doctor`; `teleop` opens a `cbreak`-mode terminal and publishes to
`/safety/cmd_vel/dashboard`; `record` / `stop` call the
`openbrain_recording` services; `update` pulls and restarts the systemd
unit.
