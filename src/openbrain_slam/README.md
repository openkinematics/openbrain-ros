# openbrain_slam

RTAB-Map (RGB-D + odometry) preconfigured for an indoor mobile robot.

## Topics

**Subscribes**
- `/camera/front/color/image_raw`
- `/camera/front/color/camera_info`
- `/camera/front/depth/image_rect_raw`
- `/odom`

**Publishes**
- `/map` (`nav_msgs/OccupancyGrid`)
- `tf: map -> odom`

## Usage

```bash
# Mapping (clears DB on start)
ros2 launch openbrain_slam rtabmap.launch.py

# Localization-only against the persisted map at /maps/openbrain.db
ros2 launch openbrain_slam rtabmap.launch.py localization:=true
```

## Map persistence

Stored at `/maps/openbrain.db`. Mount this path in the Docker container so
maps survive container restarts.

## Upstream

[`introlab/rtabmap_ros`](https://github.com/introlab/rtabmap_ros) (BSD-3).
