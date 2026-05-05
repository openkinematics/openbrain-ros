"""Argparse-only tests for the CLI dispatcher."""

import pytest
from openbrain_cli.main import _build_parser


def test_version_flag():
    parser = _build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0


@pytest.mark.parametrize(
    "cmd",
    [
        "status",
        "doctor",
        "teleop",
        "record",
        "stop",
        "play",
        "logs",
        "update",
        "estop",
        "estop-release",
        "ip",
    ],
)
def test_subcommands_recognised(cmd):
    parser = _build_parser()
    extra = ["foo"] if cmd == "play" else []
    args = parser.parse_args([cmd, *extra])
    assert args.cmd == cmd


def test_doctor_flags():
    parser = _build_parser()
    args = parser.parse_args(["doctor", "--json", "--no-color"])
    assert args.json and args.no_color
