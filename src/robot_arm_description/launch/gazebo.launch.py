from launch.substitutions import EnvironmentVariable
from launch.actions import SetEnvironmentVariable
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    package_share = Path(
        get_package_share_directory('robot_arm_description')
    )

    urdf_file = package_share / 'urdf' / 'robot_arm_4dof_gazebo.urdf'
    world_file = package_share / 'worlds' / 'robot_arm_world.sdf'

    robot_description = urdf_file.read_text()

    ros_lib = '/opt/ros/lyrical/lib'

    gazebo_env = SetEnvironmentVariable(
    name='GZ_SIM_SYSTEM_PLUGIN_PATH',
    value=[
        ros_lib,
        ':',
        EnvironmentVariable(
            'GZ_SIM_SYSTEM_PLUGIN_PATH',
            default_value=''
        )
    ]
)

    library_path = SetEnvironmentVariable(
    name='LD_LIBRARY_PATH',
    value=[
        ros_lib,
        ':',
        EnvironmentVariable(
            'LD_LIBRARY_PATH',
            default_value=''
        )
    ]
)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', str(world_file)],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'robot_arm_world',
            '-file', str(urdf_file),
            '-name', 'robot_arm',
            '-z', '0.0'
        ],
        output='screen'
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager'
        ],
        output='screen'
    )

    arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'arm_controller',
            '--controller-manager', '/controller_manager'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_env,
        library_path,
        gazebo,
        clock_bridge,
        robot_state_publisher,

        # Allow Gazebo to initialize before spawning the robot.
        TimerAction(
            period=5.0,
            actions=[spawn_robot]
        ),

        # Allow the robot and ros2_control plugin to load.
        TimerAction(
            period=10.0,
            actions=[joint_state_broadcaster]
        ),

        TimerAction(
            period=12.0,
            actions=[arm_controller]
        )
    ])
