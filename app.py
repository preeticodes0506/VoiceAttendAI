import streamlit as st
from datetime import datetime

from utils.theme import apply_theme, render_sidebar, PRIMARY, TEXT_MUTED

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="VoiceAttendAI", page_icon="🎙", layout="wide")
apply_theme()
render_sidebar()

now = datetime.now()

# =====================================================
# TOP BAR
# =====================================================
st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
                padding-bottom:14px; margin-bottom:26px; border-bottom:1px solid #E7E5F5;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:26px;">🎙</span>
            <span style="font-size:20px; font-weight:800;">
                Voice<span style="color:{PRIMARY};">AttendAI</span>
            </span>
        </div>
        <div style="color:{TEXT_MUTED}; font-size:13px;">
            📅 {now.strftime('%A, %d %B %Y')} &nbsp;&nbsp; 🕒 {now.strftime('%I:%M %p')}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# HERO SECTION
# =====================================================
hero_left, hero_right = st.columns([1.1, 1])

with hero_left:
    st.markdown(
        f"""
        <div style="padding-top:10px;">
            <div style="font-size:30px; font-weight:800; line-height:1.25;">
                Welcome to<br>
                Voice<span style="color:{PRIMARY};">AttendAI</span>
            </div>
            <div style="font-size:16px; font-weight:600; color:{TEXT_MUTED}; margin-top:10px;">
                AI Powered Smart Attendance System
            </div>
            <div style="width:52px; height:4px; background:{PRIMARY}; border-radius:4px; margin:14px 0;"></div>
            <div style="font-size:14px; color:{TEXT_MUTED}; line-height:1.6;">
                Mark attendance using voice recognition technology.<br>
                Secure, accurate, and a smart solution for modern education.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🚀 Enter System", type="primary"):
        st.switch_page("pages/dashboard.py")

with hero_right:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:center; height:230px;">
            <div style="width:190px; height:190px; border-radius:50%;
                        background: radial-gradient(circle at 35% 30%, #A79CFB, {PRIMARY});
                        display:flex; align-items:center; justify-content:center;
                        box-shadow: 0 12px 30px rgba(109,93,246,0.35);">
                <span style="font-size:70px;">🎙️</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# =====================================================
# FEATURE CARDS
# =====================================================
f1, f2, f3, f4 = st.columns(4)

features = [
    ("🎙", "AI Voice Recognition", "Mark attendance using advanced voice recognition technology.", "#6D5DF6"),
    ("👥", "Student Management", "Add, update and manage student details easily and securely.", "#22C55E"),
    ("📊", "Smart Reports", "Generate detailed attendance reports and analyze performance.", "#F59E0B"),
    ("🛡", "Secure & Reliable", "Your data is safe with us. Reliable, secure and efficient system.", "#3B82F6"),
]

for col, (icon, title, desc, color) in zip([f1, f2, f3, f4], features):
    with col:
        st.markdown(
            f"""
            <div class="vai-card" style="min-height:180px;">
                <div style="font-size:22px;">{icon}</div>
                <div style="font-weight:700; color:{color}; margin-top:8px; font-size:15px;">{title}</div>
                <div style="font-size:12.5px; color:#6B7280; margin-top:6px; line-height:1.5;">{desc}</div>
                <div style="height:3px; background:{color}; border-radius:4px; margin-top:12px; opacity:0.85;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =====================================================
# TRUST STRIP
# =====================================================
t1, t2, t3, t4 = st.columns(4)
trust_items = [
    ("🛡", "100% Secure", "Your data is protected"),
    ("⚡", "Fast & Accurate", "Real-time attendance"),
    ("🎯", "AI Powered", "Smart voice technology"),
    ("☁️", "Easy to Use", "Simple and intuitive"),
]
for col, (icon, title, sub) in zip([t1, t2, t3, t4], trust_items):
    with col:
        st.markdown(
            f"""
            <div style="text-align:center; padding:10px 4px;">
                <div style="font-size:20px;">{icon}</div>
                <div style="font-weight:700; font-size:13px; margin-top:4px;">{title}</div>
                <div style="font-size:11.5px; color:#6B7280;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
st.markdown(
    f"""
    <div style="text-align:center; color:#6B7280; font-size:12.5px; padding-top:10px; border-top:1px solid #E7E5F5;">
        ❤️ VoiceAttendAI v1.0 — AI Powered Smart Attendance System
    </div>
    """,
    unsafe_allow_html=True,
)