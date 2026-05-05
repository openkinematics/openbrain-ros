"""``doctor`` console entry point.

Runs every check synchronously, prints a colorized table, and exits with
status 0 if all OK, 1 if any WARN, 2 if any ERROR. The CLI uses no rclpy
so it works even when the workspace isn't sourced.
"""

from __future__ import annotations

import argparse
import sys

from openbrain_diagnostics.checks import Severity, run_all_checks, to_json

COLOR = {
    Severity.OK: "\033[1;32m",  # green
    Severity.WARN: "\033[1;33m",  # yellow
    Severity.ERROR: "\033[1;31m",  # red
    Severity.UNKNOWN: "\033[1;90m",  # grey
}
RESET = "\033[0m"
LABEL = {Severity.OK: "OK", Severity.WARN: "WARN", Severity.ERROR: "FAIL", Severity.UNKNOWN: "??"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="openbrain-doctor", description="OpenBrain hardware self-test."
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of a table"
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI color")
    args = parser.parse_args(argv)

    results = run_all_checks()

    if args.json:
        print(to_json(results))
    else:
        _render_table(results, color=not args.no_color)

    if any(r.severity == Severity.ERROR for r in results):
        return 2
    if any(r.severity == Severity.WARN for r in results):
        return 1
    return 0


def _render_table(results, *, color: bool) -> None:
    name_w = max(len(r.name) for r in results)
    print(f"{'CHECK'.ljust(name_w)}  STATUS  MESSAGE")
    print("-" * (name_w + 8 + 60))
    for r in results:
        status = LABEL[r.severity]
        status = f"{COLOR[r.severity]}{status:<6}{RESET}" if color else status.ljust(6)
        print(f"{r.name.ljust(name_w)}  {status}  {r.message}")
    print()


if __name__ == "__main__":
    sys.exit(main())
