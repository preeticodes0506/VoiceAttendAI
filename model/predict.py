import librosa
import numpy as np
import joblib
import sys

# =====================================================
# SETTINGS -- must match train_model.py exactly
# =====================================================
SR = 22050
N_MFCC = 40
SILENCE_RMS_THRESHOLD = 0.01

# -----------------------------
# Load Trained Model + Scaler
# -----------------------------
model = joblib.load("models/voice_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# -----------------------------
# Select Audio File
# -----------------------------
if len(sys.argv) > 1:
    voice_file = sys.argv[1]
else:
    voice_file = "test_voice/test.wav"


def extract_features_from_signal(signal, sr):
    """Must stay identical to train_model.py's version."""
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=N_MFCC)
    feature = np.concatenate([np.mean(mfcc, axis=1), np.std(mfcc, axis=1)])
    return feature


# -----------------------------
# Load Audio
# -----------------------------
signal, sr = librosa.load(voice_file, sr=SR)

# =====================================================
# SILENCE DETECTION
# =====================================================
rms = float(np.sqrt(np.mean(signal ** 2))) if len(signal) else 0.0

print(f"\nAudio RMS Value : {rms:.6f}")

if rms < SILENCE_RMS_THRESHOLD:
    print("=" * 50)
    print("❌ NO VOICE DETECTED")
    print("Attendance : ABSENT")
    print("=" * 50)
    sys.exit()

# =====================================================
# FEATURE EXTRACTION
# =====================================================
feature = extract_features_from_signal(signal, sr)
feature = feature.reshape(1, -1)

# =====================================================
# FEATURE SCALING
# =====================================================
feature = scaler.transform(feature)

# =====================================================
# PREDICTION
# =====================================================
prediction = model.predict(feature)
probabilities = model.predict_proba(feature)
confidence = np.max(probabilities) * 100

# =====================================================
# RESULT
# =====================================================
print("=" * 50)
print("Predicted Roll Number :", prediction[0])
print(f"Prediction Confidence : {confidence:.2f}%")
print("=" * 50)
