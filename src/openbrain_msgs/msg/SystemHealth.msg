# System telemetry for the edge box (Jetson Orin Nano / AGX Orin / Thor / T4000 / T5000).
# Published at ~1 Hz on /system/health by the openbrain_demos/health node.
#
# Field shape mirrors the contract consumed by openbrain-dashboard at
# `lib/types.ts :: SystemHealthMsg`. Treat as part of the v1 public API.

std_msgs/Header header

# Per-core CPU utilization in [0, 100].
float32[] cpu_per_core

# Aggregate CPU package temperature, degrees Celsius. NaN if unavailable.
float32 cpu_temp_c

# Aggregate GPU utilization in [0, 100].
float32 gpu_percent

# GPU die temperature, degrees Celsius. NaN if unavailable.
float32 gpu_temp_c

# Memory.
uint64 ram_used_bytes
uint64 ram_total_bytes

# Named thermal zones reported by the platform (e.g. "CPU", "GPU", "SOC").
openbrain_msgs/ThermalZone[] thermal_zones

# Named power rails reported by the platform's INA sensors.
openbrain_msgs/PowerRail[] power_rails

# Process uptime of this telemetry node, seconds.
uint64 uptime_s

# Names of currently running ROS 2 nodes, snapshot at publish time.
# Not consumed by the dashboard today; kept for diagnostic tooling.
string[] node_names_running
