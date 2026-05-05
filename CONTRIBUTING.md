# Contributing to OpenBrain ROS

Thanks for taking the time to contribute. This guide covers everything from
your first PR to landing a new robot adapter.

## Table of contents

- [Quick start](#quick-start)
- [Development environment](#development-environment)
- [Project layout](#project-layout)
- [Coding conventions](#coding-conventions)
- [Testing](#testing)
- [Commit style](#commit-style)
- [Pull request flow](#pull-request-flow)
- [Adding a new demo](#adding-a-new-demo)
- [Adding a new robot adapter](#adding-a-new-robot-adapter)
- [Adding a new sensor driver wrapper](#adding-a-new-sensor-driver-wrapper)
- [Releasing](#releasing)
- [Code of Conduct](#code-of-conduct)

## Quick start

```bash
git clone https://github.com/openkinematics/openbrain-ros
cd openbrain-ros
make dev          # spins up the dev container with the workspace mounted
make build        # colcon build inside it
make test         # ament + pytest
make lint         # ruff + clang-format + shellcheck
```

For non-trivial changes, open an issue first to discuss the approach.

## Development environment

| Path | Use it for |
|---|---|
| `make dev` | Interactive shell in a ROS Humble dev container. Recommended. |
| `.devcontainer/` | VS Code "Reopen in Container". |
| `docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up` | Long-running services (rosbridge + streamer) for dashboard work. |
| `make sim` | Bring up the Gazebo simulation profile (no hardware needed). |
| Native ROS Humble on Ubuntu 22.04 | Possible, but you'll fight `rosdep` more than you'd like. |

The dev container ships ROS 2 Humble + RealSense + Nav2 + RTAB-Map + the pip
deps the streamer needs (aiortc, aiohttp, av, psutil, requests).

## Project layout

```
openbrain-ros/
├── src/                         # ROS 2 packages (38)
│   ├── openbrain_msgs/          # contracts shared with the dashboard
│   ├── openbrain_bringup/       # mini / max launch composition
│   ├── openbrain_drivers_*/     # sensor wrappers
│   ├── openbrain_slam/          # RTAB-Map config
│   ├── openbrain_nav/           # Nav2 + behavior tree
│   ├── openbrain_perception/    # YOLO + NVBlox
│   ├── openbrain_teleop/        # rosbridge + WebRTC streamer
│   ├── openbrain_safety/        # twist_mux, dead-man, e-stop
│   ├── openbrain_joystick/      # gamepad input
│   ├── openbrain_recording/     # rosbag2 wrapper
│   ├── openbrain_diagnostics/   # hardware self-test
│   ├── openbrain_simulation/    # Gazebo bringup
│   ├── openbrain_robots/        # vendor adapters (Go2, G1, Tita, generic)
│   ├── openbrain_modelhub/      # SaaS policy deployment client
│   ├── openbrain_cli/           # `openbrain` / `ob` console command
│   └── openbrain_demos/         # 20 demo packages
├── docker/                      # Dockerfile + compose files
├── docs/                        # api.md, installation.md, etc.
├── config/                      # mini.yaml, max.yaml
├── utils/                       # standalone helper scripts
├── install.sh                   # one-shot installer
├── Makefile                     # common dev tasks
└── .github/                     # CI, templates, dependabot
```

Each ROS package follows the [REP 149](https://www.ros.org/reps/rep-0149.html)
package format 3 spec. Python packages are `ament_python`; C++ and metadata
packages are `ament_cmake`.

## Coding conventions

### Python

- Target Python **3.10** (Jetson JetPack 6.2 ships 3.10).
- Format with **ruff** (`ruff check src/` is part of CI). Config in `pyproject.toml`.
- Type-hint public APIs. Use `from __future__ import annotations` so forward
  references work without quoting.
- Keep modules under ~300 lines; if a file grows past that, consider splitting.
- Prefer `dataclasses.dataclass(frozen=True)` for plain value objects.

### C++

- Target **C++17**.
- Format with **clang-format-15** (`.clang-format` in repo root).
- Default to `rclcpp::Node` over LifecycleNode unless you need lifecycle.

### Launch files

- Always implement `generate_launch_description() -> LaunchDescription`.
- Declare every `LaunchConfiguration` with a sensible `default_value`.
- Skip optional hardware with `IfCondition` so partial-hardware boxes still
  launch — never let a missing camera / LiDAR crash the bringup.

### Logging

- ROS logger only (`self.get_logger().info(...)`). No bare `print`.
- One log line per state transition; not one per loop iteration.

### Per-package READMEs

Every package needs a `README.md`. Use the canonical template at
[`docs/package-readme-template.md`](docs/package-readme-template.md) —
same headings, same first-line shape, no "TODO: package description"
placeholders. Linting against the template lands in CI for Phase 2.

## Testing

- ROS package tests live under `<package>/test/test_*.py`.
- Use plain `pytest` for pure-Python logic; reach for `launch_testing` only when
  testing launch composition.
- Keep helpers that tests want to import in a small **rclpy-free**
  module (e.g. `openbrain_safety/sources.py`,
  `openbrain_recording/defaults.py`). Pytest collects without rclpy on
  developer laptops, so a single top-level `import rclpy` in the
  module under test breaks `make test`.
- For `ament_cmake` packages, register tests with
  `ament_add_pytest_test(<name> test/<file>.py)` inside an
  `if(BUILD_TESTING)` block, and add `ament_cmake_pytest` plus
  `python3-pytest` to `<test_depend>` in `package.xml`. See
  [`openbrain_msgs/CMakeLists.txt`](src/openbrain_msgs/CMakeLists.txt)
  for the pattern.
- `make test` runs `colcon test` then surfaces results.
- New code should not lower coverage. Add a test for every bug you fix.

## Commit style

We use a relaxed [Conventional Commits](https://www.conventionalcommits.org/)
flavor:

```
feat(safety): add watchdog that publishes zero-velocity on /cmd_vel timeout
fix(teleop): handle MJPEG client disconnect without leaking aiohttp tasks
docs(api): clarify yaw frame convention in Waypoint.msg
```

Allowed types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`,
`ci`, `build`. Scope is the package or area, lowercase.

Sign off your commits with `Signed-off-by:` (DCO).

## Pull request flow

1. Fork → branch off `main` → push → open PR.
2. Fill in the PR template (what / why / how-tested / breaking-change?).
3. CI must be green: `build`, `lint`, `docker` workflows.
4. One reviewer approval is enough for non-breaking PRs; two for changes that
   touch `openbrain_msgs/` or any v1 contract.
5. Squash-merge by default.

## Adding a new demo

1. Pick a slug (kebab-case) and add a row to
   [`src/openbrain_demos/README.md`](src/openbrain_demos/README.md).
2. Copy the structure of an existing 🟢 demo (`cockpit`, `health`, or
   `missions`) — they show the canonical layout.
3. Each demo needs `package.xml`, `setup.py` (or `CMakeLists.txt`),
   `launch/<slug>.launch.py`, `<slug>/` Python module if applicable, and a
   `README.md` matching the
   [package README template](docs/package-readme-template.md).
4. The marketing site at
   [openkinematics.com/demos](https://www.openkinematics.com/demos)
   pulls demo metadata directly from this folder — no separate registry
   to update.

## Adding a new robot adapter

1. Copy `src/openbrain_robots/generic/` to `src/openbrain_robots/<robot>/`.
2. Rename the Python package to `openbrain_robots_<robot>` and update
   `setup.py`, `package.xml`, the resource marker, and `setup.cfg`.
3. Subclass `RobotAdapter`. Override `send_velocity(twist)`. Optionally
   override `read_odometry()` if your SDK exposes an odom stream.
4. Add the new robot to
   [`openbrain_bringup/launch/_robot_type.py :: ADAPTER_PACKAGES`](src/openbrain_bringup/launch/_robot_type.py)
   and to the `VALID` enum.
5. Add a row to [`docs/supported-robots.md`](docs/supported-robots.md) with
   status (🟢 / 🟡 / 🔴).
6. Tests: at minimum a unit test that the adapter clamps velocity correctly
   under each speed profile.

## Adding a new sensor driver wrapper

1. Copy `src/openbrain_drivers/realsense/` (or one of the stubs) as the
   template.
2. Wrap the upstream driver — do not vendor source code, depend on the apt
   package.
3. Document expected topics + frames in the package README.
4. If the driver requires UDP/multicast, document the firewall ports in
   [`docs/troubleshooting.md`](docs/troubleshooting.md).

## Releasing

Tag releases as `vMAJOR.MINOR.PATCH` (semver). The `docker.yml` workflow
publishes `ghcr.io/openkinematics/openbrain-ros:<version>` and `:latest` on
push to `main` and on tag push. Update `CHANGELOG.md` in the release PR.

## Code of Conduct

We follow the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind, assume
good intent, give credit. Disagreements get resolved in PR threads, not
personal attacks.

## License

By contributing, you agree your work is released under the
[MIT License](./LICENSE).
