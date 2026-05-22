cmake_minimum_required(VERSION 3.5)
project(imv_plansys2)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(plansys2_msgs REQUIRED)
find_package(plansys2_executor REQUIRED)

set(CMAKE_CXX_STANDARD 17)

set(dependencies
    rclcpp
    rclcpp_action
    plansys2_msgs
    plansys2_executor
)

add_executable(imv_move_action_node src/move_action_node.cpp)
ament_target_dependencies(imv_move_action_node ${dependencies})

add_executable(imv_move_into_tunnel_from_site_action_node src/move_into_tunnel_action_node.cpp)
ament_target_dependencies(imv_move_into_tunnel_from_site_action_node ${dependencies})

add_executable(imv_move_into_tunnel_from_beta_action_node src/move_into_tunnel_from_beta_action_node.cpp)
ament_target_dependencies(imv_move_into_tunnel_from_beta_action_node ${dependencies})

add_executable(imv_move_out_of_tunnel_to_site_action_node src/move_out_of_tunnel_action_node.cpp)
ament_target_dependencies(imv_move_out_of_tunnel_to_site_action_node ${dependencies})

add_executable(imv_move_out_of_tunnel_to_beta_action_node src/move_out_of_tunnel_to_beta_action_node.cpp)
ament_target_dependencies(imv_move_out_of_tunnel_to_beta_action_node ${dependencies})

add_executable(imv_activate_sealing_site_action_node src/activate_sealing_action_node.cpp)
ament_target_dependencies(imv_activate_sealing_site_action_node ${dependencies})

add_executable(imv_activate_sealing_beta_action_node src/activate_sealing_beta_action_node.cpp)
ament_target_dependencies(imv_activate_sealing_beta_action_node ${dependencies})

add_executable(imv_deactivate_sealing_site_action_node src/deactivate_sealing_action_node.cpp)
ament_target_dependencies(imv_deactivate_sealing_site_action_node ${dependencies})

add_executable(imv_deactivate_sealing_beta_action_node src/deactivate_sealing_beta_action_node.cpp)
ament_target_dependencies(imv_deactivate_sealing_beta_action_node ${dependencies})

add_executable(imv_load_site_action_node src/load_action_node.cpp)
ament_target_dependencies(imv_load_site_action_node ${dependencies})

add_executable(imv_load_beta_action_node src/load_beta_action_node.cpp)
ament_target_dependencies(imv_load_beta_action_node ${dependencies})

add_executable(imv_unload_site_action_node src/unload_action_node.cpp)
ament_target_dependencies(imv_unload_site_action_node ${dependencies})

add_executable(imv_unload_beta_action_node src/unload_beta_action_node.cpp)
ament_target_dependencies(imv_unload_beta_action_node ${dependencies})

install(DIRECTORY launch pddl DESTINATION share/${PROJECT_NAME})

set(_install_targets
  imv_move_action_node
  imv_move_into_tunnel_from_site_action_node
  imv_move_into_tunnel_from_beta_action_node
  imv_move_out_of_tunnel_to_site_action_node
  imv_move_out_of_tunnel_to_beta_action_node
  imv_activate_sealing_site_action_node
  imv_activate_sealing_beta_action_node
  imv_deactivate_sealing_site_action_node
  imv_deactivate_sealing_beta_action_node
  imv_load_site_action_node
  imv_load_beta_action_node
  imv_unload_site_action_node
  imv_unload_beta_action_node
)

install(TARGETS ${_install_targets}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
endif()

ament_export_dependencies(${dependencies})

ament_package()
