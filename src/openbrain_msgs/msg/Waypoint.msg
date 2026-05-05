# A single mission waypoint in the /map frame.
#
# This shape mirrors `LoadMissionRequest.waypoints[]` on openbrain-dashboard.
# Treat as part of the v1 public API.
float32 x       # meters in /map frame
float32 y       # meters in /map frame
float32 yaw     # radians, CCW from +X

# Optional human-readable label (e.g. "loading_dock", "charger").
string label

# Linger time at the waypoint in seconds before advancing to the next one.
float32 dwell_seconds
