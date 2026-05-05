from setuptools import find_packages, setup

package_name = "openbrain_robots_unitree_g1"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/unitree_g1.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Unitree G1 humanoid adapter (Phase 2 scaffold).",
    license="MIT",
    entry_points={
        "console_scripts": [
            "unitree_g1_adapter = openbrain_robots_unitree_g1.unitree_g1_adapter:main",
        ],
    },
)
