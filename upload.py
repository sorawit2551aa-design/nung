"""
upload.py - อัปโหลด pages.csv เข้า Supabase (ตาราง college_pages)
(ต้องรัน setup.sql ใน Supabase ก่อน 1 ครั้ง เพื่อให้ตารางมีคอลัมน์ images)

วิธีใช้ (หลังรัน scraper.py เสร็จ):
    py upload.py

ต้องมี SUPABASE_URL และ SUPABASE_SERVICE_KEY (secret key) ในไฟล์ .env
คีย์นี้ข้ามข้อจำกัด RLS ได้ ใช้บนเครื่องตัวเองเท่านั้น ห้ามใส่ในแอปที่ขึ้นออนไลน์
"""
import csv
import json
import os
import re

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
if not (url and key):
    raise SystemExit("ไม่พบ SUPABASE_URL หรือ SUPABASE_SERVICE_KEY ในไฟล์ .env")

IMAGE_URL = re.compile(r"https?://[^\s;|]+\.(?:jpe?g|png|webp)", re.I)


def read_images(row):
    """อ่านลิงก์รูปจากคอลัมน์ images ของ pages.csv
    ถ้าเป็น pages.csv รุ่นเก่าที่ยังไม่มีคอลัมน์นี้ จะดึงลิงก์รูปจากข้อความ "ลิงก์ในหน้านี้" แทน (ได้เฉพาะหน้ากิจกรรม)"""
    raw = (row.get("images") or "").strip()
    if raw:
        try:
            return [x for x in json.loads(raw) if isinstance(x, str)]
        except ValueError:
            pass
    images = []
    for link in IMAGE_URL.findall(row.get("content") or ""):
        link = link.replace("http://", "https://", 1)
        if link not in images:
            images.append(link)
    return images[:12]


csv.field_size_limit(10**8)
with open("pages.csv", encoding="utf-8-sig", newline="") as f:
    rows = [
        {"url": r["url"], "title": r["title"], "content": r["content"], "images": read_images(r)}
        for r in csv.DictReader(f)
    ]
if not rows:
    raise SystemExit("pages.csv ว่างเปล่า ยกเลิกการอัปโหลด")

supabase = create_client(url, key)

# เช็กก่อนว่าตารางมีคอลัมน์ images แล้ว (ถ้ายังไม่มี ให้หยุดก่อนที่จะลบข้อมูลเดิม)
try:
    supabase.table("college_pages").select("images").limit(1).execute()
except Exception as error:
    raise SystemExit(
        "ตาราง college_pages ยังไม่มีคอลัมน์ images -> ให้รัน setup.sql ใน Supabase SQL Editor ก่อน "
        f"แล้วค่อยรัน upload.py ใหม่ ({type(error).__name__})"
    )

# จำ id ล่าสุดของข้อมูลเก่าไว้ก่อน แล้วค่อยลบเมื่ออัปโหลดข้อมูลใหม่ครบแล้ว
# (ถ้าอัปโหลดล้มกลางทาง ข้อมูลเก่ายังอยู่ บอทไม่ว่างเปล่า)
latest = supabase.table("college_pages").select("id").order("id", desc=True).limit(1).execute().data
old_max_id = latest[0]["id"] if latest else None

BATCH = 50
for i in range(0, len(rows), BATCH):
    supabase.table("college_pages").insert(rows[i:i + BATCH]).execute()
    print(f"อัปโหลดแล้ว {min(i + BATCH, len(rows))}/{len(rows)}")

if old_max_id is not None:
    supabase.table("college_pages").delete().lte("id", old_max_id).execute()
    print("ลบข้อมูลเก่าเรียบร้อย")

with_images = sum(1 for r in rows if r["images"])
print(f"เสร็จแล้ว (มีรูปภาพ {with_images} หน้า)")
