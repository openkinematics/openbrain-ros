# openbrain_drivers_quectel_5g

Manages the **Quectel RM520N** 5G modem on the Kinematics Max upper deck.
Talks to the modem over QMI/MBIM via ModemManager and exposes signal /
failover status to ROS so the dashboard can display link health.

**Status:** 🔴 Phase 3.

## Will publish

| Topic | Type |
|---|---|
| `/network/cellular/status` | `openbrain_msgs/CellularStatus` *(future)* |

## What's needed to make this work

**Hardware** — Quectel RM520N 5G modem (≈ $300) on an M.2 carrier with two 5G antennas + a SIM card with a data plan. The modem is on the Kinematics Max upper deck.

**Software dependencies**

- [`ModemManager`](https://www.freedesktop.org/wiki/Software/ModemManager/) (LGPL) — usually pre-installed on Ubuntu
- `libqmi` for the QMI control interface
- `libmbim` if your operator prefers MBIM over QMI

**Steps to ship this driver**

1. Insert the SIM, attach antennas, power-cycle the modem.
2. Verify enumeration: `mmcli -L` (should list one modem).
3. Configure the APN: `mmcli -m 0 --simple-connect="apn=internet"`.
4. Write a small node that polls `mmcli` for signal + status and publishes `openbrain_msgs/CellularStatus` (define this in `openbrain_msgs/` first)

**Estimated effort:** Small-Medium (≈ 1 week). Most of the work is the new message definition + the polling node.
## Upstream

[`ModemManager`](https://www.freedesktop.org/wiki/Software/ModemManager/) (LGPL),
plus Quectel's QMI command reference (vendor docs).

