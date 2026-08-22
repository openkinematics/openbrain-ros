# Raspberry Pi skill runtime

This runbook prepares an explicitly authorized Raspberry Pi as the edge host
for an OpenKinematics live-shadow session. It does not authorize camera, servo,
GPIO, CAN, actuator, torque-enable, goal-position, or motor access. The
Raspberry Pi remains the only future edge authority; a remote inference host
may return signed action proposals but never receives motor access.

The read-only Dashboard integration is documented separately in
[`edge-runtime-status.md`](edge-runtime-status.md). Version 1 of
`openbrain_connector` reports status only: it does not capture cameras, run a
policy, calibrate a robot, or command hardware.

## Required authorization and inventory

Do not run this procedure until the operator explicitly authorizes Gate B for
the named Raspberry Pi target. Record the following values without guessing:

- Raspberry Pi model, RAM, OS image, storage, and power supply;
- intended Tailscale hostname and primary inference host;
- exact hardware-profile and active-skill descriptor paths;
- expected release, tree, checkpoint, observation-spec, action-spec, and
  embodiment SHA-256 identities.

Keep unknown values `null` in the hardware profile. Gate B must not enumerate
or open `/dev/video*`, `/dev/tty*`, GPIO, CAN, USB servo devices, or ROS
actuator endpoints.

## Read-only platform preflight

Run only against the authorized Pi. Preserve the output as dated Gate B
evidence, excluding secrets and unrelated user data.

```bash
hostnamectl
uname -m
cat /etc/os-release
df -h /
free -h
timedatectl show --property=NTPSynchronized --property=Timezone
tailscale status --json
```

The gate stops unless the architecture is `aarch64`, storage and memory are
adequate, clock synchronization is true, and the expected Tailscale identity
is present. Do not infer device bindings from host output.

## Non-root runtime identity

Create a dedicated system account with no interactive login. Use distribution
packages pinned for the recorded OS image, and preserve package names,
versions, licenses, and repository identities in the Gate B evidence.

```bash
sudo useradd --system --home /var/lib/openbrain-edge \
  --create-home --shell /usr/sbin/nologin openbrain-edge
sudo install -d -o root -g openbrain-edge -m 0750 /etc/openbrain
sudo install -d -o openbrain-edge -g openbrain-edge -m 0750 /run/openbrain
```

Do not add this account to groups that grant camera, serial, GPIO, CAN, Docker,
or actuator access during Gate B.

## External session secret

The authenticated shadow supervisor requires
`OPENKINEMATICS_EDGE_SESSION_KEY` with at least 32 random bytes. Store it
outside the repository and never print it in logs, evidence, shell history, or
the Dashboard. One acceptable root-only environment-file layout is:

```text
/etc/openbrain/edge-session.env
```

The file must be owned by `root:openbrain-edge`, mode `0640`, and contain only
the runtime variable. Generate and install it through an operator-reviewed
secret-management procedure. The read-only `openbrain_connector` neither
needs nor receives this secret. Rotation starts a new session and invalidates
all prior signed envelopes.

## Fail-closed inputs

Install two immutable, non-secret inputs:

```text
/etc/openbrain/hardware-profile.json
/etc/openbrain/active-skill.json
```

The profile must remain `mode: shadow`, with calibration absent, actuator
gateway absent, e-stop unverified, actuation unauthorized, motor commands
unauthorized, and servo writes disabled. The exported
`openkinematics.edge-skill.v1` descriptor must match the same robot and release
lineage. Connector startup must fail on a mismatch or open motor gate.

Validate the files before enabling a service:

```bash
openbrain_connector \
  --hardware-profile /etc/openbrain/hardware-profile.json \
  --skill-descriptor /etc/openbrain/active-skill.json \
  --runtime-state /run/openbrain/skill-runtime.json \
  --bind 127.0.0.1 \
  --port 8090 \
  --allow-origin https://dashboard.openkinematics.com
```

An initial missing runtime-state file is allowed and reports unavailable
telemetry. If present, it must use `openbrain.connector.runtime.v1` and be
atomically replaced by the local supervisor. Runtime telemetry cannot widen
hardware authority.

Before Pi deployment, run the SkillOps software-only contract audit with a
temporary external key. Its report is explicitly synthetic and cannot be used
as live-hardware evidence:

```bash
OPENKINEMATICS_EDGE_SESSION_KEY_FILE=/path/to/operator-managed-secret
export OPENKINEMATICS_EDGE_SESSION_KEY="$(<"$OPENKINEMATICS_EDGE_SESSION_KEY_FILE")"
python -m openkinematics_skillops.edge_contract_audit \
  --hardware-profile /path/to/so101-raspberry-pi-shadow-v1.json \
  --output /path/to/new-edge-contract-audit.json
unset OPENKINEMATICS_EDGE_SESSION_KEY
```

Do not use shell tracing while loading the key, and do not preserve the
environment or command output in evidence. The audit opens no network or
device interface and refuses to overwrite an existing report.

## Service boundary

Run the connector as `openbrain-edge`, with a read-only filesystem where the
host supports it, no device grants, and write access limited to
`/run/openbrain`. Bind to `127.0.0.1:8090`; expose only `GET /healthz` and
`GET /v1/status` through a private authenticated TLS route such as Tailscale
Serve. Configure an exact Dashboard origin. Every POST must return
`405 Method Not Allowed`.

The connector service must not load the edge session secret. A later,
separately reviewed shadow-supervisor service may read that secret and update
only `/run/openbrain/skill-runtime.json`. It still receives no camera or servo
device grants until the corresponding gate is separately authorized.

## Gate B verification

Gate B passes only when evidence confirms all of the following:

- pinned aarch64 OS/platform identity, sufficient storage and memory, clock
  synchronization, and the intended Tailscale hostname;
- connector runs as the dedicated non-root identity;
- the session secret is external, at least 32 bytes, permission-restricted,
  absent from repositories and captured output;
- profile and descriptor lineage match exactly;
- connector is reachable only through the intended private route;
- status reports all calibration, manual-control, actuation, and motor
  capabilities disabled;
- POST rejection, contract, wrong-lineage, tamper, replay, stale-message, and
  500 ms watchdog regression tests pass;
- camera and servo devices were not enumerated or opened, and actuator calls,
  motor commands, and hardware writes equal zero.

Gate B does not prove camera capture or authenticated live shadow. Two distinct
cameras require a separate Gate C authorization. Pi-to-inference HMAC
transport, network-loss behavior, immutable report/trace capture, and the rule
that every accepted proposal has `execute=false` require Gate D.

## Stop conditions

Stop immediately on an unexpected hostname, architecture, OS, Tailscale
identity, clock state, lineage hash, open hardware gate, public listener,
secret exposure, device access, or non-zero actuator/motor/write counter.
Preserve the failure as evidence without attempting a broader hardware probe.
