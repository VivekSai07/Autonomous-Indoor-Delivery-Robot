import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('robot_slam')
    amcl_config = os.path.join(pkg_dir, 'config', 'amcl_params.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/amr_ws/maps/office_map.yaml'),
        description='Full path to the map YAML file'
    )

    return LaunchDescription([
        map_arg,

        # Serves the saved occupancy grid on /map
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

        # Particle-filter localization — subscribes to /scan + odom TF,
        # publishes /particle_cloud, /amcl_pose, and map→odom TF
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                amcl_config,
                {'use_sim_time': True},
            ],
        ),

        # Drives map_server and amcl through their lifecycle transitions
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'autostart': True},
                {'node_names': ['map_server', 'amcl']},
            ],
        ),
    ])
