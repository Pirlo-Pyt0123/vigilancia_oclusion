import csv
import json
import os
from config import LOGS_DIR

def log_alert_csv(alert_data):
    filename = os.path.join(LOGS_DIR, "alerts_log.csv")
    fieldnames = ["id", "type", "timestamp", "image_path"]
    # Crea carpeta de logs si no existe
    os.makedirs(LOGS_DIR, exist_ok=True)
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(alert_data)

def log_alert_json(alert_data):
    filename = os.path.join(LOGS_DIR, "alerts_log.json")
    os.makedirs(LOGS_DIR, exist_ok=True)
    alerts = []
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            alerts = json.load(f)
    alerts.append(alert_data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
