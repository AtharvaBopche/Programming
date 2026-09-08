import sqlite3
import sys
import json
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\athar\Downloads\c_recovery_questions.db"

if not os.path.exists(db_path):
    print(f"DB file not found at: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", tables)

for table in tables:
    table_name = table[0]
    print(f"\n--- Table: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print("Columns:", [col[1] for col in columns])

    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"Row count: {count}")

    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
    rows = cursor.fetchall()
    print("Sample rows:")
    for r in rows:
        print(" ", r)

conn.close()
