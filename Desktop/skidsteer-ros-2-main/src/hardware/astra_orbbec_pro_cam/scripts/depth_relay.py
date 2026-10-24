#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, CameraInfo

class DepthRelay(Node):
    def __init__(self):
        super().__init__('depth_relay')
        
        qos_be = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )
        qos_rel = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )
        
        # Depth
        self.depth_pub = self.create_publisher(Image, '/camera/depth/image_raw_relay', qos_rel)
        self.depth_info_pub = self.create_publisher(CameraInfo, '/camera/depth/camera_info_relay', qos_rel)
        self.create_subscription(Image, '/camera/depth/image_raw',
            lambda msg: self.depth_pub.publish(msg), qos_be)
        self.create_subscription(CameraInfo, '/camera/depth/camera_info',
            lambda msg: self.depth_info_pub.publish(msg), qos_be)

        # Color
        self.color_pub = self.create_publisher(Image, '/camera/color/image_raw_relay', qos_rel)
        self.color_info_pub = self.create_publisher(CameraInfo, '/camera/color/camera_info_relay', qos_rel)
        self.create_subscription(Image, '/camera/color/image_raw',
            lambda msg: self.color_pub.publish(msg), qos_be)
        self.create_subscription(CameraInfo, '/camera/color/camera_info',
            lambda msg: self.color_info_pub.publish(msg), qos_be)

def main():
    rclpy.init()
    rclpy.spin(DepthRelay())

if __name__ == '__main__':
    main()
