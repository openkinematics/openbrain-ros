# openbrain_joystick

Gamepad input. Reads `sensor_msgs/Joy` from `joy_node` and republishes a
clamped `geometry_msgs/Twist` on `/safety/cmd_vel/joystick`. The
[`openbrain_safety`](../openbrain_safety) `twist_mux` then arbitrates that
against the dashboard, Nav2, and AI policy outputs.

## Run

```bash
ros2 launch openbrain_joystick joystick.launch.py pad:=xbox    # or ps5 / generic
```

Plug a controller into a USB port. Press and **hold the dead-man button**
(LB on Xbox, L1 on PS5) for cmd_vel to flow. Releasing it lets the safety
mux time out within ~0.5 s and the robot stops.

## Buttons

| Action | Xbox | PS5 |
|---|---|---|
| Dead-man (hold) | LB | L1 |
| Turbo (×2) | RB | R1 |
| E-stop engage | B | ◯ |
| E-stop release | Y | △ |

## Tuning

The pad mapping lives in `config/{xbox,ps5,generic}.yaml`. Override scales
or button indices there, or launch with your own params file:

```bash
ros2 launch openbrain_joystick joystick.launch.py pad:=xbox
ros2 param set /joystick_teleop scale_linear 1.5
```
