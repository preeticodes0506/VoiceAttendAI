import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import librosa
import joblib
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import pyttsx3
import os
import time

from utils.theme import apply_theme, render_sidebar, page_header, section_label

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="VoiceAttendAI - Attendance", page_icon="🎤", layout="wide")
apply_theme()
render_sidebar()
page_header("🎤", "AI Voice Attendance", "Automated roll call with voice recognition")

# =====================================================
# CONSTANTS
# =====================================================
DB_PATH = "database/students.db"
MODEL_PATH = "models/voice_model.pkl"
SCALER_PATH = "models/scaler.pkl"
TEMP_DIR = "temp"
SAMPLE_RATE = 44100
FEATURE_SR = 22050
N_MFCC = 40                      # must match model/train_model.py
SILENCE_THRESHOLD = 0.01

os.makedirs(TEMP_DIR, exist_ok=True)

# =====================================================
# CACHED RESOURCES (load once, not on every rerun)
# =====================================================
@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler

try:
    model, scaler = load_model()
    MODEL_READY = True
except Exception as e:
    MODEL_READY = False
    st.error(f"⚠️ Could not load trained model/scaler. Train the model first. ({e})")

def speak(text):
    """
    IMPORTANT: pyttsx3 on Windows (SAPI5) only reliably runs once per
    engine instance in a single process. Reusing one cached engine
    across multiple speak() calls makes runAndWait() hang forever on
    the 2nd call onward (no error, it just freezes) -- which is why
    only the first roll number used to get called. Creating a fresh
    engine every call avoids that.
    """
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty("rate", 150)
        local_engine.setProperty("volume", 1.0)
        local_engine.say(text)
        local_engine.runAndWait()
        local_engine.stop()
        del local_engine
    except Exception as e:
        print(f"TTS error: {e}")

# =====================================================
# DB CONNECTION
# =====================================================
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# make sure a 'confidence' column exists (safe if it already does)
try:
    cursor.execute("ALTER TABLE attendance ADD COLUMN confidence REAL")
    conn.commit()
except sqlite3.OperationalError:
    pass

cursor.execute("SELECT roll, name FROM students ORDER BY CAST(roll AS INTEGER) ASC")
students = cursor.fetchall()

# =====================================================
# SESSION STATE
# =====================================================
defaults = {
    "current_index": 0,
    "running": False,
    "results": {},          # roll -> {"name":.., "status":.., "confidence":.., "predicted_as":..}
    "session_active": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================
# SIDEBAR SETTINGS
# =====================================================
st.sidebar.header("⚙️ Attendance Settings")

call_mode = st.sidebar.radio(
    "Call students by",
    ["Roll Number + Name", "Roll Number Only", "Name Only"],
    index=0
)

record_duration = st.sidebar.slider("Recording duration (sec)", 1, 5, 2)

confidence_threshold = st.sidebar.slider(
    "Minimum confidence to accept (%)", 0, 100, 40
)

margin_threshold = st.sidebar.slider(
    "Minimum margin over next-best guess (%)", 0, 30, 12,
    help="If the model's top guess isn't clearly ahead of its second guess "
         "(e.g. 46% vs 41%), it's too ambiguous to trust — this blocks that."
)

max_attempts = st.sidebar.slider(
    "Retry attempts if unclear", 1, 3, 2,
    help="If the voice is too low-confidence or ambiguous, give the student "
         "another chance to speak before marking them absent."
)

st.sidebar.caption(
    "If the recognized voice doesn't match the roll number called, "
    "it is marked as **Proxy Detected**. If confidence or margin is too low, "
    "or no voice is detected, it is marked **Absent**."
)

if not students:
    st.warning("No students registered yet. Add students first.")
    st.stop()

st.info(f"👥 Total Students : {len(students)}")

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def build_call_text(roll, name):
    if call_mode == "Roll Number Only":
        return f"Roll number {roll}"
    elif call_mode == "Name Only":
        return f"{name}"
    else:
        return f"Roll number {roll}, {name}"


def record_audio(duration=2, fs=SAMPLE_RATE):
    """Record from the microphone and save to a temp wav file."""
    filename = os.path.join(TEMP_DIR, "response.wav")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    write(filename, fs, recording)
    return filename


def extract_features_from_signal(signal, sr):
    """Must stay identical to model/train_model.py's version."""
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=N_MFCC)
    feature = np.concatenate([np.mean(mfcc, axis=1), np.std(mfcc, axis=1)])
    return feature


