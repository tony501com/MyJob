import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor

DB_FILE = "channels.db"
OUTPUT_FILE = "valid2.m3u"

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
            for _ in r.iter_content(chunk_size=1024):
                print(url)
                return True
    except Exception:
        return False
    return False

def load_channels(limit=50):
    """从数据库加载频道（默认取前50个）"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_name, url FROM channels ORDER BY id LIMIT ?", (limit,))
    rows = cursor.fetchall()
    # print(rows)
    conn.close()
    return rows

def group_first_channels(rows):
    """按 channel_name 分组，取第1个"""
    seen = {}
    for channel_name, url in rows:
        if channel_name not in seen:
            # print( channel_name, '  ', url)

            seen[channel_name] = url
    return seen

def save_m3u(valid_channels):
    """保存 M3U 文件"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in valid_channels.items():
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"✅ 已保存 {len(valid_channels)} 个有效频道到 {OUTPUT_FILE}")

def main():
    rows = load_channels(1100)
    grouped = group_first_channels(rows)

    valid_channels = {}

    def check_item(item):
        name, url = item
        if check_url(url):
            return name, url
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_item, grouped.items())

    for result in results:
        if result:
            name, url = result
            valid_channels[name] = url

    save_m3u(valid_channels)

if __name__ == "__main__":
    main()
