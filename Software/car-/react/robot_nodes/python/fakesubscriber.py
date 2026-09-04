
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FriendCommandNode(Node):
    def __init__(self):
        super().__init__("friend_command_node")
        self.declare_parameter("topic", "cmd_drive")
        topic = self.get_parameter("topic").get_parameter_value().string_value

        self.create_subscription(String, topic, self.callback, 10)
        self.get_logger().info(f"Listening for commands on: {topic}")

    def callback(self, msg: String):
        print(f"Command received: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = FriendCommandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()