def extract_features(file_path):
    """Same feature pipeline used in model/train_model.py / model/predict.py."""
    signal, sr = librosa.load(file_path, sr=FEATURE_SR)

    rms = float(np.sqrt(np.mean(signal ** 2))) if len(signal) else 0.0

    if rms < SILENCE_THRESHOLD:
        return None, rms

    feature = extract_features_from_signal(signal, sr)
    feature = feature.reshape(1, -1)
    feature = scaler.transform(feature)
    return feature, rms


def predict_speaker(file_path):
    """
    Returns dict: {status, rms, predicted_roll, confidence, margin}
    status is one of: NO_VOICE, LOW_CONFIDENCE, AMBIGUOUS, PREDICTED

    Two separate checks now guard against bad matches:
    1. confidence_threshold -- is the top guess confident at all?
    2. margin_threshold -- is the top guess CLEARLY ahead of the next-best
       guess? This is what stops a "coin flip" between two similar-sounding
       students from accidentally being accepted as a confident match.
    """
    feature, rms = extract_features(file_path)

    if feature is None:
        return {"status": "NO_VOICE", "rms": rms, "predicted_roll": None,
                "confidence": 0.0, "margin": 0.0}

    probabilities = model.predict_proba(feature)[0]
    classes = model.classes_

    sorted_idx = np.argsort(probabilities)[::-1]
    top1_idx, top2_idx = sorted_idx[0], sorted_idx[1]

    top1_roll = classes[top1_idx]
    top1_conf = float(probabilities[top1_idx] * 100)
    top2_conf = float(probabilities[top2_idx] * 100)
    margin = top1_conf - top2_conf

    if top1_conf < confidence_threshold:
        return {"status": "LOW_CONFIDENCE", "rms": rms, "predicted_roll": top1_roll,
                "confidence": top1_conf, "margin": margin}

    if margin < margin_threshold:
        return {"status": "AMBIGUOUS", "rms": rms, "predicted_roll": top1_roll,
                "confidence": top1_conf, "margin": margin}

    return {"status": "PREDICTED", "rms": rms, "predicted_roll": top1_roll,
            "confidence": top1_conf, "margin": margin}


def already_marked(roll, today):
    cursor.execute("SELECT 1 FROM attendance WHERE roll=? AND date=?", (roll, today))
    return cursor.fetchone() is not None


def mark_attendance(roll, name, status, confidence):
    today = datetime.now().strftime("%d-%m-%Y")
    now = datetime.now().strftime("%H:%M:%S")

    if already_marked(roll, today):
        return

    cursor.execute(
        "INSERT INTO attendance(roll, name, date, time, status, confidence) VALUES(?,?,?,?,?,?)",
        (roll, name, today, now, status, confidence),
    )
    conn.commit()


def roll_name_map():
    return {r: n for r, n in students}


# =====================================================
# CONTROLS
# =====================================================
st.subheader("🎙 Roll Call")

col1, col2, col3 = st.columns(3)

with col1:
    start_disabled = not MODEL_READY
    if st.button("▶️ Start / Resume", disabled=start_disabled, use_container_width=True):
        st.session_state.running = True
        st.session_state.session_active = True

with col2:
    if st.button("⏸ Stop", use_container_width=True):
        st.session_state.running = False

with col3:
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.current_index = 0
        st.session_state.running = False
        st.session_state.results = {}
        st.session_state.session_active = False
        st.success("Roll call position reset. Note: this does NOT delete already-marked attendance in the database — students already marked today will be skipped. Use 'Clear & Retest' below to actually wipe today's records.")

