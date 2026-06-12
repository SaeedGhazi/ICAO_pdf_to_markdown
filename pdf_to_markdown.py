# ================================================
# 📄 pdf_to_markdown.py
#
# این برنامه برای استخراج متن و جدول‌ها از فایل‌های PDF و
# تبدیل آن‌ها به فرمت Markdown طراحی شده است.
# ویژگی‌ها:
#   - استخراج متن و جداول از PDF (با پشتیبانی از صفحات چندستونه)
#   - تشخیص و حذف هدر/فوتر تکراری
#   - تولید Anchor یکتا برای بندها (شماره‌گذاری‌های فارسی و انگلیسی)
#   - ایجاد فهرست مطالب (TOC) در صورت وجود
#   - نمایش شماره صفحه اصلی PDF
#   - خروجی تمیز و آماده پردازش‌های بعدی (AI، سرچ، وب)
# ================================================

import argparse
import re
import gc
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from tqdm import tqdm
from datetime import datetime

import md_combiner

# ---------------------------------------------------------------------------
# شماره‌گذاری بندها و Anchorها
# ---------------------------------------------------------------------------

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
DIGIT_TRANSLATION = str.maketrans(
    PERSIAN_DIGITS + ARABIC_INDIC_DIGITS, "0123456789" * 2
)

# پشتیبانی از ارقام انگلیسی، فارسی و عربی، و از جداکننده‌های "." و "٫"
# (مثال: 5.4.2 یا ۴٫۳٫۲٫۱). حداقل دو سطح برای جلوگیری از تشخیص اشتباه
# جملاتی که با یک عدد و نقطه شروع می‌شوند.
NUMBERING_RE = re.compile(
    r"^([0-9۰-۹٠-٩]+(?:[.٫][0-9۰-۹٠-٩]+)+)"
    r"\.?(?=$|\s+(?![a-z]))"
)


def numbering_match(line):
    """اگر خط با یک شماره‌گذاری بندی شروع شود، آن را برمی‌گرداند، در غیر این صورت None."""
    m = NUMBERING_RE.match(line.strip())
    return m.group(1) if m else None


def normalize_numbering(numbering):
    """شماره‌گذاری را برای استفاده در Anchor به ارقام/جداکننده‌های ASCII یکدست می‌کند."""
    numbering = numbering.rstrip(".٫")
    return numbering.translate(DIGIT_TRANSLATION).replace("٫", ".")


def count_number_depth(numbering):
    """محاسبه عمق شماره‌گذاری (مثلاً 5.4.2 → عمق 3)."""
    parts = [p for p in re.split(r"[.٫]", numbering) if p]
    return len(parts) if parts else 1


# ---------------------------------------------------------------------------
# جداول
# ---------------------------------------------------------------------------

def clean_cell(cell):
    """پاکسازی سلول‌های جدول: حذف None، تبدیل خط جدید به <br> و فرار دادن |."""
    if cell is None:
        return ""
    return str(cell).replace("\n", "<br>").replace("|", "\\|").strip()


def table_to_markdown(table):
    """تبدیل جدول استخراج‌شده به Markdown استاندارد."""
    if not table or not any(any(cell for cell in row) for row in table):
        return ""
    cleaned = [[clean_cell(cell) for cell in row] for row in table]
    headers = cleaned[0] if any(cleaned[0]) else [f"Col {i+1}" for i in range(len(cleaned[0]))]
    separators = ["-" * max(3, len(h)) for h in headers]
    md = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separators) + " |",
    ]
    md.extend("| " + " | ".join(row) + " |" for row in cleaned[1:])
    return "\n".join(md)


# ---------------------------------------------------------------------------
# فهرست مطالب (TOC)
# ---------------------------------------------------------------------------

def extract_toc(pdf_path):
    """استخراج فهرست مطالب (TOC) از PDF اگر موجود باشد."""
    try:
        with fitz.open(pdf_path) as doc:
            return [(lvl, title, page) for lvl, title, page in doc.get_toc()]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# تحلیل چیدمان صفحه: تشخیص ستون‌بندی و ترتیب صحیح خواندن
# ---------------------------------------------------------------------------

