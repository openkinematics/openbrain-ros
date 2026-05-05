# examples/teleop

Standalone teleop clients. Each writes to
`/safety/cmd_vel/dashboard` so the safety mux still arbitrates and the
e-stop still works — **never publish straight to `/cmd_vel`**.

## Index

| File | What |
|---|---|
| [`drive_circle.py`](./drive_circle.py) | 30 s circle at 0.3 m/s (great for SLAM smoke tests) |
| [`stop_pulse.py`](./stop_pulse.py) | Engage e-stop, sleep, release — smoke tests the safety service surface |