with st.expander("🧹 Testing with different voices? Clear today's attendance & retest"):
    st.warning(
        "This permanently deletes ALL attendance (both voice-marked and manual) "
        "recorded **today**, so every student becomes callable again."
    )
    confirm_retest = st.checkbox("Yes, delete today's attendance and let me retest", key="confirm_retest")
    if st.button("🗑 Clear Today's Attendance & Reset", disabled=not confirm_retest):
        cursor.execute("DELETE FROM attendance WHERE date=?", (datetime.now().strftime("%d-%m-%Y"),))
        conn.commit()
        st.session_state.current_index = 0
        st.session_state.running = False
        st.session_state.results = {}
        st.session_state.manual_skip = set()
        st.success("Today's attendance cleared. Click ▶️ Start / Resume to retest from scratch.")
        st.rerun()

remaining = len(students) - st.session_state.current_index
progress_val = st.session_state.current_index / max(1, len(students))
st.progress(min(progress_val, 1.0))
st.write(f"Remaining Students : {remaining} / {len(students)}")

# ---- live stats ----
present_count = sum(1 for r in st.session_state.results.values() if r["status"] == "Present")
absent_count = sum(1 for r in st.session_state.results.values() if r["status"] != "Present")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total", len(students))
m2.metric("✅ Present", present_count)
m3.metric("❌ Absent / Proxy", absent_count)
m4.metric("⏳ Remaining", remaining)

placeholder = st.empty()

# =====================================================
# MAIN ATTENDANCE LOOP (one step per rerun)
# =====================================================
today = datetime.now().strftime("%d-%m-%Y")

if st.session_state.running and MODEL_READY:

    if st.session_state.current_index < len(students):

        roll, name = students[st.session_state.current_index]

        with placeholder.container():
            st.info(f"🎤 Calling : {roll} - {name}")

            if already_marked(roll, today):
                st.warning(f"{name} ({roll}) already marked today. Skipping.")
                st.session_state.current_index += 1
                time.sleep(0.5)
                st.rerun()

            # 1) Announce
            speak(build_call_text(roll, name))

            # 2) Record + Predict, with retries if the model is unsure
            #    (same voice can score differently attempt to attempt --
            #    give it another try before deciding, instead of failing
            #    on a single noisy reading)
            result = None
            for attempt in range(1, max_attempts + 1):
                if attempt > 1:
                    st.warning(f"🔁 Not sure yet — try again (attempt {attempt}/{max_attempts})...")
                    speak("Please say present again.")

                st.warning(f"🎙 Listening for {record_duration} sec...")
                audio_path = record_audio(duration=record_duration)
                result = predict_speaker(audio_path)

                if result["status"] not in ("LOW_CONFIDENCE", "AMBIGUOUS"):
                    break   # either a clean match, a clean mismatch, or no voice -- stop retrying

            # 4) Decide status
            if result["status"] == "NO_VOICE":
                status = "Absent"
                note = "No voice detected"
                confidence = 0.0
                speak(f"No response from {name}. Marked absent.")

            elif result["status"] == "LOW_CONFIDENCE":
                status = "Absent"
                note = f"Low confidence ({result['confidence']:.1f}%)"
                confidence = result["confidence"]
                speak(f"Voice not recognized clearly for {name}. Marked absent.")

            elif result["status"] == "AMBIGUOUS":
                status = "Absent"
                note = (f"Too close to call ({result['confidence']:.1f}% vs next-best, "
                         f"margin {result['margin']:.1f}%)")
                confidence = result["confidence"]
                speak(f"Voice unclear for {name}. Marked absent.")

            elif result["predicted_roll"] == roll:
                status = "Present"
                note = f"Matched voice ({result['confidence']:.1f}%)"
                confidence = result["confidence"]
                speak(f"{name}, marked present.")

            else:
                # voice matched someone else's profile -> proxy attempt
                rn_map = roll_name_map()
                impostor_name = rn_map.get(result["predicted_roll"], result["predicted_roll"])
                status = "Absent"
                note = f"Proxy Detected (sounded like {impostor_name}, {result['confidence']:.1f}%)"
                confidence = result["confidence"]
                speak(f"Proxy detected for {name}. Marked absent.")

            mark_attendance(roll, name, status, confidence)

            st.session_state.results[roll] = {
                "name": name,
                "status": status,
                "confidence": round(confidence, 2),
                "note": note,
            }

            if status == "Present":
                st.success(f"✅ {roll} - {name} : {note}")
            else:
                st.error(f"❌ {roll} - {name} : {note}")

        st.session_state.current_index += 1
        time.sleep(1)
        st.rerun()

    else:
        st.success("✅ Attendance Roll Call Completed")
        speak("Attendance roll call completed.")
        st.session_state.running = False