Y_TOLERANCE = 2.0            # تلورانس عمودی (pt) برای گروه‌بندی کلمات در یک خط
MIN_GUTTER_WIDTH = 10.0      # حداقل عرض شکاف افقی (pt) برای در نظر گرفتن آن به‌عنوان شکاف بین ستون‌ها
GUTTER_SEARCH_MARGIN = 0.2   # مرکز شکاف باید در بازه [margin, 1-margin] عرض صفحه باشد
GUTTER_CONSISTENCY = 30.0    # تلورانس (pt) برای همگرایی محل شکاف‌های نامزد
MIN_GUTTER_CANDIDATES = 4    # حداقل تعداد نامزدهای همگرا برای تأیید دو ستونه بودن صفحه

HEADER_ZONE = 0.08           # نسبتی از ارتفاع صفحه که هدر تکراری در آن قرار دارد
FOOTER_ZONE = 0.08           # نسبتی از ارتفاع صفحه که فوتر تکراری در آن قرار دارد
BOILERPLATE_MIN_COUNT = 3    # حداقل تکرار یک خط در سند برای حذف به‌عنوان هدر/فوتر

CID_RE = re.compile(r"\(cid:\d+\)")           # گلیف‌های نگاشت‌نشده برخی فونت‌ها
HAS_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def _looks_like_stamp(text):
    """تشخیص خطوطی که فقط شامل عدد/تاریخ/علامت هستند (مثل مهر شماره صفحه/ویرایش)."""
    return not HAS_LETTER_RE.search(text)


def cluster_words_by_line(words):
    """گروه‌بندی کلمات یک صفحه به خطوط بصری بر اساس موقعیت عمودی."""
    cleaned = []
    for w in words:
        text = CID_RE.sub("", w["text"])
        if text:
            cleaned.append({**w, "text": text} if text != w["text"] else w)
    words = cleaned
    if not words:
        return []
    words = sorted(words, key=lambda w: (w["top"], w["x0"]))
    clusters = [[words[0]]]
    current_top = words[0]["top"]
    for w in words[1:]:
        if abs(w["top"] - current_top) <= Y_TOLERANCE:
            clusters[-1].append(w)
        else:
            clusters.append([w])
            current_top = w["top"]

    lines = []
    for ws in clusters:
        ws = sorted(ws, key=lambda w: w["x0"])
        lines.append({
            "type": "text",
            "words": ws,
            "x0": min(w["x0"] for w in ws),
            "x1": max(w["x1"] for w in ws),
            "top": min(w["top"] for w in ws),
            "bottom": max(w["bottom"] for w in ws),
        })
    return lines


