import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_robot_desc   = get_package_share_directory('robot_description')
    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')
    pkg_rl_cfg       = get_package_share_directory('robot_localization_cfg')

    rviz_config = os.path.join(pkg_robot_desc, 'config', 'sim.rviz')
    ekf_config  = os.path.join(pkg_rl_cfg,     'config', 'ekf.yaml')

    return LaunchDescription([

        # 1. Full Gazebo stack: daemon start + gzserver/gzclient + robot_state_publisher
        #    + Python spawner (all from our gazebo.launch.py)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_robot_gazebo, 'launch', 'gazebo.launch.py')
            ),
        ),

        # 2. EKF node (fuses /odom + /imu → /odometry/filtered + odom→base_footprint TF)
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

        # 3. RViz with simulation config (robot model, TF, LaserScan, odom comparison)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),
    ])
