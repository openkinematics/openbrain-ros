# openbrain_robots_generic

Two things in one package:

1. The **`RobotAdapter` base class** that every vendor adapter extends.
2. A concrete **`GenericAdapter`** — pass-through for any ROS 2-native
   robot that already consumes `/cmd_vel` and publishes `/odom` directly.

## When to use it

Use the generic adapter when your robot's vendor driver is already a
well-behaved ROS 2 citizen — for example, a community Spot, Husky,
Stretch, or custom mobile base that subscribes to `/cmd_vel` natively.
The adapter contributes the things every OpenBrain robot needs but the
vendor driver doesn't:

- the `/teleop/set_speed_profile` service with `beginner | normal | insane`,
- a latched `/robot_description` (URDF) on the standard topic,
- the input-side velocity clamp under the active speed profile.

It does **not** translate `/cmd_vel` into a vendor SDK call — the
robot's own driver does that.

## RobotAdapter API

Subclass `RobotAdapter`, override two methods:

```python
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from openbrain_robots_generic.robot_adapter import RobotAdapter

class MyRobotAdapter(RobotAdapter):
    def __init__(self):
        super().__init__("my_robot_adapter", urdf=load_my_urdf())

    def send_velocity(self, twist: Twist) -> None:
        # Required: translate the (already speed-profile-clamped) Twist
        # into your vendor SDK's velocity command.
        self._sdk.move(twist.linear.x, twist.linear.y, twist.angular.z)

    def read_odometry(self) -> Odometry | None:
        # Optional: pull the latest filtered odometry from the SDK.
        return _build_odom(self._sdk.high_state())
```

The base class wires up `/cmd_vel` subscription, `/odom` publication
(via your `read_odometry` at 20 Hz), latched `/robot_description`, and
the speed-profile service. Velocity arriving on `/cmd_vel` is clamped to
the active profile's `max_linear` / `max_angular` **before** your
`send_velocity` is called — so vendor SDKs always see safe values.

## Speed profiles

| Profile | max_linear (m/s) | max_angular (rad/s) |
|---|---|---|
| `beginner` | 0.3 | 0.5 |
| `normal` (default) | 1.0 | 1.5 |
| `insane` | 2.5 | 3.0 |

Profile defaults live in
[`openbrain_robots_generic/robot_adapter.py :: SPEED_PROFILES`](openbrain_robots_generic/robot_adapter.py).

## Run

```bash
ros2 launch openbrain_robots_generic generic.launch.py
```

This is what `openbrain_bringup` chooses when `robot_type=GENERIC`.

## URDF

Set `OPENBRAIN_URDF_PATH=/path/to/my.urdf` and the adapter publishes the
file's contents on the latched `/robot_description` topic, which the
dashboard's 3D viewer subscribes to.

## Tests

`test/test_robot_adapter.py` exercises the velocity clamp and the
profile registry — these are the parts that must stay correct across
every adapter, so they're tested at the base class.
