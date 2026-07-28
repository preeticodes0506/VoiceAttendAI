import streamlit as st
import sqlite3
import pandas as pd

from utils.theme import apply_theme, render_sidebar, page_header, section_label

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Register - VoiceAttendAI", page_icon="📝", layout="wide")

apply_theme()
render_sidebar()

page_header("📝", "Student Registration", "Add a new student to the system")

# =====================================================
# REGISTRATION FORM
# =====================================================
st.markdown('<div class="vai-card">', unsafe_allow_html=True)
section_label("Student Details")

col1, col2 = st.columns(2)

with col1:
    student_name = st.text_input("Student Name")
    branch = st.selectbox("Branch", ["CSE", "Civil", "Mechanical", "EEE", "ET&T"])
    email = st.text_input("Email")

with col2:
    roll_number = st.text_input("Roll Number")
    sem_col, sec_col = st.columns(2)
    with sem_col:
        semester = st.selectbox("Semester", ["1", "2", "3", "4", "5", "6", "7", "8"])
    with sec_col:
        section = st.selectbox("Section", ["A", "B", "C"])
    mobile = st.text_input("Mobile Number")

st.write("")

if st.button("💾 Register Student", type="primary"):
    if not student_name or not roll_number:
        st.warning("Student Name and Roll Number are required.")
    else:
        conn = sqlite3.connect("database/students.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO students
            (name, roll, branch, semester, section, email, mobile)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (student_name, roll_number, branch, semester, section, email, mobile),
        )
        conn.commit()
        conn.close()
        st.success(f"✅ {student_name} registered successfully!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# REGISTERED STUDENTS
# =====================================================
section_label("Registered Students")

conn = sqlite3.connect("database/students.db")
df = pd.read_sql_query(
    """
    SELECT name AS Name, roll AS Roll, branch AS Branch, semester AS Semester,
           section AS Section, email AS Email, mobile AS Mobile
    FROM students
    ORDER BY CAST(roll AS INTEGER) ASC
    """,
    conn,
)
conn.close()

st.markdown('<div class="vai-card">', unsafe_allow_html=True)
if df.empty:
    st.info("No students registered yet.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)