# =====================================================
# SESSION SUMMARY (after roll call finishes)
# =====================================================
if st.session_state.results and not st.session_state.running:
    st.markdown("---")
    st.subheader("📋 Roll Call Summary (this session)")

    summary_rows = [
        {"Roll": roll, "Name": r["name"], "Status": r["status"],
         "Confidence %": r["confidence"], "Note": r["note"]}
        for roll, r in st.session_state.results.items()
    ]
    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.metric("✅ Present", present_count)
    c2.metric("❌ Absent / Proxy", absent_count)

# =====================================================
# MANUAL OVERRIDE (auto-advancing queue)
# =====================================================
st.markdown("---")
st.subheader("✍️ Manual Attendance")

if "manual_skip" not in st.session_state:
    st.session_state.manual_skip = set()

# students not yet marked today, in ascending roll order, minus any skipped
unmarked_queue = [
    s for s in students
    if not already_marked(s[0], today) and s[0] not in st.session_state.manual_skip
]

if not unmarked_queue:
    st.success("🎉 Everyone has been marked for today!")
else:
    next_roll, next_name = unmarked_queue[0]
    st.info(f"**Next up : {next_roll} - {next_name}**  "
            f"({len(unmarked_queue)} student(s) left to mark)")

    mc1, mc2, mc3 = st.columns(3)

    with mc1:
        if st.button("✅ Present", key="q_present", use_container_width=True):
            mark_attendance(next_roll, next_name, "Present", None)
            st.rerun()

    with mc2:
        if st.button("❌ Absent", key="q_absent", use_container_width=True):
            mark_attendance(next_roll, next_name, "Absent", None)
            st.rerun()

    with mc3:
        if st.button("⏭ Skip for now", key="q_skip", use_container_width=True):
            st.session_state.manual_skip.add(next_roll)
            st.rerun()

# skipped students can be brought back or marked directly
if st.session_state.manual_skip:
    skipped_students = [s for s in students if s[0] in st.session_state.manual_skip]
    with st.expander(f"⏭ Skipped students ({len(skipped_students)})"):
        for roll, name in skipped_students:
            sc1, sc2, sc3 = st.columns([2, 1, 1])
            sc1.write(f"{roll} - {name}")
            if sc2.button("✅ Present", key=f"skip_present_{roll}"):
                mark_attendance(roll, name, "Present", None)
                st.session_state.manual_skip.discard(roll)
                st.rerun()
            if sc3.button("↩ Bring back", key=f"skip_back_{roll}"):
                st.session_state.manual_skip.discard(roll)
                st.rerun()

