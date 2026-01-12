# Quick Start Guide

## 🚀 Quick Run (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: (Optional) Start Backend Server
Open a **new terminal** and run:
```bash
pip install flask
python test_backend_server.py
```
Keep this terminal open - this will receive and display your alerts.

### Step 3: Run Detection System
In your **main terminal**, run:
```bash
python live_detection.py
```

## 🎯 How to Get Alert Messages

### Method 1: Console Output (No Backend Needed)
- Run `python live_detection.py`
- All detection results and alert status will print to console
- You'll see messages like:
  - `✅ Both conditions met! Sending alert...`
  - `⚠️ Alert NOT sent: Human not detected`
  - `⚠️ Alert NOT sent: Gunshot is not Chainsaw or Footsteps`

### Method 2: Backend Server (Recommended)
1. Start backend server: `python test_backend_server.py`
2. Start detection: `python live_detection.py`
3. When alert is triggered, you'll see it in **both** terminals:
   - Detection terminal: Shows detection process
   - Backend terminal: Shows formatted alert message

## 📋 What You'll See

### When Conditions Are Met:
```
🔍 Detected: Chainsaw (0.85)

🔍 Checking conditions for alert...
   Audio Detection: Chainsaw (confidence: 0.85)
👤 Checking for human detection...
   Human Detection: ✅ DETECTED
✅ Both conditions met! Sending alert...
📡 Alert sent: 200
```

### When Human Not Detected:
```
🔍 Detected: Footsteps (0.75)

🔍 Checking conditions for alert...
   Audio Detection: Footsteps (confidence: 0.75)
👤 Checking for human detection...
   Human Detection: ❌ NOT DETECTED
⚠️ Alert NOT sent: Human not detected (both conditions required)
```

### When Wrong Sound Type:
```
🔍 Detected: Gunshot (0.90)

🔍 Checking conditions for alert...
   Audio Detection: Gunshot (confidence: 0.90)
⚠️ Alert NOT sent: Gunshot is not Chainsaw or Footsteps
```

## 🔧 Troubleshooting

**No alerts showing?**
- Make sure you're detecting Chainsaw or Footsteps (not Gunshot)
- Make sure a person is visible in the camera
- Check that confidence is ≥ 0.60

**Backend not reachable?**
- Start the backend server first: `python test_backend_server.py`
- Or just use console output (Method 1)

**Webcam issues?**
- Close other camera applications
- Check camera permissions
