from setuptools import find_packages, setup

package_name = "openbrain_recording"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/recording.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="rosbag2 wrapper exposed over ROS services.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "recording_node = openbrain_recording.recording_node:main",
        ],
    },
)