# fallback: jump straight to any specific student if needed
with st.expander("🔎 Jump to a specific student instead"):
    jump_student = st.selectbox(
        "Select student",
        students,
        format_func=lambda x: f"{x[0]} - {x[1]}",
        key="jump_select",
    )
    jc1, jc2 = st.columns(2)
    with jc1:
        if st.button("✅ Mark Present", key="jump_present"):
            if already_marked(jump_student[0], today):
                st.warning("Already marked today.")
            else:
                mark_attendance(jump_student[0], jump_student[1], "Present", None)
                st.session_state.manual_skip.discard(jump_student[0])
                st.rerun()
    with jc2:
        if st.button("❌ Mark Absent", key="jump_absent"):
            if already_marked(jump_student[0], today):
                st.warning("Already marked today.")
            else:
                mark_attendance(jump_student[0], jump_student[1], "Absent", None)
                st.session_state.manual_skip.discard(jump_student[0])
                st.rerun()

# =====================================================
# TODAY'S ATTENDANCE (from DB)
# =====================================================
st.markdown("---")
st.subheader("📅 Today's Attendance")

df = pd.read_sql_query(
    "SELECT roll, name, date, time, status, confidence FROM attendance WHERE date=? ORDER BY CAST(roll AS INTEGER)",
    conn,
    params=(today,),
)

if df.empty:
    st.info("No attendance marked today yet.")
else:
    total_present = (df["status"] == "Present").sum()
    total_students = len(students)
    pct = (total_present / total_students * 100) if total_students else 0

    d1, d2, d3 = st.columns(3)
    d1.metric("Total Students", total_students)
    d2.metric("Present Today", int(total_present))
    d3.metric("Attendance %", f"{pct:.1f}%")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Today's Attendance (CSV)",
        data=csv,
        file_name=f"attendance_{today}.csv",
        mime="text/csv",
    )

# =====================================================
# DELETE / RESET ATTENDANCE (works for voice AND manual records)
# =====================================================
st.markdown("---")
st.subheader("🗑 Delete / Reset Attendance")
st.caption(
    "This deletes from the same attendance table used by both AI voice "
    "roll call and manual marking — it doesn't matter how a record was created."
)

del_tab1, del_tab2, del_tab3 = st.tabs(
    ["Delete one record", "Delete all for today", "Delete by student (any date)"]
)

# ---- Delete one record (from today's table) ----
with del_tab1:
    if df.empty:
        st.info("No records today to delete.")
    else:
        row_options = {
            f"{r.roll} - {r.name} ({r.status}, {r.time})": r.roll
            for r in df.itertuples()
        }
        chosen_label = st.selectbox("Select a record to delete", list(row_options.keys()))
        chosen_roll = row_options[chosen_label]

        if st.button("🗑 Delete this record", type="primary"):
            cursor.execute(
                "DELETE FROM attendance WHERE roll=? AND date=?",
                (chosen_roll, today),
            )
            conn.commit()
            st.success(f"Deleted today's record for roll {chosen_roll}.")
            st.rerun()

# ---- Delete all of today's attendance ----
with del_tab2:
    st.warning("This clears every attendance record marked today. Cannot be undone.")
    confirm = st.checkbox("Yes, I understand — clear all of today's attendance")
    if st.button("🗑 Delete ALL today's attendance", disabled=not confirm):
        cursor.execute("DELETE FROM attendance WHERE date=?", (today,))
        conn.commit()
        st.success("All of today's attendance has been cleared.")
        st.session_state.results = {}
        st.rerun()

# ---- Delete a specific student's record on any date ----
with del_tab3:
    del_student = st.selectbox(
        "Student",
        students,
        format_func=lambda x: f"{x[0]} - {x[1]}",
        key="del_student_select",
    )

    cursor.execute(
        "SELECT DISTINCT date FROM attendance WHERE roll=? ORDER BY date",
        (del_student[0],),
    )
    dates = [d[0] for d in cursor.fetchall()]

    if not dates:
        st.info(f"No attendance history found for {del_student[1]}.")
    else:
        del_date = st.selectbox("Date", dates)
        if st.button("🗑 Delete this student's record for selected date"):
            cursor.execute(
                "DELETE FROM attendance WHERE roll=? AND date=?",
                (del_student[0], del_date),
            )
            conn.commit()
            st.success(f"Deleted {del_student[1]}'s record for {del_date}.")
            st.rerun()

conn.close()
