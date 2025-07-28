# 📄 Adobe Hackathon 2025 – Round 1A: PDF Title & Heading Extractor
**_Made by: Aditya Mondal and Abhishek Sen Sarma_**

## 🧠 Objective

Extract full document title and hierarchical headings (H1, H2, H3) from PDF files and return them in structured JSON format.

## 🚀 Features

- Combines multi-line titles from the top of the first page.
- Detects heading levels by font size and position.
- Skips headers, footers, and page numbers.
- Maps heading page numbers to logical order.
- Outputs `title` and `outline` JSON file for each PDF.

## 📦 Output Format

```json
{
  "title": "Overview Foundation Level Extensions",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "1.1 Scope",
      "page": 2
    }
  ]
}
```

## 🖥️ How to Run

1. Put PDFs in `input/` directory.
2. Run the script:

```bash
python extractor.py
```

3. Output JSONs appear in `output/`.

## 📁 Folder Structure

```
.
├── extractor.py
├── input/
│   └── *.pdf
└── output/
    └── *.json
```
