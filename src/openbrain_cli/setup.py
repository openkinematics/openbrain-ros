from setuptools import find_packages, setup

package_name = "openbrain_cli"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="`openbrain` / `ob` operator CLI.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "openbrain = openbrain_cli.main:main",
            "ob = openbrain_cli.main:main",
        ],
    },
)
