#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================
# 📄 text_to_markdown.py
#
# تبدیل فایل‌های متنی/سورس‌کد یک یا چند پروژه (هر فایل غیرباینری) به یک
# فایل Markdown واحد، با همان جداکننده‌های <<<FILE_START/END>>> که در
# md_combiner.py استفاده می‌شود. مناسب برای آپلود یک پروژه چندفایلی به
# ابزارهای هوش مصنوعی.
# ================================================

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path

SEPARATOR_START = "<<<FILE_START:"
SEPARATOR_END   = ">>>"
END_START       = "<<<FILE_END:"
END_END         = ">>>"

# پوشه‌هایی که به‌طور پیش‌فرض نادیده گرفته می‌شوند (نسبت به هر مسیر ورودی)
DEFAULT_EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".tox", "dist", "build", ".next", ".nuxt", "target", ".idea",
    ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "coverage", ".cache", "vendor",
}

# الگوهای فایل که به‌طور پیش‌فرض نادیده گرفته می‌شوند (شامل قفل‌فایل‌ها،
# فایل‌های ساخته‌شده، رسانه‌ها و فایل‌های حساس مثل کلید/رمز)
DEFAULT_EXCLUDE_PATTERNS = [
    "*.min.js", "*.min.css", "*.map",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "Pipfile.lock", "Cargo.lock", "composer.lock",
    ".env", ".env.*", "*.pem", "*.key", "id_rsa*", "id_ed25519*",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg", "*.bmp",
    "*.pdf", "*.zip", "*.tar", "*.gz", "*.7z", "*.rar",
    "*.exe", "*.dll", "*.so", "*.dylib", "*.bin", "*.class", "*.jar",
    "*.pyc", "*.woff", "*.woff2", "*.ttf", "*.eot",
]

# نگاشت پسوند فایل به زبان مورد استفاده در بلوک کد Markdown
LANGUAGE_MAP = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".jsx": "jsx", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "tsx",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin", ".scala": "scala",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".cs": "csharp", ".go": "go", ".rs": "rust", ".rb": "ruby",
    ".php": "php", ".swift": "swift", ".dart": "dart", ".lua": "lua",
    ".pl": "perl", ".r": "r", ".m": "objectivec",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash", ".ps1": "powershell",
    ".sql": "sql", ".html": "html", ".htm": "html", ".css": "css",
    ".scss": "scss", ".less": "less", ".vue": "vue",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".xml": "xml", ".md": "markdown", ".ini": "ini", ".cfg": "ini",
    ".conf": "ini", ".graphql": "graphql", ".proto": "protobuf",
    ".tf": "hcl", ".hcl": "hcl",
}


def guess_language(path: Path) -> str:
    """تشخیص زبان بلوک کد بر اساس پسوند یا نام فایل."""
    name = path.name.lower()
    if name in ("dockerfile", "makefile"):
        return name
    return LANGUAGE_MAP.get(path.suffix.lower(), "")


def is_probably_text(path: Path, sample_size: int = 4096) -> bool:
    """تشخیص ساده‌ی فایل متنی بودن: نبود بایت null و قابل‌دیکود بودن UTF-8."""
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(sample_size)
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _display_path(f: Path, raw: str, root: Path | None) -> str:
    """
    مسیر نمایشی فایل برای استفاده در عنوان و متادیتای JSON.
    - برای فایل‌هایی که از یک پوشه پیدا شده‌اند: <نام پوشه>/<مسیر نسبی>
      (یا فقط مسیر نسبی اگر پوشه همان پوشه جاری باشد).
    - برای فایل‌هایی که مستقیم به‌عنوان آرگومان داده شده‌اند: همان مسیر
      ورودی (نسبی) یا نام فایل (اگر مطلق بوده).
    """
    if root is not None:
        rel = f.relative_to(root)
        if root.resolve() == Path.cwd().resolve():
            return rel.as_posix()
        return (Path(root.name) / rel).as_posix()
    raw_path = Path(raw)
    if raw_path.is_absolute():
        return f.name
    return raw_path.as_posix()


