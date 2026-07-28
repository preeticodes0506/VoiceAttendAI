import streamlit as st
import sqlite3
import sounddevice as sd
from scipy.io.wavfile import write
import os

from utils.theme import apply_theme, render_sidebar, page_header, section_label

# =====================================================
# SETTINGS
# =====================================================
TARGET_SAMPLES = 20

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Voice Registration - VoiceAttendAI", page_icon="🎙", layout="wide")

apply_theme()
render_sidebar()

page_header("🎙", "Voice Registration", f"Record {TARGET_SAMPLES} voice samples per student for AI training")

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect("database/students.db")
cursor = conn.cursor()

cursor.execute("SELECT roll, name FROM students ORDER BY CAST(roll AS INTEGER) ASC")
students = cursor.fetchall()

if not students:
    st.warning("No students registered. Add students first from the Register page.")
    conn.close()
    st.stop()

# =====================================================
# STUDENT SELECTION
# =====================================================
st.markdown('<div class="vai-card">', unsafe_allow_html=True)
section_label("Select Student")

student = st.selectbox(
    "Student",
    students,
    format_func=lambda x: f"{x[0]} - {x[1]}",
    label_visibility="collapsed",
)

roll = student[0]
name = student[1]

folder = f"voice_samples/{roll}"
os.makedirs(folder, exist_ok=True)

files = sorted([f for f in os.listdir(folder) if f.endswith(".wav")])
sample_count = len(files)

st.write("")
st.progress(sample_count / TARGET_SAMPLES)
st.write(f"**{sample_count} / {TARGET_SAMPLES} samples collected** for {name}")
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# RECORD BUTTON
# =====================================================
st.markdown('<div class="vai-card">', unsafe_allow_html=True)

if sample_count < TARGET_SAMPLES:
    st.info(f"🎙 Next recording: Sample {sample_count + 1}")

    if st.button("🎤 Record Sample", type="primary"):
        duration = 2
        fs = 44100

        with st.spinner("🎤 Recording... say 'Present'"):
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()

        filename = os.path.join(folder, f"voice{sample_count + 1}.wav")
        write(filename, fs, recording)

        st.success(f"✅ Sample {sample_count + 1} saved successfully!")
        st.rerun()
else:
    st.success(f"🎉 All {TARGET_SAMPLES} samples completed for {name}!")

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SAMPLE GRID (compact progress view)
# =====================================================
section_label("Sample Progress")
st.markdown('<div class="vai-card">', unsafe_allow_html=True)

cols = st.columns(10)
for i in range(1, TARGET_SAMPLES + 1):
    with cols[(i - 1) % 10]:
        st.write("✅" if i <= sample_count else "⬜")

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# RECORDED SAMPLES (playback + delete)
# =====================================================
section_label("Recorded Samples")
st.markdown('<div class="vai-card">', unsafe_allow_html=True)

if files:
    for file in files:
        filepath = os.path.join(folder, file)
        fc1, fc2, fc3 = st.columns([2, 5, 1])
        with fc1:
            st.write(f"🎵 {file}")
        with fc2:
            with open(filepath, "rb") as audio:
                st.audio(audio.read())
        with fc3:
            if st.button("🗑", key=f"del_{file}"):
                os.remove(filepath)
                st.success("Sample deleted.")
                st.rerun()

    st.write("")
    confirm_all = st.checkbox(f"Yes, delete all {sample_count} samples for {name}")
    if st.button("🗑 Delete All Samples", disabled=not confirm_all):
        for file in files:
            os.remove(os.path.join(folder, file))
        st.success("All samples deleted.")
        st.rerun()
else:
    st.info("No voice samples recorded yet.")

st.markdown('</div>', unsafe_allow_html=True)

conn.close()
