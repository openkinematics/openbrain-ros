from setuptools import find_packages, setup

package_name = "openbrain_joystick"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/joystick.launch.py"]),
        (
            f"share/{package_name}/config",
            [
                "config/ps5.yaml",
                "config/xbox.yaml",
                "config/generic.yaml",
            ],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Gamepad → /safety/cmd_vel/joystick translator.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "joystick_teleop = openbrain_joystick.joystick_teleop:main",
        ],
    },
)
