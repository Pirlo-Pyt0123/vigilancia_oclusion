from ultralytics import YOLO
import cv2
from config import POSE_PAIRS
from utils import scalar

model = YOLO('yolov8n-pose.pt')

def detect_and_draw(frame):
    results = model.predict(frame, stream=True)
    output_imgs = []
    current_ids = []
    for r in results:
        result_img = r.plot()
        person_idx = 0
        for kp in r.keypoints:
            pts = kp.xy.cpu().numpy()
            id_actual = person_idx
            current_ids.append(id_actual)
            for pt in pts:
                x, y = scalar(pt[0]), scalar(pt[1])
                cv2.circle(result_img, (int(x), int(y)), 4, (0, 255, 255), -1)
            for partA, partB in POSE_PAIRS:
                if partA < len(pts) and partB < len(pts):
                    xA, yA = scalar(pts[partA][0]), scalar(pts[partA][1])
                    xB, yB = scalar(pts[partB][0]), scalar(pts[partB][1])
                    cv2.line(result_img, (int(xA), int(yA)), (int(xB), int(yB)), (255, 0, 0), 2)
            person_idx += 1
        output_imgs.append((result_img, current_ids))
    return output_imgs, current_ids
