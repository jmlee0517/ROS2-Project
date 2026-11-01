import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


class JointStateBridge(Node):
    """
    Joint State Bridge

    This node connects the inverse kinematics node to robot_state_publisher.

    Main responsibilities:
    1. Subscribe to /joint_commands to receive joint angles calculated by IK.
    2. Store the received joint angles in joint_positions.
    3. Publish the complete joint state to /joint_states at 30 Hz.
    """
    def __init__(self):
        super().__init__('joint_state_bridge')

        # Joint states maintained by this bridge.
        self.joint_positions = {
            'base_rotation_joint': 0.0,
            'shoulder_joint': 0.0,
            'elbow_joint': 0.0,
            'wrist_joint': 0.0,
            'gripper_joint': 0.025,
        }

        self.joint_names = list(self.joint_positions.keys())

        # Subscribe to IK commands.
        self.command_subscriber = self.create_subscription(
            JointState,
            '/joint_commands',
            self.command_callback,
            10
        )

        # Publish joint states for robot_state_publisher.
        self.state_publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # Publish at 30 Hz.
        self.timer = self.create_timer(
            1.0 / 30.0,
            self.publish_joint_states
        )

        self.get_logger().info(
            'Joint State Bridge started. '
            'Waiting for commands on /joint_commands.'
        )

    def command_callback(self, msg):

        for name, position in zip(msg.name, msg.position):

            if name in self.joint_positions:
                self.joint_positions[name] = position

        self.get_logger().info(
            'Received joint command: '
            + ', '.join(
                f'{name}={self.joint_positions[name]:.3f}'
                for name in msg.name
                if name in self.joint_positions
            )
        )

    def publish_joint_states(self):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [
            self.joint_positions[name]
            for name in self.joint_names
        ]

        self.state_publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = JointStateBridge()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()