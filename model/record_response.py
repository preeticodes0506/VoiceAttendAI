import sounddevice as sd
from scipy.io.wavfile import write
import os

FS = 44100
DURATION = 2

def record_response():

    os.makedirs("temp", exist_ok=True)

    filename = "temp/response.wav"

    print("Recording...")

    recording = sd.rec(
        int(DURATION * FS),
        samplerate=FS,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    write(filename, FS, recording)

    print("Recording Finished")

    return filename