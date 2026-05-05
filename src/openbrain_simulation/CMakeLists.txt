cmake_minimum_required(VERSION 3.8)
project(openbrain_simulation)
find_package(ament_cmake REQUIRED)
install(DIRECTORY launch worlds urdf config DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_sim_bridge_config test/test_sim_bridge_config.py)
endif()

ament_package()
