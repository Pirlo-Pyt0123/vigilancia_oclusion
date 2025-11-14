from flask import Flask, jsonify, send_from_directory, Response
from flask_cors import CORS
import csv
import os
import cv2

from detection import detect_and_draw
from alerting import alert
from config import UMBRAL_ALERTA
from utils import make_dirs, timestamp
from logger import log_alert_csv, log_alert_json

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

LOGS_DIR = "logs"
CAPTURES_DIR = "captures"

ausente = {}
all_ids_vistos = set()
capture_count = 0

make_dirs()

@app.route("/api/video_feed")
def video_feed():
    def generate_frames():
        global ausente, all_ids_vistos, capture_count
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            outputs, current_ids = detect_and_draw(frame)
            for result_img, ids_in_img in outputs:
                for id in all_ids_vistos | set(ids_in_img):
                    if id in ids_in_img:
                        if ausente.get(id, 0) >= UMBRAL_ALERTA:
                            filename = alert(id, result_img, capture_count)
                            alert_data = {
                                "id": str(id),
                                "type": "oclusion-reaparecido",
                                "timestamp": timestamp(),
                                "image_path": filename
                            }
                            log_alert_csv(alert_data)
                            log_alert_json(alert_data)
                            capture_count += 1
                        ausente[id] = 0
                    else:
                        ausente[id] = ausente.get(id, 0) + 1
                all_ids_vistos.update(ids_in_img)
                _, buffer = cv2.imencode('.jpg', result_img)
                frame_bytes = buffer.tobytes()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )
        cap.release()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/api/snapshot")
def get_snapshot():
    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    cap.release()
    outputs, _ = detect_and_draw(frame)
    if success and len(outputs) > 0:
        result_img, _ = outputs[0]
        os.makedirs(CAPTURES_DIR, exist_ok=True)
        temp_path = os.path.join(CAPTURES_DIR, "current_snapshot.jpg")
        cv2.imwrite(temp_path, result_img)
        return send_from_directory(CAPTURES_DIR, "current_snapshot.jpg")
    else:
        return jsonify({"error": "No se pudo capturar imagen"}), 500

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    filename = os.path.join(LOGS_DIR, "alerts_log.csv")
    alerts = []
    if os.path.isfile(filename):
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alerts.append(row)
    return jsonify(alerts)

@app.route("/api/captures", methods=["GET"])
def get_captures():
    captures = []
    if os.path.isdir(CAPTURES_DIR):
        for img in os.listdir(CAPTURES_DIR):
            if img.endswith(".jpg"):
                try:
                    _parts = img.split("_")
                    _id = _parts[3].replace(".jpg", "")
                    _timestamp = _parts[2]
                except Exception:
                    _id = "_"
                    _timestamp = "_"
                captures.append({
                    "id": _id,
                    "src": f"/api/captures/{img}",
                    "timestamp": _timestamp,
                    "tipo": "oclusion-reaparecido"
                })
    return jsonify(captures)

@app.route("/api/captures/<filename>")
def get_capture_file(filename):
    return send_from_directory(CAPTURES_DIR, filename)

@app.route("/api/summary", methods=["GET"])
def get_summary():
    filename = os.path.join(LOGS_DIR, "alerts_log.csv")
    personas = set()
    alertas = 0
    capturas = 0
    if os.path.isfile(filename):
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                capturas += 1
                personas.add(row["id"])
                alertas += 1
    return jsonify({
        "personsDetected": len(personas),
        "activeAlerts": alertas,
        "capturesGenerated": capturas
    })

if __name__ == "__main__":
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(CAPTURES_DIR, exist_ok=True)
    app.run(debug=True, port=8000)
