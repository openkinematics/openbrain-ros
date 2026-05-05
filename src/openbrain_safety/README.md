# openbrain_safety

The safety stack that sits between every velocity producer and the robot
adapter. **Nothing should publish to `/cmd_vel` directly.** Publish to one
of the namespaced inputs and let `twist_mux` arbitrate.

## Components

### `twist_mux`

Priority-arbitrated multiplexer with per-source watchdog:

| Source | Topic | Priority | Timeout |
|---|---|---|---|
| joystick | `/safety/cmd_vel/joystick` | 100 | 0.5 s |
| dashboard | `/safety/cmd_vel/dashboard` | 80 | 0.5 s |
| nav | `/safety/cmd_vel/nav` | 50 | 1.0 s |
| ai | `/safety/cmd_vel/ai` | 30 | 1.0 s |

Output: `/cmd_vel` at 50 Hz. If no input is fresh, publishes **zero**
velocity (the robot stops; it does not coast).

### `estop_node`

Software e-stop. Latches a `Bool` on `/safety/estop`. Two services flip it:

- `/safety/estop_engage` (`std_srvs/Trigger`) — engage
- `/safety/estop_release` (`std_srvs/Trigger`) — release (manual gesture)

While latched, `twist_mux` ignores all inputs and publishes zero.

## Run

```bash
ros2 launch openbrain_safety safety.launch.py
```

`openbrain_bringup/mini.launch.py` includes this automatically.

## Wiring with Nav2 and the dashboard

Remap inside the launch composition so producers land on the namespaced
input topics:

```python
Node(package='nav2_controller', ...,
     remappings=[('/cmd_vel', '/safety/cmd_vel/nav')])
```

## Testing

```bash
colcon test --packages-select openbrain_safety
```
