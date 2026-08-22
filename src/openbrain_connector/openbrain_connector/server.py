from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .status import ConnectorState

ServerAddress = tuple[str, int]


def make_handler(state: ConnectorState, allowed_origins: frozenset[str]):
    class StatusHandler(BaseHTTPRequestHandler):
        server_version = "OpenBrainConnector/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            if self.path != "/v1/status":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.send_response(HTTPStatus.NO_CONTENT)
            self._cors_headers()
            self.send_header("Allow", "GET, OPTIONS")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/healthz":
                self._send(b"ok\n", "text/plain; charset=utf-8")
                return
            if self.path == "/v1/status":
                body = json.dumps(state.snapshot(), separators=(",", ":")).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "connector is read-only")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(body)

        def _cors_headers(self) -> None:
            origin = self.headers.get("Origin")
            if origin and origin in allowed_origins:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

    return StatusHandler


def create_server(
    address: ServerAddress,
    state: ConnectorState,
    *,
    allowed_origins: frozenset[str],
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(address, make_handler(state, allowed_origins))
