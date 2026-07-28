import sqlite3

conn = sqlite3.connect("database/students.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM attendance")

rows = cursor.fetchall()

print("Attendance Records:\n")

for row in rows:
    print(row)

conn.close()