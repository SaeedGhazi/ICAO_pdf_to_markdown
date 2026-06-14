#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================
# 📄 web_to_markdown.py
#
# دانلود تمام صفحات یک زیردامنه (یا یک مسیر مشخص از آن) و تبدیل محتوای
# متنی هر صفحه به Markdown، سپس ترکیب همه‌ی صفحات در یک فایل Markdown
# واحد با همان جداکننده‌های <<<FILE_START/END>>> که در text_to_markdown.py
# و md_combiner.py استفاده می‌شود. مناسب برای آپلود محتوای یک وبسایت/ویکی
# به ابزارهای هوش مصنوعی.
# ================================================

import argparse
import hashlib
import json
import re
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup
import html2text

SEPARATOR_START = "<<<FILE_START:"
SEPARATOR_END   = ">>>"
END_START       = "<<<FILE_END:"
END_END         = ">>>"

# پسوند فایل‌هایی که محتوای صفحه‌ی HTML نیستند و نباید دنبال شوند
SKIP_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".bmp", ".ico", ".webp",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".mp3", ".mp4", ".avi", ".mov",
    ".css", ".js", ".json", ".xml", ".rss", ".woff", ".woff2", ".ttf", ".eot",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".exe", ".dmg",
}

DEFAULT_USER_AGENT = "web_to_markdown.py (https://github.com/SaeedGhazi/ICAO_pdf_to_markdown)"


def normalize_url(url: str, keep_query: bool) -> str:
    """نرمال‌سازی URL: حذف fragment، حذف اسلش انتهایی تکراری، و در صورت نیاز حذف query string."""
    parsed = urlparse(url)
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    query = parsed.query if keep_query else ""
    return urlunparse((parsed.scheme, parsed.netloc, path, "", query, ""))


def is_html_link(url: str) -> bool:
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in SKIP_EXTENSIONS)


def matches_any(patterns, text) -> bool:
    return any(re.search(pat, text) for pat in patterns)


def fetch(session, url, timeout):
    try:
        resp = session.get(url, timeout=timeout)
    except requests.RequestException as e:
        return None, None, f"خطای درخواست: {e}"
    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code != 200:
        return resp, content_type, f"کد وضعیت {resp.status_code}"
    if "text/html" not in content_type:
        return resp, content_type, f"نوع محتوا غیر HTML: {content_type}"
    return resp, content_type, None


def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        absolute = urljoin(base_url, a["href"])
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        links.add(absolute)
    return links


def page_to_markdown(soup, keep_images):
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_images = not keep_images
    converter.ignore_links = False

    body = soup.body or soup
    markdown_text = converter.handle(str(body))
    # حذف خط‌های خالی پشت‌سرهم بیش از حد
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text)
    return markdown_text.strip()


def get_title(soup, url):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return url


def crawl(start_url, max_pages, max_depth, delay, same_path_only, keep_query,
          include_patterns, exclude_patterns, keep_images, user_agent,
          timeout, respect_robots):
    start_parsed = urlparse(start_url)
    netloc = start_parsed.netloc
    path_prefix = start_parsed.path if start_parsed.path.endswith("/") else start_parsed.path.rsplit("/", 1)[0] + "/"

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    rp = None
    if respect_robots:
        rp = robotparser.RobotFileParser()
        rp.set_url(urljoin(start_url, "/robots.txt"))
        try:
            rp.read()
        except Exception:
            rp = None

    start_norm = normalize_url(start_url, keep_query)
    queue = deque([(start_norm, 0)])
    visited = {start_norm}
    pages = []

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()

        if respect_robots and rp is not None and not rp.can_fetch(user_agent, url):
            print(f"⏭️  رد شد (robots.txt): {url}")
            continue

        resp, content_type, err = fetch(session, url, timeout)
        if err:
            print(f"⚠️  {url} -> {err}")
            time.sleep(delay)
            continue

        final_url = normalize_url(resp.url, keep_query)
        if urlparse(final_url).netloc != netloc:
            print(f"⏭️  رد شد (خارج از زیردامنه پس از redirect): {final_url}")
            time.sleep(delay)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        title = get_title(soup, final_url)
        markdown_text = page_to_markdown(soup, keep_images)
        pages.append((final_url, title, markdown_text))
        print(f"✅ ({len(pages)}/{max_pages}) {final_url}")

        if max_depth is None or depth < max_depth:
            for link in extract_links(soup, final_url):
                norm = normalize_url(link, keep_query)
                if norm in visited:
                    continue
                parsed = urlparse(norm)
                if parsed.netloc != netloc:
                    continue
                if not is_html_link(norm):
                    continue
                if same_path_only and not parsed.path.startswith(path_prefix):
                    continue
                if include_patterns and not matches_any(include_patterns, norm):
                    continue
                if exclude_patterns and matches_any(exclude_patterns, norm):
                    continue
                visited.add(norm)
                queue.append((norm, depth + 1))

        time.sleep(delay)

    return pages


