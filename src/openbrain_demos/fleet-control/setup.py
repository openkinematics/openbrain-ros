from setuptools import find_packages, setup

package_name = "openbrain_demos_fleet_control"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/fleet.launch.py"]),
        (f"share/{package_name}/config", ["config/default.yaml"]),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Multi-robot fleet aggregator.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "fleet_node = openbrain_demos_fleet_control.fleet_node:main",
        ],
    },
)
