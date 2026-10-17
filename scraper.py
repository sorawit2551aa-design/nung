"""
scraper.py - ดึงข้อความ และลิงก์รูปภาพ จากเว็บวิทยาลัย แล้วเก็บเป็นไฟล์ pages.csv
(คอลัมน์: url, title, content, images)

วิธีรัน (ใน Terminal ของ VS Code):
    py -m pip install requests beautifulsoup4
    py scraper.py

เสร็จแล้วจะได้ไฟล์ pages.csv ในโฟลเดอร์เดียวกัน
(ใช้เวลาประมาณ 10-15 นาที เพราะพักระหว่างหน้าเพื่อไม่ให้เว็บวิทยาลัยทำงานหนัก)
"""
import csv
import heapq
import json
import re
import time
from collections import Counter
from urllib import robotparser
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------- ตั้งค่า ----------
START_URL = "https://cicec.ac.th/web/index.php"
ALLOWED_HOSTS = {"cicec.ac.th", "www.cicec.ac.th"}
MAX_PAGES = 400        # เก็บเนื้อหาไม่เกินกี่หน้า
DELAY_SECONDS = 1.0    # พักระหว่างหน้า เพื่อไม่ให้เว็บวิทยาลัยทำงานหนัก
MAX_CHARS = 20000      # เก็บเนื้อหาหน้าละไม่เกินกี่ตัวอักษร (app.py จะแบ่งเป็นส่วนย่อยเอง)
OUTPUT_FILE = "pages.csv"
MAX_IMAGES_PER_PAGE = 12   # เก็บลิงก์รูปหน้าละไม่เกินกี่รูป (บอทจะแสดงตามจำนวนที่ตั้งใน app.py อีกที)

# เว็บ Google Sites ของวิทยาลัย (ตารางเรียน ข้อมูลบุคลากร แผนปฏิบัติการ ฯลฯ)
# ถ้าไม่ต้องการ ให้เปลี่ยนเป็น False
INCLUDE_GOOGLE_SITES = True
GOOGLE_SITES_PREFIXES = ("/cicec.ac.th/cicec/", "/view/cicecdata/")
HEADERS = {"User-Agent": "cicec-student-chatbot-project (student graduation project)"}

# หน้าที่ต้องการเก็บ
WANTED = re.compile(
    r"^/web/("
    r"viewdetail|gallerydetail|listnews|gallery|contactus|download|research"
    r"|academics|brt|pakm|ptn"
    r")\.php$|^/web/[a-d]\d\.php$"
)


def normalize(url):
    """ทำให้ลิงก์เป็นรูปแบบเดียวกัน ถ้าไม่ใช่เว็บวิทยาลัยหรือไม่ใช่หน้าที่ต้องการ จะคืนค่า None"""
    parts = urlparse(url)
    if parts.hostname == "sites.google.com":
        # เก็บเฉพาะ Google Sites ของวิทยาลัย และตัดส่วนท้ายลิงก์ เช่น ?authuser=1 ออก
        path = unquote(parts.path)  # แปลง %E0%B8... กลับเป็นตัวอักษร จะได้ไม่เก็บหน้าเดียวกันซ้ำ
        if INCLUDE_GOOGLE_SITES and path.startswith(GOOGLE_SITES_PREFIXES):
            return "https://sites.google.com" + path.rstrip("/")
        return None
    if parts.hostname not in ALLOWED_HOSTS:
        return None
    if not WANTED.match(parts.path):
        return None
    result = "https://cicec.ac.th" + parts.path
    if parts.query:
        result += "?" + parts.query
    return result


IMAGE_EXT = re.compile(r"\.(jpe?g|png|webp)$", re.I)   # ไม่เก็บ .gif เพราะมักเป็นไอคอน/แบนเนอร์ขยับ
# รูปที่เป็นส่วนตกแต่งของเว็บ (โลโก้ แบนเนอร์ ไอคอน) ไม่ต้องเก็บ
SKIP_IMAGE_WORDS = ("/banner/", "/link_banner/", "logo", "icon", "sprite", "loading", "spacer", "blank", "button")


