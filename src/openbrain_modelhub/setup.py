from setuptools import find_packages, setup

package_name = "openbrain_modelhub"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools", "requests>=2.31"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="Model Hub deployment client.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "modelhub_pull = openbrain_modelhub.cli:pull",
            "modelhub_list = openbrain_modelhub.cli:ls",
        ],
    },
)
