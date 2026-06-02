cmake_minimum_required(VERSION 3.8)
project(robot_gazebo)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY worlds launch scripts
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/spawn_robot.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
