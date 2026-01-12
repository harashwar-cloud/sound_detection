import cv2
from ultralytics import YOLO
import os

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8n.pt"
HUMAN_CONF = 0.5

# Load model
_human_model = None

def get_human_model():
    """Get or load the human detection model (singleton pattern)"""
    global _human_model
    if _human_model is None:
        if os.path.exists(MODEL_PATH):
            _human_model = YOLO(MODEL_PATH)
        else:
            raise FileNotFoundError(f"YOLO model not found at: {MODEL_PATH}")
    return _human_model

def check_human_detection():
    """
    Check if human is detected using YOLO model.
    Returns (bool, frame) tuple: (True/False, image_frame or None)
    Returns image frame only when human is detected.
    """
    try:
        human_model = get_human_model()
        
        # Capture one frame from webcam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("⚠️ Webcam not available")
            return False, None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("⚠️ Could not capture frame")
            return False, None
        
        # Run detection
        results = human_model(frame, conf=HUMAN_CONF, verbose=False)
        
        # Check if human detected
        human_detected = False
        for r in results:
            for box in r.boxes:
                label = human_model.names[int(box.cls[0])]
                if label == "person":
                    human_detected = True
                    break
            if human_detected:
                break
        
        # Return image only if human is detected
        if human_detected:
            return True, frame
        else:
            return False, None
        
    except Exception as e:
        print(f"⚠️ Human detection check failed: {e}")
        return False, None
