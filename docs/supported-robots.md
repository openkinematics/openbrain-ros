# Supported robots

The OpenBrain backend ships an adapter layer
([`openbrain_robots/`](../src/openbrain_robots)) that translates the v1
contract (`/cmd_vel`, `/odom`, `/robot_description`,
`/teleop/set_speed_profile`) onto each vendor's SDK. Adding a new robot is
typically a 100-line subclass of
[`RobotAdapter`](../src/openbrain_robots/generic/openbrain_robots_generic/robot_adapter.py).

## Status

| Robot | Adapter | Status | Notes |
|---|---|---|---|
| Unitree Go2 / Go2-W | `openbrain_robots_unitree_go2` | 🟢 v0.1 | High-level Move + odom from HighState |
| Unitree G1 | `openbrain_robots_unitree_g1` | 🟡 Phase 2 | Walking-primitive translation pending |
| DirectDrive Tita | `openbrain_robots_tita` | 🟡 Phase 2 | Needs body-balance controller |
| Any ROS 2-native robot | `openbrain_robots_generic` | 🟢 v0.1 | Pass-through; robot's own driver consumes /cmd_vel |
| Boston Dynamics Spot | — | 🔴 Planned | Adapter against BD's gRPC SDK |
| Stretch RE2 | — | 🔴 Planned | Stretch Body adapter |
| ALOHA / Koch arms | — | 🔴 Planned | LeRobot teleop bridge |
| Franka Panda / UR5e | — | 🔴 Planned | MoveIt 2 wrapping |

🟢 = tested  ·  🟡 = adapter scaffolded, not yet validated on hardware  ·  🔴 = planned

## Adding a new robot

1. Copy `src/openbrain_robots/generic/` to `src/openbrain_robots/<robot>/`.
2. Rename the package to `openbrain_robots_<robot>` and add it to
   `openbrain_bringup/launch/_robot_type.py :: ADAPTER_PACKAGES`.
3. Subclass `RobotAdapter`. Override `send_velocity(twist)` and (optionally)
   `read_odometry()`.
4. Add a row to the table above and submit a PR.
