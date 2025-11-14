import cv2
import os
from detection import detect_and_draw
from alerting import alert
from config import UMBRAL_ALERTA
from utils import make_dirs

make_dirs()
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

ausente = {}
all_ids_vistos = set()
capture_count = 0

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("No se pudo capturar el frame. Saliendo...")
        break
    outputs, current_ids = detect_and_draw(frame)
    for result_img, ids_in_img in outputs:
        for id in all_ids_vistos | set(ids_in_img):
            if id in ids_in_img:
                if ausente.get(id, 0) >= UMBRAL_ALERTA:
                    filename = alert(id, result_img, capture_count)
                    capture_count += 1
                ausente[id] = 0
            else:
                ausente[id] = ausente.get(id, 0) + 1
        all_ids_vistos.update(ids_in_img)
        cv2.imshow("VIGILANCIA IA", result_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()
