"""Pure-Python store + schema tests. No rclpy."""

from __future__ import annotations

import tempfile
from pathlib import Path

from openbrain_demos_profile.store import Profile, ProfileStore, coerce


def test_coerce_drops_unknown_keys():
    p = coerce({"theme": "dark", "evil_key": "rm -rf"})
    assert not hasattr(p, "evil_key")
    assert p.theme == "dark"


def test_coerce_clamps_invalid_choice():
    p = coerce({"theme": "neon-purple"})
    assert p.theme == "dark"  # default


def test_coerce_clamps_invalid_language():
    p = coerce({"language": "klingon"})
    assert p.language == "en"


def test_coerce_clamps_invalid_speed_profile():
    p = coerce({"default_speed_profile": "ludicrous"})
    assert p.default_speed_profile == "normal"


def test_coerce_clamps_invalid_pad():
    p = coerce({"pad_layout": "wheel"})
    assert p.pad_layout == "xbox"


def test_accent_color_must_be_hex():
    p = coerce({"accent_color": "blue"})
    assert p.accent_color == "#76b900"


def test_accent_color_short_hex_ok():
    p = coerce({"accent_color": "#abc"})
    assert p.accent_color == "#abc"


def test_save_then_load_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        original = Profile(
            user="alex",
            theme="light",
            accent_color="#ff8800",
            language="pt",
            default_speed_profile="beginner",
        )
        path = store.save(original)
        assert path.exists()
        # Fresh store, same root.
        store2 = ProfileStore(tmp)
        loaded = store2.load("alex")
        assert loaded.user == "alex"
        assert loaded.theme == "light"
        assert loaded.accent_color == "#ff8800"
        assert loaded.language == "pt"
        assert loaded.default_speed_profile == "beginner"


def test_load_missing_user_returns_default():
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        loaded = store.load("nonexistent")
        assert loaded.user == "nonexistent"
        assert loaded.theme == "dark"


def test_load_corrupt_yaml_falls_back_to_default():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "broken.yaml"
        path.write_text(": : not yaml : :")
        store = ProfileStore(tmp)
        loaded = store.load("broken")
        assert loaded.theme == "dark"  # default


def test_save_uses_safe_filename():
    """``user`` strings with slashes / dots must not escape the root."""
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        store.save(Profile(user="../../../etc/passwd"))
        # file should land somewhere under tmp, not at /etc/passwd
        files = list(Path(tmp).glob("*.yaml"))
        assert len(files) == 1
        assert "passwd" in files[0].name


def test_list_users():
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        store.save(Profile(user="alex"))
        store.save(Profile(user="zara"))
        assert store.list_users() == ["alex", "zara"]


def test_to_json_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        store.save(Profile(user="alex", language="es"))
        body = store.to_json()
        import json

        parsed = json.loads(body)
        assert parsed["user"] == "alex"
        assert parsed["language"] == "es"


def test_yaml_on_disk_keeps_canonical_order():
    """Field order matters for stable diffs."""
    with tempfile.TemporaryDirectory() as tmp:
        store = ProfileStore(tmp)
        store.save(Profile(user="alex"))
        body = (Path(tmp) / "alex.yaml").read_text()
        # 'user' should appear before 'theme' which appears before 'accent_color'
        assert body.find("user:") < body.find("theme:") < body.find("accent_color:")
