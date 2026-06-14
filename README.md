# PDF to Markdown Converter for Structured Documents

A set of Python tools to convert PDF documents (e.g., ICAO standards) into structured Markdown files, preserving numbered sections, tables, and page references — and to combine multiple Markdown/source files into a single AI-friendly document.

## Tools

- **`pdf_to_markdown.py`** — Converts one or more PDFs (a single file, multiple files, one folder, or multiple folders) into structured Markdown, with an optional combined output.
- **`md_combiner.py`** — Combines multiple Markdown files into a single file with unique anchors and JSON metadata per document.
- **`text_to_markdown.py`** — Combines the text/source files of one or more projects into a single Markdown file, using the same AI-friendly separator format. Useful for uploading a multi-file codebase to AI tools.
- **`web_to_markdown.py`** — Crawls every page of a website/subdomain (e.g., a wiki) and combines the text content of all pages into a single AI-friendly Markdown file, using the same separator format.

All four tools share a common separator convention:

```
<<<FILE_START:{...json metadata...}>>>
...content...
<<<FILE_END:{...json metadata...}>>>
```

This lets AI tools reliably detect the boundaries between documents/files and avoid mixing up content from different sources.

## Features

- **Structured Sections**: Converts numbered sections (e.g., `۴٫۳٫۲٫۱` or `5.4.2`) into Markdown headings with unique anchors (e.g., `{#id1-4.3.2.1}`).
- **Two-Column Layouts**: Detects and correctly reorders text from two-column PDF pages.
- **Table Extraction**: Detects and converts PDF tables into Markdown format, preserving multi-line cells with `<br>`.
- **Header/Footer & Stamp Removal**: Automatically detects and removes repeated headers, footers, page numbers, and official stamps.
- **`(cid:xx)` Cleanup**: Removes broken font-encoding artifacts from extracted text.
- **Table of Contents (TOC)**: Includes TOC as Markdown headings if present in the PDF.
- **Page References**: Adds `[Page: X]` tags for precise navigation.
- **Flexible Input**: Accepts a single PDF, multiple PDFs, a folder, or multiple folders (with optional recursive search).
- **Dual Output**: Generates individual Markdown files per PDF and, optionally, a combined file with unique anchors across documents.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SaeedGhazi/ICAO_pdf_to_markdown.git
   cd ICAO_pdf_to_markdown
   ```

2. **Install Python**: Ensure Python 3.8+ is installed. Download from [python.org](https://www.python.org/) if needed.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Dependencies:
   - **PyMuPDF**: For TOC extraction.
   - **pdfplumber**: For text and table extraction.
   - **tqdm**: For progress bars.
   - **requests**, **beautifulsoup4**, **html2text**: Used by `web_to_markdown.py` to crawl and convert web pages.

   `md_combiner.py` and `text_to_markdown.py` only use the Python standard library and need no extra installation.

## Usage

### 1. Convert PDFs to Markdown

```bash
python3 pdf_to_markdown.py [paths ...] [options]
```

`paths` can be any combination of PDF files and folders (defaults to the current directory).

| Option | Description |
|---|---|
| `paths` | PDF file(s) and/or folder(s) (default: `.`) |
| `-R`, `--recursive` | Recursively search folders for PDFs |
| `--pattern PATTERN` | File pattern to use when a folder is given (default: `*.pdf`) |
| `-o`, `--output-dir DIR` | Output directory for Markdown files (default: `markdown_output`) |
| `--id-start N` | Starting number for document `id`s, to keep anchors unique across runs (default: `1`) |
| `--combine [OUTPUT]` | Also build a combined Markdown file (default name: `combined_output_with_separators.md`) |

Examples:

```bash
# Convert all PDFs in the current directory (default behavior)
python3 pdf_to_markdown.py

# Convert a single file
python3 pdf_to_markdown.py docs/icao_doc1.pdf

# Convert multiple files
python3 pdf_to_markdown.py docs/icao_doc1.pdf docs/icao_doc2.pdf

# Convert all PDFs in a folder (recursively) and build a combined output
python3 pdf_to_markdown.py pdfs/ -R --combine

# Convert multiple folders, custom output dir and combined filename
python3 pdf_to_markdown.py annex1/ annex2/ -R -o markdown_output --combine annexes_combined.md

