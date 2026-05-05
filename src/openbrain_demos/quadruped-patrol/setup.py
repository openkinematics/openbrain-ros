from setuptools import find_packages, setup

package_name = "openbrain_demos_quadruped_patrol"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/patrol.launch.py"]),
        (
            f"share/{package_name}/config",
            [
                "config/default.yaml",
                "config/example_loop.json",
            ],
        ),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Quadruped patrol with battery-aware return-to-charger.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "patrol_node = openbrain_demos_quadruped_patrol.patrol_node:main",
        ],
    },
)
