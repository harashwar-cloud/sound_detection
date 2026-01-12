import os
import librosa
import numpy as np
import pandas as pd
import cv2
from tensorflow.keras.models import load_model

# ------------------ PATHS ------------------
MODEL_PATH = "forest_audio_model.h5"
CSV_PATH = "C:\\Users\\haras\\OneDrive\\Desktop\\preprocess\\audio dataset\\esc50.csv"
AUDIO_PATH = "C:\\Users\\haras\\OneDrive\\Desktop\\preprocess\\audio dataset\\audio"

# ------------------ CONFIG ------------------
SAMPLE_RATE = 22050
DURATION = 3
SAMPLES = SAMPLE_RATE * DURATION

# Classes used during training
TARGET_CLASSES = [
    "gun_shot",
    "chainsaw",
    "footsteps",
    "rain",
    "wind",
    "chirping_birds"
]

LABEL_MAP = {
    "gun_shot": 0,
    "chainsaw": 1,
    "footsteps": 2,
    "rain": 3,
    "wind": 3,
    "chirping_birds": 3
}

REVERSE_LABELS = {
    0: "Gunshot",
    1: "Chainsaw",
    2: "Footsteps",
    3: "Normal"
}

# ------------------ LOAD MODEL ------------------
model = load_model(MODEL_PATH)
print("[OK] Model loaded")

# ------------------ PREPROCESS ------------------
def extract_mel(file_path):
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    audio = audio[:SAMPLES]

    if len(audio) < SAMPLES:
        audio = np.pad(audio, (0, SAMPLES - len(audio)))

    mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128)
    mel = librosa.power_to_db(mel, ref=np.max)
    mel = cv2.resize(mel, (128, 128))
    mel = mel[np.newaxis, ..., np.newaxis]

    return mel

# ------------------ LOAD CSV ------------------
df = pd.read_csv(CSV_PATH)
df = df[df["category"].isin(TARGET_CLASSES)]

correct = 0
total = 0

print("\n[INFO] Testing model on dataset...\n")

# ------------------ TEST LOOP ------------------
for _, row in df.iterrows():
    # Only process .wav files (skip .m4a files that don't exist)
    if not row["filename"].endswith('.wav'):
        continue
    
    # Try both sample rate directories
    file_path = None
    for sr_dir in ['16000', '44100']:
        potential_path = os.path.join(AUDIO_PATH, sr_dir, row["filename"])
        if os.path.exists(potential_path):
            file_path = potential_path
            break
    
    if file_path is None:
        continue
    
    true_label = LABEL_MAP[row["category"]]

    try:
        mel = extract_mel(file_path)
        prediction = model.predict(mel, verbose=0)[0]

        pred_index = np.argmax(prediction)
        confidence = prediction[pred_index]

        predicted_label = REVERSE_LABELS[pred_index]
        true_label_name = REVERSE_LABELS[true_label]

        total += 1

        if pred_index == true_label:
            correct += 1
            status = "[CORRECT]"
        else:
            status = "[WRONG]"

        print(f"{row['filename']}")
        print(f"   True: {true_label_name}")
        print(f"   Pred: {predicted_label} ({confidence:.2f}) -> {status}\n")

    except Exception as e:
        print(f"Error processing {row['filename']}: {e}")
        continue

# ------------------ FINAL ACCURACY ------------------
if total == 0:
    print("No files were processed. Check dataset path or preprocessing errors.")
else:
    accuracy = (correct / total) * 100
    print("===================================")
    print(f"Final Accuracy: {accuracy:.2f}%")
    print("===================================")
    print(f"Correct: {correct}/{total}")