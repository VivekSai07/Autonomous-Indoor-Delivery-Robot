import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_slam = get_package_share_directory('robot_slam')
    pkg_nav2 = get_package_share_directory('robot_nav2')

    amcl_config = os.path.join(pkg_slam, 'config', 'amcl_params.yaml')
    nav2_params = os.path.join(pkg_nav2, 'config', 'nav2_params.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/amr_ws/maps/office_map.yaml'),
        description='Full path to map YAML'
    )

    # Single lifecycle manager activates nodes SEQUENTIALLY in the order listed.
    # map_server and amcl come first so AMCL publishes map→odom TF before
    # bt_navigator / costmaps try to use it.
    managed_nodes = [
        'map_server',
        'amcl',
        'bt_navigator',
        'planner_server',
        'controller_server',
        'behavior_server',
        'velocity_smoother',
        'waypoint_follower',
    ]

    return LaunchDescription([
        map_arg,

        # ── Localization ──────────────────────────────────────────────────────
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'yaml_filename': LaunchConfiguration('map')},
            ],
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[amcl_config, {'use_sim_time': True}],
        ),

        # ── Navigation stack ──────────────────────────────────────────────────
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # controller_server outputs to cmd_vel_nav; velocity_smoother consumes
        # cmd_vel_nav and republishes to cmd_vel for the diff drive plugin.
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
            remappings=[('cmd_vel', 'cmd_vel_nav')],
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
            remappings=[
                ('cmd_vel',          'cmd_vel_nav'),
                ('cmd_vel_smoothed', 'cmd_vel'),
            ],
        ),

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': True}],
        ),

        # ── Lifecycle manager ─────────────────────────────────────────────────
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'autostart': True},
                {'node_names': managed_nodes},
            ],
        ),
    ])
