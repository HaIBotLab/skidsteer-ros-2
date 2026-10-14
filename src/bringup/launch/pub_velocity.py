#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class TestVelocityNode(Node):
    def __init__(self):
        super().__init__('test_velocity_node')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.5   # m/s
        self.duration     = 5.0   # seconds

        self.get_logger().info(
            f"Bắt đầu chạy thẳng {self.linear_speed} m/s trong {self.duration}s..."
        )

        # Chạy sau 1s để đảm bảo publisher đã kết nối
        self.timer_start = self.create_timer(1.0, self.start_moving)
        self.start_time  = None
        self.moving      = False
        self.done        = False

    def start_moving(self):
        # Chỉ trigger 1 lần
        self.timer_start.cancel()
        self.start_time = time.time()
        self.moving     = True
        self.get_logger().info("GO!")
        self.timer_move = self.create_timer(0.05, self.move_callback)  # 20Hz

    def move_callback(self):
        if self.done:
            return

        elapsed = time.time() - self.start_time

        if elapsed < self.duration:
            msg = Twist()
            msg.linear.x  = self.linear_speed
            msg.angular.z = 0.0
            self.publisher.publish(msg)
            self.get_logger().info(
                f"t={elapsed:.2f}s | v={self.linear_speed} m/s",
                throttle_duration_sec=0.5
            )
        else:
            # Dừng robot
            stop_msg = Twist()
            stop_msg.linear.x  = 0.0
            stop_msg.angular.z = 0.0
            self.publisher.publish(stop_msg)
            self.get_logger().info(
                f"DỪNG! Hoàn thành {self.duration}s. "
                f"Lý thuyết đi được: {self.linear_speed * self.duration:.2f}m"
            )
            self.done = True
            self.timer_move.cancel()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = TestVelocityNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Dừng khẩn cấp khi Ctrl+C
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.get_logger().info("Dừng khẩn cấp!")
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
