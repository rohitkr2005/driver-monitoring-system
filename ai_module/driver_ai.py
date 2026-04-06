import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
from ultralytics import YOLO
import requests
import time

# ---------------- ALERT SYSTEM ----------------
last_alert_time = 0
ALERT_COOLDOWN = 5  # seconds

def send_alert(alert_type):
    global last_alert_time

    current_time = time.time()

    # Prevent spamming alerts
    if current_time - last_alert_time < ALERT_COOLDOWN:
        return

    last_alert_time = current_time

    data = {
        "vehicle_id": "RJ14AB1234",
        "alert_type": alert_type
    }

    try:
        requests.post("http://127.0.0.1:8000/alert", params=data)
        print(f"[ALERT SENT]: {alert_type}")
    except:
        print("[ERROR] Could not send alert")

# ---------------- SOUND ----------------
SOUND_FILE = "alert.mp3"
pygame.mixer.init()
USE_SOUND = False

if os.path.exists(SOUND_FILE):
    try:
        pygame.mixer.music.load(SOUND_FILE)
        USE_SOUND = True
    except:
        pass

def play_alert():
    if USE_SOUND and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()

# ---------------- YOLO (PHONE DETECTION) ----------------
yolo_model = YOLO("yolov8n.pt")  # use yolov8s.pt for better accuracy
PHONE_CLASS_ID = 67
CONF_THRESHOLD = 0.6

def detect_phone(frame):
    results = yolo_model(frame, verbose=False)[0]
    phone_detected = False

    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        # Only detect mobile phones
        if cls == PHONE_CLASS_ID and conf > CONF_THRESHOLD:
            phone_detected = True

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(frame, f"Phone ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    return phone_detected

# ---------------- THRESHOLDS ----------------
EAR_THRESHOLD = 0.30
EAR_CRITICAL_FRAMES = 15
MAR_THRESHOLD = 0.65
HEAD_TILT_THRESHOLD = 15

eye_counter = 0
eye_not_visible_counter = 0

# ---------------- MEDIAPIPE ----------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH = [13, 14, 78, 308]

# ---------------- FUNCTIONS ----------------
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def EAR(eye):
    A = distance(eye[1], eye[5])
    B = distance(eye[2], eye[4])
    C = distance(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def MAR(mouth):
    vertical = distance(mouth[0], mouth[1])
    horizontal = distance(mouth[2], mouth[3])
    return vertical / horizontal

def is_valid(points, w, h):
    for x, y in points:
        if x <= 0 or y <= 0 or x >= w or y >= h:
            return False
    return True

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

print("[INFO] Smart Driver Monitoring System Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # -------- PHONE DETECTION --------
    phone_detected = detect_phone(frame)

    if phone_detected:
        cv2.putText(frame, "PHONE USAGE DETECTED!", (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
        play_alert()
        send_alert("PHONE")

    # -------- FACE PROCESSING --------
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0]

        # -------- LANDMARKS --------
        left_eye = [(int(face.landmark[i].x * w), int(face.landmark[i].y * h)) for i in LEFT_EYE]
        right_eye = [(int(face.landmark[i].x * w), int(face.landmark[i].y * h)) for i in RIGHT_EYE]
        mouth = [(int(face.landmark[i].x * w), int(face.landmark[i].y * h)) for i in MOUTH]

        # -------- EYE CHECK --------
        if is_valid(left_eye, w, h) and is_valid(right_eye, w, h):
            eye_not_visible_counter = 0

            ear = (EAR(left_eye) + EAR(right_eye)) / 2.0

            if ear < EAR_THRESHOLD:
                eye_counter += 1
                if eye_counter > EAR_CRITICAL_FRAMES:
                    cv2.putText(frame, "DROWSINESS ALERT!", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    play_alert()
                    send_alert("DROWSINESS")
            else:
                eye_counter = 0

            cv2.putText(frame, f"EAR: {ear:.2f}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        else:
            eye_not_visible_counter += 1
            eye_counter = 0

            cv2.putText(frame, "Eyes not visible", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # -------- YAWNING --------
        mar = MAR(mouth)
        if mar > MAR_THRESHOLD:
            cv2.putText(frame, "YAWNING DETECTED!", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            play_alert()
            send_alert("YAWNING")

        # -------- HEAD TILT --------
        nose = (int(face.landmark[1].x * w), int(face.landmark[1].y * h))
        chin = (int(face.landmark[152].x * w), int(face.landmark[152].y * h))

        dx = chin[0] - nose[0]
        dy = chin[1] - nose[1]

        angle = np.degrees(np.arctan2(dy, dx))

        if abs(angle) > HEAD_TILT_THRESHOLD:
            cv2.putText(frame, "HEAD TILT DETECTED!", (30, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # -------- DRAW --------
        for (x, y) in left_eye + right_eye:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        for (x, y) in mouth:
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)

    else:
        cv2.putText(frame, "Face not detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # -------- DISPLAY --------
    cv2.imshow("Driver Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()