"""Entry point for the `openbrain` / `ob` CLI.

Sub-commands intentionally lazy-import their heavy dependencies so that
e.g. `openbrain --version` doesn't need rclpy on the path.
"""

from __future__ import annotations

import argparse
import sys

from openbrain_cli import __version__


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="openbrain",
        description="OpenBrain operator CLI.",
    )
    p.add_argument("--version", action="version", version=f"openbrain {__version__}")

    sub = p.add_subparsers(dest="cmd", required=True, metavar="<command>")

    sub.add_parser("status", help="Robot type, IPs, running ROS nodes, recent logs.")

    sp_doctor = sub.add_parser("doctor", help="Run hardware self-test.")
    sp_doctor.add_argument("--json", action="store_true")
    sp_doctor.add_argument("--no-color", action="store_true")

    sp_teleop = sub.add_parser("teleop", help="Interactive WASD teleop in this terminal.")
    sp_teleop.add_argument("--linear", type=float, default=0.5)
    sp_teleop.add_argument("--angular", type=float, default=1.0)

    sp_rec = sub.add_parser("record", help="Start a rosbag2 recording (calls /recording/start).")
    sp_rec.add_argument(
        "name",
        nargs="?",
        default=None,
        help="(reserved) custom bag name; not yet honored by the service.",
    )

    sub.add_parser("stop", help="Stop the active rosbag2 recording.")

    sp_play = sub.add_parser("play", help="Play back a rosbag2 from /recordings/<name>.")
    sp_play.add_argument("name", help="Bag name (directory under /recordings/).")
    sp_play.add_argument("--rate", type=float, default=1.0)

    sub.add_parser("logs", help="Tail journalctl -u openbrain -f.")

    sub.add_parser("update", help="Pull the latest image and restart the systemd unit.")

    sub.add_parser("estop", help="Engage the software e-stop (calls /safety/estop_engage).")
    sub.add_parser("estop-release", help="Release the software e-stop.")

    sub.add_parser("ip", help="Print the LAN IPs the dashboard can reach this robot at.")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "status": _cmd_status,
        "doctor": _cmd_doctor,
        "teleop": _cmd_teleop,
        "record": _cmd_record,
        "stop": _cmd_stop,
        "play": _cmd_play,
        "logs": _cmd_logs,
        "update": _cmd_update,
        "estop": _cmd_estop,
        "estop-release": _cmd_estop_release,
        "ip": _cmd_ip,
    }
    return dispatch[args.cmd](args)


# ---- commands -------------------------------------------------------------


def _cmd_status(_args) -> int:
    from openbrain_cli.commands import status

    return status.run()


def _cmd_doctor(args) -> int:
    from openbrain_diagnostics.doctor import main as doctor_main

    rc_args = []
    if args.json:
        rc_args.append("--json")
    if args.no_color:
        rc_args.append("--no-color")
    return doctor_main(rc_args)


def _cmd_teleop(args) -> int:
    from openbrain_cli.commands import teleop

    return teleop.run(linear=args.linear, angular=args.angular)


def _cmd_record(_args) -> int:
    from openbrain_cli.commands import recording

    return recording.start()


def _cmd_stop(_args) -> int:
    from openbrain_cli.commands import recording

    return recording.stop()


def _cmd_play(args) -> int:
    from openbrain_cli.commands import recording

    return recording.play(args.name, rate=args.rate)


def _cmd_logs(_args) -> int:
    from openbrain_cli.commands import logs

    return logs.run()


def _cmd_update(_args) -> int:
    from openbrain_cli.commands import update

    return update.run()


def _cmd_estop(_args) -> int:
    from openbrain_cli.commands import safety

    return safety.engage()


def _cmd_estop_release(_args) -> int:
    from openbrain_cli.commands import safety

    return safety.release()


def _cmd_ip(_args) -> int:
    from openbrain_cli.commands import status

    return status.print_ips()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