def find_column_gutter(lines, page_width):
    """
    تشخیص شکاف عمودی بین دو ستون.
    در چیدمان دوستونه، خطوطی که از دو ستون در یک ارتفاع قرار دارند به یک
    "خط" تجمیع می‌شوند (چون ارتفاع آن‌ها به هم نزدیک است) و یک شکاف بزرگ
    افقی بین آن دو بخش دارند. اگر چنین شکافی به‌طور پیوسته در چند خط دیده شود،
    صفحه دوستونه در نظر گرفته می‌شود.
    """
    candidates = []
    for line in lines:
        ws = line["words"]
        if len(ws) < 2:
            continue
        best = None
        for i in range(len(ws) - 1):
            g0, g1 = ws[i]["x1"], ws[i + 1]["x0"]
            if g1 - g0 >= MIN_GUTTER_WIDTH and (best is None or (g1 - g0) > (best[1] - best[0])):
                best = (g0, g1)
        if best:
            center = (best[0] + best[1]) / 2
            if GUTTER_SEARCH_MARGIN * page_width <= center <= (1 - GUTTER_SEARCH_MARGIN) * page_width:
                candidates.append(best)

    if len(candidates) < MIN_GUTTER_CANDIDATES:
        return None

    centers = sorted((g0 + g1) / 2 for g0, g1 in candidates)
    median_center = centers[len(centers) // 2]
    close = [c for c in candidates if abs((c[0] + c[1]) / 2 - median_center) < GUTTER_CONSISTENCY]
    if len(close) < MIN_GUTTER_CANDIDATES:
        return None

    g0 = sorted(c[0] for c in close)[len(close) // 2]
    g1 = sorted(c[1] for c in close)[len(close) // 2]
    return (g0, g1)


def _make_text_item(words):
    return {
        "type": "text",
        "words": words,
        "x0": min(w["x0"] for w in words),
        "x1": max(w["x1"] for w in words),
        "top": min(w["top"] for w in words),
        "bottom": max(w["bottom"] for w in words),
    }


def split_for_columns(item, gutter):
    """دسته‌بندی یک خط/جدول به ستون چپ، راست یا تمام‌عرض نسبت به شکاف صفحه."""
    if gutter is None:
        return [("full", item)]
    g0, g1 = gutter
    gutter_mid = (g0 + g1) / 2
    if item["x1"] <= gutter_mid:
        return [("left", item)]
    if item["x0"] >= gutter_mid:
        return [("right", item)]
    if item["type"] == "text":
        ws = item["words"]
        for i in range(len(ws) - 1):
            a0, a1 = ws[i]["x1"], ws[i + 1]["x0"]
            if a1 - a0 >= MIN_GUTTER_WIDTH and a0 <= gutter_mid <= a1:
                return [("left", _make_text_item(ws[: i + 1])), ("right", _make_text_item(ws[i + 1:]))]
    return [("full", item)]


def order_reading_flow(items, gutter):
    """
    ترتیب صحیح خواندن: آیتم‌های تمام‌عرض (تیتر، هدر، جدول سراسری) سر جای
    خود باقی می‌مانند؛ بین دو آیتم تمام‌عرض، ابتدا کل ستون چپ از بالا به
    پایین و سپس کل ستون راست خوانده می‌شود.
    """
    out = []
    block_left, block_right = [], []

    def flush_blocks():
        if block_left:
            out.extend(block_left)
        if block_right:
            if block_left:
                out.append({"type": "break"})
            out.extend(block_right)
        block_left.clear()
        block_right.clear()

    for item in items:
        for kind, sub in split_for_columns(item, gutter):
            if kind == "full":
                flush_blocks()
                if out and out[-1]["type"] != "break":
                    out.append({"type": "break"})
                out.append(sub)
                out.append({"type": "break"})
            elif kind == "left":
                block_left.append(sub)
            else:
                block_right.append(sub)
    flush_blocks()
    return out


# ---------------------------------------------------------------------------
# تشخیص هدر/فوتر تکراری (boilerplate)
# ---------------------------------------------------------------------------

def normalize_for_boilerplate(text):
    """نرمال‌سازی متن برای تشخیص الگوهای تکراری (اعداد را با # جایگزین می‌کند)."""
    norm = re.sub(r"[0-9۰-۹٠-٩]+", "#", text)
    return re.sub(r"\s+", " ", norm).strip()


def detect_boilerplate(pdf):
    """
    خطوطی که در نوار بالا/پایین صفحات (مثل عنوان فصل، نام سند یا شماره
    صفحه) به‌طور تکراری در سند ظاهر می‌شوند را شناسایی می‌کند تا از خروجی
    حذف شوند.
    """
    counter = Counter()
    for page in pdf.pages:
        h = page.height
        for line in cluster_words_by_line(page.extract_words()):
            if line["top"] <= h * HEADER_ZONE or line["bottom"] >= h * (1 - FOOTER_ZONE):
                text = " ".join(w["text"] for w in line["words"])
                norm = normalize_for_boilerplate(text)
                if norm:
                    counter[norm] += 1
    return {norm for norm, c in counter.items() if c >= BOILERPLATE_MIN_COUNT}


# ---------------------------------------------------------------------------
# پردازش هر صفحه
# ---------------------------------------------------------------------------

def _word_in_any_bbox(word, bboxes):
    cx = (word["x0"] + word["x1"]) / 2
    cy = (word["top"] + word["bottom"]) / 2
    for x0, top, x1, bottom in bboxes:
        if x0 <= cx <= x1 and top <= cy <= bottom:
            return True
    return False


def extract_page_items(page, boilerplate, processed_table_hashes):
    """
    استخراج محتوای یک صفحه (متن + جداول) و چیدن آن‌ها به ترتیب صحیح خواندن
    با در نظر گرفتن چیدمان تک‌ستونه یا دوستونه و حذف هدر/فوتر تکراری.
    """
    h, w = page.height, page.width

    table_bboxes = []
    table_items = []
    for t in page.find_tables():
        x0, top, x1, bottom = t.bbox
        # جدول‌هایی که کاملاً داخل نوار هدر/فوتر هستند معمولاً تشخیص اشتباه
        # از روی خطوط فوتر هستند، نه جدول واقعی.
        if bottom <= h * HEADER_ZONE or top >= h * (1 - FOOTER_ZONE):
            continue
        table_bboxes.append(t.bbox)
        data = t.extract()
        key = hash(str(data))
        if key in processed_table_hashes:
            continue
        processed_table_hashes.add(key)
        md = table_to_markdown(data)
        if md:
            table_items.append({"type": "table", "x0": x0, "x1": x1, "top": top, "bottom": bottom, "md": md})

    words = [w for w in page.extract_words() if not _word_in_any_bbox(w, table_bboxes)]
    lines = cluster_words_by_line(words)

    kept_lines = []
    for line in lines:
        if line["top"] <= h * HEADER_ZONE or line["bottom"] >= h * (1 - FOOTER_ZONE):
            text = " ".join(word["text"] for word in line["words"])
            if normalize_for_boilerplate(text) in boilerplate or _looks_like_stamp(text):
                continue
        kept_lines.append(line)

    gutter = find_column_gutter(kept_lines, w)
    items = sorted(kept_lines + table_items, key=lambda it: it["top"])
    return order_reading_flow(items, gutter)


def write_page(f, ordered_items, page_num, doc_id):
    """نوشتن محتوای چیده‌شده یک صفحه به‌صورت Markdown، با تشخیص بندهای شماره‌دار."""
    para = []
    current_numbering = None

    def flush(final=False):
        nonlocal para, current_numbering
        if not para:
            # یک شماره‌بند که هنوز متنی برایش نیامده (مثلاً قبل از یک break) را
            # نگه می‌داریم تا به پاراگراف بعدی بچسبد؛ فقط در پایان صفحه، در
            # صورت نبود ادامه، به‌تنهایی نوشته می‌شود تا Anchor آن از دست نرود.
            if final and current_numbering:
                depth = count_number_depth(current_numbering)
                anchor = f"{{#{doc_id}-{normalize_numbering(current_numbering)}}}"
                f.write(f"{'#' * min(depth, 6)} {current_numbering} {anchor}\n[Page: {page_num}]\n\n")
                current_numbering = None
            return
        text = " ".join(para)
        if current_numbering:
            depth = count_number_depth(current_numbering)
            anchor = f"{{#{doc_id}-{normalize_numbering(current_numbering)}}}"
            f.write(f"{'#' * min(depth, 6)} {current_numbering} {anchor}\n{text}\n[Page: {page_num}]\n\n")
        else:
            f.write(f"{text}\n[Page: {page_num}]\n\n")
        para = []
        current_numbering = None

    for item in ordered_items:
        if item["type"] == "break":
            flush()
            continue
        if item["type"] == "table":
            flush()
            f.write(item["md"] + f"\n[Page: {page_num}]\n\n")
            continue

        line_text = " ".join(word["text"] for word in item["words"]).strip()
        if not line_text:
            continue

        num = numbering_match(line_text)
        if num:
            flush()
            current_numbering = num
            rest = line_text[len(num):].lstrip(".٫").strip()
            if rest:
                para.append(rest)
        else:
            para.append(line_text)

    flush(final=True)


# ---------------------------------------------------------------------------
# پردازش اصلی PDF
# ---------------------------------------------------------------------------

def process_pdf(pdf_path, output_file, doc_id):
    """
    پردازش اصلی PDF:
    - باز کردن فایل PDF
    - استخراج متن و جداول با ترتیب خواندن صحیح
    - ایجاد TOC و Anchor
    - نوشتن خروجی به Markdown
    """
    start = datetime.now()
    success = True
    errors = []

    toc = extract_toc(pdf_path)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            boilerplate = detect_boilerplate(pdf)
            processed_table_hashes = set()

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {pdf_path.name}\n\n> **Note:** Page numbers refer to the PDF.\n\n")
                if toc:
                    f.write("## Table of Contents\n")
                    for level, title, page_no in toc:
                        f.write(f"{'  ' * (level - 1)}- {title} (Page {page_no})\n")
                    f.write("\n")

                for page_num, page in enumerate(tqdm(pdf.pages, desc=f"🔄 {pdf_path.name}"), 1):
                    try:
                        ordered_items = extract_page_items(page, boilerplate, processed_table_hashes)
                        write_page(f, ordered_items, page_num, doc_id)
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


def find_pdf_files(paths, pattern, recursive):
    """
    پیدا کردن فایل‌های PDF بر اساس آرگومان‌های ورودی.
    هر آرگومان می‌تواند یک فایل PDF، یک پوشه (با پشتیبانی از جستجوی
    بازگشتی) یا ترکیبی از این‌ها باشد. ترتیب ورودی حفظ می‌شود و فایل‌های
    تکراری (مسیرهای یکسان) حذف می‌گردند.
    """
    files = []
    seen = set()

    def add(p):
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            files.append(p)

    for raw in paths:
        p = Path(raw)
        if p.is_file():
            if p.suffix.lower() == ".pdf":
                add(p)
            else:
                print(f"⚠️  نادیده گرفته شد (PDF نیست): {p}")
        elif p.is_dir():
            glob_fn = p.rglob if recursive else p.glob
            for f in sorted(glob_fn(pattern)):
                if f.is_file():
                    add(f)
        else:
            print(f"⚠️  مسیر پیدا نشد: {p}")

    return files


def main():
    """
    تابع اصلی برنامه:
    - پردازش آرگومان‌های خط فرمان (فایل/پوشه/چند فایل/چند پوشه)
    - ساخت پوشه خروجی
    - اجرای پردازش برای هر PDF
    - نمایش خلاصه‌ی نتایج
    - تجمیع اختیاری خروجی‌ها در یک فایل Markdown واحد
    """
    parser = argparse.ArgumentParser(
        description="تبدیل فایل‌های PDF به Markdown ساخت‌یافته."
    )
    parser.add_argument(
        "paths", nargs="*", default=["."],
        help="فایل(های) PDF و/یا پوشه(های) ورودی (پیش‌فرض: پوشه جاری)"
    )
    parser.add_argument(
        "-R", "--recursive", action="store_true",
        help="جستجوی بازگشتی برای PDF در زیرپوشه‌ها"
    )
    parser.add_argument(
        "--pattern", default="*.pdf",
        help="الگوی جستجوی فایل هنگام دادن پوشه (پیش‌فرض: *.pdf)"
    )
    parser.add_argument(
        "-o", "--output-dir", default="markdown_output",
        help="پوشه خروجی برای فایل‌های Markdown (پیش‌فرض: markdown_output)"
    )
    parser.add_argument(
        "--id-start", type=int, default=1,
        help="شماره شروع شناسه‌های id (برای یکتا ماندن Anchorها بین چند اجرا)"
    )
    parser.add_argument(
        "--combine", nargs="?", const="combined_output_with_separators.md",
        default=None, metavar="OUTPUT",
        help="علاوه بر خروجی تفکیکی، یک فایل Markdown تجمیعی هم بسازد "
             "(نام پیش‌فرض: combined_output_with_separators.md)"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = find_pdf_files(args.paths, args.pattern, args.recursive)
    if not pdf_files:
        print("No PDF files found.")
        return

    summary = []
    output_files = []
    used_names = set()
    for offset, pdf in enumerate(pdf_files):
        doc_num = args.id_start + offset
        doc_id = f"id{doc_num}"
        print(f"\n📄 Processing {pdf.name} ({offset + 1}/{len(pdf_files)})...")
        out_name = f"{pdf.stem}.md"
        if out_name in used_names:
            # برای جلوگیری از رونویسی هنگام پردازش چند پوشه با فایل‌های هم‌نام
            out_name = f"{doc_id}_{pdf.stem}.md"
        used_names.add(out_name)
        output_file = output_dir / out_name
        success, errors, duration = process_pdf(pdf, output_file, doc_id)
        summary.append((pdf.name, success, duration, errors))
        if success:
            output_files.append(output_file)

    print("\n📋 Summary:")
    for name, success, duration, errors in summary:
        status = "✅ Success" if success else "❌ Failed"
        print(f"- {name}: {status} in {duration:.1f}s")
        if errors:
            for err in errors:
                print(f"   ⚠️  {err}")

    if args.combine is not None:
        if not output_files:
            print("\n⚠️  هیچ خروجی موفقی برای تجمیع وجود ندارد.")
            return
        combined_text, last_id = md_combiner.combine_md_files(output_files, id_start=args.id_start)
        combined_path = output_dir / args.combine
        combined_path.write_text(combined_text, encoding="utf-8")
        print(f"\n✅ خروجی تجمیعی ساخته شد: {combined_path}")
        print(f"🔢 LAST_ID_NUMBER={last_id}")


if __name__ == "__main__":
    main()