def build_combined_markdown(pages, title):
    lines = [f"# {title}\n"]
    for idx, (url, page_title, _) in enumerate(pages, 1):
        lines.append(f"- {idx}. [{page_title}]({url})")
    lines.append("")

    for idx, (url, page_title, content) in enumerate(pages, 1):
        sha1 = hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()
        header_obj = {"index": idx, "url": url, "title": page_title, "size": len(content), "sha1": sha1}
        lines.append(f'{SEPARATOR_START}{json.dumps(header_obj, ensure_ascii=False)}{SEPARATOR_END}')
        lines.append(f"## {idx}. {page_title}")
        lines.append(f"Source: {url}\n")
        lines.append(content)
        lines.append(f'{END_START}{json.dumps({"index": idx, "url": url}, ensure_ascii=False)}{END_END}')
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="دانلود تمام صفحات یک زیردامنه (یا یک مسیر از آن) و ترکیب محتوای متنی "
                     "آن‌ها در یک فایل Markdown واحد، مناسب برای آپلود به ابزارهای هوش مصنوعی."
    )
    parser.add_argument(
        "url",
        help="آدرس شروع کراول (مثلاً https://wiki.flightgear.org/)"
    )
    parser.add_argument(
        "-o", "--output", default="web_combined.md",
        help="نام فایل خروجی Markdown (پیش‌فرض: web_combined.md)"
    )
    parser.add_argument(
        "--title", default=None,
        help="عنوان فایل خروجی (پیش‌فرض: نام دامنه)"
    )
    parser.add_argument(
        "--max-pages", type=int, default=200,
        help="حداکثر تعداد صفحاتی که دانلود می‌شوند (پیش‌فرض: 200)"
    )
    parser.add_argument(
        "--max-depth", type=int, default=None,
        help="حداکثر عمق دنبال‌کردن لینک‌ها از صفحه شروع (پیش‌فرض: بدون محدودیت)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="فاصله‌ی زمانی بین درخواست‌ها به ثانیه (پیش‌فرض: 0.5)"
    )
    parser.add_argument(
        "--same-path-only", action="store_true",
        help="فقط صفحاتی که زیرمسیر آدرس شروع هستند کراول شوند "
             "(مثلاً برای https://example.com/docs/ فقط /docs/...)"
    )
    parser.add_argument(
        "--include-query", action="store_true",
        help="آدرس‌هایی با query string (مثل ?action=edit) را نیز کراول کند "
             "(پیش‌فرض: نادیده گرفته می‌شوند)"
    )
    parser.add_argument(
        "--include", nargs="*", default=[],
        help="فقط آدرس‌هایی که با یکی از این الگوهای regex مطابقت دارند کراول شوند"
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[],
        help="آدرس‌هایی که با یکی از این الگوهای regex مطابقت دارند نادیده گرفته شوند "
             "(مثلاً 'Special:' 'action=edit' 'Talk:')"
    )
    parser.add_argument(
        "--keep-images", action="store_true",
        help="لینک تصاویر را در خروجی Markdown نگه دارد (پیش‌فرض: حذف می‌شوند)"
    )
    parser.add_argument(
        "--user-agent", default=DEFAULT_USER_AGENT,
        help="مقدار هدر User-Agent برای درخواست‌ها"
    )
    parser.add_argument(
        "--timeout", type=float, default=15,
        help="حداکثر زمان انتظار برای هر درخواست به ثانیه (پیش‌فرض: 15)"
    )
    parser.add_argument(
        "--ignore-robots", action="store_true",
        help="قوانین robots.txt را نادیده بگیرد (پیش‌فرض: رعایت می‌شود)"
    )
    args = parser.parse_args()

    title = args.title or urlparse(args.url).netloc

    pages = crawl(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        same_path_only=args.same_path_only,
        keep_query=args.include_query,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        keep_images=args.keep_images,
        user_agent=args.user_agent,
        timeout=args.timeout,
        respect_robots=not args.ignore_robots,
    )

    if not pages:
        print("هیچ صفحه‌ای دانلود نشد.")
        return

    combined = build_combined_markdown(pages, title)
    Path(args.output).write_text(combined, encoding="utf-8")

    total_size = sum(len(c.encode("utf-8")) for _, _, c in pages)
    print(f"\n✅ انجام شد. {len(pages)} صفحه ({total_size / 1024:.1f} KB) در '{args.output}' نوشته شد.")


if __name__ == "__main__":
    main()
