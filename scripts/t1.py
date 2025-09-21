import sqlite3

DB_FILE = "channels.db"

def read_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 读取前 50 条
    cursor.execute("SELECT id, source_file, channel_name, url FROM channels LIMIT 50")
    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        print(row)

if __name__ == "__main__":
    read_db()
