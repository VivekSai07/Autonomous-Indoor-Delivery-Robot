import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')
    pkg_rl_cfg       = get_package_share_directory('robot_localization_cfg')
    pkg_nav2         = get_package_share_directory('robot_nav2')

    ekf_config  = os.path.join(pkg_rl_cfg, 'config', 'ekf.yaml')
    rviz_config = os.path.join(pkg_nav2,   'config', 'navigation.rviz')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/amr_ws/maps/office_map.yaml'),
        description='Full path to map YAML'
    )

    return LaunchDescription([
        map_arg,

        # 1. Gazebo + robot_state_publisher + spawn
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_robot_gazebo, 'launch', 'gazebo.launch.py')
            ),
        ),

        # 2. EKF — odom→base_footprint TF + /odometry/filtered
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config, {'use_sim_time': True}],
        ),

        # 3. Full Nav2 stack (map_server + amcl + bt_navigator + planner
        #    + controller + behaviors + velocity_smoother + waypoint_follower
        #    + both lifecycle managers)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2, 'launch', 'navigation.launch.py')
            ),
            launch_arguments={'map': LaunchConfiguration('map')}.items(),
        ),

        # 4. RViz with Nav2 displays and goal-setting tools
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),
    ])
