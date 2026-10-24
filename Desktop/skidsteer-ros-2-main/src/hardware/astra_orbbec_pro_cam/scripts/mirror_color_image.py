#!/usr/bin/env python3
import cv2
import rclpy

from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class MirrorColorImageNode(Node):
    def __init__(self) -> None:
        super().__init__('mirror_color_image')
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(
            Image,
            '/camera/color/image_mirrored',
            qos_profile_sensor_data,
        )
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.handle_image,
            qos_profile_sensor_data,
        )

    def handle_image(self, msg: Image) -> None:
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        mirrored = cv2.flip(frame, 1)
        mirrored_msg = self.bridge.cv2_to_imgmsg(mirrored, encoding=msg.encoding)
        mirrored_msg.header = msg.header
        self.publisher.publish(mirrored_msg)


def main() -> None:
    rclpy.init()
    node = MirrorColorImageNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
