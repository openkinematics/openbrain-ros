#!/usr/bin/env bash
# Bundle everything a maintainer would want when triaging a robot:
#   - journalctl -u openbrain.service (last 5000 lines)
#   - /var/log/openbrain/*  (if any)
#   - rosbridge / streamer port-state
#   - openbrain doctor --json
#   - /etc/openbrain/robot.conf (sanitized)
#   - dmesg (last 1000 lines)
#
# Output: /tmp/openbrain-support-<UTC-timestamp>.tgz

set -euo pipefail

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="/tmp/openbrain-support-${stamp}"
mkdir -p "${out}"

# Logs
journalctl -u openbrain.service -n 5000 --no-pager >"${out}/journal.log" 2>&1 || true
journalctl -u openbrain-dashboard.service -n 5000 --no-pager >"${out}/journal-dashboard.log" 2>&1 || true
if [[ -d /var/log/openbrain ]]; then
  cp -r /var/log/openbrain "${out}/var-log-openbrain"
fi

# State snapshots
{
  echo "## uname -a"; uname -a
  echo
  echo "## /etc/os-release"; cat /etc/os-release 2>/dev/null || true
  echo
  echo "## ip addr"; ip addr 2>/dev/null || true
  echo
  echo "## ip route"; ip route 2>/dev/null || true
  echo
  echo "## docker ps"; docker ps 2>/dev/null || true
  echo
  echo "## systemctl is-active openbrain.service"
  systemctl is-active openbrain.service 2>/dev/null || true
} >"${out}/state.txt"

# Doctor (machine-readable)
if command -v openbrain >/dev/null; then
  openbrain doctor --json --no-color >"${out}/doctor.json" 2>&1 || true
fi

# Sanitized robot.conf — strip any *_token / *_key just in case.
if [[ -f /etc/openbrain/robot.conf ]]; then
  sed -E 's/^(.*token|.*key|.*secret).*=.*$/\1=<redacted>/i' \
    /etc/openbrain/robot.conf >"${out}/robot.conf"
fi

# Kernel ring buffer for hardware errors.
dmesg -T 2>/dev/null | tail -n 1000 >"${out}/dmesg.tail" || true

tarball="/tmp/openbrain-support-${stamp}.tgz"
tar -C /tmp -czf "${tarball}" "openbrain-support-${stamp}"
rm -rf "${out}"

echo "wrote ${tarball}"
echo "Attach this file when filing an issue or emailing support@openkinematics.com."
