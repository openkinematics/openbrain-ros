cmake_minimum_required(VERSION 3.8)
project(openbrain_demos_vslam_gps_denied)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_config test/test_config.py)
endif()

ament_package()
