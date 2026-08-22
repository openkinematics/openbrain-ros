# openbrain_connector

Read-only edge-status endpoint that joins an OpenKinematics SkillOps release to
the OpenBrain Dashboard. It runs on any compatible robot-side computer;
Kinematics Mini, Kinematics Max, a Raspberry Pi, and custom ARM64/x86 hosts use
the same HTTP contract. Version 1 reports configuration and safety state; it
cannot calibrate, command, or open a servo device.

## Inputs

- a fail-closed hardware profile from `openkinematics-skillops`;
- an `openkinematics.edge-skill.v1` descriptor exported by SkillOps.

Both inputs must pin the same robot and release lineage. Startup fails if any
motor gate is open or the lineage differs.

Hardware profiles may use the neutral `edge_runtime` section. Existing v1
profiles containing `raspberry_pi` remain supported for compatibility. If
neither section is present, the connector reports the actual hostname and
architecture and keeps the required architecture unset.

## Run on an edge host

```bash
openbrain_connector \
  --hardware-profile /etc/openbrain/so101-shadow.json \
  --skill-descriptor /etc/openbrain/active-skill.json \
  --runtime-state /run/openbrain/skill-runtime.json \
  --bind 127.0.0.1 \
  --port 8090 \
  --allow-origin http://localhost:3000
```

Expose `127.0.0.1:8090` to the operator through Tailscale Serve or an HTTPS
reverse proxy. Keep the service off public interfaces. Add the exact deployed
Dashboard origin with another `--allow-origin` argument.

The same service can be started through ROS launch:

```bash
ros2 launch openbrain_connector connector.launch.py \
  hardware_profile:=/etc/openbrain/hardware-profile.json \
  skill_descriptor:=/etc/openbrain/active-skill.json \
  allowed_origin:=https://dashboard.openkinematics.com
```

Mini and Max bringup expose this as `enable_edge_status:=true`; the default is
`false`, so existing robots do not start a status endpoint implicitly.

## HTTP contract

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/healthz` | liveness |
| `GET` | `/v1/status` | robot, runtime, active skill, hardware gates, telemetry |
| `OPTIONS` | `/v1/status` | browser CORS preflight |

Every `POST` returns `405 Method Not Allowed`. Control and calibration APIs are
not part of this package.

The optional runtime-state file lets the local shadow supervisor publish live
inference connectivity, heartbeat freshness, proposal counters, latency, and
its last decision. It must be atomically replaced and use schema
`openbrain.connector.runtime.v1`. Unknown authority fields are ignored; runtime
state can never enable a motor gate.
