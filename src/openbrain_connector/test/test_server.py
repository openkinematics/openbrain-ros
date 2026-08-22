from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

from openbrain_connector.server import create_server


class _State:
    def snapshot(self) -> dict:
        return {"schemaVersion": "openbrain.connector.status.v1"}


def test_http_surface_is_read_only() -> None:
    server = create_server(
        ("127.0.0.1", 0),
        _State(),  # type: ignore[arg-type]
        allowed_origins=frozenset({"http://localhost:3000"}),
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        get_request = urllib.request.Request(
            f"{base}/v1/status",
            headers={"Origin": "http://localhost:3000"},
        )
        with urllib.request.urlopen(get_request) as response:
            assert json.load(response)["schemaVersion"] == "openbrain.connector.status.v1"
            assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        request = urllib.request.Request(f"{base}/v1/status", data=b"{}", method="POST")
        try:
            urllib.request.urlopen(request)
        except urllib.error.HTTPError as error:
            assert error.code == 405
        else:
            raise AssertionError("POST unexpectedly succeeded")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_cors_does_not_reflect_an_unlisted_origin() -> None:
    server = create_server(
        ("127.0.0.1", 0),
        _State(),  # type: ignore[arg-type]
        allowed_origins=frozenset({"https://dashboard.example"}),
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/v1/status",
            headers={"Origin": "https://untrusted.example"},
        )
        with urllib.request.urlopen(request) as response:
            assert response.headers.get("Access-Control-Allow-Origin") is None
            assert response.headers["Cache-Control"] == "no-store"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
