# openbrain_drivers_ti_mmwave

Wraps the TI mmWave ROS 2 toolbox for the **IWR6843** 60 GHz radar.

**Status:** 🔴 Phase 3.

## Will publish

| Topic | Type |
|---|---|
| `/radar/iwr6843/points` | `sensor_msgs/PointCloud2` (range-doppler-azimuth) |
| `/radar/iwr6843/tracks` | `radar_msgs/RadarTracks` |

## What's needed to make this work

**Hardware** — TI IWR6843ISK 60 GHz mmWave radar (≈ $300). USB cable (the kit exposes two USB-CDC ports — CLI + data).

**Software dependencies**

- TI mmWave ROS 2 toolbox (download from ti.com)
- TI mmWave Studio for one-time radar configuration
- Python `pyserial` for the CLI port handshake

**Steps to ship this driver**

1. Flash the radar with a configuration profile (people-counting, occupancy detection, etc.) using mmWave Studio on a Windows host.
2. Plug into the Jetson; verify two `/dev/ttyACM*` show up.
3. Install the ROS 2 toolbox in this workspace.
4. Replace the TODO launch with the toolbox's example launch, parameter-pinned to your config profile

**Estimated effort:** Small-Medium (≈ 1 week). Initial Studio config is the longest part.
## Upstream

[TI mmWave ROS 2 toolbox](https://www.ti.com/tool/MMWAVE-DEMO-VISUALIZER) (BSD).

