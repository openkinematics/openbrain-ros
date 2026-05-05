#!/usr/bin/env python3
"""mDNS scan for `_openbrain._tcp` services on the local network.

Finds OpenKinematics robots running the systemd unit. Each found robot
prints one line:

    <hostname>.local   <ip>:9090   <robot_type>

The systemd unit registers an mDNS service via Avahi when present
(post-install hook in install.sh). If Avahi isn't running, this script
just prints nothing — that's fine, the dashboard's manual entry box still
works.
"""

from __future__ import annotations

import sys
import time

try:
    from zeroconf import ServiceBrowser, Zeroconf
except ImportError:
    print("install zeroconf: pip install zeroconf", file=sys.stderr)
    sys.exit(2)


SERVICE_TYPE = "_openbrain._tcp.local."


class Listener:
    def __init__(self) -> None:
        self.found: dict[str, str] = {}

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if not info or not info.addresses:
            return
        ip = ".".join(str(b) for b in info.addresses[0])
        port = info.port or 9090
        robot_type = (info.properties.get(b"robot_type", b"?") or b"?").decode("utf-8", "replace")
        line = f"{info.server.rstrip('.'):<32}  {ip}:{port:<5}  {robot_type}"
        self.found[name] = line
        print(line, flush=True)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:  # noqa: ARG002
        self.found.pop(name, None)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        # Re-print on update.
        self.add_service(zc, type_, name)


def main(timeout: float = 5.0) -> int:
    print(f"# scanning for {SERVICE_TYPE} ({timeout}s)")
    print(f"# {'hostname':<32}  {'address':<22}  robot_type")
    zc = Zeroconf()
    listener = Listener()
    ServiceBrowser(zc, SERVICE_TYPE, listener)
    try:
        time.sleep(timeout)
    finally:
        zc.close()
    return 0 if listener.found else 1


if __name__ == "__main__":
    sys.exit(main())
