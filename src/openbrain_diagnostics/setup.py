from setuptools import find_packages, setup

package_name = "openbrain_diagnostics"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/diagnostics.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Hardware self-test driver and `doctor` CLI entry point.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "diagnostics_node = openbrain_diagnostics.diagnostics_node:main",
            "doctor = openbrain_diagnostics.doctor:main",
        ],
    },
)
