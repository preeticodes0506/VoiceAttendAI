import sqlite3

# Connect to database
conn = sqlite3.connect("database/students.db")

cursor = conn.cursor()

# ---------------------------------------
# STUDENTS TABLE
# ---------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    semester TEXT NOT NULL,
    section TEXT NOT NULL,
    email TEXT,
    mobile TEXT
)
""")

# ---------------------------------------
# ATTENDANCE TABLE
# ---------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully!")