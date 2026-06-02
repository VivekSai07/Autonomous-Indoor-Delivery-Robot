import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('robot_description')
    rviz_config = os.path.join(pkg_dir, 'config', 'sim.rviz')

    return LaunchDescription([
        # RViz2 connected to the running simulation.
        # robot_state_publisher is already running from gazebo.launch.py —
        # do NOT start it again here.
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),
    ])
