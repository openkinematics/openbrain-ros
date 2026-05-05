"""HTTP client for the OpenKinematics Model Hub.

The Model Hub is the SaaS surface at ``https://api.openkinematics.com/v1`` that
distributes trained RL / VLA policies. Endpoints (Phase-2 contract, subject to
coordination with the SaaS team):

  GET  /v1/models                       -> list available models
  GET  /v1/models/{id}                  -> model metadata + checksum + URL
  GET  /v1/models/{id}/download         -> 302 redirect to a signed CDN URL

Auth is a bearer token (``OPENBRAIN_API_TOKEN``) that the user provisions on
their OpenKinematics account. The client is intentionally synchronous and
network-only — it owns no ROS state, so it can run from a CLI, a systemd
timer, or be imported by a launch hook.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import requests

DEFAULT_BASE_URL = "https://api.openkinematics.com/v1"
DEFAULT_LOCAL_ROOT = Path("/opt/openbrain/models")
TOKEN_ENV = "OPENBRAIN_API_TOKEN"


@dataclass(frozen=True)
class ModelMetadata:
    id: str
    name: str
    version: str
    framework: str  # e.g. "tensorrt", "torchscript", "openvla"
    sha256: str
    size_bytes: int
    download_url: str  # signed CDN URL or proxy path


class ModelHubClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        token: str | None = None,
        local_root: Path = DEFAULT_LOCAL_ROOT,
        session: requests.Session | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token or os.environ.get(TOKEN_ENV)
        self._local_root = local_root
        self._session = session or requests.Session()

    def list(self) -> list[ModelMetadata]:
        data = self._get("/models")
        return [_parse(entry) for entry in data.get("models", [])]

    def get(self, model_id: str) -> ModelMetadata:
        return _parse(self._get(f"/models/{model_id}"))

    def pull(self, model_id: str, *, force: bool = False) -> Path:
        """Download a model into ``local_root/<model_id>/<version>/<filename>``.

        Verifies the SHA-256 checksum and returns the local path. If the
        target file already exists with the right checksum, it's reused
        unless ``force=True``.
        """
        meta = self.get(model_id)
        target_dir = self._local_root / meta.id / meta.version
        filename = meta.download_url.rsplit("/", 1)[-1].split("?", 1)[0] or "model.bin"
        target = target_dir / filename

        if target.exists() and not force and _sha256(target) == meta.sha256:
            return target

        target_dir.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".part")
        with self._session.get(meta.download_url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    if chunk:
                        fh.write(chunk)

        actual = _sha256(tmp)
        if actual != meta.sha256:
            tmp.unlink(missing_ok=True)
            raise IntegrityError(meta.id, expected=meta.sha256, actual=actual)

        shutil.move(str(tmp), target)
        return target

    # ---- internal -----------------------------------------------------

    def _get(self, path: str) -> dict:
        url = f"{self._base_url}{path}"
        resp = self._session.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _headers(self) -> dict[str, str]:
        h = {"User-Agent": "openbrain-modelhub/0.1"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h


class IntegrityError(RuntimeError):
    def __init__(self, model_id: str, *, expected: str, actual: str) -> None:
        super().__init__(f"checksum mismatch for {model_id}: expected {expected}, got {actual}")
        self.model_id = model_id
        self.expected = expected
        self.actual = actual


def _parse(entry: dict) -> ModelMetadata:
    return ModelMetadata(
        id=entry["id"],
        name=entry["name"],
        version=entry["version"],
        framework=entry["framework"],
        sha256=entry["sha256"],
        size_bytes=int(entry.get("size_bytes", 0)),
        download_url=entry["download_url"],
    )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_local_models(root: Path = DEFAULT_LOCAL_ROOT) -> Iterable[Path]:
    if not root.exists():
        return
    for model_dir in sorted(root.iterdir()):
        if not model_dir.is_dir():
            continue
        for version_dir in sorted(model_dir.iterdir()):
            if version_dir.is_dir():
                yield version_dir
