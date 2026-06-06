import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')
    pkg_robot_desc   = get_package_share_directory('robot_description')
    pkg_rl_cfg       = get_package_share_directory('robot_localization_cfg')
    pkg_slam         = get_package_share_directory('robot_slam')

    ekf_config  = os.path.join(pkg_rl_cfg,  'config', 'ekf.yaml')
    slam_config = os.path.join(pkg_slam,    'config', 'mapper_params_online_async.yaml')
    rviz_config = os.path.join(pkg_slam,    'config', 'slam.rviz')

    return LaunchDescription([

        # 1. Gazebo + robot_state_publisher + spawn
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_robot_gazebo, 'launch', 'gazebo.launch.py')
            ),
        ),

        # 2. EKF — fuses /odom + /imu, publishes /odometry/filtered + odom→base_footprint TF
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config,
                {'use_sim_time': True},
            ],
        ),

        # 3. SLAM Toolbox (async online) — subscribes to /scan, reads odom TF, publishes /map
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_config,
                {'use_sim_time': True},
            ],
        ),

        # 4. RViz with SLAM display (robot model, TF, LaserScan, /map)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),
    ])
