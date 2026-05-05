cmake_minimum_required(VERSION 3.8)
project(openbrain_drivers_realsense)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_d435i_config test/test_d435i_config.py)
endif()

ament_package()
