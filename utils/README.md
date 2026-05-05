# utils/

Standalone helper scripts that don't belong inside a ROS package — calibration
helpers, log bundling, network discovery, factory reset, etc. None of these
require sourcing the workspace.

| Script | What it does |
|---|---|
| [`calibrate_cameras.py`](./calibrate_cameras.py) | Capture intrinsics + extrinsics for the dual D435i pair using a checkerboard. |
| [`upload_logs.sh`](./upload_logs.sh) | Tar `/var/log/openbrain` + journalctl + `openbrain doctor --json` and write a single bundle for support. |
| [`discover_robot.py`](./discover_robot.py) | mDNS scan for `_openbrain._tcp` services on the LAN — finds robots running our systemd unit. |
| [`factory_reset.sh`](./factory_reset.sh) | Wipe `/maps`, `/recordings`, `/opt/openbrain/models`, and `/etc/openbrain/robot.conf`. Asks twice. |
| [`setup_wifi.sh`](./setup_wifi.sh) | nmcli helper: scan, pick SSID, prompt for password, save the connection. |
| [`joystick_test.py`](./joystick_test.py) | Verify a connected gamepad — prints axis/button events and the ROS joy_node mapping. |

Run them directly:

```bash
sudo bash utils/factory_reset.sh
python3 utils/discover_robot.py
```

Or add `utils/` to your `PATH` so `factory_reset.sh` etc. are reachable
without the prefix.
