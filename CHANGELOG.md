# Changelog

All notable changes to this project will be documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- `kinematics-lab` sister repo dissolved. The demo catalog now lives
  exclusively at [`src/openbrain_demos/`](src/openbrain_demos) — one
  folder per demo with its own README. The marketing site at
  `openkinematics.com/demos` reads metadata directly from
  `openkinematics/lib/demos.ts`, where each entry's `repo` field now
  points at `github.com/openkinematics/openbrain-ros/tree/main/src/openbrain_demos/<slug>`.
- `PLAN.md` deleted by maintainer — README + CONTRIBUTING + CHANGELOG
  cover the v0.1 scope.

### Added
- Real implementations for 5 of the 17 stub demos:
  `profile`, `yolo-perception`, `fleet-control`,
  `vslam-gps-denied`, `quadruped-patrol`. Catalog status flipped
  from 🟡 to 🟢 in [`src/openbrain_demos/README.md`](src/openbrain_demos/README.md).
- `openbrain_perception/launch/yolo.launch.py` now delegates to the
  real `openbrain_demos_yolo_perception` implementation (was a Phase-2
  TODO stub). `ros2 launch openbrain_perception yolo.launch.py` now
  works end-to-end.
- Every 🟡 stub README (12 demos + 6 drivers + 2 robot adapters) gained
  a **What's needed to make this work** section: specific hardware list
  with rough pricing, software dependencies with deep links, ordered
  steps to ship, and an effort estimate. A graduating contributor now
  has a single screen telling them what to buy, what to install, and
  what to write.
- Per-SKU Max profiles: `config/max_t4000_64gb.yaml`,
  `config/max_t5000_128gb.yaml`, `config/max_agx_orin_64gb.yaml`. The
  bringup auto-detects the SoC via `/proc/device-tree/model` and applies
  the matching overlay; override with `OPENBRAIN_MAX_SKU` or the
  `compute=` line in `/etc/openbrain/robot.conf`.
- `install.sh` prompts for the Max compute SKU on Max boxes (and
  auto-detects in non-interactive mode).
- `openbrain_bringup/launch/_max_sku.py` — SKU resolver consumed by
  `max.launch.py`.

### Changed
- `config/max.yaml` is now a SKU-agnostic base; SKU-specific files
  override only what the SoC actually changes (perception precision,
  Nav2 control rate, NVBlox default, thermal envelope, model memory
  budget).

## [0.1.0] — 2026-05-05

### Added — Phase 1 v0.1

#### Core
- `openbrain_msgs` — `SystemHealth`, `MissionStatus`, `Waypoint`, `ThermalZone`,
  `PowerRail` messages plus `LoadMission` and `SetSpeedProfile` services.
- `openbrain_bringup` — `mini.launch.py` and `max.launch.py` with auto-detected
  robot adapter (`/etc/openbrain/robot.conf` → env → CLI override).
- `openbrain_msgs/SystemHealth.msg` shape locked to v1 for the dashboard.

#### Drivers
- `openbrain_drivers_realsense` — dual D435i / D456 with serial-number
  remapping into `/camera/{front,back}/*`.
- Phase-3 stubs for `livox`, `hesai`, `xsens`, `flir_boson`, `ti_mmwave`,
  `quectel_5g`.

#### Navigation & perception
- `openbrain_slam` — RTAB-Map RGB-D defaults, persistent map at
  `/maps/openbrain.db`, localization-only mode.
- `openbrain_nav` — Nav2 stack with a custom behavior tree
  (`nav_to_pose_bt.xml`), tuned for a 0.22 m-radius indoor robot.
- `openbrain_perception` — YOLOv11 + NVBlox launch scaffolds for Phase 2.

#### Teleop
- `openbrain_teleop` — `rosbridge_websocket` on `:9090` and an aiortc-based
  video streamer on `:8080` exposing `POST /stream/{name}/offer`,
  `GET /stream/{name}.mjpeg`, `GET /stream/{name}/snapshot`.

#### Safety & control
- `openbrain_safety` — `twist_mux` priority arbitration, dead-man switch,
  emergency-stop, watchdog timer.
- `openbrain_joystick` — gamepad → `/cmd_vel` with PS5/Xbox/generic mappings.

#### Recording & diagnostics
- `openbrain_recording` — rosbag2 wrapper that records on `/recording/start`
  and stops on `/recording/stop`, files land in `/recordings/`.
- `openbrain_diagnostics` — hardware self-test (cameras, GPU, network, disk,
  thermal, ROS topics) emitting on `/diagnostics`.

#### Simulation
- `openbrain_simulation` — Gazebo bringup with a sim mobile robot so the
  full stack runs without hardware.

#### Robot adapters
- `openbrain_robots_generic` — `RobotAdapter` base class (speed-profile clamp,
  `/teleop/set_speed_profile` service, latched `/robot_description`).
- `openbrain_robots_unitree_go2` — high-level Move + odom from HighState,
  lazy SDK import.
- `openbrain_robots_unitree_g1` — Phase-2 scaffold.
- `openbrain_robots_tita` — Phase-2 scaffold.

#### Model Hub
- `openbrain_modelhub` — synchronous client for `api.openkinematics.com/v1`
  with SHA-256 verification, atomic downloads, `modelhub_pull` /
  `modelhub_list` console scripts.

#### Demos
- `cockpit`, `health`, `missions` shipped as full implementations.
- 17 additional demo packages scaffolded (`my-ui`, `profile`, `fleet-control`,
  `groot-vla-pick-place`, `openvla-grasp`, `diffusion-policy`, `lerobot-act`,
  `yolo-perception`, `nvblox-mapping`, `rememb-r-navigation`,
  `rosa-voice-control`, `vslam-gps-denied`, `humanoid-locomotion`,
  `quadruped-patrol`, `warehouse-pick`, `edge-nerf`, `vlm-isaac-sim`).

#### CLI tooling
- `openbrain` / `ob` console command — `status`, `doctor`, `teleop`,
  `record`, `play`, `update`, `logs`.

#### Infrastructure
- `docker/Dockerfile.jetson` — multi-layer image based on
  `nvcr.io/nvidia/l4t-jetpack:r36.2`.
- `docker/docker-compose.yml` and dev overlay (`docker-compose.dev.yml`).
- `.devcontainer/` for VS Code remote dev.
- `Makefile` — common targets (`make build`, `make test`, `make image`,
  `make lint`, `make sim`).
- `install.sh` — interactive robot-type prompt, Docker + NVIDIA toolkit
  autoinstall, post-install hardware self-test.
- `utils/` — `calibrate_cameras.py`, `upload_logs.sh`, `discover_robot.py`,
  `factory_reset.sh`, `setup_wifi.sh`, `joystick_test.py`.

#### Governance
- `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`, GitHub issue/PR
  templates, dependabot config, `.pre-commit-config.yaml`.

#### CI / quality
- `.github/workflows/build.yml` — `colcon build` + `colcon test` inside the
  ROS Humble container.
- `.github/workflows/lint.yml` — `ruff`, `clang-format-15`, `shellcheck`.
- `.github/workflows/docker.yml` — multi-arch image build, push to GHCR on
  `main` and tags.
- 4 packages ship unit tests (`openbrain_robots_generic`,
  `openbrain_teleop`, `openbrain_demos_health`, `openbrain_demos_missions`,
  `openbrain_modelhub`).

[Unreleased]: https://github.com/openkinematics/openbrain-ros/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/openkinematics/openbrain-ros/releases/tag/v0.1.0