def normalize_image(src, page_url):
    """ทำลิงก์รูปให้เป็น https แบบสมบูรณ์ ถ้าไม่ใช่รูปของเว็บวิทยาลัย หรือเป็นรูปตกแต่ง จะคืนค่า None"""
    if not src or src.strip().startswith("data:"):
        return None
    parts = urlparse(urljoin(page_url, src.strip()))
    if parts.hostname not in ALLOWED_HOSTS:
        return None
    path = unquote(parts.path)
    if not IMAGE_EXT.search(path):
        return None
    if any(word in path.lower() for word in SKIP_IMAGE_WORDS):
        return None
    # เข้ารหัสชื่อไฟล์ภาษาไทย/ช่องว่างให้เป็น %XX เพื่อให้เบราว์เซอร์โหลดได้แน่นอน
    return "https://cicec.ac.th" + quote(path, safe="/")


def page_number(url):
    """เลขหน้าจากลิงก์แบบ ...?page=5 (ถ้าไม่มีให้เป็น 1)"""
    try:
        return int(parse_qs(urlparse(url).query).get("page", ["1"])[0])
    except ValueError:
        return 1


def kind_of(url):
    """แยกประเภทหน้า เพื่อจัดลำดับว่าดึงอะไรก่อน"""
    parts = urlparse(url)
    if parts.hostname == "sites.google.com":
        return "sites"
    path = parts.path
    if path.endswith("/gallerydetail.php"):
        return "gallery_detail"
    if path.endswith("/gallery.php"):
        return "gallery_list"
    if path.endswith("/listnews.php"):
        return "news_list"
    return "main"


# เลขน้อยดึงก่อน: หลักสูตร/ประกาศ/ฝ่ายงาน -> รายการข่าว -> Google Sites -> รายละเอียดกิจกรรม -> รายการกิจกรรม
PRIORITY = {"main": 0, "news_list": 1, "sites": 2, "gallery_detail": 3, "gallery_list": 4}
# จำนวนหน้าสูงสุดที่ดึงของแต่ละประเภท (หน้ารายการกิจกรรมใช้เดินหาลิงก์เท่านั้น ไม่เก็บเนื้อหา)
LIMIT = {"main": 10**9, "news_list": 30, "sites": 80, "gallery_detail": 40, "gallery_list": 8}
SAVE_KINDS = {"main", "news_list", "sites", "gallery_detail"}


def fetch(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    if response.encoding is None or response.encoding.lower() in ("iso-8859-1", "latin-1"):
        response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def parse_page(html, page_url):
    """คืนค่า (ลิงก์ที่เจอทั้งหมด, หัวข้อ, บรรทัดข้อความ, ลิงก์ในเนื้อหา, ลิงก์รูปภาพ)"""
    soup = BeautifulSoup(html, "html.parser")

    # 1) เก็บลิงก์ทั้งหมดไว้ใช้เดินไปหน้าอื่น (ก่อนตัดเมนูออก)
    found = set()
    for a in soup.find_all("a", href=True):
        target = normalize(urljoin(page_url, a["href"]))
        if target:
            found.add(target)

    # 2) ตัดส่วนที่ไม่ใช่เนื้อหาออก
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "form"]):
        tag.decompose()

    # 3) หัวข้อ
    title = ""
    for name in ("h1", "h2", "h3"):
        tag = soup.find(name)
        if tag and tag.get_text(strip=True):
            title = re.sub(r"\s+", " ", tag.get_text(" ", strip=True))
            break

    # 4) ลิงก์ในเนื้อหา (เช่น ไฟล์หลักสูตร) เก็บเป็น "ข้อความ -> ลิงก์"
    links = []
    for a in soup.find_all("a", href=True):
        text = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        href = urljoin(page_url, a["href"])
        if IMAGE_EXT.search(urlparse(href).path):
            continue   # ลิงก์รูปไปเก็บในคอลัมน์ images แทน (ไม่ให้แย่งที่ลิงก์ข้อความ)
        if text and href.startswith("http"):
            links.append(f"{text} -> {href}")

    # 5) รูปภาพในเนื้อหา (ถ้ารูปเล็กครอบด้วยลิงก์ไปรูปใหญ่ จะเก็บรูปใหญ่แทน)
    images = []
    for tag in soup.find_all(["a", "img"]):
        if tag.name == "a":
            candidate = tag.get("href")
        else:
            parent = tag.find_parent("a")
            if parent and parent.get("href") and IMAGE_EXT.search(urlparse(parent["href"]).path):
                continue   # รูปเล็กที่ลิงก์ไปรูปใหญ่ ได้เก็บจากลิงก์ไปแล้ว
            candidate = tag.get("src") or tag.get("data-src") or tag.get("data-original")
        image = normalize_image(candidate, page_url)
        if image and image not in images:
            images.append(image)

    # 6) ข้อความ แยกเป็นบรรทัด
    lines = []
    for raw in soup.get_text("\n").split("\n"):
        line = re.sub(r"\s+", " ", raw).strip()
        if line:
            lines.append(line)

    return found, title, lines, links, images


