import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
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

    # Step 0 — kill any stale Gazebo processes from a previous run.
    # Without this, a leftover gzserver causes the new one to crash
    # (entity-already-exists conflict → exit code 255 → no odom TF).
    kill_stale_gazebo = ExecuteProcess(
        cmd=['bash', '-c',
             'pkill -9 -f gzserver; pkill -9 -f gzclient; '
             'pkill -9 -f gz; true'],
        output='log',
        name='kill_stale_gazebo',
    )

    # Steps 1-3 — delayed 2 s so killed processes fully exit before new ones start.
    bringup = TimerAction(
        period=2.0,
        actions=[
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

            # 3. Full Nav2 stack with single lifecycle manager
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_nav2, 'launch', 'navigation.launch.py')
                ),
                launch_arguments={'map': LaunchConfiguration('map')}.items(),
            ),
        ],
    )

    # Step 4 — RViz delayed 15 s from launch start (= 13 s after Gazebo starts).
    # Gives the lifecycle manager time to activate all nodes and AMCL time to
    # publish the first map→odom TF before RViz starts querying transforms.
    rviz = TimerAction(
        period=15.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': True}],
                output='screen',
            ),
        ],
    )

    return LaunchDescription([
        map_arg,
        kill_stale_gazebo,
        bringup,
        rviz,
    ])
