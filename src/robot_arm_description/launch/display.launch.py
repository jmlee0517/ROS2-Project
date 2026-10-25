from pathlib import Path

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    urdf_path = (
        Path(__file__).resolve().parents[1]
        / "urdf"
        / "robot_arm_4dof.urdf"
    )

    robot_description = urdf_path.read_text()

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}],
        ),
    ])
