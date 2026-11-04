import rclpy

from rclpy.node import Node
from rclpy.time import Time

from geometry_msgs.msg import PoseStamped

from tf2_ros import Buffer
from tf2_ros import TransformListener
from tf2_ros import TransformException


class EndEffectorTracker(Node):

    def __init__(self):
        super().__init__('end_effector_tracker')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        self.publisher = self.create_publisher(
            PoseStamped,
            '/end_effector_pose',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.update_pose
        )

        self.get_logger().info(
            'End-effector tracker started.'
        )

    def update_pose(self):

        try:
            transform = self.tf_buffer.lookup_transform(
                'world',
                'end_effector',
                Time()
            )

            pose = PoseStamped()

            pose.header = transform.header

            pose.pose.position.x = (
                transform.transform.translation.x
            )
            pose.pose.position.y = (
                transform.transform.translation.y
            )
            pose.pose.position.z = (
                transform.transform.translation.z
            )

            pose.pose.orientation = (
                transform.transform.rotation
            )

            self.publisher.publish(pose)

        except TransformException as ex:
            self.get_logger().warning(
                f'Could not get end-effector transform: {ex}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = EndEffectorTracker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()