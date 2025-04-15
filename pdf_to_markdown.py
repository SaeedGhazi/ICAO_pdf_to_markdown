import fitz  # PyMuPDF
import pdfplumber
import os
import re
from pathlib import Path
import yaml

def count_number_depth(numbering):
    """Count the number of dots for heading level."""
    if not numbering:
        return 0
    return len(numbering.split(".")) if "." in numbering else 1

def is_numbering(line):
    """Detect numbering (e.g., ۴٫۳٫۲٫۱)."""
    return bool(re.match(r"^\d+\.\d+(\.\d+)*\s", line.strip()))

def is_paragraph_start(line, prev_line):
    """Detect paragraph start."""
    line = line.strip()
    prev_line = prev_line.strip()
    if is_numbering(line):
        return True
    if line and not prev_line and re.match(r"^[^\d\s]", line):
        return True
    return False

def is_paragraph_end(line, next_line):
    """Detect paragraph end: period followed by uppercase or numbering."""
    line = line.strip()
    next_line = next_line.strip() if next_line else ""
    if line.endswith("."):
        if not next_line or (next_line and (next_line[0].isupper() or is_numbering(next_line))):
            return True
    return False

def clean_text(text):
    """Clean text from extra newlines and spaces."""
    lines = text.split("\n")
    cleaned_lines = []
    current_line = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        current_line.append(line)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        
        if is_paragraph_end(line, next_line):
            cleaned_lines.append(" ".join(current_line))
            current_line = []
    
    if current_line:
        cleaned_lines.append(" ".join(current_line))
    
    return "\n\n".join(cleaned_lines)

def clean_cell_content(cell):
    """Clean cell content for Markdown table."""
    if cell is None:
        return ""
    # Remove newlines and escape pipes
    cell = str(cell).replace("\n", " ").replace("|", "\\|").strip()
    return cell

def table_to_markdown(table):
    """Convert a table (list of lists) to Markdown format."""
    if not table or not table[0]:
        return ""
    
    # Assume first row is header; if not, create default headers
    headers = table[0]
    if all(cell is None or not str(cell).strip() for cell in headers):
        headers = [f"Column {i+1}" for i in range(len(headers))]
    
    # Clean all cells
    cleaned_table = [[clean_cell_content(cell) for cell in row] for row in table]
    
    # Create Markdown table
    markdown_lines = []
    markdown_lines.append("| " + " | ".join(cleaned_table[0]) + " |")
    markdown_lines.append("| " + " | ".join(["-" * len(h) for h in cleaned_table[0]]) + " |")
    for row in cleaned_table[1:]:
        markdown_lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(markdown_lines)

def extract_toc(pdf_path):
    """Extract table of contents (TOC)."""
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()
        if toc:
            return [(level, title, page) for level, title, page in toc]
        return []
    except Exception:
        return []

