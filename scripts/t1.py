import sqlite3
import os

DB_FILE = "scripts/channels.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            channel_name TEXT,
            url TEXT
        )
    """)
    conn.commit()
    conn.close()

def read_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, source_file, channel_name, url FROM channels LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("⚠️ 数据库是空的")
    else:
        for row in rows:
            print(row)

if __name__ == "__main__":
    init_db()
    read_db()
