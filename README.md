

# PDF to Markdown Converter for Structured Documents

A Python tool to convert PDF documents (e.g., ICAO standards) into structured Markdown files, preserving numbered sections, tables, and page references. Ideal for technical documents requiring easy referencing and AI analysis.

## Features
- **Structured Sections**: Converts numbered sections (e.g., `۴٫۳٫۲٫۱`) into Markdown headings with unique anchors (e.g., `{#id1-4.3.2.1}`).
- **Table Extraction**: Detects and converts PDF tables into Markdown format.
- **YAML Metadata**: Maps document IDs (e.g., `id1`) to filenames in the combined output.
- **Table of Contents (TOC)**: Includes TOC as Markdown headings if present in the PDF.
- **Page References**: Adds `[Page: X]` tags for precise navigation.
- **Dual Output**: Generates individual Markdown files per PDF and a combined file.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SaeedGhazi/ICAO_pdf_to_markdown.git
   cd ICAO_pdf_to_markdown

Install Python:
Ensure Python 3.8+ is installed. Download from python.org if needed.

Install Dependencies:
bash

pip install -r requirements.txt

Dependencies:
PyMuPDF: For TOC extraction.

pdfplumber: For text and table extraction.

PyYAML: For metadata generation.

Usage
Place PDF files (e.g., icao_doc1.pdf) in the project directory.

Run the script:
bash

python pdf_to_markdown.py

Outputs appear in markdown_output/:
Individual files (e.g., icao_doc1.md).

Combined file (combined_output.md).

Example Output
For icao_doc1.pdf:
markdown_output/icao_doc1.md:
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

markdown_output/combined_output.md (snippet):
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

## Documentation
See [docs/user_manual.md](docs/user_manual.md) for detailed usage instructions, including troubleshooting and use cases.

## Limitations
- **Complex Tables**: Tables without clear borders may need `camelot-py`.
- **Scanned PDFs**: Requires OCR (e.g., Tesseract) for non-text PDFs.
- **Custom Numbering**: Non-standard formats (e.g., `A.1.b`) may need code adjustments.

## Troubleshooting
- **Module Errors**: Run `pip install -r requirements.txt`.
- **PDF Issues**: Ensure PDFs have extractable text (test with Adobe Reader).
- **Table Problems**: Verify tables have borders; consider `camelot-py` for complex cases.

## Contributing
1. Fork the repository.
2. Create a branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push (`git push origin feature-name`).
5. Open a Pull Request.

File issues for bugs or suggestions.

## License
[MIT License](LICENSE)

