from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import requests

DB_FILE = "scripts/channels.db"

def load_channels(limit=100): 
    """从数据库加载频道"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_name, url FROM channels ORDER BY id LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def group_channels(rows):
    """按 channel_name 分组"""
    grouped = {}
    for channel_name, url in rows:
        grouped.setdefault(channel_name, []).append(url)
    return grouped

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

def check_group(name, urls):
    """检测某个频道的所有候选 URL，取第一个有效的"""
    for url in urls:
        if check_url(url):
            return name, url
    return None

def save_m3u(valid_channels, filename="valid.m3u"):
    """保存结果到 M3U 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in valid_channels.items():
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"[保存成功] {filename}, 可用频道数: {len(valid_channels)}")

def main():
    rows = load_channels(limit=100)
    grouped = group_channels(rows)

    valid_channels = {}

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_name = {
            executor.submit(check_group, name, urls): name
            for name, urls in grouped.items()
        }
        for future in as_completed(future_to_name):
            result = future.result()
            if result:
                name, url = result
                valid_channels[name] = url

    save_m3u(valid_channels)

if __name__ == "__main__":
    main()


