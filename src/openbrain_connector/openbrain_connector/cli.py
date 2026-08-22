from __future__ import annotations

import argparse

from .server import create_server
from .status import ConnectorState


def main() -> None:
    parser = argparse.ArgumentParser(prog="openbrain_connector")
    parser.add_argument("--hardware-profile", required=True)
    parser.add_argument("--skill-descriptor", required=True)
    parser.add_argument(
        "--runtime-state",
        help="optional atomically replaced openbrain.connector.runtime.v1 telemetry JSON",
    )
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument(
        "--allow-origin",
        action="append",
        default=["http://localhost:3000"],
        help="exact Dashboard origin; repeat for multiple operator origins",
    )
    args = parser.parse_args()
    state = ConnectorState.from_files(
        args.hardware_profile,
        args.skill_descriptor,
        args.runtime_state,
    )
    server = create_server(
        (args.bind, args.port),
        state,
        allowed_origins=frozenset(args.allow_origin),
    )
    print(f"read-only connector listening on http://{args.bind}:{args.port}")
    server.serve_forever()
