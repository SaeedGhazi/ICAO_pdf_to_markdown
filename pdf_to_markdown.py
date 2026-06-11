# ================================================
# 📄 pdf_to_markdown.py
#
# این برنامه برای استخراج متن و جدول‌ها از فایل‌های PDF و
# تبدیل آن‌ها به فرمت Markdown طراحی شده است.
# ویژگی‌ها:
#   - استخراج متن و جداول از PDF
#   - تولید Anchor یکتا برای بندها (شماره‌گذاری‌ها)
#   - ایجاد فهرست مطالب (TOC) در صورت وجود
#   - نمایش شماره صفحه اصلی PDF
#   - خروجی تمیز و آماده پردازش‌های بعدی (AI، سرچ، وب)
# ================================================

import fitz  # PyMuPDF
import pdfplumber
import re
import gc
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

"""
    محاسبه عمق شماره‌گذاری (مثلاً 5.4.2 → عمق 3)
"""
def count_number_depth(numbering):
    return len(numbering.split(".")) if numbering and "." in numbering else 1

"""
    بررسی می‌کند آیا خط با یک شماره‌گذاری (مثل 3.2.1) شروع شده یا نه
"""
def is_numbering(line):
    return bool(re.match(r"^\d+\.\d+(\.\d+)*\s", line.strip()))

"""
    پاکسازی سلول‌های جدول:
    - حذف None
    - جایگزینی \n با فاصله
    - فرار دادن | برای Markdown
"""
def clean_cell(cell):
    if cell is None:
        return ""
    return str(cell).replace("\n", " ").replace("|", "\\|").strip()

"""
    تبدیل جدول استخراج‌شده به Markdown استاندارد
"""
def table_to_markdown(table):
    if not table or not any(any(cell for cell in row) for row in table):
        return ""
    cleaned = [[clean_cell(cell) for cell in row] for row in table]
    headers = cleaned[0] if any(cleaned[0]) else [f"Col {i+1}" for i in range(len(cleaned[0]))]
    md = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["-" * len(h) for h in headers]) + " |"
    ]
    md.extend("| " + " | ".join(row) + " |" for row in cleaned[1:])
    return "\n".join(md)

"""
    استخراج فهرست مطالب (TOC) از PDF اگر موجود باشد
"""
def extract_toc(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return [(lvl, title, page) for lvl, title, page in doc.get_toc()]
    except Exception:
        return []

"""
    پردازش اصلی PDF:
    - باز کردن فایل PDF
    - استخراج متن و جداول
    - ایجاد TOC و Anchor
    - نوشتن خروجی به Markdown
"""
def process_pdf(pdf_path, output_dir, doc_id):
    start = datetime.now()
    success = True
    errors = []

    toc = extract_toc(pdf_path)
    processed_tables = set()
    output_file = output_dir / f"{pdf_path.stem}.md"

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {pdf_path.name}\n\n> **Note:** Page numbers refer to the PDF.\n\n")
            if toc:
                f.write("## Table of Contents\n")
                for level, title, page in toc:
                    f.write(f"{'  ' * (level - 1)}- {title} (Page {page})\n")
                f.write("\n")

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(tqdm(pdf.pages, desc=f"🔄 {pdf_path.name}"), 1):
                    try:
                        text = page.extract_text(layout=True) or ""
                        tables = page.extract_tables()
                        for table in tables:
                            h = hash(str(table))
                            if h not in processed_tables:
                                processed_tables.add(h)
                                md = table_to_markdown(table)
                                if md:
                                    f.write(md + f"\n[Page: {page_num}]\n\n")

                        lines = text.split("\n")
                        para = []
                        current_numbering = None
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if is_numbering(line):
                                if para:
                                    f.write(" ".join(para) + f"\n[Page: {page_num}]\n\n")
                                    para = []
                                current_numbering = line.split(" ")[0]
                                para.append(line)
                            else:
                                para.append(line)

                        if para:
                            paragraph = " ".join(para)
                            if current_numbering:
                                depth = count_number_depth(current_numbering)
                                anchor = f"{{#{doc_id}-{current_numbering}}}"
                                f.write(f"{'#' * min(depth, 6)} {current_numbering} {anchor}\n{paragraph}\n[Page: {page_num}]\n\n")
                            else:
                                f.write(f"{paragraph}\n[Page: {page_num}]\n\n")
                    except Exception as pe:
                        errors.append(f"Page {page_num}: {pe}")
                        continue

    except Exception as e:
        success = False
        errors.append(str(e))

    gc.collect()
    end = datetime.now()
    duration = (end - start).total_seconds()
    return success, errors, duration

"""
    تابع اصلی برنامه:
    - ساخت پوشه خروجی
    - پیدا کردن PDFها
    - اجرای پردازش برای هر PDF
    - نمایش خلاصه‌ی نتایج
"""
def main():
    current_dir = Path.cwd()
    output_dir = current_dir / "markdown_output"
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(current_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found.")
        return

    summary = []
    for i, pdf in enumerate(pdf_files, 1):
        print(f"\n📄 Processing {pdf.name} ({i}/{len(pdf_files)})...")
        doc_id = f"id{i}"
        success, errors, duration = process_pdf(pdf, output_dir, doc_id)
        summary.append((pdf.name, success, duration, errors))

    print("\n📋 Summary:")
    for name, success, duration, errors in summary:
        status = "✅ Success" if success else "❌ Failed"
        print(f"- {name}: {status} in {duration:.1f}s")
        if errors:
            for err in errors:
                print(f"   ⚠️  {err}")

if __name__ == "__main__":
    main()
