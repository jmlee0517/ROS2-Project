import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ForwardKinematics(Node):
    def __init__(self):
        super().__init__('forward_kinematics')

        self.shoulder_angle = 0.0
        self.elbow_angle = 0.0

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.get_logger().info('Forward kinematics node started')

    def joint_state_callback(self, msg):
        joint_positions = dict(zip(msg.name, msg.position))

        if 'shoulder_joint' not in joint_positions:
            return
        if 'elbow_joint' not in joint_positions:
            return

        self.shoulder_angle = joint_positions['shoulder_joint']
        self.elbow_angle = joint_positions['elbow_joint']

        # Link lengths in metres
        L1 = 0.5
        L2 = 0.4

        # Joint angles in radians
        theta1 = self.shoulder_angle
        theta2 = self.elbow_angle

        # Forward kinematics for links extending along local +Z,
        # with both revolute joints rotating about the Y-axis.
        x = L1 * math.sin(theta1) + L2 * math.sin(theta1 + theta2)
        z = L1 * math.cos(theta1) + L2 * math.cos(theta1 + theta2)

        self.get_logger().info(
            f'End-effector estimate: x={x:.3f} m, z={z:.3f} m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ForwardKinematics()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()