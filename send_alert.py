import requests
from datetime import datetime
from human_detection import check_human_detection
import cv2
import os
import tempfile

BACKEND_URL = "http://localhost:8000/alert"

def send_alert(sound, confidence):
    """
    Send alert only if human is detected.
    Includes the captured image with the alert.
    """
    print(f"\n🔍 Checking conditions for alert...")
    print(f"   Audio Detection: {sound} (confidence: {confidence:.2f})")
    
    # Only check for Chainsaw or Footsteps
    if sound not in ["Chainsaw", "Footsteps"]:
        print(f"⚠️ Alert NOT sent: {sound} is not Chainsaw or Footsteps")
        return
    
    # Check human detection and get image
    print("👤 Checking for human detection...")
    human_detected, image_frame = check_human_detection()
    print(f"   Human Detection: {'✅ DETECTED' if human_detected else '❌ NOT DETECTED'}")
    
    # Only send alert if human is detected
    if not human_detected or image_frame is None:
        print("⚠️ Alert NOT sent: Human not detected")
        return
    
    print("✅ Human detected! Sending alert with image...")
    
    # Save image to temporary file
    temp_image_path = None
    try:
        # Create temporary file for image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_image_path = temp_file.name
        temp_file.close()
        
        # Save image
        cv2.imwrite(temp_image_path, image_frame)
        print(f"📸 Image captured and saved: {temp_image_path}")
        
        # Prepare multipart form data
        payload = {
            "sound": sound,
            "confidence": float(confidence),
            "sensor_id": "MIC_01",
            "zone_id": "ZONE_A",
            "risk": "HIGH",
            "message": f"{sound} detected with human presence – immediate action required",
            "timestamp": str(datetime.now())
        }
        
        # Prepare files for upload
        with open(temp_image_path, 'rb') as img_file:
            files = {
                'image': ('human_detection.jpg', img_file, 'image/jpeg')
            }
            
            try:
                res = requests.post(BACKEND_URL, data=payload, files=files)
                print(f"📡 Alert sent with image: {res.status_code}")
            except Exception as e:
                print(f"❌ Backend not reachable: {e}")
        
    finally:
        # Clean up temporary file
        if temp_image_path and os.path.exists(temp_image_path):
            os.unlink(temp_image_path)