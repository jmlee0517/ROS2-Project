
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class TrajectoryController(Node):
    """
    Trajectory Controller

    This node generates smooth joint trajectories between
    the current joint positions and target joint positions.

    Main responsibilities:
    1. Subscribe to /joint_targets to receive target joint angles.
    2. Interpolate between current and target joint positions.
    3. Publish interpolated joint commands to /joint_commands.
    """

    def __init__(self):
        super().__init__('trajectory_controller')

        self.joint_names = [
            'base_rotation_joint',
            'shoulder_joint',
            'elbow_joint',
            'wrist_joint',
        ]

        self.current_positions = {
            name: 0.0 for name in self.joint_names
        }

        self.start_positions = None
        self.target_positions = None

        self.trajectory_duration = 3.0
        self.trajectory_start_time = None
        self.trajectory_active = False

        self.target_subscriber = self.create_subscription(
            JointState,
            '/joint_targets',
            self.target_callback,
            10
        )

        self.command_publisher = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

        self.timer = self.create_timer(
            1.0 / 30.0,
            self.update_trajectory
        )

        self.get_logger().info(
            'Trajectory Controller started. '
            'Waiting for targets on /joint_targets.'
        )

    def target_callback(self, msg):

        received_positions = dict(zip(msg.name, msg.position))

        if not all(
            name in received_positions
            for name in self.joint_names
        ):
            self.get_logger().warning(
                'Received target with missing joint positions.'
            )
            return

        if not all(
            math.isfinite(received_positions[name])
            for name in self.joint_names
        ):
            self.get_logger().warning(
                'Received target containing invalid joint positions.'
            )
            return

        # Use the latest commanded position as the starting point.
        self.start_positions = self.current_positions.copy()

        self.target_positions = {
            name: received_positions[name]
            for name in self.joint_names
        }

        self.trajectory_start_time = (
            self.get_clock().now()
        )

        self.trajectory_active = True

        self.get_logger().info(
            'New trajectory received. '
            f'Duration: {self.trajectory_duration:.1f} seconds.'
        )

    def update_trajectory(self):

        if not self.trajectory_active:
            return

        elapsed_time = (
            self.get_clock().now()
            - self.trajectory_start_time
        ).nanoseconds / 1e9

        progress = min(
            elapsed_time / self.trajectory_duration,
            1.0
        )

        # Linear interpolation.
        for name in self.joint_names:

            start = self.start_positions[name]
            target = self.target_positions[name]

            self.current_positions[name] = (
                start + progress * (target - start)
            )

        # Publish interpolated joint positions.
        command = JointState()

        command.header.stamp = self.get_clock().now().to_msg()
        command.name = self.joint_names
        command.position = [
            self.current_positions[name]
            for name in self.joint_names
        ]

        self.command_publisher.publish(command)

        if progress >= 1.0:

            self.trajectory_active = False

            self.get_logger().info(
                'Trajectory execution completed.'
            )


def main(args=None):

    rclpy.init(args=args)

    node = TrajectoryController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
