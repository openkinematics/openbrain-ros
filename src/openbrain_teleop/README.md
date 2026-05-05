# openbrain_teleop

The teleop surface area the [openbrain-dashboard](https://github.com/openkinematics/openbrain-dashboard)
talks to:

| Endpoint | Protocol | Purpose |
|---|---|---|
| `ws://<robot>:9090` | WebSocket (rosbridge) | Topics + services |
| `http://<robot>:8080/stream/{name}/offer` | WebRTC SDP exchange | Live video |
| `http://<robot>:8080/stream/{name}.mjpeg` | multipart/x-mixed-replace | Fallback video |
| `http://<robot>:8080/stream/{name}/snapshot` | image/jpeg | Single still (poster) |
| `http://<robot>:8080/healthz` | text/plain | Liveness probe |

Stream names default to `front` and `back` (configured in `config/streams.yaml`).

## Run

```bash
ros2 launch openbrain_teleop teleop.launch.py
```

This launches both `rosbridge_websocket` on `:9090` and `video_streamer`
on `:8080`. The streamer subscribes to `/camera/{front,back}/color/image_raw`,
keeps the latest frame in memory, and serves it over WebRTC (preferred) or
MJPEG (fallback) on demand.

## Add a stream

Edit `config/streams.yaml`:

```yaml
streams:
  thermal:
    topic: /camera/thermal/image_raw
    framerate: 9
```

Then `colcon build` and re-launch. The new endpoint is
`/stream/thermal/offer` + `/stream/thermal.mjpeg`.

## Upstream

* [`rosbridge_suite`](https://github.com/RobotWebTools/rosbridge_suite) (BSD-3)
* [`aiortc`](https://github.com/aiortc/aiortc) (BSD-3) — WebRTC
* [`aiohttp`](https://github.com/aio-libs/aiohttp) (Apache-2.0) — HTTP server
