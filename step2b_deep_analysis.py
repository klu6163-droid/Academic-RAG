#!/usr/bin/env python3
"""Deep analysis: extract full text from PDF for manual review."""

import pdfplumber
import json
import sys
from pathlib import Path

ENGLISH_DIR = Path(r"D:\Academic-RAG\00_manifest\english_pdf_copies")

def extract_full_text(pdf_path, max_pages=20):
    """Extract text from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {i+1} ---\n{page_text}"
            return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    paper_id = sys.argv[1] if len(sys.argv) > 1 else "P001"
    pdf_path = ENGLISH_DIR / f"{paper_id}_unidentified.pdf"

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    text = extract_full_text(pdf_path, max_pages=20)
    # Write to file to avoid encoding issues
    out_path = Path(r"D:\Academic-RAG\06_logs") / f"{paper_id}_text.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text[:20000])
    print(f"Text saved to {out_path} ({len(text)} chars)")

if __name__ == "__main__":
    main()
