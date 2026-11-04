import csv
import math
from pathlib import Path

import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Point, PoseStamped


class ExperimentRunner(Node):

    def __init__(self):
        super().__init__('experiment_runner')

        # Experiment configuration
        self.tolerance = 0.002       # 2 mm
        self.stable_duration = 0.5   # seconds
        self.timeout = 15.0          # seconds

        # 40 test positions distributed across the reachable workspace.
        # All coordinates are in meters.
        self.targets = [

            # Workspace region 1
            (0.0202, -0.0901, 0.1603),
            (0.0721, -0.0577, 0.1603),
            (0.0923,  0.0000, 0.1603),
            (0.0721,  0.0577, 0.1603),
            (0.0202,  0.0901, 0.1603),

            # Workspace region 2
            (0.0193, -0.0859, 0.1367),
            (0.0687, -0.0550, 0.1367),
            (0.0880,  0.0000, 0.1367),
            (0.0687,  0.0550, 0.1367),
            (0.0193,  0.0859, 0.1367),

            # Workspace region 3
            (0.0264, -0.1175, 0.1335),
            (0.0940, -0.0753, 0.1335),
            (0.1204,  0.0000, 0.1335),
            (0.0940,  0.0753, 0.1335),
            (0.0264,  0.1175, 0.1335),

            # Workspace region 4
            (0.0342, -0.1522, 0.1333),
            (0.1218, -0.0975, 0.1333),
            (0.1560,  0.0000, 0.1333),
            (0.1218,  0.0975, 0.1333),
            (0.0342,  0.1522, 0.1333),

            # Workspace region 5
            (0.0276, -0.1230, 0.0820),
            (0.0984, -0.0787, 0.0820),
            (0.1260,  0.0000, 0.0820),
            (0.0984,  0.0787, 0.0820),
            (0.0276,  0.1230, 0.0820),

            # Workspace region 6
            (0.0413, -0.1841, 0.1250),
            (0.1473, -0.1179, 0.1250),
            (0.1887,  0.0000, 0.1250),
            (0.1473,  0.1179, 0.1250),
            (0.0413,  0.1841, 0.1250),

            # Workspace region 7
            (0.0335, -0.1492, 0.0637),
            (0.1194, -0.0956, 0.0637),
            (0.1529,  0.0000, 0.0637),
            (0.1194,  0.0956, 0.0637),
            (0.0335,  0.1492, 0.0637),

            # Workspace region 8
            (0.0475, -0.2115, 0.1094),
            (0.1692, -0.1354, 0.1094),
            (0.2167,  0.0000, 0.1094),
            (0.1692,  0.1354, 0.1094),
            (0.0475,  0.2115, 0.1094),
        ]

        self.target_index = 0
        self.current_target = None

        self.actual_position = None
        self.target_start_time = None
        self.stable_start_time = None

        self.waiting_for_target = False
        self.target_stamp = None

        self.publisher = self.create_publisher(
            Point,
            '/target_position',
            10
        )

        self.subscription = self.create_subscription(
            PoseStamped,
            '/end_effector_pose',
            self.pose_callback,
            10
        )

        self.timer = self.create_timer(
            0.05,
            self.experiment_callback
        )

        # CSV output
        self.csv_path = (
            Path.home()
            / 'ROS2-Project'
            / 'experiments'
            / 'analytical_results.csv'
        )

        self.csv_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.csv_file = open(
            self.csv_path,
            'w',
            newline=''
        )

        self.writer = csv.writer(self.csv_file)

        # Store trial results for automatic summary calculation
        self.results = []

        self.writer.writerow([
            'trial',
            'target_x',
            'target_y',
            'target_z',
            'actual_x',
            'actual_y',
            'actual_z',
            'position_error_m',
            'movement_time_s',
            'status'
        ])

        self.csv_file.flush()

        self.get_logger().info(
            'Experiment runner initialized.'
        )

        self.get_logger().info(
            f'Results will be saved to: {self.csv_path}'
        )

    def pose_callback(self, msg):

        self.actual_position = (
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        )

        self.actual_pose_stamp = (
            msg.header.stamp.sec
            + msg.header.stamp.nanosec * 1e-9
        )

    def publish_target(self):

        if self.target_index >= len(self.targets):
            self.finish_experiment()
            return

        self.current_target = self.targets[
            self.target_index
        ]

        msg = Point()

        msg.x = self.current_target[0]
        msg.y = self.current_target[1]
        msg.z = self.current_target[2]

        self.publisher.publish(msg)

        self.target_start_time = self.get_clock().now()
        self.target_stamp = (
            self.target_start_time.nanoseconds * 1e-9
        )

        self.stable_start_time = None
        self.waiting_for_target = True

        self.get_logger().info(
            f'Trial {self.target_index + 1}: '
            f'Target = {self.current_target}'
        )

    def experiment_callback(self):

        if self.target_index >= len(self.targets):
            self.finish_experiment()
            return

        if not self.waiting_for_target:
            self.publish_target()
            return

        if self.actual_position is None:
            return

        now = self.get_clock().now()

        elapsed = (
            now - self.target_start_time
        ).nanoseconds * 1e-9

        # Ignore pose measurements from before this target.
        if self.actual_pose_stamp < self.target_stamp:
            return

        target = self.current_target
        actual = self.actual_position

        error = math.sqrt(
            (target[0] - actual[0]) ** 2
            + (target[1] - actual[1]) ** 2
            + (target[2] - actual[2]) ** 2
        )

        if error <= self.tolerance:

            if self.stable_start_time is None:
                self.stable_start_time = now

            stable_time = (
                now - self.stable_start_time
            ).nanoseconds * 1e-9

            if stable_time >= self.stable_duration:
                self.record_trial(
                    actual,
                    error,
                    elapsed,
                    'SUCCESS'
                )

        else:
            self.stable_start_time = None

        if elapsed >= self.timeout:
            self.record_trial(
                actual,
                error,
                elapsed,
                'TIMEOUT'
            )

    def record_trial(
        self,
        actual,
        error,
        movement_time,
        status
    ):

        target = self.current_target

        self.writer.writerow([
            self.target_index + 1,
            *target,
            *actual,
            error,
            movement_time,
            status
        ])

        self.results.append({
            'error_m': error,
            'movement_time_s': movement_time,
            'status': status
        })

        self.csv_file.flush()

        self.get_logger().info(
            f'Trial {self.target_index + 1}: '
            f'{status} | '
            f'Position error: {error * 1000:.3f} mm | '
            f'Movement time: {movement_time:.3f} s'
        )

        self.target_index += 1
        self.waiting_for_target = False
        self.stable_start_time = None

    def finish_experiment(self):

        self.timer.cancel()

        total = len(self.results)

        successful = sum(
            1 for result in self.results
            if result['status'] == 'SUCCESS'
        )

        failed = total - successful

        errors_mm = [
            result['error_m'] * 1000
            for result in self.results
        ]

        movement_times = [
            result['movement_time_s']
            for result in self.results
        ]

        if total > 0:

            mean_error = sum(errors_mm) / total

            sorted_errors = sorted(errors_mm)
            middle = total // 2

            if total % 2 == 0:
                median_error = (
                    sorted_errors[middle - 1]
                    + sorted_errors[middle]
                ) / 2
            else:
                median_error = sorted_errors[middle]

            max_error = max(errors_mm)

            rmse = math.sqrt(
                sum(error ** 2 for error in errors_mm) / total
            )

            mean_movement = sum(movement_times) / total
            min_movement = min(movement_times)
            max_movement = max(movement_times)

            success_rate = successful / total * 100

            # Append summary to CSV
            self.writer.writerow([])
            self.writer.writerow(['EXPERIMENT SUMMARY'])
            self.writer.writerow(['Metric', 'Value', 'Unit'])

            summary = [
                ['Total trials', total, 'trials'],
                ['Successful trials', successful, 'trials'],
                ['Failed trials', failed, 'trials'],
                ['Success rate', success_rate, '%'],
                ['Mean positioning error', mean_error, 'mm'],
                ['Median positioning error', median_error, 'mm'],
                ['Maximum positioning error', max_error, 'mm'],
                ['Positioning error RMSE', rmse, 'mm'],
                ['Mean movement time', mean_movement, 's'],
                ['Minimum movement time', min_movement, 's'],
                ['Maximum movement time', max_movement, 's'],
            ]

            for row in summary:
                self.writer.writerow(row)

        self.csv_file.flush()
        self.csv_file.close()

        self.get_logger().info(
            'Experiment completed.'
        )

        self.get_logger().info(
            f'Total trials: {total}'
        )

        self.get_logger().info(
            f'Success rate: {successful}/{total} '
            f'({successful / total * 100:.2f}%)'
            if total > 0 else 'No trials recorded.'
        )

        if total > 0:
            self.get_logger().info(
                f'Mean positioning error: {mean_error:.6f} mm'
            )

            self.get_logger().info(
                f'Mean movement time: {mean_movement:.3f} s'
            )

        self.get_logger().info(
            f'Results saved to: {self.csv_path}'
        )

        rclpy.shutdown()


def main(args=None):

    rclpy.init(args=args)

    node = ExperimentRunner()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if not node.csv_file.closed:
            node.csv_file.close()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()