import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


class JointTargetToTrajectory(Node):

    def __init__(self):
        super().__init__('joint_target_to_trajectory')

        self.joint_names = [
            'base_rotation_joint',
            'shoulder_joint',
            'elbow_joint',
            'wrist_joint'
        ]

        self.subscription = self.create_subscription(
            JointState,
            '/joint_targets',
            self.target_callback,
            10
        )

        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        self.get_logger().info(
            'Joint target to trajectory node started.'
        )

    def target_callback(self, msg):

        positions = dict(zip(msg.name, msg.position))

        if not all(name in positions for name in self.joint_names):
            self.get_logger().warning(
                'Received incomplete joint target.'
            )
            return

        trajectory = JointTrajectory()

        trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()

        point.positions = [
            positions[name] for name in self.joint_names
        ]

        point.time_from_start.sec = 3

        trajectory.points.append(point)

        self.publisher.publish(trajectory)

        self.get_logger().info(
            f'Published trajectory: {point.positions}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = JointTargetToTrajectory()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()