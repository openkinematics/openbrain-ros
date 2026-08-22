# Edge runtime status

`openbrain_connector` is an optional, read-only observability service for
robots running a lineage-pinned OpenKinematics skill. It joins a fail-closed
hardware profile with an `openkinematics.edge-skill.v1` descriptor and exposes
`openbrain.connector.status.v1` to OpenBrain Dashboard.

The contract describes a robot-side edge runtime, not a hardware SKU. It can
run on Kinematics Mini, Kinematics Max, Raspberry Pi, a compatible Jetson, or a
custom ARM64/x86_64 computer. A normal Dashboard connection does not require
this service; ROS and video continue to use ports `9090` and `8080`.

## System boundary

```text
openkinematics-skillops
  └─ exports a non-secret, lineage-pinned skill descriptor

robot-side edge host
  ├─ owns sensors, timestamps, watchdogs, limits, and physical safety gates
  ├─ runs rosbridge :9090 and video :8080
  └─ exposes read-only edge status :8090

remote inference host (optional)
  └─ receives observations and returns action proposals, never motor access

openbrain-dashboard
  └─ observes ROS, video, runtime lineage, and closed/open safety state
```

The Dashboard is not in the inference timing loop. The connector has no
actuator object, calibration route, manual-control route, or command endpoint.
Every POST returns `405 Method Not Allowed`.

## Hardware profile

New profiles should use an optional hardware-neutral section:

```json
{
  "mode": "shadow",
  "edge_runtime": {
    "platform": "custom-arm64",
    "required_architecture": "aarch64"
  }
}
```

Existing v1 profiles with a `raspberry_pi` section remain accepted. If neither
section is present, the connector reports the actual hostname and architecture
and leaves `requiredArchitecture` unset. Missing camera, servo, e-stop, or
certification sections always resolve to unavailable/false; missing data can
never widen authority.

## Prepare the inputs

Export an active skill descriptor from SkillOps:

```bash
ok-skillops export-edge-descriptor \
  --hardware-profile /path/to/hardware-profile.json \
  --skill-id my-skill \
  --skill-name "My skill" \
  --skill-version 1 \
  --output /etc/openbrain/active-skill.json
```

The descriptor carries release/checkpoint/spec hashes but no session key,
device path, or actuator authorization. Connector startup fails when robot
identity or lineage differs, or when the hardware profile opens a motor gate.

## Start the service

Run it directly:

```bash
openbrain_connector \
  --hardware-profile /etc/openbrain/hardware-profile.json \
  --skill-descriptor /etc/openbrain/active-skill.json \
  --runtime-state /run/openbrain/skill-runtime.json \
  --bind 127.0.0.1 \
  --port 8090 \
  --allow-origin https://dashboard.openkinematics.com
```

Or start the standalone ROS launch file:

```bash
ros2 launch openbrain_connector connector.launch.py \
  hardware_profile:=/etc/openbrain/hardware-profile.json \
  skill_descriptor:=/etc/openbrain/active-skill.json \
  allowed_origin:=https://dashboard.openkinematics.com
```

Mini and Max bringup provide the same service behind
`enable_edge_status:=true`. It is `false` by default.

## Private access

Bind the service to loopback and expose it only through a private TLS route,
for example Tailscale Serve or an authenticated reverse proxy. Configure the
exact Dashboard origin for CORS. A hosted HTTPS Dashboard must use an HTTPS
edge-status URL; browsers block mixed content.

In Dashboard, add the base URL under:

```text
Fleet → Add/Edit robot → Advanced runtime monitoring
```

Dashboard polls `GET /v1/status`. The endpoint is never used for ROS, video,
inference transport, or control commands.

## Runtime telemetry

An optional supervisor may atomically replace the runtime-state JSON using
schema `openbrain.connector.runtime.v1`. Only inference connectivity,
heartbeat freshness, proposal counters, latency, and a decision reason are
accepted. Unknown authority fields are ignored, and runtime telemetry cannot
enable a motor gate.

## Version 1 scope

Ready now:

- release-to-robot identity and lineage validation;
- fail-closed profile checks;
- exact-origin CORS;
- read-only runtime, camera, e-stop, inference, and skill status;
- explicit disabled calibration, manual-control, and actuation capabilities.

Not included:

- camera or servo discovery;
- calibration;
- actuator gateway;
- motor commands;
- policy execution.

Those capabilities require separate hardware-specific packages, physical
safety evidence, and explicit operator authorization.
