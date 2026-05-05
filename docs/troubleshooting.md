# Troubleshooting

## "no camera frames in the dashboard"

1. Check the camera USB enumeration:
   ```bash
   rs-enumerate-devices --short
   ```
2. Confirm the serials in `config/mini.yaml` (or via
   `OPENBRAIN_FRONT_SERIAL` / `OPENBRAIN_BACK_SERIAL`) match the printed
   serials.
3. Confirm the streamer is up:
   ```bash
   curl http://localhost:8080/healthz       # -> ok
   curl http://localhost:8080/stream/front/snapshot --output /tmp/snap.jpg
   ```
4. If WebRTC fails behind a symmetric NAT, the dashboard auto-falls back to
   MJPEG. Configure TURN via `NEXT_PUBLIC_TURN_URLS` on the dashboard side.

## "dashboard says 'rosbridge not connected'"

1. Confirm port 9090 is reachable from the dashboard host:
   ```bash
   ss -tlnp | grep 9090
   ```
2. Check rosbridge logs:
   ```bash
   ros2 node info /rosbridge_websocket
   ```
3. Firewall? On the Jetson:
   ```bash
   sudo ufw status
   sudo ufw allow 9090
   sudo ufw allow 8080
   ```

## "Nav2 won't accept goals"

1. Make sure the Nav2 lifecycle is `active`:
   ```bash
   ros2 lifecycle get /bt_navigator
   ```
2. Confirm there's a `/map` topic:
   ```bash
   ros2 topic hz /map
   ```
   If silent, RTAB-Map didn't initialize — check that
   `/camera/front/{color,depth}` are flowing.
3. Confirm there's a `map -> odom` TF:
   ```bash
   ros2 run tf2_ros tf2_echo map odom
   ```

## "missions service rejects with 'no waypoints provided'"

The dashboard sends `LoadMissionRequest{waypoints: [...], loop: bool}`.
Make sure the array is non-empty. Each waypoint needs `x`, `y`, `yaw` in
the `/map` frame.

## Getting more help

- File an issue: https://github.com/openkinematics/openbrain-ros/issues
- Sister repos:
  - [openbrain-dashboard](https://github.com/openkinematics/openbrain-dashboard)
  - [kinematics-mini-hw](https://github.com/openkinematics/kinematics-mini-hw)
