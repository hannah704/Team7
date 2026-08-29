import argparse
import asyncio
import json
import logging
import threading
from abc import ABC, abstractmethod

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String

import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backend")


class SensorFrame:
    def __init__(self, voltage, current, accel, gyro):
        self.voltage = voltage
        self.current = current
        self.accel = accel
        self.gyro = gyro

    @classmethod
    def from_line(cls, line):
        try:
            parts = dict(p.split(":", 1) for p in line.strip().split(","))
            voltage = float(parts["V"])
            current = float(parts["I"])
            accel = [float(parts["AX"]), float(parts["AY"]), float(parts["AZ"])]
            gyro = [float(parts["GX"]), float(parts["GY"]), float(parts["GZ"])]
            return cls(voltage, current, accel, gyro)
        except (KeyError, ValueError, IndexError):
            log.warning("Malformed line from ROS topic: %r", line)
            return None

    def to_json(self):
        return json.dumps({
            "type": "telemetry",
            "voltage": self.voltage,
            "current": self.current,
            "accel": {"x": self.accel[0], "y": self.accel[1], "z": self.accel[2]},
            "gyro": {"x": self.gyro[0], "y": self.gyro[1], "z": self.gyro[2]},
        })


class MotionCommand(ABC):
    @abstractmethod
    def to_message(self) -> str:
        ...


class DriveCommand(MotionCommand):
    DIRECTIONS = {"forward": "F", "backward": "B", "left": "L", "right": "R", "stop": "S",
                  "forward_left": "FL", "forward_right": "FR", "backward_left": "BL", "backward_right": "BR"}

    def __init__(self, direction, speed):
        if direction not in self.DIRECTIONS:
            raise ValueError(f"unknown direction: {direction}")
        if not 0 <= speed <= 255:
            raise ValueError("speed must be 0-255")
        self.direction = direction
        self.speed = speed

    def to_message(self) -> str:
        return f"M,{self.DIRECTIONS[self.direction]},{self.speed}"


class ModeCommand(MotionCommand):
    def __init__(self, mode):
        self.mode = mode

    def to_message(self) -> str:
        return f"M{self.mode[0].upper()}"

class SensorSubscriberNode(Node):
    def __init__(self, on_message, topic: str):
        super().__init__("sensor_subscriber")
        self.on_message = on_message
        self.create_subscription(String, topic, self._callback, 10)
        self.get_logger().info(f"Subscribed to sensor topic: {topic}")

    def _callback(self, msg: String):
        self.on_message(msg.data)

class CommandPublisherNode(Node):
    def __init__(self, topic: str):
        super().__init__("command_publisher")
        self.publisher_ = self.create_publisher(String, topic, 10)
        self.get_logger().info(f"Publishing commands on topic: {topic}")

    def publish_command(self, text: str):
        msg = String()
        msg.data = text
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published command: {text}")


class GuiBackendServer:
    def __init__(self, host="0.0.0.0", ws_port=8765):
        self.host = host
        self.ws_port = ws_port
        self.clients = set()
        self.loop = None
        self.command_node: CommandPublisherNode | None = None

    async def register(self, ws):
        self.clients.add(ws)
        log.info("Client connected (%d total)", len(self.clients))

    async def unregister(self, ws):
        self.clients.discard(ws)
        log.info("Client disconnected (%d total)", len(self.clients))

    async def broadcast(self, message: str):
        if not self.clients:
            return
        await asyncio.gather(*(ws.send(message) for ws in self.clients), return_exceptions=True)

    def analyze_and_warn(self, frame: SensorFrame):
        if frame.voltage < 9.0:
            return "LOW_VOLTAGE"
        if frame.current > 5.0:
            return "OVERCURRENT"
        return None

    def on_ros_message(self, line: str):
        frame = SensorFrame.from_line(line)
        if not frame or self.loop is None:
            return

        asyncio.run_coroutine_threadsafe(self.broadcast(frame.to_json()), self.loop)

        warning = self.analyze_and_warn(frame)
        if warning:
            asyncio.run_coroutine_threadsafe(
                self.broadcast(json.dumps({"type": "warning", "code": warning})), self.loop
            )

    async def handle_client(self, ws):
        await self.register(ws)
        try:
            async for raw in ws:
                await self.handle_command(raw)
        finally:
            await self.unregister(ws)

    async def handle_command(self, raw: str):
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            log.warning("Bad JSON from client: %r", raw)
            return

        if msg.get("type") == "drive":
            cmd = DriveCommand(msg["direction"], msg.get("speed", 3))
        elif msg.get("type") == "mode":
            cmd = ModeCommand(msg["mode"])
        else:
            log.warning("Unknown command type: %s", msg.get("type"))
            return

        if self.command_node is not None:
            self.command_node.publish_command(cmd.to_message())

    async def run(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self.handle_client, self.host, self.ws_port):
            log.info("WebSocket server listening on ws://%s:%d", self.host, self.ws_port)
            await asyncio.Future()  # run forever


def ros_spin_thread(executor: SingleThreadedExecutor):
    executor.spin()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ws-port", type=int, default=8765)
    parser.add_argument("--sensor-topic", default="sensor_data")
    parser.add_argument("--cmd-topic", default="cmd_drive")
    args = parser.parse_args()

    backend = GuiBackendServer(ws_port=args.ws_port)

    rclpy.init()
    sensor_node = SensorSubscriberNode(backend.on_ros_message, args.sensor_topic)
    command_node = CommandPublisherNode(args.cmd_topic)
    backend.command_node = command_node

    executor = SingleThreadedExecutor()
    executor.add_node(sensor_node)
    executor.add_node(command_node)

    ros_thread = threading.Thread(target=ros_spin_thread, args=(executor,), daemon=True)
    ros_thread.start()

    try:
        asyncio.run(backend.run())
    except KeyboardInterrupt:
        pass
    finally:
        sensor_node.destroy_node()
        command_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()