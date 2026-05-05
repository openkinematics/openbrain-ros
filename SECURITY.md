# Security policy

## Supported versions

We actively maintain the latest minor release on the `main` branch. Security
fixes are backported to the previous minor release for **90 days** after a new
minor ships.

| Version | Status |
|---|---|
| `0.1.x` | ✅ supported |
| `< 0.1`  | ❌ not supported |

## Reporting a vulnerability

**Please do not file a public issue for security vulnerabilities.**

Email `security@openkinematics.com` with:

- a description of the vulnerability,
- steps to reproduce (or a proof-of-concept),
- the version / commit you tested,
- your assessment of impact (denial-of-service, code execution, data leak, …),
- whether the issue is already public.

We will acknowledge receipt within **2 business days** and aim to provide a
remediation timeline within **5 business days**. Coordinated disclosure
windows are typically 30–90 days depending on severity.

We support PGP-encrypted reports — request our public key in your first email
and we will reply with the fingerprint via a separate channel.

## Scope

In scope:

- The OpenBrain ROS workspace and any package under `src/openbrain_*`.
- The Docker images we publish to `ghcr.io/openkinematics/openbrain-ros`.
- The installer at `install.sh` and the systemd unit it provisions.
- The HTTP video streamer (`openbrain_teleop`) and rosbridge endpoints.
- The Model Hub client (`openbrain_modelhub`).

Out of scope:

- Vulnerabilities in upstream ROS 2 / Nav2 / RTAB-Map / aiortc itself — please
  report those upstream and link us in CC.
- Vendor SDKs we wrap (Unitree, Intel RealSense, NVIDIA, Livox, Hesai, …).
- Vulnerabilities that require physical access to the robot.

## Hardening recommendations

- Run the rosbridge WebSocket on a private network or behind a TLS terminator
  (the dashboard supports `wss://`). The default install binds `0.0.0.0:9090`.
- The video streamer (`:8080`) likewise should not be exposed to the public
  internet without TLS + auth in front. Use a reverse proxy.
- Set `OPENBRAIN_API_TOKEN` for Model Hub access via `/etc/openbrain/api.env`
  (chmod 0600), not via shell history.
- Keep `/etc/openbrain/robot.conf` mode 0644 — it contains no secrets, but
  treat anything you add to that file as world-readable.

## Hall of thanks

We credit reporters in `CHANGELOG.md` under each release unless they request
anonymity. Coordinated disclosures may also be acknowledged in a release blog
post on `openkinematics.com`.