# Continue anchor numbering for a new batch (previous batch ended at id10)
python3 pdf_to_markdown.py more_pdfs/ -R --id-start 11 --combine
```

Output is written to the output directory (default `markdown_output/`): one `.md` file per PDF (named `<filename>.md`; if a name collides, the duplicate is saved as `id<N>_<filename>.md`), plus an optional combined file when `--combine` is used.

### 2. Combine Markdown Files

```bash
python3 md_combiner.py [path] [options]
```

| Option | Description |
|---|---|
| `path` | Input folder (default: current directory) |
| `-o`, `--output FILE` | Output file name (default: `combined_output_with_separators.md`) |
| `--pattern PATTERN` | Search pattern (default: `*.md`) |
| `-R`, `--recursive` | Recursively search subfolders |
| `--id-start N` | Starting number for `id`s (e.g., `101` for a second batch, default: `1`) |

Examples:

```bash
python3 md_combiner.py markdown_output/ -o combined_output_with_separators.md

# Combine a new batch without colliding with a previous batch that ended at id10
python3 md_combiner.py more_markdown/ -o combined_part2.md --id-start 11
```

The program prints `LAST_ID_NUMBER` at the end, so you know where to start the next batch.

### 3. Combine a Source Code / Text Project

```bash
python3 text_to_markdown.py [paths ...] [options]
```

`paths` can be files and/or folders (default: current directory).

| Option | Description |
|---|---|
| `paths` | Input file(s) and/or folder(s) (default: `.`) |
| `--no-recursive` | Don't search subfolders recursively (default: recursive) |
| `-o`, `--output FILE` | Output file name (default: `code_combined.md`) |
| `--max-size BYTES` | Maximum size per file in bytes (default: `1000000`) |
| `--exclude [PATTERN ...]` | Extra folder names or file patterns to exclude (e.g., `tests` or `'*.spec.js'`) |
| `--title TITLE` | Title for the output file (default: `Project Source Combined`) |

Examples:

```bash
# Combine all text files in the current project
python3 text_to_markdown.py . -o project_combined.md --title "My Project"

# Combine multiple projects
python3 text_to_markdown.py backend/ frontend/ -o full_stack_combined.md

# Exclude an extra folder and pattern
python3 text_to_markdown.py . --exclude tests "*.spec.js" -o code_combined.md
```

By default, sensitive files (`.env`, `*.pem`, `*.key`, `id_rsa*`, etc.), lock files, media/binary files, and dependency/build folders (`.git`, `node_modules`, `venv`, `dist`, `build`, etc.) are excluded.

### 4. Crawl a Website/Subdomain to Markdown

```bash
python3 web_to_markdown.py URL [options]
```

`URL` is the starting page (e.g., the homepage of a subdomain). The crawler follows links that stay on the same domain and downloads each page's text content, converted to Markdown.

| Option | Description |
|---|---|
| `url` | Starting URL to crawl (required) |
| `-o`, `--output FILE` | Output file name (default: `web_combined.md`) |
| `--title TITLE` | Title for the output file (default: the domain name) |
| `--max-pages N` | Maximum number of pages to download (default: `200`) |
| `--max-depth N` | Maximum link-following depth from the start page (default: unlimited) |
| `--delay SECONDS` | Delay between requests, in seconds (default: `0.5`) |
| `--same-path-only` | Only crawl pages under the same path prefix as the start URL |
| `--include-query` | Also crawl URLs with a query string (default: skipped) |
| `--include [PATTERN ...]` | Only crawl URLs matching one of these regex patterns |
| `--exclude [PATTERN ...]` | Skip URLs matching one of these regex patterns (e.g., `'Special:'`, `'action=edit'`, `'Talk:'`) |
| `--keep-images` | Keep image links in the Markdown output (default: stripped) |
| `--user-agent UA` | Custom `User-Agent` header |
| `--timeout SECONDS` | Request timeout, in seconds (default: `15`) |
| `--ignore-robots` | Ignore `robots.txt` rules (default: respected) |

Examples:

```bash
# Crawl an entire wiki subdomain into a single AI-friendly Markdown file
python3 web_to_markdown.py https://wiki.flightgear.org/ -o flightgear_wiki.md --title "FlightGear Wiki"

