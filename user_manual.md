# راهنمای کاربر: تبدیل PDF به Markdown برای اسناد ساختاریافته

## مقدمه
این ابزار پایتون برای تبدیل فایل‌های PDF (مثل استانداردهای ایکائو) به Markdown طراحی شده است. هدفش استخراج محتوای اسناد به صورت ساختاریافته (با بندها، جداول، و ارجاعات صفحه) برای استفاده در تحلیل، جستجو، یا مستندسازی است. خروجی‌ها برای هوش مصنوعی و کاربران انسانی بهینه‌اند.

## ویژگی‌ها
- **بندهای شماره‌دار:** بندها (مثل `۴٫۳٫۲٫۱`) به هدینگ‌های Markdown با انکرهای یکتا (مثل `{#id1-4.3.2.1}`) تبدیل می‌شوند.
- **جداول:** جدول‌های PDF به فرمت Markdown (مثل `| Code | Description | Value |`) استخراج می‌شوند.
- **فهرست مطالب (TOC):** اگر PDF فهرست مطالب داشته باشد، به هدینگ اضافه می‌شود.
- **متادیتا:** فایل YAML نگاشت شناسه‌ها (مثل `id1`) به نام فایل‌ها را ذخیره می‌کند.
- **ارجاع صفحه:** هر بخش و جدول با `[Page: X]` مشخص است.
- **خروجی دوگانه:** فایل‌های جداگانه برای هر PDF و یک فایل تجمیعی.

## پیش‌نیازها
- **سیستم‌عامل:** ویندوز، لینوکس، یا مک.
- **پایتون:** نسخه ۳٫۸ یا بالاتر.
- **کتابخانه‌ها:**
  - `PyMuPDF`
  - `pdfplumber`
  - `PyYAML`
- **فضای دیسک:** برای PDFها و خروجی‌ها.

## نصب
1. **نصب پایتون:**
   - از [python.org](https://www.python.org/downloads/) پایتون ۳٫۸+ را نصب کنید.
   - چک کنید `pip` کار کند:
     ```bash
     pip --version
     ```

2. **نصب کتابخانه‌ها:**
   ```bash
   pip install -r requirements.txt

   یا مستقیم:
bash

pip install PyMuPDF pdfplumber PyYAML

آماده‌سازی پروژه:
مخزن را کلون کنید:
bash

git clone https://github.com/yourusername/pdf-to-markdown-converter.git
cd pdf-to-markdown-converter

یا فایل pdf_to_markdown.py را در یک پوشه ذخیره کنید.

استفاده
قرار دادن PDFها:
PDFها (مثل icao_doc1.pdf) را در پوشه پروژه بگذارید:

pdf-to-markdown-converter/
  - pdf_to_markdown.py
  - icao_doc1.pdf
  - icao_doc2.pdf

اجرای کد:
bash

python pdf_to_markdown.py

بررسی خروجی:
پوشه markdown_output/ شامل:
فایل‌های جداگانه (مثل icao_doc1.md).

فایل تجمیعی (combined_output.md).

ساختار خروجی
فایل جداگانه (مثل icao_doc1.md)
شروع با نام PDF.

هشدار:
markdown

> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers.

فهرست مطالب (در صورت وجود).

جداول به صورت Markdown.

بندها با هدینگ (مثل #### ۴٫۳٫۲٫۱) و انکر (مثل {#id1-4.3.2.1}).

ارجاع صفحه با [Page: X].

مثال:
markdown

# icao_doc1.pdf

> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers.

# Chapter 1: Introduction [Page: 1]

| Code | Description     | Value |
|------|-----------------|-------|
| A1   | System Check    | 100   |
| A2   | Compliance Test | 200   |
[Page: 4]

#### ۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]

فایل تجمیعی (combined_output.md)
متادیتای YAML:
```yaml
documents:
  - id: id1
    title: icao_doc1.pdf
    pages: 10

فهرست اولیه:
markdown

- 1. id1: icao_doc1.pdf [10 Pages]

اسناد با هدینگ (مثل ## 1. id1: icao_doc1.pdf) و جداکننده‌ها (--- Start ---).

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

## سناریوهای استفاده
1. **پردازش اسناد ایکائو:**
   - PDFهای استاندارد (مثل Annex 6) را پردازش کنید.
   - از فایل تجمیعی برای جستجوی بندها (مثل `۴٫۳٫۲٫۱`) استفاده کنید.
   - انکرها (مثل `#id1-4.3.2.1`) را برای ارجاع سریع کپی کنید.

2. **تحلیل جداول:**
   - جداول (مثل کدها یا مشخصات) را به Markdown تبدیل کنید.
   - خروجی را در Excel یا دیتابیس وارد کنید.

3. **کار با هوش مصنوعی:**
   - فایل تجمیعی را برای جستجو یا تحلیل به مدل‌های AI بدید.
   - متادیتای YAML و انکرها ارجاع دقیق را آسان می‌کنند.

## نکات مهم
- **جداول:** جدول‌های بدون خط ممکن است به صورت متن خام استخراج شوند.
- **انکرها:** از `{#id1-4.3.2.1}` برای لینک‌دهی استفاده کنید.
- **PDFهای اسکن‌شده:** نیاز به OCR دارند (مثل Tesseract).
- **خطاها:** اگر PDF پردازش نشد، مطمئن شوید متن قابل استخراج دارد.

## عیب‌یابی
- **خطای نصب:**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt

خطای PDF:
PDF را با Adobe Reader تست کنید.

مطمئن شوید PDF متن دارد (نه تصویر).

جداول نادرست:
چک کنید جدول خطوط مرزی دارد.

برای جدول‌های پیچیده، با توسعه‌دهنده تماس بگیرید.

پیشنهادها
PDFها را با نام‌های ساده (مثل icao_annex6.pdf) ذخیره کنید.

قبل از پردازش، PDFها را پشتیبان بگیرید.

با یک PDF کوچک تست کنید.

پشتیبانی
برای سوالات یا مشکلات:
در گیتهاب Issue باز کنید.

یا با توسعه‌دهنده تماس بگیرید.

