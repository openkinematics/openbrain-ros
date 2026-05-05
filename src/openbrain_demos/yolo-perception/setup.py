from setuptools import find_packages, setup

package_name = "openbrain_demos_yolo_perception"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/yolo.launch.py"]),
        (f"share/{package_name}/config", ["config/default.yaml"]),
    ],
    install_requires=["setuptools", "ultralytics>=8.2", "numpy", "opencv-python"],
    zip_safe=True,
    maintainer="OpenKinematics",
    maintainer_email="opensource@openkinematics.com",
    description="YOLO object detector for OpenBrain.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "yolo_node = openbrain_demos_yolo_perception.yolo_node:main",
        ],
    },
)
