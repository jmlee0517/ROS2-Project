import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointCommandSimulator(Node):
    def __init__(self):
        super().__init__('joint_command_simulator')

        self.command_subscriber = self.create_subscription(
            JointState,
            '/joint_commands',
            self.command_callback,
            10
        )

        self.state_publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.get_logger().info('Joint command simulator started')

    def command_callback(self, msg):
        positions = dict(zip(msg.name, msg.position))

        if 'shoulder_joint' not in positions or 'elbow_joint' not in positions:
            self.get_logger().warning(
                'Command must include shoulder_joint and elbow_joint'
            )
            return

        state = JointState()
        state.header.stamp = self.get_clock().now().to_msg()
        state.name = ['shoulder_joint', 'elbow_joint']
        state.position = [
            positions['shoulder_joint'],
            positions['elbow_joint']
        ]

        self.state_publisher.publish(state)

        self.get_logger().info(
            f"Published shoulder={state.position[0]:.3f} rad, "
            f"elbow={state.position[1]:.3f} rad"
        )


def main(args=None):
    rclpy.init(args=args)
    node = JointCommandSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()