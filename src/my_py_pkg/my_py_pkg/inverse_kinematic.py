
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState


class InverseKinematics(Node):

    def __init__(self):
        super().__init__('inverse_kinematics')

        # Robot geometry from robot_arm_4dof.urdf
        self.shoulder_height = 0.110
        self.L1 = 0.1375
        self.L2 = 0.120
        self.tool_length = 0.075

        # Joint limits from URDF (radians)
        self.base_limits = (-1.5708, 1.5708)
        self.shoulder_limits = (-0.7854, 1.3090)
        self.elbow_limits = (-2.0944, 2.0944)
        self.wrist_limits = (-1.5708, 1.5708)

        # Desired gripper pitch, measured from vertical.
        # pi radians means the gripper points downward.
        self.declare_parameter('target_pitch', math.pi)
        self.target_pitch = (
            self.get_parameter('target_pitch')
            .get_parameter_value().double_value
        )

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

        self.get_logger().info(
            '4-DOF IK node started. Waiting for targets '
            'on /target_position'
        )

    def target_callback(self, msg):

        # -------------------------------------------------
        # 1. BASE ROTATION
        # -------------------------------------------------

        x = msg.x
        y = msg.y
        z = msg.z

        theta0 = math.atan2(y, x)
        r = math.sqrt(x**2 + y**2)

        if not (
            self.base_limits[0] <= theta0 <= self.base_limits[1]
        ):
            self.get_logger().warning(
                'Target rejected: base rotation exceeds joint limits.'
            )
            return

        # -------------------------------------------------
        # 2. CALCULATE WRIST CENTER
        # -------------------------------------------------

        phi = self.target_pitch

        r_w = r - self.tool_length * math.sin(phi)
        z_w = z - self.tool_length * math.cos(phi)

        # Coordinates relative to the shoulder joint
        z_s = z_w - self.shoulder_height

        # -------------------------------------------------
        # 3. ELBOW ANGLE USING THE COSINE RULE
        # -------------------------------------------------

        D_squared = r_w**2 + z_s**2

        cos_theta2 = (
            D_squared - self.L1**2 - self.L2**2
        ) / (2.0 * self.L1 * self.L2)

        if cos_theta2 < -1.0 - 1e-9 or cos_theta2 > 1.0 + 1e-9:
            self.get_logger().warning(
                'Target rejected: outside the reachable workspace.'
            )
            return

        cos_theta2 = max(-1.0, min(1.0, cos_theta2))

        # -------------------------------------------------
        # 4. SHOULDER AND ELBOW SOLUTIONS
        # -------------------------------------------------

        alpha = math.atan2(r_w, z_s)

        valid_solutions = []

        # Try both elbow configurations
        for theta2 in (
            math.acos(cos_theta2),
            -math.acos(cos_theta2)
        ):

            beta = math.atan2(
                self.L2 * math.sin(theta2),
                self.L1 + self.L2 * math.cos(theta2)
            )

            theta1 = alpha - beta

            # -------------------------------------------------
            # 5. WRIST ANGLE
            # -------------------------------------------------

            theta3 = phi - theta1 - theta2

            # Check URDF joint limits
            shoulder_valid = (
                self.shoulder_limits[0]
                <= theta1
                <= self.shoulder_limits[1]
            )

            elbow_valid = (
                self.elbow_limits[0]
                <= theta2
                <= self.elbow_limits[1]
            )

            wrist_valid = (
                self.wrist_limits[0]
                <= theta3
                <= self.wrist_limits[1]
            )

            if shoulder_valid and elbow_valid and wrist_valid:
                valid_solutions.append(
                    (theta1, theta2, theta3)
                )

        if not valid_solutions:
            self.get_logger().warning(
                'Target rejected: no IK solution satisfies '
                'the shoulder, elbow and wrist joint limits.'
            )
            return

        # Prefer the positive-elbow solution if both are valid.
        theta1, theta2, theta3 = valid_solutions[0]

        # -------------------------------------------------
        # 6. PUBLISH JOINT COMMANDS
        # -------------------------------------------------

        command = JointState()

        command.header.stamp = self.get_clock().now().to_msg()

        command.name = [
            'base_rotation_joint',
            'shoulder_joint',
            'elbow_joint',
            'wrist_joint'
        ]

        command.position = [
            theta0,
            theta1,
            theta2,
            theta3
        ]

        self.command_publisher.publish(command)

        self.get_logger().info(
            f'Target: x={x:.3f}, y={y:.3f}, z={z:.3f} m | '
            f'Base={theta0:.3f}, '
            f'Shoulder={theta1:.3f}, '
            f'Elbow={theta2:.3f}, '
            f'Wrist={theta3:.3f} rad'
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
