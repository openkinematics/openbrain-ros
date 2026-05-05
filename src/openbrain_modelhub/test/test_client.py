"""Unit tests that don't hit the network — exercise parsing + checksum."""

import hashlib
import tempfile
from pathlib import Path

from openbrain_modelhub.client import ModelMetadata, _parse, _sha256


def test_parse_metadata():
    meta = _parse(
        {
            "id": "openvla-7b",
            "name": "OpenVLA 7B Pick-Place",
            "version": "1.0.0",
            "framework": "openvla",
            "sha256": "deadbeef" * 8,
            "size_bytes": 12345,
            "download_url": "https://cdn.example/openvla-7b.safetensors?sig=x",
        }
    )
    assert isinstance(meta, ModelMetadata)
    assert meta.id == "openvla-7b"
    assert meta.framework == "openvla"
    assert meta.size_bytes == 12345


def test_sha256_round_trip():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"hello world")
        path = Path(f.name)
    try:
        assert _sha256(path) == hashlib.sha256(b"hello world").hexdigest()
    finally:
        path.unlink()
