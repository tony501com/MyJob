import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor

DB_FILE = "scripts/channels.db"
VALID_FILE = "scripts/valid.m3u"

# ----------------------
# 数据库相关
# ----------------------
def init_db():
    """保证 channels 表存在"""
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


def load_channels(limit=1000):
    """从数据库加载频道"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_name, url FROM channels ORDER BY id LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ----------------------
# 检测直播源
# ----------------------
def check_url(url, timeout=5):
    """检测直播源是否可用"""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    try:
        r = requests.get(url, stream=True, timeout=timeout)
        if r.status_code == 200:
            for _ in r.iter_content(chunk_size=512):
                return True
    except Exception:
        return False

    return False


# ----------------------
# 主流程
# ----------------------
def main():
    init_db()  # 确保表存在

    rows = load_channels(limit=1100)
    print(f"读取到 {len(rows)} 条记录")

    valid_entries = ["#EXTM3U"]

    def process_row(row):
        name, url = row
        if check_url(url):
            return f"#EXTINF:-1,{name}\n{url}"
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(process_row, rows)

    for r in results:
        if r:
            valid_entries.append(r)

    # 保存到 m3u 文件
    with open(VALID_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(valid_entries))

    print(f"[完成] 可用频道数: {len(valid_entries)-1}, 已保存到 {VALID_FILE}")


if __name__ == "__main__":
    main()