def iter_files(paths, recursive, exclude_dirs, exclude_patterns, max_size, skip_paths):
    """
    پیدا کردن فایل‌های متنی برای ترکیب.
    هر مسیر ورودی می‌تواند یک فایل یا یک پوشه باشد. حذف پوشه‌ها/الگوها
    نسبت به مسیر هر ورودی (نه ریشه دیسک) اعمال می‌شود.
    """
    seen = set()
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            candidates = [(p, [], _display_path(p, raw, None))]
        elif p.is_dir():
            glob_fn = p.rglob if recursive else p.glob
            candidates = []
            for f in sorted(glob_fn("*")):
                if not f.is_file():
                    continue
                rel_parts = f.relative_to(p).parts[:-1]
                candidates.append((f, rel_parts, _display_path(f, raw, p)))
        else:
            print(f"⚠️  مسیر پیدا نشد: {p}")
            continue

        for f, rel_parts, display in candidates:
            resolved = f.resolve()
            if resolved in seen or resolved in skip_paths:
                continue
            if any(part in exclude_dirs for part in rel_parts):
                continue
            if any(fnmatch.fnmatch(f.name, pat) for pat in exclude_patterns):
                continue
            try:
                size = f.stat().st_size
            except OSError:
                continue
            if size > max_size:
                continue
            if not is_probably_text(f):
                continue
            seen.add(resolved)
            yield f, display


def fence_for(content: str) -> str:
    """
    انتخاب نوار Markdown (```` یا بیشتر) به‌گونه‌ای که با هر بلوک کد
    تودرتوی داخل خود فایل تداخل نداشته باشد.
    """
    longest = run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def build_combined_markdown(files, title):
    """ساخت محتوای Markdown ترکیبی با جداکننده‌های <<<FILE_START/END>>>."""
    entries = []
    for f, display in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"⚠️ خطا در خواندن {f}: {e}")
            continue
        entries.append((f, display, content))

    lines = [f"# {title}\n"]
    for idx, (_, rel, _) in enumerate(entries, 1):
        lines.append(f"- {idx}. {rel}")
    lines.append("")

    for idx, (f, rel, content) in enumerate(entries, 1):
        sha1 = hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()
        header_obj = {"index": idx, "path": rel, "size": len(content), "sha1": sha1}
        lines.append(f'{SEPARATOR_START}{json.dumps(header_obj, ensure_ascii=False)}{SEPARATOR_END}')
        lines.append(f"## {idx}. {rel}\n")
        fence = fence_for(content)
        lang = guess_language(f)
        lines.append(f"{fence}{lang}")
        lines.append(content.rstrip("\n"))
        lines.append(fence)
        lines.append(f'{END_START}{json.dumps({"index": idx, "path": rel}, ensure_ascii=False)}{END_END}')
        lines.append("")

    return "\n".join(lines), entries


def main():
    parser = argparse.ArgumentParser(
        description="تبدیل فایل‌های متنی/سورس‌کد یک یا چند پروژه به یک Markdown واحد "
                     "برای آپلود به ابزارهای هوش مصنوعی."
    )
    parser.add_argument(
        "paths", nargs="*", default=["."],
        help="فایل(ها) و/یا پوشه(های) ورودی (پیش‌فرض: پوشه جاری)"
    )
    parser.add_argument(
        "--no-recursive", action="store_true",
        help="عدم جستجوی بازگشتی در زیرپوشه‌ها (پیش‌فرض: بازگشتی)"
    )
    parser.add_argument(
        "-o", "--output", default="code_combined.md",
        help="نام فایل خروجی (پیش‌فرض: code_combined.md)"
    )
    parser.add_argument(
        "--max-size", type=int, default=1_000_000,
        help="حداکثر حجم هر فایل بر حسب بایت (پیش‌فرض: 1000000)"
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[],
        help="نام پوشه یا الگوی فایل اضافی برای نادیده گرفتن (مثلاً tests یا '*.spec.js')"
    )
    parser.add_argument(
        "--title", default="Project Source Combined",
        help="عنوان فایل خروجی"
    )
    args = parser.parse_args()

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude)
    exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS) + list(args.exclude)

    out_path = Path(args.output).resolve()
    skip_paths = {out_path}

    files = list(iter_files(
        args.paths, not args.no_recursive, exclude_dirs, exclude_patterns,
        args.max_size, skip_paths,
    ))
    if not files:
        print("No matching text files found.")
        return

    combined, entries = build_combined_markdown(files, args.title)
    Path(args.output).write_text(combined, encoding="utf-8")

    total_size = sum(len(c.encode("utf-8")) for _, _, c in entries)
    print(f"✅ انجام شد. {len(entries)} فایل ({total_size / 1024:.1f} KB) در '{args.output}' نوشته شد.")


if __name__ == "__main__":
    main()
