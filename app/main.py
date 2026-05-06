import cv2
from ultralytics import YOLO
import time
import winsound
import math
from database import insert_alert
model = YOLO("yolov8n.pt")
VIDEO_PATH = "test.mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("Video error")
    exit()
last_alert_time = 0
ALERT_COOLDOWN = 5
CROWD_THRESHOLD = 3
prev_centers = []
while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    frame = cv2.resize(frame, (640, 480))
    h, w, _ = frame.shape
    zx1, zy1 = int(w * 0.3), int(h * 0.3)
    zx2, zy2 = int(w * 0.7), int(h * 0.7)

    cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (255, 0, 0), 2)
    cv2.putText(frame, "Restricted Zone", (zx1, zy1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    results = model(frame, conf=0.4)
    person_count = 0
    intrusion_detected = False
    centers = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls == 0: 
                person_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                centers.append((cx, cy))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)
                if zx1 < cx < zx2 and zy1 < cy < zy2:
                    intrusion_detected = True
    cv2.putText(frame, f"People: {person_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    crowd_detected = person_count >= CROWD_THRESHOLD
    if crowd_detected:
        cv2.putText(frame, "CROWD DETECTED!", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    fight_detected = False
    if len(prev_centers) == len(centers):
        for i in range(len(centers)):
            dx = centers[i][0] - prev_centers[i][0]
            dy = centers[i][1] - prev_centers[i][1]
            movement = math.sqrt(dx * dx + dy * dy)
            if movement > 20:
                fight_detected = True
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            dist = math.sqrt(
                (centers[i][0] - centers[j][0])**2 +
                (centers[i][1] - centers[j][1])**2
            )
            if dist < 50:
                fight_detected = True
    if fight_detected:
        cv2.putText(frame, "FIGHT DETECTED!", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    if intrusion_detected:
        cv2.putText(frame, "INTRUSION ALERT!", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    if intrusion_detected or crowd_detected or fight_detected:
        current_time = time.time()
        if current_time - last_alert_time > ALERT_COOLDOWN:
            try:
                winsound.Beep(1000, 300)
            except:
                pass
            if intrusion_detected:
                insert_alert("intrusion", person_count)
            if crowd_detected:
                insert_alert("crowd", person_count)
            if fight_detected:
                insert_alert("fight", person_count)
            last_alert_time = current_time
    prev_centers = centers.copy()
    cv2.imshow("AI CCTV FINAL SYSTEM", frame)
    if cv2.waitKey(25) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()