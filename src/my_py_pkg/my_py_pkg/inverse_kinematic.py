import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState


class InverseKinematics(Node):
    def __init__(self):
        super().__init__('inverse_kinematics')

        self.target_subscriber = self.create_subscription(
            Point,
            '/target_position',
            self.target_callback,
            10
        )

        self.command_publisher = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

        self.L1 = 0.5
        self.L2 = 0.4
        self.shoulder_offset = 0.025
        self.joint_limit = 1.57

        self.get_logger().info(
            'IK node started. Waiting for targets on /target_position'
        )

    def target_callback(self, msg):
        # This robot is planar: its target must lie in the X-Z plane.
        if abs(msg.y) > 0.001:
            self.get_logger().warning(
                'Target rejected: this arm only supports y = 0.'
            )
            return

        # Convert the target to coordinates relative to the shoulder joint.
        x = msg.x
        z = msg.z - self.shoulder_offset

        L1 = self.L1
        L2 = self.L2

        # Inverse kinematics using the cosine rule.
        cos_theta2 = (
            x**2 + z**2 - L1**2 - L2**2
        ) / (2.0 * L1 * L2)

        # Allow for tiny floating-point errors at workspace boundaries.
        if cos_theta2 < -1.0 - 1e-9 or cos_theta2 > 1.0 + 1e-9:
            self.get_logger().warning(
                'Target rejected: outside the reachable workspace.'
            )
            return

        cos_theta2 = max(-1.0, min(1.0, cos_theta2))

        # Choose the positive-elbow solution.
        theta2 = math.acos(cos_theta2)

        theta1 = (
            math.atan2(x, z)
            - math.atan2(
                L2 * math.sin(theta2),
                L1 + L2 * math.cos(theta2)
            )
        )

        # Enforce the joint limits defined in the URDF.
        if not (-self.joint_limit <= theta1 <= self.joint_limit):
            self.get_logger().warning(
                f'Target rejected: shoulder angle {theta1:.3f} rad '
                'exceeds joint limits.'
            )
            return

        if not (-self.joint_limit <= theta2 <= self.joint_limit):
            self.get_logger().warning(
                f'Target rejected: elbow angle {theta2:.3f} rad '
                'exceeds joint limits.'
            )
            return

        # Publish the desired joint angles.
        command = JointState()
        command.header.stamp = self.get_clock().now().to_msg()
        command.name = ['shoulder_joint', 'elbow_joint']
        command.position = [theta1, theta2]

        self.command_publisher.publish(command)

        self.get_logger().info(
            f'Target accepted: x={msg.x:.3f}, z={msg.z:.3f} m | '
            f'Shoulder={theta1:.3f} rad, Elbow={theta2:.3f} rad'
        )


def main(args=None):
    rclpy.init(args=args)
    node = InverseKinematics()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()