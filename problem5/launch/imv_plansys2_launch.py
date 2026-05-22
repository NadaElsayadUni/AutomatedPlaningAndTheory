import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get the launch directory
    example_dir = get_package_share_directory('imv_plansys2')
    namespace = LaunchConfiguration('namespace')

    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace')

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED', '1')

    plansys2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('plansys2_bringup'),
            'launch',
            'plansys2_bringup_launch_monolithic.py')),
        launch_arguments={
          'model_file': example_dir + '/pddl/domain.pddl',
          'namespace': namespace
          }.items())

    move_cmd = Node(
        package='imv_plansys2',
        executable='imv_move_action_node',
        name='imv_move_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    move_into_tunnel_from_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_move_into_tunnel_from_site_action_node',
        name='imv_move_into_tunnel_from_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    move_into_tunnel_from_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_move_into_tunnel_from_beta_action_node',
        name='imv_move_into_tunnel_from_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    move_out_of_tunnel_to_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_move_out_of_tunnel_to_site_action_node',
        name='imv_move_out_of_tunnel_to_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    move_out_of_tunnel_to_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_move_out_of_tunnel_to_beta_action_node',
        name='imv_move_out_of_tunnel_to_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    activate_sealing_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_activate_sealing_site_action_node',
        name='imv_activate_sealing_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    activate_sealing_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_activate_sealing_beta_action_node',
        name='imv_activate_sealing_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    deactivate_sealing_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_deactivate_sealing_site_action_node',
        name='imv_deactivate_sealing_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    deactivate_sealing_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_deactivate_sealing_beta_action_node',
        name='imv_deactivate_sealing_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    load_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_load_site_action_node',
        name='imv_load_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    load_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_load_beta_action_node',
        name='imv_load_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    unload_site_cmd = Node(
        package='imv_plansys2',
        executable='imv_unload_site_action_node',
        name='imv_unload_site_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    unload_beta_cmd = Node(
        package='imv_plansys2',
        executable='imv_unload_beta_action_node',
        name='imv_unload_beta_action_node',
        namespace=namespace,
        output='screen',
        parameters=[])

    ld = LaunchDescription()

    ld.add_action(stdout_linebuf_envvar)
    ld.add_action(declare_namespace_cmd)
    ld.add_action(plansys2_cmd)

    ld.add_action(move_cmd)
    ld.add_action(move_into_tunnel_from_site_cmd)
    ld.add_action(move_into_tunnel_from_beta_cmd)
    ld.add_action(move_out_of_tunnel_to_site_cmd)
    ld.add_action(move_out_of_tunnel_to_beta_cmd)
    ld.add_action(activate_sealing_site_cmd)
    ld.add_action(activate_sealing_beta_cmd)
    ld.add_action(deactivate_sealing_site_cmd)
    ld.add_action(deactivate_sealing_beta_cmd)
    ld.add_action(load_site_cmd)
    ld.add_action(load_beta_cmd)
    ld.add_action(unload_site_cmd)
    ld.add_action(unload_beta_cmd)

    return ld
