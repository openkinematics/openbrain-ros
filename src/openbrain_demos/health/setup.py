from setuptools import find_packages, setup

package_name = "openbrain_demos_health"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/health.launch.py"]),
    ],
    install_requires=["setuptools", "psutil>=5.9"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Jetson telemetry publisher (/system/health).",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "health_node = openbrain_demos_health.health_node:main",
        ],
    },
)
