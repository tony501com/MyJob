import os
import sqlite3

# 自动定位项目根目录（scripts 的上一级目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "sources")
DB_FILE = os.path.join(BASE_DIR, "channels.db")

def init_db():
    """初始化数据库（如果已存在则清空表）"""
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
    # 清空已有数据
    cursor.execute("DELETE FROM channels")
    conn.commit()
    conn.close()

def parse_m3u(file_path):
    """解析单个 M3U 文件"""
    channels = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # 提取频道名
            if "," in line:
                channel_name = line.split(",")[-1].strip()
            else:
                channel_name = "未知频道"

            # 下一行是 URL
            if i + 1 < len(lines) and lines[i + 1].startswith("http"):
                url = lines[i + 1].strip()
                channels.append((os.path.basename(file_path), channel_name, url))
    return channels

def save_to_db(channels):
    """保存解析结果到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO channels (source_file, channel_name, url) VALUES (?, ?, ?)", channels)
    conn.commit()
    conn.close()

def main():
    init_db()
    all_channels = []
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 未找到 sources 文件夹: {SOURCE_DIR}")
        return

    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith(".m3u"):
            path = os.path.join(SOURCE_DIR, filename)
            print(f"正在解析 {path} ...")
            channels = parse_m3u(path)
            all_channels.extend(channels)

    if all_channels:
        save_to_db(all_channels)
        print(f"✅ 已保存 {len(all_channels)} 条频道数据到 {DB_FILE}")
    else:
        print("⚠️ 没有解析到任何频道数据")

if __name__ == "__main__":
    main()
