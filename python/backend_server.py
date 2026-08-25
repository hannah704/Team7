
import argparse
import asyncio
import json
import logging
from abc import ABC, abstractmethod

import serial
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backend")


class SensorFrame:
    """Parses one line of telemetry sent by the firmware.

    Expected firmware line format (adjust to match your firmware's
    actual output — this is the one thing you MUST agree on with the
    firmware/hardware sub-team):

        V:12.40,I:1.23,IMU:0.10;0.20;0.30

    where IMU is roll;pitch;yaw (or ax;ay;az — whatever you're sending).
    """

    def __init__(self, voltage: float, current: float, imu: list[float]):
        self.voltage = voltage
        self.current = current
        self.imu = imu

    @classmethod
    def from_line(cls, line: str) -> "SensorFrame | None":
        try:
            parts = dict(p.split(":", 1) for p in line.strip().split(","))
            voltage = float(parts["V"])
            current = float(parts["I"])
            imu = [float(x) for x in parts["IMU"].split(";")]
            return cls(voltage, current, imu)
        except (KeyError, ValueError, IndexError):
            log.warning("Malformed line from firmware: %r", line)
            return None

    def to_json(self) -> str:
        return json.dumps(
            {
                "type": "telemetry",
                "voltage": self.voltage,
                "current": self.current,
                "imu": self.imu,
            }
        )


class MotionCommand(ABC):
    """Base class for anything that can be turned into a byte/line
    sent down the serial link to the ATmega. Subclass per command type
    if you want richer behavior later (this satisfies the spec's
    'OOP concepts / abstract classes' requirement)."""

    @abstractmethod
    def to_wire(self) -> bytes:
        ...


class DriveCommand(MotionCommand):
    DIRECTIONS = {"forward": "F", "backward": "B", "left": "L", "right": "R", "stop": "S"
                  ,"forward_left": "FL", "forward_right": "FR", "backward_left": "BL", "backward_right": "BR"}

    def __init__(self, direction: str, speed: int):
        if direction not in self.DIRECTIONS:
            raise ValueError(f"unknown direction: {direction}")
        if not 0 <= speed <= 255:
            raise ValueError("speed must be 0-255")
        self.direction = direction
        self.speed = speed

    def to_wire(self) -> bytes:
        letter = self.DIRECTIONS[self.direction]
        return f"M,{letter},{self.speed}\n".encode()


class SerialLink:
    """Wraps the HC-05 serial port. All serial I/O is funneled through
    here so nothing else touches pyserial directly."""

    def __init__(self, port: str, baudrate: int = 9600):
        self.port_name = port
        self.baudrate = baudrate
        self.ser: serial.Serial | None = None

    def open(self) -> None:
        self.ser = serial.Serial(self.port_name, self.baudrate, timeout=1)
        log.info("Serial link open on %s @ %d", self.port_name, self.baudrate)

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

    def readline(self) -> str | None:
        if not self.ser or not self.ser.in_waiting:
            return None
        try:
            return self.ser.readline().decode(errors="ignore")
        except serial.SerialException as exc:
            log.error("Serial read error: %s", exc)
            return None

    def write(self, data: bytes) -> None:
        if self.ser and self.ser.is_open:
            self.ser.write(data)


class GuiBackendServer:
    """Owns the set of connected React clients and the serial link,
    and runs the two async loops that move data between them."""

    def __init__(self, link: SerialLink, host: str = "0.0.0.0", ws_port: int = 8765):
        self.link = link
        self.host = host
        self.ws_port = ws_port
        self.clients: set[WebSocketServerProtocol] = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        log.info("Client connected (%d total)", len(self.clients))

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.discard(ws)
        log.info("Client disconnected (%d total)", len(self.clients))

    async def broadcast(self, message: str) -> None:
        if not self.clients:
            return
        await asyncio.gather(
            *(ws.send(message) for ws in self.clients), return_exceptions=True
        )

    def analyze_and_warn(self, frame: SensorFrame) -> str | None:
        """Spec requires the backend to issue warnings on risky readings."""
        if frame.voltage < 9.0:
            return "LOW_VOLTAGE"
        if frame.current > 5.0:
            return "OVERCURRENT"
        return None

    async def serial_poll_loop(self) -> None:
        """Continuously reads serial and broadcasts telemetry + warnings."""
        while True:
            line = self.link.readline()
            if line:
                frame = SensorFrame.from_line(line)
                if frame:
                    await self.broadcast(frame.to_json())
                    warning = self.analyze_and_warn(frame)
                    if warning:
                        await self.broadcast(json.dumps({"type": "warning", "code": warning}))
            await asyncio.sleep(0.02)  # yield control, ~50Hz poll

    async def handle_client(self, ws: WebSocketServerProtocol) -> None:
        await self.register(ws)
        try:
            async for raw in ws:
                await self.handle_command(raw)
        finally:
            await self.unregister(ws)

    async def handle_command(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            log.warning("Bad JSON from client: %r", raw)
            return

        if msg.get("type") == "drive":
            cmd = DriveCommand(msg["direction"], msg.get("speed", 150))
            self.link.write(cmd.to_wire())
        elif msg.get("type") == "mode":
            # e.g. {"type": "mode", "mode": "autonomous"} — extend as needed
            self.link.write(f"M{msg['mode'][0].upper()}\n".encode())
        else:
            log.warning("Unknown command type: %s", msg.get("type"))

    async def run(self) -> None:
        self.link.open()
        async with websockets.serve(self.handle_client, self.host, self.ws_port):
            log.info("WebSocket server listening on ws://%s:%d", self.host, self.ws_port)
            await self.serial_poll_loop()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/rfcomm0 or COM5")
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--ws-port", type=int, default=8765)
    args = parser.parse_args()

    link = SerialLink(args.port, args.baud)
    server = GuiBackendServer(link, ws_port=args.ws_port)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        pass
    finally:
        link.close()


if __name__ == "__main__":
    main()
