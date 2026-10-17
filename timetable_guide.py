"""Lookup for public class schedules linked from Chomthong College's website."""

import re


SOURCE_URL = "https://sites.google.com/view/cicecdata/บริการข้อมูลสารสนเทศ/ตารางเรียน-ตารางสอน"

# The published drive folder currently exposes semester 1/2568 files. Keep the
# term visible in the UI so an old timetable is never presented as current.
TIMETABLES = (
    {
        "title": "ช่างไฟฟ้า ปวช. 1/1",
        "term": "ภาคเรียนที่ 1/2568",
        "file_name": "ชฟ1-1.pdf",
        "drive_id": "1oZ1PziHOKXm_ExdGPUBoK3tSqvcDs1y1",
        "aliases": (
            "ชฟ.1/1",
            "ชฟ1/1",
            "ชฟ1-1",
            "ชฟ1",
            "ช่างไฟฟ้า 1/1",
            "ช่างไฟฟ้า 1",
            "ไฟฟ้า 1/1",
            "ไฟฟ้า 1",
            "ไฟฟ้าปี 1",
        ),
    },
)


def normalize(value):
    """Normalize Thai schedule phrases while retaining letters and digits."""
    text = str(value or "").casefold().translate(str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789"))
    return re.sub(r"[^\wก-๙]+", "", text, flags=re.UNICODE)


def is_timetable_question(question):
    q = normalize(question)
    return any(term in q for term in ("ตารางเรียน", "ตารางสอน", "ตารางการใช้ห้องเรียน", "ตารางห้องเรียน", "classschedule", "timetable"))


def find_timetable(question):
    """Return only an exact class match; do not guess when the class is vague."""
    q = normalize(question)
    matches = []
    for item in TIMETABLES:
        for alias in item["aliases"]:
            key = normalize(alias)
            if key and key in q:
                matches.append((len(key), item))
    if not matches:
        return None
    return max(matches, key=lambda match: match[0])[1]


def preview_url(item):
    return f"https://drive.google.com/file/d/{item['drive_id']}/preview"


def source_file_url(item):
    return f"https://drive.google.com/file/d/{item['drive_id']}/view?usp=sharing"

