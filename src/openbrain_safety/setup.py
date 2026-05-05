from setuptools import find_packages, setup

package_name = "openbrain_safety"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/safety.launch.py"]),
        (f"share/{package_name}/config", ["config/twist_mux.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Safety stack: twist mux + dead-man + e-stop + watchdog.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "twist_mux = openbrain_safety.twist_mux:main",
            "estop_node = openbrain_safety.estop_node:main",
        ],
    },
)
