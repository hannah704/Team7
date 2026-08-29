
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FriendSensorNode(Node):
    def __init__(self):
        super().__init__("friend_sensor_node")

        self.declare_parameter("topic", "sensor_data")
        self.declare_parameter("publish_interval_sec", 0.2)

        topic = self.get_parameter("topic").get_parameter_value().string_value
        interval = self.get_parameter("publish_interval_sec").get_parameter_value().double_value

        self.publisher_ = self.create_publisher(String, topic, 10)
        self.timer = self.create_timer(interval, self.publish_reading)

        self.get_logger().info(f"Publishing fake readings on: {topic}")

    def publish_reading(self):
        voltage = round(random.uniform(9.5, 12.6), 2)
        current = round(random.uniform(0.5, 3.0), 2)
        ax = round(random.uniform(-1.0, 1.0), 2)
        ay = round(random.uniform(-1.0, 1.0), 2)
        az = round(random.uniform(9.5, 10.1), 2)
        gx = round(random.uniform(-5.0, 5.0), 2)
        gy = round(random.uniform(-5.0, 5.0), 2)
        gz = round(random.uniform(-5.0, 5.0), 2)

        line = f"V:{voltage},I:{current},AX:{ax},AY:{ay},AZ:{az},GX:{gx},GY:{gy},GZ:{gz}"

        msg = String()
        msg.data = line
        self.publisher_.publish(msg)
        print(f"Sent: {line}")


def main(args=None):
    rclpy.init(args=args)
    node = FriendSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
