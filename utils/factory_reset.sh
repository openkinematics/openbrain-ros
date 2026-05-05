#!/usr/bin/env bash
# Wipe operator state on the robot. Useful when handing off a unit, or after
# a corrupted map / model.
#
# Removes:
#   /maps/                                   — RTAB-Map databases
#   /recordings/                             — rosbag2 sessions
#   /opt/openbrain/models/                   — Model Hub cache
#   /etc/openbrain/robot.conf                — robot type + image tag
#   the openbrain.service systemd unit       — re-installed by install.sh
#
# Does NOT remove:
#   the Docker image, Docker itself, the workspace, /etc/openbrain/api.env
#
# Asks twice.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Please run with sudo." >&2
  exit 1
fi

cat <<'BANNER'
============================================================
                   FACTORY RESET
This will permanently delete:
  - /maps/                  (SLAM maps)
  - /recordings/            (recorded rosbags)
  - /opt/openbrain/models/  (downloaded RL/VLA policies)
  - /etc/openbrain/robot.conf
  - the openbrain.service systemd unit
============================================================
BANNER

read -rp "Type FACTORY-RESET to confirm: " a
[[ "$a" == "FACTORY-RESET" ]] || { echo "aborted"; exit 1; }
read -rp "Are you absolutely sure? [y/N] " b
[[ "$b" =~ ^[yY]$ ]] || { echo "aborted"; exit 1; }

echo "stopping openbrain.service..."
systemctl stop openbrain.service 2>/dev/null || true
systemctl disable openbrain.service 2>/dev/null || true

for path in /maps /recordings /opt/openbrain/models; do
  if [[ -d "$path" ]]; then
    echo "removing $path"
    rm -rf "$path"
  fi
done

if [[ -f /etc/openbrain/robot.conf ]]; then
  echo "removing /etc/openbrain/robot.conf"
  rm -f /etc/openbrain/robot.conf
fi

if [[ -f /etc/systemd/system/openbrain.service ]]; then
  rm -f /etc/systemd/system/openbrain.service
  systemctl daemon-reload
fi

echo "done. Re-run sudo ./install.sh to provision again."
