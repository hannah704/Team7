
import { useEffect, useRef, useState, useCallback } from "react";

const WS_URL = "ws://localhost:8765";
const WARNING_DISPLAY_MS = 5000;

export function useCarSocket(url = WS_URL) {
  const [connected, setConnected] = useState(false);
  const [telemetry, setTelemetry] = useState({
    voltage: null,
    current: null,
    accel: { x: 0, y: 0, z: 0 },
    gyro: { x: 0, y: 0, z: 0 },
  });
  const [warning, setWarning] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const warningTimer = useRef(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onclose = () => {
      setConnected(false);
 
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
          accel: msg.accel, 
          gyro: msg.gyro,   
        });
      } else if (msg.type === "warning") {
        setWarning(msg.code);
 
        clearTimeout(warningTimer.current);
        warningTimer.current = setTimeout(() => setWarning(null), WARNING_DISPLAY_MS);
      }
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      clearTimeout(warningTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  const sendDrive = useCallback(
    (direction, speed = 3) => send({ type: "drive", direction: direction.toLowerCase(), speed }),
    [send]
  );

  const sendMode = useCallback((mode) => send({ type: "mode", mode }), [send]);

  return { connected, telemetry, warning, sendDrive, sendMode };
}