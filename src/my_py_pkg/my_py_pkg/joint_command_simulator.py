
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

        # Trajectory settings
        self.update_rate = 20.0
        self.dt = 1.0 / self.update_rate
        self.duration = 2.0

        self.current_positions = {
            'shoulder_joint': 0.0,
            'elbow_joint': 0.0
        }

        self.start_positions = self.current_positions.copy()
        self.target_positions = self.current_positions.copy()
        self.elapsed_time = 0.0
        self.trajectory_active = False

        self.timer = self.create_timer(
            self.dt,
            self.timer_callback
        )

        self.get_logger().info(
            'Joint command simulator started. '
            'Cubic trajectory interpolation enabled: '
            f'{self.duration:.1f}s, {self.update_rate:.0f} Hz'
        )

    def command_callback(self, msg):
        positions = dict(zip(msg.name, msg.position))

        required_joints = [
            'shoulder_joint',
            'elbow_joint'
        ]

        if not all(joint in positions for joint in required_joints):
            self.get_logger().warning(
                'Command must include shoulder_joint and elbow_joint'
            )
            return

        # Start from the current simulated joint positions
        self.start_positions = self.current_positions.copy()

        self.target_positions = {
            joint: positions[joint]
            for joint in required_joints
        }

        self.elapsed_time = 0.0
        self.trajectory_active = True

        self.get_logger().info(
            'New cubic trajectory: '
            f"shoulder {self.start_positions['shoulder_joint']:.3f} "
            f"-> {self.target_positions['shoulder_joint']:.3f} rad, "
            f"elbow {self.start_positions['elbow_joint']:.3f} "
            f"-> {self.target_positions['elbow_joint']:.3f} rad"
        )

    def timer_callback(self):
        if self.trajectory_active:
            self.elapsed_time += self.dt

            # Normalized time from 0 to 1
            alpha = min(
                self.elapsed_time / self.duration,
                1.0
            )

            # Cubic time scaling: zero velocity at both endpoints
            s = 3.0 * alpha**2 - 2.0 * alpha**3

            # Interpolate each joint using the cubic scale
            for joint in self.current_positions:
                start = self.start_positions[joint]
                target = self.target_positions[joint]

                self.current_positions[joint] = (
                    start + s * (target - start)
                )

            if alpha >= 1.0:
                self.trajectory_active = False

                # Ensure the final position is exact
                self.current_positions = self.target_positions.copy()

                self.get_logger().info(
                    'Cubic trajectory completed.'
                )

        # Publish the latest simulated joint state
        state = JointState()
        state.header.stamp = self.get_clock().now().to_msg()
        state.name = [
            'shoulder_joint',
            'elbow_joint'
        ]
        state.position = [
            self.current_positions['shoulder_joint'],
            self.current_positions['elbow_joint']
        ]

        self.state_publisher.publish(state)


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
