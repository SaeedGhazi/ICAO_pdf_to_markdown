# PDF to Markdown Converter for Structured Documents

This Python tool converts PDF documents (e.g., ICAO standards) into structured Markdown files, preserving headings, numbered sections, tables, and page references. It generates both individual Markdown files for each PDF and a combined file with metadata, making it ideal for technical documents requiring easy referencing and analysis.

## Features
- **Structured Output**: Converts PDF sections (e.g., `۴٫۳٫۲٫۱`) into Markdown headings with unique anchors (e.g., `{#id1-4.3.2.1}`).
- **Table Extraction**: Detects and converts PDF tables into Markdown tables.
- **Metadata**: Includes YAML metadata mapping document IDs (e.g., `id1`) to filenames.
- **Table of Contents (TOC)**: Extracts and includes TOC as Markdown headings (if available in the PDF).
- **Page Numbers**: Adds `[Page: X]` references for each section and table.
- **Combined Output**: Merges all documents into a single Markdown file with a clear index.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/pdf-to-markdown-converter.git
   cd pdf-to-markdown-converter
Install Dependencies:
Ensure Python 3.8+ is installed, then run:
bash
pip install -r requirements.txt
Required packages:
PyMuPDF (for TOC extraction)
pdfplumber (for text and table extraction)
PyYAML (for metadata)
Optional: For complex tables, consider installing camelot-py (requires Ghostscript).
Usage
Place your PDF files in the project directory.
Run the script:
bash
python pdf_to_markdown.py
Find outputs in the markdown_output/ folder:
Individual files (e.g., icao_doc1.md)
Combined file (combined_output.md)
Example Output
For a PDF named icao_doc1.pdf with a table and sections:
icao_doc1.md:
markdown
# icao_doc1.pdf

> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers.

# Chapter 1: Introduction [Page: 1]

|
 Code 
|
 Description     
|
 Value 
|
|
------
|
-----------------
|
-------
|
|
 A1   
|
 System Check    
|
 100   
|
|
 A2   
|
 Compliance Test 
|
 200   
|
[Page: 4]

#### ۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
combined_output.md (snippet):
```markdown
documents:
  - id: id1
    title: icao_doc1.pdf
    pages: 10
Documents Combined:
id1: icao_doc1.pdf [10 Pages]
1. id1: icao_doc1.pdf
--- Start ---
Note: Page numbers refer to the PDF sequence and may differ from printed page numbers.
Chapter 1: Introduction [Page: 1]
Code
Description
Value
A1
System Check
100
A2
Compliance Test
200
[Page: 4]
۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
--- End ---

## Limitations
- **Complex Tables**: Tables without clear borders may require `camelot-py` for better detection.
- **Scanned PDFs**: Text extraction may fail for non-text PDFs; OCR support (e.g., Tesseract) can be added.
- **Custom Numbering**: Assumes standard numbering (e.g., `۴٫۳٫۲٫۱`). Non-standard formats may need tweaks.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

Issues and feature requests are welcome!

## License
MIT License
توضیحات فایل README:
ساختار: مختصر و شامل بخش‌های استاندارد (هدف، نصب، استفاده، مثال، محدودیت‌ها، مشارکت).
زبان: انگلیسی، چون مخاطب گیتهاب معمولاً بین‌المللیه.
فرضیات: فرض کردم پروژه تو یه مخزن عمومیه (آدرس yourusername باید با نام کاربری واقعی جایگزین بشه). اگه پروژه خصوصیه یا نیاز به لینک خاصی نداره، می‌تونم این بخش رو حذف کنم.
محتوا: ویژگی‌های کلیدی (مثل جدول‌ها و انکرها) واضح توضیح داده شدن، و یه مثال واقعی از خروجی آوردم.
۲- User Manual (راهنمای کاربر) به فارسی
این راهنما برای استفاده شخصی شما نوشته شده و جزئیات بیشتری داره، با تمرکز روی سناریوهای واقعی و نکات فنی.
راهنمای کاربر: تبدیل PDF به Markdown برای اسناد ساختاریافته
مقدمه
این ابزار پایتون برای تبدیل فایل‌های PDF (مثل استانداردهای ایکائو) به فایل‌های Markdown طراحی شده و به شما کمک می‌کنه محتوای اسناد رو به صورت ساختاریافته (با بندها، جداول، و ارجاعات صفحه) استخراج کنید. خروجی‌ها برای تحلیل توسط هوش مصنوعی، جستجوی سریع، و استفاده در پروژه‌های فنی (مثل مستندسازی یا اتوماسیون) بهینه شدن.
ویژگی‌ها
بندهای شماره‌دار: بندها (مثل ۴٫۳٫۲٫۱) به هدینگ‌های Markdown با انکرهای یکتا (مثل {#id1-4.3.2.1}) تبدیل می‌شن.
جداول: جدول‌های PDF به جدول‌های Markdown تبدیل می‌شن (مثلاً | Code | Description | Value |).
فهرست مطالب (TOC): اگه PDF فهرست مطالب داشته باشه، به هدینگ‌های Markdown اضافه می‌شه.
متادیتا: یه فایل YAML در خروجی تجمیعی نگاشت شناسه‌ها (مثل id1) به نام فایل‌ها رو ذخیره می‌کنه.
ارجاعات صفحه: هر بخش و جدول با [Page: X] مشخص می‌شه.
خروجی دوگانه: فایل‌های جداگانه برای هر PDF و یه فایل تجمیعی با همه اسناد.
پیش‌نیازها
سیستم‌عامل: ویندوز، لینوکس، یا مک.
پایتون: نسخه ۳٫۸ یا بالاتر.
کتابخانه‌ها:
PyMuPDF: برای استخراج فهرست مطالب.
pdfplumber: برای استخراج متن و جدول.
PyYAML: برای تولید متادیتا.
فضای دیسک: به اندازه کافی برای ذخیره فایل‌های PDF و Markdown.
نصب
۱. نصب پایتون:
اگه پایتون ندارید، از python.org دانلود و نصب کنید.
مطمئن بشید pip کار می‌کنه (با دستور pip --version).
۲. نصب کتابخانه‌ها:
   تو ترمینال یا Command Prompt این دستور رو اجرا کنید:
bash
pip install PyMuPDF pdfplumber PyYAML
۳. دانلود کد:
فایل pdf_to_markdown.py رو تو یه پوشه ذخیره کنید (مثلاً C:\Projects\PDFConverter).
یا اگه از گیتهاب استفاده می‌کنید:
bash
git clone <repository-url>
cd pdf-to-markdown-converter
نحوه استفاده
۱. آماده‌سازی PDFها:
فایل‌های PDF (مثلاً icao_doc1.pdf) رو تو همون پوشه‌ای بذارید که فایل pdf_to_markdown.py هست.
مثلاً:
C:\Projects\PDFConverter\
  - pdf_to_markdown.py
  - icao_doc1.pdf
  - icao_doc2.pdf
۲. اجرای کد:
تو ترمینال یا Command Prompt برید به پوشه پروژه:
bash
cd C:\Projects\PDFConverter
دستور زیر رو اجرا کنید:
bash
python pdf_to_markdown.py
۳. بررسی خروجی‌ها:
یه پوشه markdown_output تو همون مسیر ساخته می‌شه.
داخلش این فایل‌ها رو می‌بینید:
فایل‌های جداگانه (مثل icao_doc1.md) برای هر PDF.
فایل تجمیعی (combined_output.md) با همه اسناد.
مثال:
markdown_output/
  - icao_doc1.md
  - icao_doc2.md
  - combined_output.md
ساختار خروجی
فایل‌های جداگانه (مثل icao_doc1.md)
با نام PDF شروع می‌شه (مثلاً # icao_doc1.pdf).
هشدار درباره شماره صفحه:
markdown
> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers.
فهرست مطالب (اگه وجود داشته باشه) به صورت هدینگ.
جدول‌ها به فرمت Markdown (مثل | Code | Description | Value |).
بندها با هدینگ‌های مناسب (مثل #### ۴٫۳٫۲٫۱) و انکرها (مثل {#id1-4.3.2.1}).
هر بخش با [Page: X] مشخص شده.
مثال:
markdown
# icao_doc1.pdf

> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers.

# Chapter 1: Introduction [Page: 1]

|
 Code 
|
 Description     
|
 Value 
|
|
------
|
-----------------
|
-------
|
|
 A1   
|
 System Check    
|
 100   
|
|
 A2   
|
 Compliance Test 
|
 200   
|
[Page: 4]

#### ۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
فایل تجمیعی (combined_output.md)
با متادیتای YAML شروع می‌شه:
```yaml
documents:
  - id: id1
    title: icao_doc1.pdf
    pages: 10
