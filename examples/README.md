# examples/

Copy-paste recipes that exercise the workspace end-to-end. Each example
is self-contained — point it at a running OpenBrain stack and it works.

## Folders

| Folder | What |
|---|---|
| [`missions/`](./missions) | Mission JSON files you can `load + start` from the CLI or dashboard |
| [`teleop/`](./teleop) | Standalone Python clients that publish to `/safety/cmd_vel/dashboard` |
| [`replay/`](./replay) | rosbag2 hooks for recording, replaying, and analyzing sessions |

## How to use them

Most examples assume the stack is up:

```bash
sudo systemctl start openbrain.service     # on a Jetson
make sim                                   # on a laptop
```

…and the workspace is sourced (`source install/setup.bash`) if you're
running ROS commands by hand instead of through the CLI.

## Adding an example

Examples are not packages — they don't ship in the Docker image and
don't need a `package.xml`. Drop a self-contained script or data file
in the relevant subdirectory, and add a row to that subdirectory's
`README.md`.

The bar is low: the next person to land on this folder should be able
to copy-paste your example and have it run. Hard-coded paths and
"obvious to me" assumptions are the enemy.
