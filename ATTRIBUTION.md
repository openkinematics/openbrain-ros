# Attribution

OpenBrain ROS is an original work developed by **OpenKinematics** under the MIT License.

## Upstream open-source dependencies

We build on top of the following open-source projects. Each is used under its
respective license. We are grateful to their maintainers and contributors.

| Project | License | Role |
|---|---|---|
| [ROS 2 Humble Hawksbill](https://docs.ros.org/en/humble/) | Apache-2.0 | Core middleware |
| [Nav2](https://docs.nav2.org/) | Apache-2.0 | Navigation stack |
| [RTAB-Map](https://github.com/introlab/rtabmap_ros) | BSD-3 | SLAM backend |
| [rosbridge_suite](https://github.com/RobotWebTools/rosbridge_suite) | BSD-3 | WebSocket bridge |
| [Intel RealSense ROS 2](https://github.com/IntelRealSense/realsense-ros) | Apache-2.0 | Depth camera driver |
| [aiortc](https://github.com/aiortc/aiortc) | BSD-3 | WebRTC streamer |
| [jetson-stats](https://github.com/rbonghi/jetson_stats) | AGPL-3.0 | Health telemetry on Jetson (optional, not linked into binaries) |

Vendor SDKs (Livox SDK 2, Hesai HesaiLidar_SDK_2.0, Xsens MTi ROS 2 driver,
FLIR Boson SDK, TI mmWave ROS 2 toolbox, Quectel modem manager) are loaded as
runtime dependencies — see each `openbrain_drivers/<vendor>/README.md` for
provenance and license terms.

If you spot a missing attribution, please open an issue.
