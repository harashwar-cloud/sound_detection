import sounddevice as sd
import librosa
import numpy as np
import cv2
import random
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from scipy.io.wavfile import write
from send_alert import send_alert
import os
import sys

# ---------------- CONFIG ----------------
MODEL_FILENAME = "forest_audio_model.h5"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

if not os.path.exists(MODEL_PATH):
    print(f"Model file not found at: {MODEL_PATH}")
    print("Place the model file there or update MODEL_FILENAME to the correct path.")
    sys.exit(1)

def load_model_compatible(filepath):
    """Load Keras model with compatibility for quantization_config parameter."""
    try:
        # Try normal loading first
        return load_model(filepath, compile=False)
    except (TypeError, ValueError) as e:
        if 'quantization_config' in str(e):
            # Handle quantization_config compatibility issue
            # Reconstruct the model architecture (known from train_model.py)
            model = Sequential([
                Input(shape=(128,128,1)),
                Conv2D(32, (3,3), activation='relu'),
                MaxPooling2D(2,2),
                Conv2D(64, (3,3), activation='relu'),
                MaxPooling2D(2,2),
                Flatten(),
                Dense(128, activation='relu'),
                Dropout(0.3),
                Dense(4, activation='softmax')
            ])
            
            # Load weights from the saved model file
            model.load_weights(filepath, by_name=True)
            
            return model
        else:
            raise

MODEL = load_model_compatible(MODEL_PATH)
# Compile model for predictions
MODEL.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

LABELS = ["Gunshot", "Chainsaw", "Footsteps", "Normal"]

SAMPLE_RATE = 22050
DURATION = 2              # 🔥 MUST MATCH TRAINING
SAMPLES = SAMPLE_RATE * DURATION
CONF_THRESHOLD = 0.60     # safer threshold

# ----------------------------------------

def add_noise(audio, noise_level=0.005):
    noise = np.random.randn(len(audio))
    return audio + noise_level * noise

def record_audio():
    print("🎙️ Recording audio...")
    audio = sd.rec(SAMPLES, samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    audio = audio.flatten()
    write("temp.wav", SAMPLE_RATE, audio)
    return audio

def preprocess_audio(audio):
    # Pad / cut
    if len(audio) < SAMPLES:
        audio = np.pad(audio, (0, SAMPLES - len(audio)))
    else:
        audio = audio[:SAMPLES]

    # Normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    # 🔥 Light noise injection (robustness)
    if random.random() < 0.3:
        audio = add_noise(audio)

    # Mel spectrogram
    mel = librosa.feature.melspectrogram(
        y=audio, sr=SAMPLE_RATE, n_mels=128
    )
    mel = librosa.power_to_db(mel, ref=np.max)

    # Resize for CNN
    mel = cv2.resize(mel, (128, 128))
    mel = mel[np.newaxis, ..., np.newaxis]

    return mel

# ---------------- RUN PIPELINE ----------------

def main():
    print("🎯 Live Detection Started - Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            audio = record_audio()
            data = preprocess_audio(audio)
            
            prediction = MODEL.predict(data)[0]
            index = np.argmax(prediction)
            confidence = float(prediction[index])
            detected_sound = LABELS[index]
            
            print(f"🔍 Detected: {detected_sound} ({confidence:.2f})")
            
            if confidence >= CONF_THRESHOLD and detected_sound != "Normal":
                # send_alert will check if it's Chainsaw/Footsteps AND human detected
                send_alert(detected_sound, confidence)
            else:
                print("✅ No threat detected")
            
            print("-" * 60)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Detection stopped by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()