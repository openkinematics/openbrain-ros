from setuptools import find_packages, setup

package_name = "openbrain_demos_missions"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/missions.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Mission state-machine.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "missions_node = openbrain_demos_missions.missions_node:main",
        ],
    },
)
