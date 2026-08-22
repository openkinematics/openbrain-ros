# openbrain_bringup

Top-level launch files. One per box.

## Mini

```bash
ros2 launch openbrain_bringup mini.launch.py \
    front_serial:=<serial> back_serial:=<serial>
```

Brings up: 2× D435i, RTAB-Map SLAM, Nav2, rosbridge :9090, WebRTC :8080,
plus the robot adapter that matches your `/etc/openbrain/robot.conf`
(`robot_type=UNITREE_GO2 | UNITREE_G1 | TITA | GENERIC`). Override at the
CLI with `robot_type:=GENERIC`.

Optional read-only edge runtime monitoring is disabled by default. Enable it
only after installing a fail-closed hardware profile and active skill
descriptor:

```bash
ros2 launch openbrain_bringup mini.launch.py \
    enable_edge_status:=true \
    edge_hardware_profile:=/etc/openbrain/hardware-profile.json \
    edge_skill_descriptor:=/etc/openbrain/active-skill.json \
    edge_status_allowed_origin:=https://dashboard.openkinematics.com
```

The same arguments are available on `max.launch.py`. This service is an
observability endpoint only and does not participate in ROS command routing.

## Max

```bash
ros2 launch openbrain_bringup max.launch.py \
    enable_lidar:=true enable_industrial_imu:=true
```

Same as Mini plus opt-in payload drivers. Each driver is gated on its own
launch argument (`enable_lidar`, `enable_industrial_imu`, `enable_thermal`,
`enable_mmwave`, `enable_5g`). Default is **all off** so a Max box without
payloads still launches cleanly.

### Compute SKU

The Max ships in three compute variants. The bringup detects which one is
present and loads the matching profile from [`config/`](../../config):

| SKU | Profile | What changes vs. base |
|---|---|---|
| Jetson T4000 64 GB (default) | [`config/max_t4000_64gb.yaml`](../../config/max_t4000_64gb.yaml) | INT8 perception, NVBlox off |
| Jetson T5000 128 GB | [`config/max_t5000_128gb.yaml`](../../config/max_t5000_128gb.yaml) | FP16 perception, NVBlox on, 30 Hz Nav2, 4 streams |
| Jetson AGX Orin 64 GB | [`config/max_agx_orin_64gb.yaml`](../../config/max_agx_orin_64gb.yaml) | tighter thermal cap, NVBlox off |

`launch/_max_sku.py` resolves the SKU using this order:

1. `$OPENBRAIN_MAX_SKU` env var (e.g. `t5000_128gb`).
2. `compute=` line in `/etc/openbrain/robot.conf`.
3. `/proc/device-tree/model` autodetection (Jetson exposes its platform name there).
4. Fallback: `t4000_64gb`.

## Robot-type resolution

`launch/_robot_type.py` resolves the active adapter using this order:

1. `robot_type:=...` CLI argument.
2. `ROBOT_TYPE` environment variable.
3. `robot_type=` line in `/etc/openbrain/robot.conf`.
4. Fallback to `GENERIC`.

The [`install.sh`](../../install.sh) installer at the repo root writes
`/etc/openbrain/robot.conf` based on what it detects (or asks).
