"""Lookup for public class schedules linked from Chomthong College's website."""

import re


SOURCE_URL = "https://sites.google.com/view/cicecdata/บริการข้อมูลสารสนเทศ/ตารางเรียน-ตารางสอน"
CURRENT_TERM_CODE = "2/2569"
CURRENT_TERM_LABEL = "ภาคเรียนที่ 2/2569"

# The published drive folder currently exposes semester 1/2568 files. Keep the
# term visible in the UI so an old timetable is never presented as current.
TIMETABLES = (
    {
        "title": "ช่างไฟฟ้า ปวช. 1/1",
        "term": "ภาคเรียนที่ 1/2568",
        "term_code": "1/2568",
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
    """Return an exact class match for the requested term (current term by default)."""
    q = normalize(question)
    raw_question = str(question or "").translate(str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789"))
    term_match = re.search(r"([12])\s*[/\-]\s*(25\d{2})", raw_question)
    requested_term = f"{term_match.group(1)}/{term_match.group(2)}" if term_match else CURRENT_TERM_CODE
    matches = []
    for item in TIMETABLES:
        if item.get("term_code") != requested_term:
            continue
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

