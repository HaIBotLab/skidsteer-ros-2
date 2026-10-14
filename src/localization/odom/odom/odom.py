#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion

from tf_transformations import quaternion_from_euler

import math


class EncoderIMUToOdomNode(Node):

    def __init__(self):
        super().__init__('odom')

        # =========================
        # PARAMETERS
        # =========================

        self.declare_parameter('wheel_radius', 0.1)
        self.declare_parameter('wheel_base', 0.5)

        self.declare_parameter(
            'encoder_feedback_topic',
            '/zlac_encoder'
        )

        self.declare_parameter(
            'imu_topic',
            '/imu/data'
        )

        self.declare_parameter(
            'odom_topic',
            '/odom'
        )

        self.wheel_radius = self.get_parameter(
            'wheel_radius'
        ).value

        self.wheel_base = self.get_parameter(
            'wheel_base'
        ).value

        self.encoder_feedback_topic = self.get_parameter(
            'encoder_feedback_topic'
        ).value

        self.imu_topic = self.get_parameter(
            'imu_topic'
        ).value

        self.odom_topic = self.get_parameter(
            'odom_topic'
        ).value

        # =========================
        # ROBOT STATE
        # =========================

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.last_time = None

        self.left_rpm = None
        self.right_rpm = None

        # Yaw rate from IMU
        self.yaw_rate = 0.0

        # =========================
        # SUBSCRIBERS
        # =========================

        self.encoder_sub = self.create_subscription(
            Int32MultiArray,
            self.encoder_feedback_topic,
            self.encoder_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Imu,
            self.imu_topic,
            self.imu_callback,
            10
        )

        # =========================
        # PUBLISHER
        # =========================

        self.odom_pub = self.create_publisher(
            Odometry,
            self.odom_topic,
            10
        )

        # =========================
        # TIMER
        # =========================

        self.timer = self.create_timer(
            0.02,       # 50 Hz
            self.update_odom
        )

        self.get_logger().info(
            'EncoderIMUToOdomNode started'
        )

    # =====================================================
    # ENCODER CALLBACK
    # =====================================================

    def encoder_callback(self, msg: Int32MultiArray):

        if len(msg.data) < 2:
            self.get_logger().warn(
                f'/zlac_encoder has {len(msg.data)} values, '
                'but 2 are required'
            )
            return

        # ESP32:
        # data[0] = left feedback RPM
        # data[1] = right feedback RPM

        self.left_rpm = float(msg.data[0])

        # IMPORTANT:
        # Keep this sign conversion according to your
        # current encoder convention.
        self.right_rpm = -float(msg.data[1])

    # =====================================================
    # IMU CALLBACK
    # =====================================================

    def imu_callback(self, msg: Imu):

        # Angular velocity around Z axis
        self.yaw_rate = msg.angular_velocity.z

    # =====================================================
    # ODOM UPDATE
    # =====================================================

    def update_odom(self):

        if self.left_rpm is None or self.right_rpm is None:
            return

        current_time = self.get_clock().now()

        if self.last_time is None:
            self.last_time = current_time
            return

        dt = (
            current_time - self.last_time
        ).nanoseconds * 1e-9

        self.last_time = current_time

        if dt <= 0.0:
            return

        # =================================================
        # RPM -> m/s
        # =================================================

        left_vel = (
            self.left_rpm
            * 2.0
            * math.pi
            * self.wheel_radius
            / 60.0
        )

        right_vel = (
            self.right_rpm
            * 2.0
            * math.pi
            * self.wheel_radius
            / 60.0
        )

        # =================================================
        # LINEAR VELOCITY FROM ENCODER
        # =================================================

        linear_vel = (
            left_vel + right_vel
        ) / 2.0

        # =================================================
        # ANGULAR VELOCITY FROM IMU
        # =================================================

        angular_vel = self.yaw_rate

        # =================================================
        # UPDATE POSE
        # =================================================

        self.x += (
            linear_vel
            * math.cos(self.theta)
            * dt
        )

        self.y += (
            linear_vel
            * math.sin(self.theta)
            * dt
        )

        self.theta += angular_vel * dt

        self.theta = math.atan2(
            math.sin(self.theta),
            math.cos(self.theta)
        )

        # =================================================
        # QUATERNION
        # =================================================

        q = quaternion_from_euler(
            0.0,
            0.0,
            self.theta
        )

        # =================================================
        # ODOM MESSAGE
        # =================================================

        odom = Odometry()

        odom.header.stamp = (
            current_time.to_msg()
        )

        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        odom.pose.pose.orientation = Quaternion(
            x=q[0],
            y=q[1],
            z=q[2],
            w=q[3]
        )

        # Velocity
        odom.twist.twist.linear.x = linear_vel
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.linear.z = 0.0

        # IMPORTANT:
        # angular.z now comes from IMU
        odom.twist.twist.angular.x = 0.0
        odom.twist.twist.angular.y = 0.0
        odom.twist.twist.angular.z = angular_vel

        # =================================================
        # COVARIANCE
        # =================================================

        odom.pose.covariance = [
            0.01, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.01, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1e6, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1e6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1e6, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0086,
        ]

        odom.twist.covariance = [
            0.001, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 1e6, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1e6, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1e6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1e6, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.01,
        ]

        self.odom_pub.publish(odom)


def main(args=None):

    rclpy.init(args=args)

    node = EncoderIMUToOdomNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