robots_cache = {}


def allowed_by_robots(url):
    """เช็กไฟล์ robots.txt ของแต่ละเว็บ (กติกาว่าอนุญาตให้ดึงหน้าไหนบ้าง)"""
    host = urlparse(url).hostname
    if host not in robots_cache:
        parser = robotparser.RobotFileParser()
        parser.set_url(f"https://{host}/robots.txt")
        try:
            parser.read()
        except Exception:
            parser = None
        robots_cache[host] = parser
    parser = robots_cache[host]
    return parser is None or parser.can_fetch("*", url)


def main():
    start = normalize(START_URL) or START_URL
    heap = [(PRIORITY[kind_of(start)], page_number(start), 0, start)]
    seen = {start}
    counter = 1
    fetched = Counter()
    pages = []

    while heap and len(pages) < MAX_PAGES:
        _, _, _, url = heapq.heappop(heap)
        kind = kind_of(url)
        if fetched[kind] >= LIMIT[kind]:
            continue
        if not allowed_by_robots(url):
            print("ข้าม (robots.txt ไม่อนุญาต):", url)
            continue
        try:
            html = fetch(url)
        except Exception as error:
            print("ดึงไม่สำเร็จ:", url, "-", error)
            continue
        fetched[kind] += 1

        found, title, lines, links, images = parse_page(html, url)
        if kind in SAVE_KINDS:
            pages.append({"url": url, "title": title, "lines": lines, "links": links, "images": images})
            print(f"[{len(pages)}/{MAX_PAGES}] {title or '(ไม่มีหัวข้อ)'}  {url}")
        else:
            print(f"(เดินหาลิงก์) {url}")

        for target in sorted(found):
            if target not in seen:
                seen.add(target)
                heapq.heappush(
                    heap,
                    (PRIORITY[kind_of(target)], page_number(target), counter, target),
                )
                counter += 1
        time.sleep(DELAY_SECONDS)

    # ตัดข้อความที่ซ้ำกันเกือบทุกหน้า (เช่น ที่อยู่ท้ายเว็บ) ออก จะได้ไม่รก
    line_count = Counter()
    image_count = Counter()
    for page in pages:
        line_count.update(set(page["lines"]))
        line_count.update(set(page["links"]))
        image_count.update(set(page["images"]))
    limit = max(3, int(len(pages) * 0.4))

    rows = []
    for page in pages:
        lines = [x for x in page["lines"] if line_count[x] <= limit]
        links = [x for x in page["links"] if line_count[x] <= limit][:10]
        content = " | ".join(lines)
        if links:
            content += " | ลิงก์ในหน้านี้: " + " ; ".join(links)
        content = content[:MAX_CHARS]
        if len(content) < 30:
            continue
        title = page["title"] or (lines[0] if lines else page["url"])
        images = [x for x in page["images"] if image_count[x] <= limit][:MAX_IMAGES_PER_PAGE]
        rows.append({
            "url": page["url"],
            "title": title[:200],
            "content": content,
            "images": json.dumps(images, ensure_ascii=False),
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "title", "content", "images"])
        writer.writeheader()
        writer.writerows(rows)

    names = {
        "main": "เว็บหลักวิทยาลัย (หลักสูตร ประกาศ ฝ่ายงาน)",
        "news_list": "รายการข่าว",
        "sites": "Google Sites ของวิทยาลัย",
        "gallery_detail": "กิจกรรม",
    }
    summary = Counter(kind_of(r["url"]) for r in rows)
    print()
    for kind, label in names.items():
        print(f"  {label}: {summary[kind]} หน้า")
    with_images = [r for r in rows if r["images"] != "[]"]
    total_images = sum(len(json.loads(r["images"])) for r in rows)
    print(f"  มีรูปภาพ: {len(with_images)} หน้า (รวม {total_images} รูป)")
    print(f"เสร็จแล้ว: เก็บได้ {len(rows)} หน้า -> ไฟล์ {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
