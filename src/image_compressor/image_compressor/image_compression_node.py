import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge

import cv2


class ImageCompressor(Node):

    def __init__(self):
        super().__init__('image_compressor')

        self.declare_parameter('namespace', '')
        self.declare_parameter('input_topic', '/camera/camera/colour/image_raw')
        self.declare_parameter('output_topic', '/camera/image_compressed')
        self.declare_parameter('jpeg_quality', 80)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self.jpeg_quality = self.get_parameter('jpeg_quality').value

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            input_topic,
            self.image_callback,
            10
        )

        self.publisher = self.create_publisher(
            CompressedImage,
            output_topic,
            10
        )

        self.get_logger().info(
            f'Compressing {input_topic} -> {output_topic} '
            f'(JPEG quality={self.jpeg_quality})'
        )

    def image_callback(self, msg: Image):
        try:
            # ROS Image -> OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            # JPEG compression
            success, encoded_image = cv2.imencode(
                '.jpg',
                cv_image,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.jpeg_quality
                ]
            )

            if not success:
                self.get_logger().error('Failed to encode image')
                return

            # Create CompressedImage message
            compressed_msg = CompressedImage()

            compressed_msg.header = msg.header
            compressed_msg.format = 'jpeg'
            compressed_msg.data = encoded_image.tobytes()

            self.publisher.publish(compressed_msg)

        except Exception as e:
            self.get_logger().error(f'Image compression failed: {e}')


def main(args=None):
    rclpy.init(args=args)

    node = ImageCompressor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()