from setuptools import find_packages, setup

package_name = "openbrain_teleop"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (
            f"share/{package_name}/launch",
            [
                "launch/teleop.launch.py",
                "launch/rosbridge.launch.py",
                "launch/video_streamer.launch.py",
            ],
        ),
        (f"share/{package_name}/config", ["config/streams.yaml"]),
    ],
    install_requires=["setuptools", "aiohttp>=3.9", "aiortc>=1.6", "av>=11.0"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="rosbridge + WebRTC/MJPEG video streamer for the dashboard.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "video_streamer = openbrain_teleop.video_streamer:main",
        ],
    },
)
