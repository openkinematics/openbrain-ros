<div align="center">

# OpenBrain ROS

**One workspace. Any robot. Any Jetson.**

The ROS 2 Humble backend for the Kinematics Mini and Max edge boxes — and any
NVIDIA Jetson you bring. Drivers, SLAM, Nav2, perception, teleop, safety,
recording, diagnostics, sim, and a CLI in one place.

[![ROS 2 Humble](https://img.shields.io/badge/ROS%202-Humble-22314e?logo=ros)](https://docs.ros.org/en/humble/)
[![JetPack 6.2](https://img.shields.io/badge/JetPack-6.2-76b900?logo=nvidia)](https://developer.nvidia.com/embedded/jetpack)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![build](https://github.com/openkinematics/openbrain-ros/actions/workflows/build.yml/badge.svg)](https://github.com/openkinematics/openbrain-ros/actions/workflows/build.yml)
[![lint](https://github.com/openkinematics/openbrain-ros/actions/workflows/lint.yml/badge.svg)](https://github.com/openkinematics/openbrain-ros/actions/workflows/lint.yml)
[![docker](https://github.com/openkinematics/openbrain-ros/actions/workflows/docker.yml/badge.svg)](https://github.com/openkinematics/openbrain-ros/actions/workflows/docker.yml)

[**Website**](https://www.openkinematics.com) ·
[**Docs**](./docs) ·
[**Demos**](./src/openbrain_demos) ·
[**Dashboard**](https://github.com/openkinematics/openbrain-dashboard) ·
[**Hardware**](https://github.com/openkinematics/kinematics-mini-hw) ·
[**Discord**](https://www.openkinematics.com/community)

</div>

---

## Why OpenBrain

| | What it gives you |
|---|---|
| 🧠 **One brain** | A single ROS 2 workspace that drives quadrupeds, humanoids, mobile bases, and manipulators behind one velocity contract. |
| 🎯 **Dashboard-first** | Versioned, documented [public API](./docs/api.md). The web UI is a first-class client, not an afterthought. |
| 🛡️ **Safe by default** | Twist-mux priority arbitration, dead-man timeouts, watchdog, and per-profile velocity caps wired in from day one. |
| 🧰 **Real CLI** | `openbrain doctor` runs a full self-test. `openbrain teleop`, `record`, `play`, `update`, `logs` all just work. |
| 🧪 **Tested** | Unit tests in every non-trivial package. CI on every push: build + lint + multi-arch image build. |
| 🤖 **20 demos** | Three full implementations on day one (cockpit, health, missions) and 17 scaffolds you can graduate. |
| 📦 **Containers** | Multi-layer JetPack 6.2 image, dev container, sim profile, GHCR-published builds. |
| 🪙 **MIT** | Use it commercially. No CLA. |

## Architecture

```
                      ┌─────────────────────────────┐
                      │  openbrain-dashboard (web)  │
                      └───────────┬─────────────────┘
                ws :9090          │           HTTP :8080
       ┌──────────────────────────┴──────────────────────┐
       │                                                  │
┌──────▼──────┐                                  ┌────────▼────────┐
│ rosbridge   │                                  │ video_streamer  │
│             │                                  │ WebRTC + MJPEG  │
└──────┬──────┘                                  └────────┬────────┘
       │ topics + services                                │
┌──────┴───────────────────────────────────────────────────────────┐
│                         ROS 2 graph                              │
│  /cmd_vel /goal_pose /missions/* /teleop/* /system/health /...   │
│                                                                  │
│  bringup → drivers → slam → nav → perception → safety → robot    │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                       ┌────────┴────────┐
                       │  Robot SDK      │
                       │  (Go2/G1/Tita/  │
                       │   generic)      │
                       └─────────────────┘
```

## Quick start

### On a Jetson (Mini, Max, or BYO)

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
sudo ./install.sh           # interactive: detects robot, installs Docker, sets up systemd
sudo systemctl start openbrain
openbrain doctor            # verifies cameras, GPU, network, ROS topics
```

### On a dev laptop (no hardware)

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
make dev                    # interactive shell in the dev container
make sim                    # Gazebo profile — full stack with a sim robot
```

Open the dashboard pointing at `ws://localhost:9090` and you should see the
sim robot, its cameras, and a live map within 30 seconds.

### From source (native ROS Humble)

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash
ros2 launch openbrain_bringup mini.launch.py
```

## What's in the box

### Core packages

| Package | Purpose |
|---|---|
| [`openbrain_msgs`](src/openbrain_msgs) | Custom messages + services. The dashboard contract. |
| [`openbrain_bringup`](src/openbrain_bringup) | Top-level `mini.launch.py` / `max.launch.py` with auto-detected robot adapter. |
| [`openbrain_slam`](src/openbrain_slam) | RTAB-Map RGB-D, persistent map at `/maps/openbrain.db`. |
| [`openbrain_nav`](src/openbrain_nav) | Nav2 stack + custom behavior tree, tuned for a 0.22 m-radius indoor robot. |
| [`openbrain_perception`](src/openbrain_perception) | YOLOv11 + NVBlox launch scaffolds. |
| [`openbrain_teleop`](src/openbrain_teleop) | rosbridge `:9090` and aiortc-based WebRTC + MJPEG streamer `:8080`. |
| [`openbrain_safety`](src/openbrain_safety) | Twist-mux, dead-man, e-stop, watchdog. |
| [`openbrain_joystick`](src/openbrain_joystick) | Gamepad → `/cmd_vel` (PS5, Xbox, generic). |
| [`openbrain_recording`](src/openbrain_recording) | rosbag2 wrapper for mission recording / playback. |
| [`openbrain_diagnostics`](src/openbrain_diagnostics) | Hardware self-test (cameras, GPU, network, disk, thermal). |
| [`openbrain_simulation`](src/openbrain_simulation) | Gazebo bringup with a sim mobile robot. |
| [`openbrain_modelhub`](src/openbrain_modelhub) | SaaS policy deployment client (`modelhub_pull`, `modelhub_list`). |
| [`openbrain_connector`](src/openbrain_connector) | Optional read-only edge runtime, skill lineage, and hardware-gate status for the Dashboard. |
| [`openbrain_cli`](src/openbrain_cli) | `openbrain` / `ob` console command. |

### Drivers

`openbrain_drivers_realsense` ships v0.1; `livox`, `hesai`, `xsens`,
`flir_boson`, `ti_mmwave`, `quectel_5g` are scaffolded for Phase 3.

### Robot adapters

| Robot | Status |
|---|---|
| Unitree Go2 / Go2-W | ✅ v0.1 |
| Unitree G1 | 🟡 Phase 2 |
| DirectDrive Tita | 🟡 Phase 2 |
| Generic ROS 2-native | ✅ v0.1 |

Adding a robot is typically a 100-line subclass of
[`RobotAdapter`](src/openbrain_robots/generic/openbrain_robots_generic/robot_adapter.py).
See [`docs/supported-robots.md`](docs/supported-robots.md).

### Demos (20)

| Slug | Status | What it does |
|---|---|---|
| [`cockpit`](src/openbrain_demos/cockpit) | 🟢 | Full teleop stack with dual-camera streaming |
| [`health`](src/openbrain_demos/health) | 🟢 | CPU/GPU/RAM/thermal/power telemetry on `/system/health` |
| [`missions`](src/openbrain_demos/missions) | 🟢 | Multi-waypoint mission state machine over Nav2 |
| [`profile`](src/openbrain_demos/profile) | 🟢 | Per-operator preferences, YAML-backed |
| [`fleet-control`](src/openbrain_demos/fleet-control) | 🟢 | Multi-robot health + mission aggregator |
| [`yolo-perception`](src/openbrain_demos/yolo-perception) | 🟢 | YOLOv11 detector + overlay |
| [`vslam-gps-denied`](src/openbrain_demos/vslam-gps-denied) | 🟢 | RTAB-Map VIO config for warehouses / drones |
| [`quadruped-patrol`](src/openbrain_demos/quadruped-patrol) | 🟢 | Battery-aware patrol loop with return-to-charger |
| [+12 more](src/openbrain_demos) | 🟡 | Stubs ready to graduate — see the catalog |

## Public API

The dashboard talks to the robot over a documented contract — topics,
services, custom messages, network ports, all versioned. See
[**docs/api.md**](./docs/api.md). Treat it as a public interface.

## CLI

```bash
openbrain status        # robot type, IPs, running nodes, recent logs
openbrain doctor        # full self-test: cameras, GPU, network, ROS, disk
openbrain teleop        # interactive WASD teleop in your terminal
openbrain record demo   # start rosbag2 recording into /recordings/demo
openbrain play demo     # play it back
openbrain update        # pull the latest image + restart the systemd unit
openbrain logs -f       # tail journalctl + ROS logs together
```

## Hardware compatibility

| Box | Compute | Status |
|---|---|---|
| Kinematics Mini (from $1,499) | Jetson Orin Nano 8 GB | ✅ v0.1 |
| Kinematics Max (configurable) | Jetson T4000 64 GB · T5000 128 GB · AGX Orin 64 GB | ✅ v0.1 |
| BYO Jetson | Orin Nano · Orin NX · AGX Orin · AGX Thor | ✅ v0.1 |
| x86 dev laptop | any | ✅ via Docker (sim only) |

## Documentation

- [**Installation**](docs/installation.md) — three install paths, end-to-end
- [**Architecture**](docs/architecture.md) — data flow + how packages compose
- [**Public API contract**](docs/api.md) — topics, services, messages, ports
- [**Edge runtime status**](docs/edge-runtime-status.md) — optional SkillOps lineage, remote inference, and safety monitoring
- [**Supported robots**](docs/supported-robots.md) — status matrix + how to add one
- [**Examples**](examples/) — copy-paste mission JSONs, teleop scripts, replay hooks
- [**Troubleshooting**](docs/troubleshooting.md) — common pitfalls
- [**Contributing**](CONTRIBUTING.md) — dev environment, conventions, PR flow
- [**Package README template**](docs/package-readme-template.md) — canonical shape for every package
- [**Security**](SECURITY.md) — reporting vulnerabilities + hardening tips
- [**Code of Conduct**](CODE_OF_CONDUCT.md)
- [**Changelog**](CHANGELOG.md)

## Internationalization

The English docs are canonical. Translations live under `docs/i18n/<lang>/` —
contributions welcome. Open a PR with a new locale and we will wire it into
the docs index. Currently planned: `pt`, `es`, `fr`, `zh-CN`, `de`.

## Sister repos

- [**openbrain-dashboard**](https://github.com/openkinematics/openbrain-dashboard) — Next.js operator console
- [**kinematics-mini-hw**](https://github.com/openkinematics/kinematics-mini-hw) — Kinematics Mini hardware design and validation roadmap; fabrication files are not released yet

The demo catalog lives in this repo at [`src/openbrain_demos/`](src/openbrain_demos) — one folder per demo, with a per-demo README that the marketing site and the dashboard both link into.

## Community

- **Discord:** https://www.openkinematics.com/community
- **Issues:** [github.com/openkinematics/openbrain-ros/issues](https://github.com/openkinematics/openbrain-ros/issues)
- **Discussions:** [github.com/openkinematics/openbrain-ros/discussions](https://github.com/openkinematics/openbrain-ros/discussions)

## License

MIT. See [LICENSE](./LICENSE) and [ATTRIBUTION.md](./ATTRIBUTION.md) for upstream credits.

---

<div align="center">

**Built openly by [OpenKinematics](https://www.openkinematics.com).**
PRs welcome.

</div>
