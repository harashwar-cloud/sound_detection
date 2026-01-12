# How to Run the Forest Monitoring Alert System

## Prerequisites

1. **Python 3.8+** installed
2. **Virtual Environment** (recommended)
3. **Webcam** connected and working
4. **Microphone** connected and working
5. **YOLO Model File** (`yolov8n.pt`) in the project folder
6. **Audio Model File** (`forest_audio_model.h5`) in the project folder

## Setup Instructions

### Step 1: Install Dependencies

```bash
# Activate your virtual environment (if using one)
.venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Verify Files

Make sure you have these files in your project folder:
- `forest_audio_model.h5` - Audio detection model
- `yolov8n.pt` - Human detection model (YOLO)
- `live_detection.py` - Main detection script
- `send_alert.py` - Alert sending module
- `human_detection.py` - Human detection module

### Step 3: (Optional) Backend Server

The system sends alerts to `http://localhost:8000/alert`. 

**Option A: Run without backend (testing)**
- The system will work but show "Backend not reachable" when trying to send alerts
- You'll still see all detection messages in the console

**Option B: Setup a simple backend server**
- You need a backend server running on port 8000 that accepts POST requests to `/alert`

## Running the System

### Start the Detection System

```bash
python live_detection.py
```

### What Happens:

1. **Audio Recording**: The system records 2 seconds of audio from your microphone
2. **Audio Analysis**: Analyzes the audio for threats (Gunshot, Chainsaw, Footsteps, Normal)
3. **Detection Logic**: 
   - If Chainsaw or Footsteps detected → Checks camera for human
   - If human detected → Sends alert
   - If no human → No alert sent
4. **Continuous Loop**: Repeats every 2 seconds until you stop with Ctrl+C

## Alert Conditions

An alert will be sent **ONLY** when:
- ✅ Audio detection = **Chainsaw** OR **Footsteps**
- ✅ AND Human detected in camera
- ✅ AND Confidence ≥ 0.60

## Example Output

```
🎯 Live Detection Started - Press Ctrl+C to stop
============================================================
🎙️ Recording audio...
🔍 Detected: Chainsaw (0.85)

🔍 Checking conditions for alert...
   Audio Detection: Chainsaw (confidence: 0.85)
👤 Checking for human detection...
👤 Human detected!
   Human Detection: ✅ DETECTED
✅ Both conditions met! Sending alert...
📡 Alert sent: 200
------------------------------------------------------------
```

## Stopping the System

Press **Ctrl+C** to stop the detection system safely.

## Troubleshooting

### Webcam Issues
- Make sure webcam is connected and not used by another application
- Try closing other camera applications

### Microphone Issues
- Check microphone permissions in Windows settings
- Make sure microphone is the default recording device

### Model Not Found
- Verify `forest_audio_model.h5` exists in the project folder
- Verify `yolov8n.pt` exists in the project folder

### Import Errors
- Make sure all packages are installed: `pip install -r requirements.txt`
- Activate your virtual environment if using one

### Backend Connection Error
- This is normal if you don't have a backend server running
- The system will still detect and log everything to console
- To see alerts, you need a backend server on `http://localhost:8000/alert`
