#!/usr/bin/env bash
# Interactive WiFi onboarding using nmcli.
#
# Scans, lets you pick an SSID, prompts for the password, saves the
# connection, and waits for an IP. Idempotent — re-running edits the
# saved connection in place.

set -euo pipefail

if ! command -v nmcli >/dev/null; then
  echo "nmcli not found. Install NetworkManager first." >&2
  exit 2
fi

iface="${1:-}"
if [[ -z "${iface}" ]]; then
  iface="$(nmcli -t -f DEVICE,TYPE device | awk -F: '$2=="wifi"{print $1; exit}')"
fi
if [[ -z "${iface}" ]]; then
  echo "no wifi interface detected — pass one explicitly: setup_wifi.sh <iface>" >&2
  exit 2
fi
echo "using wifi interface: ${iface}"

echo "scanning..."
nmcli device wifi rescan ifname "${iface}" >/dev/null 2>&1 || true
sleep 2
nmcli -f IN-USE,SSID,SIGNAL,SECURITY device wifi list ifname "${iface}" | head -20

read -rp "SSID to join: " ssid
[[ -n "${ssid}" ]] || { echo "no SSID"; exit 2; }
read -rsp "password (leave empty for open network): " pw; echo

if [[ -z "${pw}" ]]; then
  nmcli device wifi connect "${ssid}" ifname "${iface}"
else
  nmcli device wifi connect "${ssid}" password "${pw}" ifname "${iface}"
fi

echo "waiting for IP..."
for _ in {1..15}; do
  ip="$(ip -4 addr show "${iface}" | awk '/inet /{print $2; exit}')"
  if [[ -n "${ip}" ]]; then
    echo "got ${ip}"
    exit 0
  fi
  sleep 1
done
echo "did not get an IP within 15s — check the password" >&2
exit 1
