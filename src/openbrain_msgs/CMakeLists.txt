cmake_minimum_required(VERSION 3.8)
project(openbrain_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

set(msg_files
  msg/SystemHealth.msg
  msg/ThermalZone.msg
  msg/PowerRail.msg
  msg/MissionStatus.msg
  msg/Waypoint.msg
)

set(srv_files
  srv/LoadMission.srv
  srv/SetSpeedProfile.srv
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  DEPENDENCIES std_msgs geometry_msgs
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_msg_shapes test/test_msg_shapes.py)
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
