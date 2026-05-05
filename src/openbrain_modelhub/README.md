# openbrain_modelhub

Pulls trained RL / VLA policies from the **OpenKinematics Model Hub** SaaS
(`https://api.openkinematics.com/v1`) onto the edge box at
`/opt/openbrain/models/<id>/<version>/`.

Each download is checksummed (SHA-256) and atomic (`*.part` then rename), so a
mid-flight failure won't leave a half-written model on disk.

## CLI

```bash
# Pull (or refresh) a single model
modelhub_pull openvla-7b
# /opt/openbrain/models/openvla-7b/1.0.0/openvla-7b.safetensors

# List remote models on the Hub
modelhub_list --remote

# List models cached locally
modelhub_list
```

## Auth

Set `OPENBRAIN_API_TOKEN` in the environment (or `/etc/openbrain/api.env`).
Tokens are issued from the operator's OpenKinematics account.

## Contract (Phase 2)

| Endpoint | Returns |
|---|---|
| `GET /v1/models` | `{ models: ModelMetadata[] }` |
| `GET /v1/models/{id}` | `ModelMetadata` |
| Field `download_url` in `ModelMetadata` | URL the client streams from |

`ModelMetadata` fields: `id`, `name`, `version`, `framework`, `sha256`,
`size_bytes`, `download_url`.

This contract is coordinated with the SaaS team — pin to v1 and surface
`X-OpenBrain-Hub-Version` in responses for forward-compat.
