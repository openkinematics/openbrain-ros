# openbrain_drivers_hesai

Wraps `HesaiLidar_SDK_2.0` for the **Hesai JT128** functional-safety LiDAR
on Kinematics Max.

**Status:** 🔴 Phase 3 — needs ISO 13849-1 PLd safety layer.

## Will publish

| Topic | Type |
|---|---|
| `/lidar/hesai/points` | `sensor_msgs/PointCloud2` |
| `/lidar/hesai/safety_zones` | `openbrain_msgs/SafetyZoneStatus` *(future)* |

## What's needed to make this work

**Hardware** — Hesai JT128 ISO-13849-1 PLd functional-safety LiDAR (industrial; pricing on request). 24V DC, gigabit ethernet, requires a dedicated NIC on the host (no consumer-grade switches).

**Software dependencies**

- [`HesaiTechnology/HesaiLidar_SDK_2.0`](https://github.com/HesaiTechnology/HesaiLidar_SDK_2.0) — Apache-2.0
- A safety-rated power supply + e-stop integration (the LiDAR is the diagnostic source for ISO 13849-1 PLd compliance)

**Steps to ship this driver**

1. Build HesaiLidar_SDK_2.0 from source.
2. Configure the LiDAR via Hesai's config tool (set IP, scan rate, safety zones).
3. Wire the safety-zone output into `openbrain_safety/twist_mux` so safety-zone violations trigger an e-stop pulse.
4. Replace the TODO launch with the SDK's example launch + our remappings

**Estimated effort:** Large (≈ 4 weeks). The PLd safety integration is the long pole — needs functional-safety review before deployment.
## Upstream

[`HesaiTechnology/HesaiLidar_SDK_2.0`](https://github.com/HesaiTechnology/HesaiLidar_SDK_2.0) (Apache-2.0).

