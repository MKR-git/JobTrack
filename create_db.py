import sqlite3

conn = sqlite3.connect("jobs.db")

try:
    conn.execute("ALTER TABLE jobs ADD COLUMN salary TEXT")
    print("Salary column added successfully")
except sqlite3.OperationalError:
    print("Salary column already exists")

try:
    conn.execute("ALTER TABLE jobs ADD COLUMN user_id INTEGER")
    print("User ID column added successfully")
except sqlite3.OperationalError:
    print("User ID column already exists")

conn.commit()
conn.close()