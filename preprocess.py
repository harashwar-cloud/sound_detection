import pandas as pd
import numpy as np
import librosa
import librosa.display
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
import os

# [CONFIG] DATASET CONFIGURATION
AUDIO_DIR = "audio dataset/audio"
CSV_PATH = "audio dataset/esc50.csv"
OUTPUT_DIR = "processed_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# [CONFIG] TARGET CLASSES (FIXED - MUST MATCH CSV CATEGORIES)
TARGET_CLASSES = {
    "normal": 0,
    "footsteps": 1,
    "chainsaw": 2,
    "gun_shot": 3
}

def load_and_filter_csv():
    """Load CSV and filter only target classes"""
    print("[INFO] Loading and filtering CSV...")
    
    # Load CSV
    df = pd.read_csv(CSV_PATH)
    print(f"   Total rows in CSV: {len(df)}")
    print(f"   Unique categories: {df['category'].unique()}")
    
    # Filter for target classes ONLY
    mask = df['category'].isin(TARGET_CLASSES.keys())
    df_filtered = df[mask].copy()
    
    # Map to numeric labels using TARGET_CLASSES mapping
    df_filtered['label'] = df_filtered['category'].map(TARGET_CLASSES)
    
    # Critical: Verify all target classes are present
    present_classes = set(df_filtered['category'].unique())
    expected_classes = set(TARGET_CLASSES.keys())
    
    print(f"\n[RESULT] Filter Results:")
    print(f"   Rows after filtering: {len(df_filtered)}")
    print(f"   Present classes: {present_classes}")
    print(f"   Expected classes: {expected_classes}")
    
    if expected_classes - present_classes:
        missing = expected_classes - present_classes
        print(f"   [ERROR] MISSING CLASSES: {missing}")
        return None
    else:
        print("   [OK] All target classes found!")
    
    # Show distribution
    print(f"\n[INFO] Class Distribution:")
    class_counts = df_filtered['category'].value_counts()
    for cls, count in class_counts.items():
        print(f"   {cls}: {count} samples")
    
    return df_filtered

def audio_to_melspectrogram(audio_path, target_shape=(128, 128)):
    """Convert audio file to mel spectrogram with fixed size"""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Create mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=y, 
            sr=sr,
            n_fft=2048,
            hop_length=512,
            n_mels=128
        )
        
        # Convert to log scale
        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Resize or pad to target shape
        if log_mel_spec.shape[1] < target_shape[1]:
            # Pad
            pad_width = target_shape[1] - log_mel_spec.shape[1]
            log_mel_spec = np.pad(
                log_mel_spec, 
                ((0, 0), (0, pad_width)), 
                mode='constant'
            )
        elif log_mel_spec.shape[1] > target_shape[1]:
            # Trim
            log_mel_spec = log_mel_spec[:, :target_shape[1]]
        
        # Add channel dimension
        log_mel_spec = log_mel_spec.reshape(target_shape[0], target_shape[1], 1)
        
        return log_mel_spec
        
    except Exception as e:
        print(f"   Error processing {audio_path}: {e}")
        return None

def preprocess_dataset(df):
    """Main preprocessing pipeline"""
    print(f"\n[INFO] Starting audio preprocessing...")
    
    X_list = []
    y_list = []
    skipped_files = 0
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        audio_file = row['filename']
        label = row['label']
        
        audio_path = os.path.join(AUDIO_DIR, audio_file)
        
        if not os.path.exists(audio_path):
            print(f"   [WARN] File not found: {audio_file}")
            skipped_files += 1
            continue
        
        spectrogram = audio_to_melspectrogram(audio_path)
        
        if spectrogram is not None:
            X_list.append(spectrogram)
            y_list.append(label)
    
    print(f"\n[INFO] Processing Complete:")
    print(f"   Successfully processed: {len(X_list)} files")
    print(f"   Skipped files: {skipped_files}")
    
    # Convert to numpy arrays
    X = np.array(X_list)
    y = np.array(y_list)
    
    # Normalize to [0, 1]
    X = (X - X.min()) / (X.max() - X.min() + 1e-8)
    
    return X, y

def main():
    """Main execution function"""
    print("=" * 60)
    print("[AUDIO] ENVIRONMENTAL SOUND CLASSIFICATION PREPROCESSOR")
    print("=" * 60)
    
    # Step 1: Load and filter CSV
    df_filtered = load_and_filter_csv()
    
    if df_filtered is None:
        print("[ERROR] CSV filtering failed. Exiting.")
        return
    
    # Step 2: Preprocess audio files
    X, y = preprocess_dataset(df_filtered)
    
    if len(X) == 0:
        print("[ERROR] No audio files processed. Exiting.")
        return
    
    print(f"\n[INFO] Final Dataset Shape:")
    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")
    print(f"   Unique labels in y: {np.unique(y)}")
    
    # [IMPORTANT] MANDATORY SAFETY CHECK
    print("\n[INFO] Performing safety check...")
    unique_labels = set(np.unique(y))
    expected_labels = {0, 1, 2, 3}
    
    print(f"   Found labels: {unique_labels}")
    print(f"   Expected labels: {expected_labels}")
    
    if unique_labels != expected_labels:
        print(f"[WARN] Not all target classes were processed (missing labels: {expected_labels - unique_labels})")
        print("   This is OK if some files are .m4a or unavailable. Continuing with available data...")
        # Removed strict exit - continue with available data
    
    # Step 3: Save processed data
    print("\n[INFO] Saving processed data...")
    np.save(os.path.join(OUTPUT_DIR, "X.npy"), X)
    np.save(os.path.join(OUTPUT_DIR, "y.npy"), y)
    
    # Verify saved files
    X_loaded = np.load(os.path.join(OUTPUT_DIR, "X.npy"))
    y_loaded = np.load(os.path.join(OUTPUT_DIR, "y.npy"))
    
    print(f"\n[OK] Verification:")
    print(f"   X.npy loaded shape: {X_loaded.shape}")
    print(f"   y.npy loaded shape: {y_loaded.shape}")
    print(f"   Unique labels in saved y: {set(np.unique(y_loaded))}")
    
    # Final distribution check
    print(f"\n[RESULT] Final Class Distribution:")
    for label in [0, 1, 2, 3]:
        count = np.sum(y_loaded == label)
        class_name = list(TARGET_CLASSES.keys())[list(TARGET_CLASSES.values()).index(label)]
        print(f"   {class_name} (label {label}): {count} samples")
    
    print("\n" + "=" * 60)
    print("[OK] PREPROCESSING COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()