def get_pdf_page_count(pdf_path):
    """Calculate the number of PDF pages."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0

def generate_anchor(doc_id, numbering):
    """Generate a unique anchor for a section."""
    if not numbering:
        return ""
    # Keep dots in the numbering for anchor
    return f"{{#{doc_id}-{numbering}}}"

def process_pdf_to_markdown(pdf_path, output_dir, doc_id):
    """Convert a PDF to Markdown with TOC, tables, and page numbers."""
    toc = extract_toc(pdf_path)
    markdown_content = []
    current_paragraph = []
    current_numbering = None
    current_page = 1
    toc_index = 0

    # Short warning
    warning = "> **Note:** Page numbers refer to the PDF sequence and may differ from printed page numbers."
    markdown_content.append(warning)
    markdown_content.append("")  # Empty line

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text(layout=True)
                if not text:
                    continue
                lines = text.split("\n")
                prev_line = ""

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        table_markdown = table_to_markdown(table)
                        if table_markdown:
                            markdown_content.append(table_markdown + "\n[Page: " + str(current_page) + "]\n")

                # Check TOC
                toc_section = None
                if toc and toc_index < len(toc):
                    level, title, toc_page = toc[toc_index]
                    if page_num >= toc_page:
                        toc_section = (level, title)
                        toc_index += 1

                for i, line in enumerate(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    line_stripped = line.strip()

                    # Ignore in-text numeric references
                    if re.search(r"\b\d+\.\d+(\.\d+)*\b", line_stripped) and not is_numbering(line_stripped):
                        current_paragraph.append(line_stripped)
                        continue

                    # Start new paragraph
                    if is_paragraph_start(line_stripped, prev_line):
                        if current_paragraph:
                            paragraph_text = clean_text(" ".join(current_paragraph))
                            if paragraph_text:
                                if current_numbering:
                                    depth = count_number_depth(current_numbering)
                                    anchor = generate_anchor(doc_id, current_numbering)
                                    markdown_content.append(
                                        f"{'#' * depth} {current_numbering} {anchor}\n{paragraph_text}\n[Page: {current_page}]\n"
                                    )
                                else:
                                    markdown_content.append(f"{paragraph_text}\n[Page: {current_page}]\n")
                            current_paragraph = []

                        if is_numbering(line_stripped):
                            current_numbering = line_stripped.split(" ")[0]
                        else:
                            current_numbering = None
                        current_paragraph.append(line_stripped)

                    else:
                        current_paragraph.append(line_stripped)

                    # End paragraph
                    if is_paragraph_end(line_stripped, next_line):
                        if current_paragraph:
                            paragraph_text = clean_text(" ".join(current_paragraph))
                            if paragraph_text:
                                if current_numbering:
                                    depth = count_number_depth(current_numbering)
                                    anchor = generate_anchor(doc_id, current_numbering)
                                    markdown_content.append(
                                        f"{'#' * depth} {current_numbering} {anchor}\n{paragraph_text}\n[Page: {current_page}]\n"
                                    )
                                else:
                                    markdown_content.append(f"{paragraph_text}\n[Page: {current_page}]\n")
                            current_paragraph = []
                            current_numbering = None

                    prev_line = line_stripped

                # End of page
                if current_paragraph:
                    paragraph_text = clean_text(" ".join(current_paragraph))
                    if paragraph_text:
                        if current_numbering:
                            depth = count_number_depth(current_numbering)
                            anchor = generate_anchor(doc_id, current_numbering)
                            markdown_content.append(
                                f"{'#' * depth} {current_numbering} {anchor}\n{paragraph_text}\n[Page: {current_page}]\n"
                            )
                        else:
                            markdown_content.append(f"{paragraph_text}\n[Page: {current_page}]\n")
                    current_paragraph = []
                    current_numbering = None
                
                current_page = page_num

                # Add TOC headings
                if toc_section:
                    level, title = toc_section
                    markdown_content.insert(2, f"{'#' * level} {title}\n[Page: {current_page}]\n")

    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return [], [], pdf_path.name

    # Prepare content for combined file (with adjusted headings)
    combined_markdown_content = []
    for line in markdown_content:
        if line.startswith("#"):
            match = re.match(r"^(#+)\s(.+)$", line)
            if match:
                hashes, content = match.groups()
                new_hashes = "#" * (len(hashes) + 1)
                combined_markdown_content.append(f"{new_hashes} {content}")
            else:
                combined_markdown_content.append(line)
        else:
            combined_markdown_content.append(line)

    # Save individual Markdown file
    output_file = output_dir / f"{pdf_path.stem}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {pdf_path.name}\n\n")
        f.write("\n".join(markdown_content))

    return combined_markdown_content, markdown_content, pdf_path.name

def main():
    # Current directory
    current_dir = Path.cwd()
    output_dir = current_dir / "markdown_output"
    output_dir.mkdir(exist_ok=True)

    # Combined file
    combined_file = output_dir / "combined_output.md"
    combined_content = []

    # Find all PDFs
    pdf_files = list(current_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    # Prepare metadata and index
    metadata = {"documents": []}
    document_list = []
    for i, pdf_path in enumerate(pdf_files, 1):
        page_count = get_pdf_page_count(pdf_path)
        doc_id = f"id{i}"
        metadata["documents"].append({
            "id": doc_id,
            "title": pdf_path.name,
            "pages": page_count
        })
        document_list.append(f"- {i}. {doc_id}: {pdf_path.name} [{page_count} Pages]")

    # Add YAML metadata
    combined_content.append("---")
    combined_content.append(yaml.dump(metadata, allow_unicode=True, sort_keys=False))
    combined_content.append("---")
    combined_content.append("# Documents Combined:")
    combined_content.append("")
    combined_content.extend(document_list)
    combined_content.append("")

    # Process each PDF
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"Processing: {pdf_path.name}")
        doc_id = f"id{i}"
        combined_markdown_content, markdown_content, pdf_name = process_pdf_to_markdown(pdf_path, output_dir, doc_id=doc_id)
        
        # Add to combined file
        combined_content.append(f"## {i}. {doc_id}: {pdf_name}")
        combined_content.append("--- Start ---")
        combined_content.extend(combined_markdown_content)
        combined_content.append("--- End ---")

    # Save combined file
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))

    print(f"Markdown files saved in {output_dir}")
    print(f"Combined file: {combined_file}")

if __name__ == "__main__":
    main()
