import requests
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

def is_base64(s: str) -> bool:
    """判断字符串是否是有效的 Base64 编码"""
    try:
        # 尝试解码再重新编码
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False

def fetch_first_link():
    """抓取首页第一个 <a> 的 href"""
    url = "https://xraynode.github.io/"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    target = soup.select_one("div.col-md-9.xcblog-blog-list")
    if target:
        a = target.find("a", href=True)
        if a:
            return a["href"]
    return None


def fetch_v2ray_links(link: str):
    """进入子页面，提取 xcblog-v2ray-box 里的下载链接"""
    url = "https://xraynode.github.io" + link

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    target = soup.select_one(
        "body > section.w3l-ab-section.py-5 > div > div > div.col-md-9 > div > div.xcblog-v2ray-box"
    )

    links = []
    if target:
        for p in target.find_all("p"):
            text = p.get_text(strip=True)
            if text.startswith("http"):
                links.append(text)

    return links


def download_and_concat(urls):
    """下载并拼接所有解码后的字符串（去掉空白行）"""
    headers = {"User-Agent": "Mozilla/5.0"}
    all_lines = []

    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            content = resp.text.strip()

            if is_base64(content):
                decoded = base64.b64decode(content).decode(errors="ignore").strip()
                lines = decoded.splitlines()
            else:
                lines = content.splitlines()

            # 去掉空白行
            lines = [line for line in lines if line.strip()]
            all_lines.extend(lines)

        except Exception as e:
            print(f"下载失败: {url} 错误: {e}")

    # 拼接所有非空行
    combined = "\n".join(all_lines)

    # 在返回前做 Base64 编码
    encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")

    return encoded

if __name__ == "__main__":
    link = fetch_first_link()
    if link:
        urls = fetch_v2ray_links(link)
        if urls:
            combined = download_and_concat(urls)

            # 保存到文件 v2.txt
            with open("v2.txt", "w", encoding="utf-8") as f:
                f.write(combined)

        else:
            print("未找到下载地址")
    else:
        print("未找到首页链接")
