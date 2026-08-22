from glob import glob

from setuptools import find_packages, setup

package_name = "openbrain_connector"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Read-only edge connector for OpenBrain skill runtime and safety status.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={"console_scripts": ["openbrain_connector = openbrain_connector.cli:main"]},
)
