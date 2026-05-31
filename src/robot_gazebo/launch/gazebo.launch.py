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

    robot_description = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    # Spawn command: polls /spawn_entity until it appears, then spawns.
    # This is timing-agnostic — works however long Gazebo takes to start.
    spawn_cmd = (
        'until ros2 service list 2>/dev/null | grep -q /spawn_entity; do '
        '  echo "[spawn_wait] waiting for /spawn_entity..."; sleep 2; '
        'done && '
        'ros2 run gazebo_ros spawn_entity.py '
        '-topic robot_description '
        '-entity amr_robot '
        '-x 0.0 -y 0.0 -z 0.05 -Y 0.0'
    )

    return LaunchDescription([

        # 1. Launch Gazebo (gzserver + gzclient) via gazebo_ros — sets
        #    GAZEBO_PLUGIN_PATH / GAZEBO_RESOURCE_PATH correctly.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world_file}.items(),
        ),

        # 2. Robot state publisher
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

        # 3. Spawn robot — waits for /spawn_entity service, then spawns.
        ExecuteProcess(
            cmd=['bash', '-c', spawn_cmd],
            output='screen',
        ),
    ])
