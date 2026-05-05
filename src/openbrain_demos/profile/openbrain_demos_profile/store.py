"""Pure-Python profile store. No rclpy — testable on any host.

A profile is a flat dict serialized as YAML at ``<root>/<user>.yaml``.
The store enforces the known-keys schema (extra keys are dropped at
write time so a malformed dashboard payload can't silently inject
arbitrary state) and clamps values to the ranges declared by
:data:`SCHEMA`.

The dashboard's Profile page is the primary client. It reads via
``/profile/get`` (latched ``/profile/active`` topic also republishes on
change) and writes via ``/profile/set``.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

import yaml

# ---- schema --------------------------------------------------------------


VALID_THEMES = {"light", "dark", "system"}
VALID_SPEED_PROFILES = {"beginner", "normal", "insane"}
VALID_LANGUAGES = {"en", "pt", "es", "fr", "zh-CN", "de"}
VALID_PADS = {"xbox", "ps5", "generic"}


@dataclass
class Profile:
    """A single operator's preferences.

    Field order is the canonical write-order so YAML diffs are stable.
    """

    user: str = "default"
    display_name: str = ""
    theme: str = "dark"
    accent_color: str = "#76b900"  # NVIDIA-green by default
    language: str = "en"
    default_speed_profile: str = "normal"
    default_camera: str = "front"
    pad_layout: str = "xbox"
    cockpit_layout: dict = field(default_factory=dict)
    custom_keybinds: dict = field(default_factory=dict)


# Per-field clamp/coerce table. Anything not listed here is passed through
# unchanged (cockpit_layout / custom_keybinds are operator-defined blobs).
SCHEMA: dict = {
    "user": {"type": str},
    "display_name": {"type": str},
    "theme": {"type": str, "choices": VALID_THEMES, "default": "dark"},
    "accent_color": {"type": str},  # validated as hex below
    "language": {"type": str, "choices": VALID_LANGUAGES, "default": "en"},
    "default_speed_profile": {"type": str, "choices": VALID_SPEED_PROFILES, "default": "normal"},
    "default_camera": {"type": str},
    "pad_layout": {"type": str, "choices": VALID_PADS, "default": "xbox"},
    "cockpit_layout": {"type": dict, "default": {}},
    "custom_keybinds": {"type": dict, "default": {}},
}


def coerce(payload: dict) -> Profile:
    """Build a :class:`Profile` from an arbitrary dict, dropping unknown
    fields and clamping known ones to their valid ranges."""
    known = {f.name for f in fields(Profile)}
    cleaned: dict = {}
    for k in known:
        if k not in payload:
            continue
        v = payload[k]
        spec = SCHEMA.get(k, {})
        # Type coerce
        if spec.get("type") is dict:
            v = dict(v) if isinstance(v, dict) else {}
        else:
            v = "" if v is None else str(v)
        # Choices clamp
        choices = spec.get("choices")
        if choices and v not in choices:
            v = spec.get("default", v)
        cleaned[k] = v
    # accent_color sanity (not in choices but bounded)
    if "accent_color" in cleaned and not _looks_like_hex(cleaned["accent_color"]):
        cleaned["accent_color"] = "#76b900"
    return Profile(**cleaned)


def _looks_like_hex(s: str) -> bool:
    if not s.startswith("#") or len(s) not in (4, 7):
        return False
    return all(c in "0123456789abcdefABCDEF" for c in s[1:])


# ---- store ---------------------------------------------------------------


DEFAULT_ROOT = Path("/opt/openbrain/profiles")


class ProfileStore:
    """File-backed store. One YAML per user. Atomic writes (tmp + rename)."""

    def __init__(self, root: Path | str = DEFAULT_ROOT) -> None:
        self._root = Path(root)
        self._active: Profile | None = None

    @property
    def root(self) -> Path:
        return self._root

    def list_users(self) -> list[str]:
        if not self._root.exists():
            return []
        return sorted(p.stem for p in self._root.glob("*.yaml"))

    def load(self, user: str = "default") -> Profile:
        path = self._path_for(user)
        if not path.exists():
            profile = Profile(user=user)
        else:
            try:
                payload = yaml.safe_load(path.read_text()) or {}
            except yaml.YAMLError:
                profile = Profile(user=user)
            else:
                payload["user"] = user
                profile = coerce(payload)
        self._active = profile
        return profile

    def save(self, profile: Profile) -> Path:
        coerced = coerce(asdict(profile))
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._path_for(coerced.user)
        tmp = path.with_suffix(".yaml.tmp")
        tmp.write_text(yaml.safe_dump(asdict(coerced), sort_keys=False))
        os.replace(tmp, path)
        self._active = coerced
        return path

    def active(self) -> Profile | None:
        return self._active

    def to_json(self, profile: Profile | None = None) -> str:
        target = profile if profile is not None else self._active
        if target is None:
            return "{}"
        return json.dumps(asdict(target))

    def _path_for(self, user: str) -> Path:
        safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in user) or "default"
        return self._root / f"{safe}.yaml"
