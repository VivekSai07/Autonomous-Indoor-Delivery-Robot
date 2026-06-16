import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_slam    = get_package_share_directory('robot_slam')
    pkg_nav2    = get_package_share_directory('robot_nav2')

    nav2_params = os.path.join(pkg_nav2, 'config', 'nav2_params.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/amr_ws/maps/office_map.yaml'),
        description='Full path to map YAML'
    )

    return LaunchDescription([
        map_arg,

        # 1. Map server + AMCL + lifecycle_manager_localization
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_slam, 'launch', 'localization.launch.py')
            ),
            launch_arguments={'map': LaunchConfiguration('map')}.items(),
        ),

        # 2. BT Navigator
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # 3. Planner Server (global path — NavfnPlanner)
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # 4. Controller Server (local trajectory — DWB)
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
            remappings=[('cmd_vel', 'cmd_vel_nav')],
        ),

        # 5. Behavior Server (spin, backup, wait recoveries)
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # 6. Velocity Smoother (removes jerky cmd_vel output)
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
            remappings=[
                ('cmd_vel',        'cmd_vel_nav'),
                ('cmd_vel_smoothed', 'cmd_vel'),
            ],
        ),

        # 7. Waypoint Follower (multi-goal, used in Phase 8)
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # 8. Lifecycle Manager for Nav2 nodes
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'autostart': True},
                {'node_names': [
                    'bt_navigator',
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'velocity_smoother',
                    'waypoint_follower',
                ]},
            ],
        ),
    ])
