# Status of the currently loaded / running mission.
# Published at ~2 Hz on /missions/status while a mission is loaded.

std_msgs/Header header

# State enum.
uint8 STATE_IDLE      = 0
uint8 STATE_LOADED    = 1
uint8 STATE_RUNNING   = 2
uint8 STATE_PAUSED    = 3
uint8 STATE_SUCCEEDED = 4
uint8 STATE_FAILED    = 5
uint8 STATE_CANCELED  = 6

uint8 state

# Identifier supplied at load time. Empty if no mission is loaded.
string mission_id

# Index of the waypoint currently being executed, [0, total_waypoints).
# -1 if no mission is loaded or it has not started.
int32 current_waypoint_index

# Total number of waypoints in the loaded mission.
uint32 total_waypoints

# Human-readable status, e.g. "navigating to waypoint 2/5" or an error message.
string message
