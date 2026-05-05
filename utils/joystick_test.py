#!/usr/bin/env python3
"""Verify a connected gamepad without touching ROS.

Reads ``/dev/input/js0`` directly via the linux joystick API, prints axis
and button events as they happen, and prints the index of the first axis
or button to flip — so you can fill in the YAML mapping for a new pad.

Usage:
    python3 utils/joystick_test.py [--device /dev/input/js0]
"""

from __future__ import annotations

import argparse
import struct
import sys

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default="/dev/input/js0")
    args = parser.parse_args(argv)

    try:
        fh = open(args.device, "rb")  # noqa: SIM115 — long-lived; closed in finally
    except OSError as exc:
        print(f"could not open {args.device}: {exc}", file=sys.stderr)
        return 2

    print(f"reading {args.device} — press buttons / move sticks (Ctrl-C to quit)\n")
    print(f"{'time(ms)':>10}  {'kind':>6}  {'idx':>3}  value")
    print("-" * 40)

    with fh:
        try:
            while True:
                data = fh.read(8)
                if len(data) != 8:
                    break
                time_ms, value, kind, idx = struct.unpack("IhBB", data)
                kind_name = (
                    "BUTTON" if kind & JS_EVENT_BUTTON else "AXIS" if kind & JS_EVENT_AXIS else "?"
                )
                initial = " (init)" if kind & JS_EVENT_INIT else ""
                print(f"{time_ms:>10}  {kind_name:>6}  {idx:>3}  {value:>6}{initial}")
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
