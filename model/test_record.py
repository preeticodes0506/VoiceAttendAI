import sounddevice as sd
from scipy.io.wavfile import write
import os

# ===========================================
# SETTINGS
# ===========================================

DURATION = 2          # seconds
FS = 44100            # sampling rate

# ===========================================
# CREATE FOLDER
# ===========================================

os.makedirs("test_voice", exist_ok=True)

filename = "test_voice/test.wav"

print("=" * 50)
print("🎤 Recording Started...")
print("Say 'Present'")
print("=" * 50)

# ===========================================
# RECORD AUDIO
# ===========================================

recording = sd.rec(
    int(DURATION * FS),
    samplerate=FS,
    channels=1,
    dtype='int16'
)

sd.wait()

# ===========================================
# SAVE AUDIO
# ===========================================

write(filename, FS, recording)

print("=" * 50)
print("✅ Voice Recorded Successfully!")
print("Saved at :", filename)
print("=" * 50)