import json
import time

import cv2
import websocket  
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

camera = cv2.VideoCapture(2, cv2.CAP_V4L2)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camera.isOpened():
    raise RuntimeError("Could not open camera")

model = YOLO("best.pt")

FRAME_W, FRAME_H = 640, 480
BACKEND_WS_URL = "ws://localhost:8765"

current_mode = "manual"

# Tuning
SPEED = 3
DEADZONE = 60             
CLOSE_FILL_RATIO = 0.92   

_ws = None  


def get_ws():
    """Lazily (re)connect to backend_server.py's websocket."""
    global _ws
    if _ws is None:
        try:
            _ws = websocket.create_connection(BACKEND_WS_URL, timeout=2)
            _ws.settimeout(0)  
        except Exception as exc:
            print(f"[autonomous] couldn't reach backend: {exc}")
            _ws = None
    return _ws


def send_drive(direction, speed=SPEED):
    global _ws
    ws = get_ws()
    if ws is None:
        return

    try:
        while True:
            ws.recv()
    except Exception:
        pass

    try:
        ws.send(json.dumps({"type": "drive", "direction": direction, "speed": speed}))
    except Exception as exc:
        print(f"[autonomous] send failed, reconnecting: {exc}")
        try:
            ws.close()
        except Exception:
            pass
        _ws = None


def drive_toward_detection(results):
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        send_drive("stop")
        return

    best_i = boxes.conf.argmax().item()
    x1, y1, x2, y2 = boxes.xyxy[best_i].tolist()
    cx, box_w, box_h = (x1 + x2) / 2, x2 - x1, y2 - y1

    if max(box_w / FRAME_W, box_h / FRAME_H) >= CLOSE_FILL_RATIO:
        send_drive("stop")
        return

    offset = cx - FRAME_W / 2
    if abs(offset) <= DEADZONE:
        send_drive("forward")
    elif offset > 0:
        send_drive("forward_right")
    else:
        send_drive("forward_left")


@app.route("/mode", methods=["POST"])
def set_mode():
    global current_mode
    data = request.get_json(silent=True) or {}
    mode = data.get("mode")

    if mode not in ("manual", "autonomous"):
        return jsonify({"error": "mode must be 'manual' or 'autonomous'"}), 400

    current_mode = mode
    if mode == "manual":
        send_drive("stop")

    print(f"Mode switched to: {current_mode}")
    return jsonify({"mode": current_mode})


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("Frame read failed")
            break

        frame = cv2.resize(frame, (FRAME_W, FRAME_H))

        if current_mode == "autonomous":
            results = model.predict(frame, imgsz=640, conf=0.2, verbose=False)
            drive_toward_detection(results)
            frame = results[0].plot()

        success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        if not success:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )
        time.sleep(1 / 30)


@app.route("/video")
def video():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
    return "Camera server is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)