# Limit the crawl, skip MediaWiki utility pages, and be polite with delays
python3 web_to_markdown.py https://wiki.flightgear.org/ \
    -o flightgear_wiki.md --title "FlightGear Wiki" \
    --max-pages 500 --delay 1 \
    --exclude 'Special:' 'Talk:' 'User:' 'action=' 'oldid='

# Only crawl pages under a specific path
python3 web_to_markdown.py https://example.com/docs/ --same-path-only -o docs_combined.md
```

📂 Output is a single Markdown file: a list of crawled pages at the top, followed by each page's content wrapped in `<<<FILE_START/END>>>` separators with JSON metadata (`index`, `url`, `title`, `size`, `sha1`).

> ⚠️ Be respectful of the target site: keep a reasonable `--delay`, set a sensible `--max-pages`, and leave `robots.txt` enforcement enabled unless you have permission to ignore it.

## Example Output

### Structured section:
```markdown
#### ۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
```

### Table:
```markdown
| Code | Description     | Value |
|------|-----------------|-------|
| A1   | System Check    | 100   |
| A2   | Compliance Test | 200   |
[Page: 4]
```

### Combined output entry (PDF-derived):
```markdown
<<<FILE_START:{"index": 1, "id": "id1", "name": "icao_doc1.md", "pages": 10, "sha1": "...", "path": "markdown_output/icao_doc1.md"}>>>
## 1. id1-4.3.2.1: icao_doc1.md

#### ۴٫۳٫۲٫۱ {#id1-4.3.2.1}
The operator shall ensure that all systems are operational. [Page: 5]
<<<FILE_END:{"index": 1, "id": "id1", "name": "icao_doc1.md"}>>>
```

### Combined output entry (web-derived):
```markdown
<<<FILE_START:{"index": 1, "url": "https://wiki.flightgear.org/Main_Page", "title": "Main Page - FlightGear wiki", "size": 1234, "sha1": "..."}>>>
## 1. Main Page - FlightGear wiki
Source: https://wiki.flightgear.org/Main_Page

# Welcome to the FlightGear wiki
...page content converted to Markdown...
<<<FILE_END:{"index": 1, "url": "https://wiki.flightgear.org/Main_Page"}>>>
```

## Anchor Uniqueness Across Documents

Each document gets a unique base id (`id1`, `id2`, ...), and all of its internal anchors are normalized to `{#id<N>-<section>}`. When combining multiple PDFs in one run with `--combine`, ids are assigned sequentially from `--id-start`, so no two documents share an anchor. For separate batches, set `--id-start` to `LAST_ID_NUMBER + 1` of the previous batch to keep anchors unique across the whole project.

## Documentation

See [user_manual.md](user_manual.md) (in Persian) for a detailed usage guide covering all four tools.

## Limitations

- **Scanned PDFs**: Require OCR (e.g., Tesseract) for non-text PDFs.
- **Complex Tables**: Tables without clear borders may need `camelot-py` or manual editing.
- **Custom Numbering**: Non-standard formats (e.g., `A.1.b`) may need code adjustments.
- **`web_to_markdown.py`**: Only crawls plain links (`<a href>`); content rendered dynamically by JavaScript will not be captured. Very large sites may need a higher `--max-pages` or multiple runs scoped with `--same-path-only`/`--include`/`--exclude`.

## Troubleshooting

- **Module Errors**: Run `pip install -r requirements.txt`.
- **PDF Issues**: Ensure PDFs have extractable text (test with Adobe Reader).
- **Table Problems**: Verify tables have borders; consider `camelot-py` for complex cases.
- **Missing files in `text_to_markdown.py` output**: Check `DEFAULT_EXCLUDE_DIRS`/`DEFAULT_EXCLUDE_PATTERNS`, `--exclude`, binary detection, or `--max-size`.
- **`web_to_markdown.py` finds too few/many pages**: Check `--same-path-only`, `--include-query`, and `--include`/`--exclude` patterns; some sites also block crawlers via `robots.txt` (use `--ignore-robots` only if you have permission).

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push (`git push origin feature-name`).
5. Open a Pull Request.

File issues for bugs or suggestions.

## License

[MIT License](LICENSE)
