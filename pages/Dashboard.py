import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

from utils.theme import (
    apply_theme, render_sidebar, page_header, section_label, metric_card, quick_action_card,
    GREEN, GREEN_BG, RED, RED_BG, BLUE, BLUE_BG, PRIMARY, PURPLE_BG,
    ORANGE, ORANGE_BG, TEXT_MUTED,
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Dashboard - VoiceAttendAI", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()

now = datetime.now()
today = now.strftime("%d-%m-%Y")

page_header(
    "🏠",
    f"Welcome Admin! 👋",
    "Here's what's happening with your attendance system today.",
    right_html=(
        f'<div style="text-align:right; color:{TEXT_MUTED}; font-size:13px;">'
        f'📅 {now.strftime("%A, %d %B %Y")}<br>🕒 {now.strftime("%I:%M:%S %p")}</div>'
    ),
)

# =====================================================
# DATA
# =====================================================
conn = sqlite3.connect("database/students.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM students")
total_students = cursor.fetchone()[0] or 0

cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (today,))
present_today = cursor.fetchone()[0] or 0

cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Absent'", (today,))
absent_today = cursor.fetchone()[0] or 0

attendance_pct = (present_today / total_students * 100) if total_students else 0
absent_pct = (absent_today / total_students * 100) if total_students else 0

# =====================================================
# STAT CARDS
# =====================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("👥", "Total Students", str(total_students), "Registered Students", BLUE, BLUE_BG)
with c2:
    metric_card("✅", "Present Today", str(present_today), f"{attendance_pct:.0f}% of total", GREEN, GREEN_BG)
with c3:
    metric_card("❌", "Absent Today", str(absent_today), f"{absent_pct:.0f}% of total", RED, RED_BG)
with c4:
    metric_card("📊", "Attendance %", f"{attendance_pct:.0f}%", "Today's Attendance", PRIMARY, PURPLE_BG)

st.write("")

# =====================================================
# QUICK ACTIONS + DONUT
# =====================================================
qa_col, donut_col = st.columns([1.4, 1])

with qa_col:
    section_label("Quick Actions")
    st.markdown('<div class="vai-card">', unsafe_allow_html=True)

    qc1, qc2 = st.columns(2)
    with qc1:
        quick_action_card("👤", "Register Student", "Add New Student", BLUE, BLUE_BG)
        st.page_link("pages/register.py", label="Go to Register", icon="📝")

        quick_action_card("📋", "Student List", "View All Students", ORANGE, ORANGE_BG)
        st.page_link("pages/student.py", label="Go to Students", icon="👨‍🎓")

    with qc2:
        quick_action_card("🎙", "Start AI Attendance", "Begin Voice Attendance", GREEN, GREEN_BG)
        st.page_link("pages/attendance.py", label="Go to Attendance", icon="🎤")

        quick_action_card("📊", "Reports", "View Attendance Reports", PRIMARY, PURPLE_BG)
        st.page_link("pages/dashboard.py", label="Refresh Dashboard", icon="🔄")

    st.markdown('</div>', unsafe_allow_html=True)

with donut_col:
    section_label("Today's Attendance Overview")

    # simple CSS conic-gradient donut -- no charting library needed
    present_deg = int(attendance_pct / 100 * 360) if total_students else 0
    st.markdown(
        f"""
        <div class="vai-card" style="display:flex; align-items:center; gap:18px; height:100%;">
            <div style="width:110px; height:110px; border-radius:50%;
                        background: conic-gradient({GREEN} 0deg {present_deg}deg, {RED} {present_deg}deg 360deg);
                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <div style="width:74px; height:74px; border-radius:50%; background:#FFFFFF;
                            display:flex; flex-direction:column; align-items:center; justify-content:center;">
                    <div style="font-size:20px; font-weight:800;">{total_students}</div>
                    <div style="font-size:10px; color:{TEXT_MUTED};">Total</div>
                </div>
            </div>
            <div>
                <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
                    <div style="width:10px; height:10px; border-radius:50%; background:{GREEN};"></div>
                    <div style="font-size:13px;">Present: {present_today} ({attendance_pct:.0f}%)</div>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <div style="width:10px; height:10px; border-radius:50%; background:{RED};"></div>
                    <div style="font-size:13px;">Absent: {absent_today} ({absent_pct:.0f}%)</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# =====================================================
# TODAY'S ATTENDANCE / SYSTEM STATUS / RECENT ACTIVITY
# =====================================================
att_col, status_col, activity_col = st.columns([1.6, 1, 1.2])

with att_col:
    section_label("Today's Attendance")
    st.markdown('<div class="vai-card">', unsafe_allow_html=True)

    df_today = pd.read_sql_query(
        "SELECT roll AS '#', name AS Name, time AS Time, status AS Status "
        "FROM attendance WHERE date=? ORDER BY CAST(roll AS INTEGER) LIMIT 5",
        conn, params=(today,),
    )
    if df_today.empty:
        st.info("No attendance marked yet today.")
    else:
        st.dataframe(df_today, use_container_width=True, hide_index=True)

    st.page_link("pages/attendance.py", label="View Full Attendance →", icon="📅")
    st.markdown('</div>', unsafe_allow_html=True)

with status_col:
    section_label("System Status")
    st.markdown('<div class="vai-card">', unsafe_allow_html=True)

    model_ok = os.path.exists("models/voice_model.pkl") and os.path.exists("models/scaler.pkl")
    db_ok = os.path.exists("database/students.db")

    status_rows = [
        ("🎙", "Microphone", "Ready", GREEN),
        ("🧠", "AI Model", "Loaded" if model_ok else "Not Trained", GREEN if model_ok else RED),
        ("🗄", "Database", "Connected" if db_ok else "Missing", GREEN if db_ok else RED),
        ("🔊", "Voice Recognition", "Active" if model_ok else "Inactive", GREEN if model_ok else RED),
    ]
    for icon, label, status, color in status_rows:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0;">
                <div style="font-size:13px;">{icon} {label}</div>
                <div style="font-size:12px; font-weight:700; color:{color};">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

with activity_col:
    section_label("Recent Activity")
    st.markdown('<div class="vai-card">', unsafe_allow_html=True)

    df_recent = pd.read_sql_query(
        "SELECT name, status, time FROM attendance ORDER BY date DESC, time DESC LIMIT 5",
        conn,
    )
    if df_recent.empty:
        st.info("No activity yet.")
    else:
        for _, row in df_recent.iterrows():
            icon = "✅" if row["status"] == "Present" else "❌"
            st.markdown(
                f"""
                <div style="padding:6px 0; font-size:12.5px;">
                    {icon} <b>{row['name']}</b> marked {row['status'].lower()}
                    <div style="color:{TEXT_MUTED}; font-size:11px;">{row['time']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown(
    f"""
    <div style="text-align:center; color:{TEXT_MUTED}; font-size:12px; padding-top:8px; border-top:1px solid #E7E5F5;">
        ❤️ VoiceAttendAI v1.0 — AI Powered Smart Attendance System
    </div>
    """,
    unsafe_allow_html=True,
)

conn.close()
