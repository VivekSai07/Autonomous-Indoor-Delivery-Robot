import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_robot_desc   = get_package_share_directory('robot_description')
    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')
    pkg_gazebo_ros   = get_package_share_directory('gazebo_ros')

    urdf_file  = os.path.join(pkg_robot_desc,   'urdf',   'robot.urdf.xacro')
    world_file = os.path.join(pkg_robot_gazebo, 'worlds', 'office.world')
    spawner    = os.path.join(pkg_robot_gazebo, 'scripts', 'spawn_robot.py')

    robot_description = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    return LaunchDescription([

        # 0. Ensure the ROS2 CLI daemon is running so 'ros2 topic list',
        #    'ros2 service list', 'ros2 topic echo' work in all terminals.
        ExecuteProcess(
            cmd=['ros2', 'daemon', 'start'],
            output='screen',
        ),

        # 1. Launch Gazebo (gzserver + gzclient) via gazebo_ros — sets
        #    GAZEBO_PLUGIN_PATH / GAZEBO_RESOURCE_PATH correctly.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world_file}.items(),
        ),

        # 2. Robot state publisher (publishes /robot_description as latched topic)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True,
            }],
        ),

        # 3. Spawn robot using rclpy directly — avoids the ros2 CLI daemon
        #    which hangs on WSL2. Waits for /spawn_entity + robot_description,
        #    then calls the service. x y z yaw passed as args.
        ExecuteProcess(
            cmd=['python3', spawner, '0.0', '0.0', '0.05', '0.0'],
            output='screen',
        ),
    ])
