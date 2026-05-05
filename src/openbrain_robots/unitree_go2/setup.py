from setuptools import find_packages, setup

package_name = "openbrain_robots_unitree_go2"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/unitree_go2.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Unitree Go2 / Go2-W robot adapter.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "unitree_go2_adapter = openbrain_robots_unitree_go2.unitree_go2_adapter:main",
        ],
    },
)
