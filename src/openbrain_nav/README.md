# openbrain_nav

Nav2 stack pre-tuned for the OpenKinematics Mini / Max class of mobile
robot. Subscribes `/goal_pose` and `/map`, publishes `/cmd_vel`.

## Topics

| Direction | Topic | Type |
|---|---|---|
| sub | `/goal_pose` | `geometry_msgs/PoseStamped` |
| sub | `/map` | `nav_msgs/OccupancyGrid` |
| sub | `/scan` | `sensor_msgs/LaserScan` |
| sub | `/odom` | `nav_msgs/Odometry` |
| pub | `/cmd_vel` | `geometry_msgs/Twist` |

## Run

```bash
ros2 launch openbrain_nav nav2.launch.py
```

The behavior tree at `config/nav_to_pose_bt.xml` runs plan-once + follow with
spin/backup recoveries. Tune `controller_server.FollowPath.desired_linear_vel`
in `config/nav2.yaml` if your robot is faster or slower than the default
0.5 m/s.

## Upstream

Nav2 ([`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2)) — Apache-2.0.
