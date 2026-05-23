#!/usr/bin/env python3
"""Extract text from all PDFs and save to text files for analysis."""

import os
import pdfplumber
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ENGLISH_DIR = Path(r"D:\Academic-RAG\00_manifest\english_pdf_copies")
TEXT_DIR = Path(r"D:\Academic-RAG\06_logs\extracted_texts")
TEXT_DIR.mkdir(exist_ok=True)

def extract_text(pdf_path):
    """Extract text from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:20]):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def process_one(pdf_file):
    """Process a single PDF file."""
    paper_id = pdf_file.stem.replace('_unidentified', '')
    out_file = TEXT_DIR / f"{paper_id}.txt"

    if out_file.exists():
        return paper_id, "skipped"

    text = extract_text(pdf_file)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(text)

    return paper_id, f"{len(text)} chars"

def main():
    pdf_files = sorted(ENGLISH_DIR.glob("*.pdf"))
    print(f"Processing {len(pdf_files)} PDFs...")

    results = {"success": 0, "error": 0, "skipped": 0}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_one, f): f for f in pdf_files}
        for i, future in enumerate(as_completed(futures)):
            paper_id, status = future.result()
            if "chars" in status:
                results["success"] += 1
            elif status == "skipped":
                results["skipped"] += 1
            else:
                results["error"] += 1

            if (i + 1) % 50 == 0:
                print(f"  Processed {i+1}/{len(pdf_files)}...")

    print(f"\nDone: {results['success']} extracted, {results['skipped']} skipped, {results['error']} errors")

if __name__ == "__main__":
    main()
