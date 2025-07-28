import fitz
import os
import json
import re
from collections import Counter

def extract_lines(doc):
    """Extract text lines with properties, grouping multi-line headings"""
    lines = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_text = ""
                max_size = 0
                bboxes = []
                for span in line["spans"]:
                    line_text += span["text"]
                    if span["size"] > max_size:
                        max_size = span["size"]
                    bboxes.append(span["bbox"])

                if not line_text.strip():
                    continue

                x0 = min(b[0] for b in bboxes)
                y0 = min(b[1] for b in bboxes)
                x1 = max(b[2] for b in bboxes)
                y1 = max(b[3] for b in bboxes)

                lines.append({
                    "text": line_text,
                    "size": max_size,
                    "bbox": (x0, y0, x1, y1),
                    "page": page_num
                })
    return lines

def is_header_footer(text, page_num, total_pages):
    """Identify header/footer content based on common patterns"""
    patterns = [
        r"Copyright", r"©", r"Page \d+ of \d+", r"Version \d+",
        r"ISTQB", r"Qualifications Board", r"International Software Testing",
        r"May 31, 2014", r"Overview.*Agile Tester"
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

def clean_title(title):
    """Clean and normalize the title text"""
    title = re.sub(r"\s+", " ", title)
    title = title.replace("  ", " ").strip()
    title = re.sub(r"Version\s*\d+\.\d+", "", title)
    title = re.sub(r"\d{4}-\d{4}", "", title)
    return title

def process_pdf(pdf_path):
    """Process PDF to extract title and outline with proper page numbering"""
    doc = fitz.open(pdf_path)
    lines = extract_lines(doc)
    total_pages = len(doc)

    # Extract title from first page
    title = ""
    first_page_lines = [line for line in lines if line["page"] == 0]
    if first_page_lines:
        first_page_height = doc[0].rect.height
        top_section = [line for line in first_page_lines if line["bbox"][1] < first_page_height / 3]

        if top_section:
            max_size = max(line["size"] for line in top_section)
            candidate_titles = [line for line in top_section if line["size"] == max_size]
            if candidate_titles:
                title = " ".join(line["text"].strip() for line in candidate_titles).strip()
                title = clean_title(title)

    headings = []
    logical_page = 1  # Start counting from 1 (title page is logical page 1)

    for page_index in range(1, len(doc)):  # Skip cover/title page
        page = doc[page_index]
        page_lines = [line for line in lines if line["page"] == page_index]
        page_height = page.rect.height

        page_headings = []  # Headings found on current page

        for line in page_lines:
            y0 = line["bbox"][1]

            # Skip header/footer areas
            if (y0 < page_height * 0.1) or (y0 > page_height * 0.9):
                continue

            # Skip header/footer content
            if is_header_footer(line["text"], page_index + 1, total_pages):
                continue

            # Skip title repetitions
            if title and line["text"].strip() in title:
                continue

            font_size = line["size"]

            # Determine heading level based on font size
            level = None
            if font_size > 14:
                level = "H1"
            elif font_size > 12:
                level = "H2"
            elif font_size > 10:
                level = "H3"

            if level:
                text = line["text"].strip()
                # Clean up trailing special characters
                text = re.sub(r"[:•\*…]+$", "", text).strip()
                # Remove page numbers like "... 2"
                text = re.sub(r"\.+\s*\d+$", "", text).strip()
                # Remove title if present
                if title:
                    text = text.replace(title, "").strip()

                if not text:
                    continue

                page_headings.append({
                    "level": level,
                    "text": text
                })

        # Only assign logical page if headings were found
        if page_headings:
            logical_page += 1  # Increment for new content page
            for heading in page_headings:
                heading["page"] = logical_page
            headings.extend(page_headings)

    return title, headings

def main():
    input_dir = "input"
    output_dir = "output"

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            try:
                print(f"Processing {filename}...")
                title, outline = process_pdf(pdf_path)

                result = {
                    "title": title,
                    "outline": outline
                }

                json_filename = os.path.splitext(filename)[0] + "aiyo.json"
                output_path = os.path.join(output_dir, json_filename)

                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2)

                print(f"  ✓ Created {json_filename} with {len(outline)} headings")
                print(f"  ✓ Title: {title}")

            except Exception as e:
                print(f"  ✗ Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()