فهرست اولیه:
markdown
# Documents Combined:
- 1. id1: icao_doc1.pdf [10 Pages]
محتوای هر سند با هدینگ (مثل ## 1. id1: icao_doc1.pdf) و جداکننده‌های --- Start --- و --- End ---.
هدینگ‌ها یه سطح پایین‌تر از فایل‌های جداگانه (مثلاً ##### ۴٫۳٫۲٫۱).
مثال:
```markdown
documents:
  - id: id1
    title: icao_doc1.pdf
    pages: 10
Documents Combined:
id1: icao_doc1.pdf [10 Pages]
1. id1: icao_doc1.pdf
--- Start ---
Note: Page numbers refer to the PDF sequence and may differ from printed page numbers.
Chapter 1: Introduction [Page: 1]
Code
Description
Value
A1
System Check
100
A2
Compliance Test
200
[Page: 4]
۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
--- End ---

## نکات مهم
- **جداول:** جدول‌ها با خطوط مرزی خوب تشخیص داده می‌شن. اگه جدول بدون خط باشه، ممکنه به صورت متن خام استخراج بشه.
- **انکرها:** انکرها (مثل `{#id1-4.3.2.1}`) برای ارجاع سریع توسط هوش مصنوعی یا لینک‌های داخلی طراحی شدن.
- **شماره صفحه:** شماره‌های صفحه بر اساس ترتیب PDFن و ممکنه با شماره‌های چاپی فرق کنن.
- **PDFهای اسکن‌شده:** اگه PDF متن قابل استخراج نداشته باشه (مثل تصاویر اسکن‌شده)، کد خطا می‌ده. برای این موارد، نیاز به OCR (مثل Tesseract) دارید.
- **خطاها:** اگه PDF خراب باشه یا پردازش نشه، کد یه پیام خطا نشون می‌ده (مثل `Error processing file.pdf`).

## سناریوهای استفاده
### ۱. تحلیل اسناد ایکائو
- فرض کنید چند سند ایکائو (مثل Annex 6) دارید.
- PDFها رو تو پوشه کد بذارید و کد رو اجرا کنید.
- خروجی‌ها رو باز کنید:
  - فایل‌های جداگانه برای مرور سریع هر سند.
  - فایل تجمیعی برای جستجوی یکپارچه (مثلاً پیدا کردن بند `۴٫۳٫۲٫۱` تو همه اسناد).
- از انکرها (مثل `#id1-4.3.2.1`) برای ارجاع مستقیم تو گیتهاب یا ابزارهای Markdown استفاده کنید.

### ۲. استخراج جداول
- اگه سند جدول داره (مثل کدها یا استانداردها)، خروجی Markdown جدول رو به شکل خوانا نشون می‌ده.
- جدول‌ها رو می‌تونید کپی کنید و تو ابزارهای دیگه (مثل Excel یا دیتابیس) استفاده کنید.

### ۳. استفاده با هوش مصنوعی
- فایل تجمیعی (`combined_output.md`) برای هوش مصنوعی بهینه‌ست، چون:
  - متادیتای YAML نگاشت `id1` به فایل رو مشخص می‌کنه.
  - انکرها ارجاع دقیق به بندها رو ممکن می‌کنن.
  - جدول‌ها و متن‌ها ساختاریافته‌ان و راحت پارس می‌شن.

## محدودیت‌ها و راهکارها
- **جداول پیچیده:** اگه جدول بدون خطوط مرزی باشه، ممکنه درست تشخیص داده نشه. راهکار:
  - نصب `camelot-py` و ادغامش با کد (نیاز به Ghostscript).
  - یا استفاده از OCR برای PDFهای خاص.
- **PDFهای غیرمتنی:** برای PDFهای اسکن‌شده، کد کار نمی‌کنه. راهکار:
  - استفاده از Tesseract یا یه ابزار OCR قبل از پردازش.
- **شماره‌گذاری غیراستاندارد:** اگه بندها فرمت عجیبی داشته باشن (مثلاً `A.1.b`)، ممکنه درست تشخیص داده نشن. راهکار:
  - کد رو برای فرمت خاص سفارشی کنید (مثلاً تغییر regex تو `is_numbering`).

## عیب‌یابی
- **خطای نصب کتابخانه:**
  - چک کنید `pip` به‌روزه:
    ```bash
    pip install --upgrade pip
    ```
  - دوباره نصب کنید:
    ```bash
    pip install PyMuPDF pdfplumber PyYAML
    ```
- **خطای پردازش PDF:**
  - مطمئن بشید فایل PDF خراب نیست (با Adobe Reader بازش کنید).
  - چک کنید PDF متن قابل استخراج داره (مثلاً با کپی کردن متن تو PDF).
- **جداول استخراج نشدن:**
  - PDF رو چک کنید که جدول‌ها خطوط مرزی دارن.
  - اگه جدول‌ها پیچیده‌ان، با من تماس بگیرید تا `camelot` اضافه کنم!

## پیشنهادها
- **نام‌گذاری PDFها:** از نام‌های ساده و معنی‌دار (مثل `icao_annex6.pdf`) استفاده کنید تا فهرست اولیه خواناتر بشه.
- **پشتیبان‌گیری:** قبل از پردازش، از PDFها نسخه پشتیبان بگیرید.
- **تست اولیه:** اول با یه PDF کوچک تست کنید تا مطمئن بشید خروجی درست کار می‌کنه.

## تماس برای پشتیبانی
اگه سوال، خطا، یا پیشنهادی دارید، می‌تونید:
- تو گیتهاب یه Issue باز کنید (اگه پروژه عمومیه).
- یا مستقیم با توسعه‌دهنده تماس بگیرید (ایمیل یا روشی که ترجیح می‌دید).

---

**توضیحات User Manual:**
- **زبان:** فارسی، برای راحتی شما.
- **محتوا:** شامل نصب، اجرا، توضیح خروجی‌ها، سناریوهای واقعی، و عیب‌یابی.
- **تمرکز:** روی اسناد ایکائو و نیازهای شما (مثل جدول‌ها و ارجاع‌پذیری).
- **کاربردی بودن:** نکات عملی (مثل عیب‌یابی یا پیشنهاد نام‌گذاری) اضافه کردم.

### فایل‌های پیشنهادی برای پروژه
برای کامل شدن پروژه تو گیتهاب، این فایل‌ها رو پیشنهاد می‌دم:
- `pdf_to_markdown.py`: کد اصلی (که قبلاً دادم).
- `README.md`: فایل بالا.
- `requirements.txt`: برای نصب خودکار کتابخانه‌ها:
  PyMuPDF>=1.23.0
  pdfplumber>=0.11.0
  PyYAML>=6.0
- `docs/user_manual.md`: فایل User Manual به صورت Markdown (اگه بخواید جدا از پاسخ اینجا ذخیره بشه).

اگه بخواید، می‌تونم ساختار کامل پروژه رو براتون آماده کنم (مثلاً با پوشه‌ها و فایل‌های نمونه).

### سؤالم از شما
- **README و User Manual:** آیا این دو فایل نیازتون رو برآورده می‌کنن؟ چیزی اضافه یا کم کنم؟ مثلاً بخش خاصی برای گیتهاب (مثل مثال‌های بیشتر) یا User Manual (مثلاً جزئیات فنی کد)?
- **زبان:** User Manual رو فارسی نوشتم، ولی اگه ترجیح می‌دید انگلیسی باشه یا ترکیبی، بگید. برای README هم اگه فارسی بخواید، می‌تونم تغییر بدم.
- **تست با نمونه:** اگه PDF نمونه بدید، می‌تونم خروجی‌ها رو باهاش تست کنم و مثال‌های README و User Manual رو واقعی‌تر کنم.
- **ساختار پروژه:** آیا پروژه رو تو گیتهاب آپلود می‌کنید؟ اگه آره، نیازه چیزی (مثل `.gitignore` یا license) اضافه کنم؟
- **نکته دیگه:** چیزی تو کد یا خروجی‌ها مونده که بخواید روش کار کنیم (مثلاً بهبود جدول‌ها یا انکرها)؟

ممنون از همراهی‌تون و پروژه جذابی که باهم ساختیم! منتظر نظرتونم که ببینم چطور نهایی کنیم.
