# Installation

Two paths: **flashed Jetson box** (production) and **dev laptop** (Docker).

## Flashed Jetson box (Mini, Max, BYO Jetson)

Prereqs: JetPack 6.2 already on the box (the Mini ships pre-flashed).

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
sudo ./install.sh
sudo systemctl start openbrain
```

The installer asks which robot you're driving (`UNITREE_GO2`, `UNITREE_G1`,
`TITA`, `GENERIC`), writes `/etc/openbrain/robot.conf`, installs Docker +
the NVIDIA container toolkit if missing, pulls the `openbrain-ros` image
from GHCR, and sets up a systemd unit so the stack auto-starts on boot.

On a **Max** box the installer also asks (or auto-detects) which compute
SKU is fitted — `jetson_t4000_64gb`, `jetson_t5000_128gb`, or
`jetson_agx_orin_64gb` — and writes a `compute=` line to
`/etc/openbrain/robot.conf`. The matching profile under
[`config/`](../config) is then loaded by the bringup at launch time.
Override at runtime with `OPENBRAIN_MAX_SKU=t5000_128gb`.

Verify:
```bash
ros2 topic list | grep camera     # cameras up
curl http://localhost:8080/healthz # streamer alive
```

## Dev laptop (Docker)

Prereqs: Docker 24+, ~12 GB free for the image, optional NVIDIA GPU.

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
docker compose -f docker/docker-compose.yml up --build
```

Inside the container shell:
```bash
source install/setup.bash
ros2 launch openbrain_bringup mini.launch.py front_serial:=<serial> back_serial:=<serial>
```

If you have no RealSense plugged in, leave the serials empty — the launch
file skips missing cameras and you can still exercise rosbridge / nav2 /
missions against simulated topics.

## From source (no Docker)

Prereqs: Ubuntu 22.04 + ROS 2 Humble installed natively.

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash
ros2 launch openbrain_bringup mini.launch.py
```

## Speed-profile sanity check

```bash
ros2 service call /teleop/set_speed_profile openbrain_msgs/srv/SetSpeedProfile "{profile: 'beginner'}"
```

Should respond `success: true` with `max_linear_velocity: 0.3`.
