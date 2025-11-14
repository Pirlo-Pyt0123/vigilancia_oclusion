import cv2
import os
import platform
from utils import timestamp

if platform.system() == 'Windows':
    import winsound

from config import SAVE_DIR

def alert(id, frame, capture_count):
    cv2.putText(frame, f"ALERTA: ID {id} ocluido y reaparecido!", (30, 60 + 30 * id),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    print(f"ALERTA - ID {id} estuvo ausente y reapareció")
    if platform.system() == 'Windows':
        winsound.Beep(1000, 300)
    filename = f"{SAVE_DIR}/occlusion_alert_ID{id}_{timestamp()}_{capture_count}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Captura guardada en: {filename}")
    return filename
