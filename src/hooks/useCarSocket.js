// useCarSocket.js
//
// Connects to backend_server.py over WebSocket. Exposes live telemetry
// and connection state, and gives you sendDrive()/sendMode() to control
// the rover. The backend forwards these over serial (HC-05) to the ATmega.

import { useEffect, useRef, useState, useCallback } from "react";

const WS_URL = "ws://localhost:8765";

export function useCarSocket(url = WS_URL) {
  const [connected, setConnected] = useState(false);
  const [telemetry, setTelemetry] = useState({
    voltage: null,
    current: null,
    imu: { x: 0, y: 0, z: 0 },
  });
  const [warning, setWarning] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onclose = () => {
      setConnected(false);
      // auto-reconnect so a dropped Bluetooth/wifi link doesn't require
      // a manual page refresh
      reconnectTimer.current = setTimeout(connect, 2000);
    };

    ws.onerror = () => ws.close();

    ws.onmessage = (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }

      if (msg.type === "telemetry") {
        setTelemetry({
          voltage: msg.voltage,
          current: msg.current,
          imu: { x: msg.imu[0], y: msg.imu[1], z: msg.imu[2] },
        });
      } else if (msg.type === "warning") {
        setWarning(msg.code);
      }
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  const sendDrive = useCallback(
    (direction, speed = 150) => send({ type: "drive", direction: direction.toLowerCase(), speed }),
    [send]
  );

  const sendMode = useCallback((mode) => send({ type: "mode", mode }), [send]);

  return { connected, telemetry, warning, sendDrive, sendMode };
}
