-- รันใน Supabase > SQL Editor (รันซ้ำได้ ไม่เสียหาย)

create table if not exists college_faqs (
  question text primary key,
  answer text
);

create table if not exists college_pages (
  id bigint generated always as identity primary key,
  url text,
  title text,
  content text,
  images jsonb not null default '[]'::jsonb   -- ลิงก์รูปภาพของหน้านั้น ให้บอทส่งรูปให้ผู้ใช้
);

-- ถ้าเคยสร้างตารางไว้แล้วจากรุ่นก่อน (ยังไม่มีคอลัมน์ images) บรรทัดนี้จะเพิ่มให้
alter table college_pages add column if not exists images jsonb not null default '[]'::jsonb;

-- เปิด RLS แล้วอนุญาตให้ "อ่านได้อย่างเดียว" สำหรับ publishable key
alter table college_faqs enable row level security;
alter table college_pages enable row level security;

drop policy if exists "read faqs" on college_faqs;
drop policy if exists "read pages" on college_pages;
create policy "read faqs" on college_faqs for select to anon using (true);
create policy "read pages" on college_pages for select to anon using (true);

-- ให้ Supabase รู้จักคอลัมน์ใหม่ทันที
notify pgrst, 'reload schema';
