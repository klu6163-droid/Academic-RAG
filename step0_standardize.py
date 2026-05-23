#!/usr/bin/env python3
"""Step 0: File path standardization - scan, copy, and map all PDFs."""

import os
import csv
import json
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent
PAPER_DIR = Path(os.environ.get("ACADEMIC_RAG_PAPER_DIR", PROJECT_DIR / "00_manifest" / "english_pdf_copies"))
MANIFEST_DIR = PROJECT_DIR / "00_manifest"
ENGLISH_DIR = MANIFEST_DIR / "english_pdf_copies"

def scan_pdfs():
    """Recursively find all PDF files."""
    pdfs = []
    for root, dirs, files in os.walk(PAPER_DIR):
        for f in files:
            if f.lower().endswith('.pdf'):
                full_path = Path(root) / f
                pdfs.append(full_path)
    pdfs.sort(key=lambda p: str(p))
    return pdfs

def get_file_info(filepath):
    """Get file metadata."""
    stat = filepath.stat()
    return {
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'is_pdf': filepath.suffix.lower() == '.pdf',
        'readable': os.access(filepath, os.R_OK),
    }

def is_english_safe(name):
    """Check if filename contains only ASCII-safe characters."""
    try:
        name.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def main():
    ENGLISH_DIR.mkdir(parents=True, exist_ok=True)

    print("Scanning PDF files...")
    pdfs = scan_pdfs()
    print(f"Found {len(pdfs)} PDF files.")

    # Build manifest
    records = []
    for i, pdf_path in enumerate(pdfs):
        info = get_file_info(pdf_path)
        rel_path = pdf_path.relative_to(PAPER_DIR)
        paper_id = f"P{i+1:03d}"

        # Copy to English-safe directory
        safe_name = f"{paper_id}_unidentified.pdf"
        dest = ENGLISH_DIR / safe_name
        try:
            shutil.copy2(pdf_path, dest)
            copy_status = "success"
        except Exception as e:
            copy_status = f"error: {e}"

        records.append({
            'paper_id': paper_id,
            'original_file_path': str(pdf_path),
            'original_file_name': pdf_path.name,
            'original_folder': str(pdf_path.parent),
            'relative_path': str(rel_path),
            'english_safe_file_path': str(dest),
            'english_safe_file_name': safe_name,
            'file_size': info['size'],
            'modified_time': info['modified'],
            'is_pdf': info['is_pdf'],
            'readable': info['readable'],
            'copy_status': copy_status,
            'is_english_original': is_english_safe(pdf_path.name),
        })

    # Write original_file_paths.md
    with open(MANIFEST_DIR / "original_file_paths.md", 'w', encoding='utf-8') as f:
        f.write("# Original File Paths Manifest\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total PDF files found: {len(records)}\n\n")
        f.write("## File List\n\n")
        for r in records:
            f.write(f"### {r['paper_id']}: {r['original_file_name']}\n")
            f.write(f"- **Path**: `{r['original_file_path']}`\n")
            f.write(f"- **Folder**: `{r['original_folder']}`\n")
            f.write(f"- **Size**: {r['file_size']:,} bytes\n")
            f.write(f"- **Modified**: {r['modified_time']}\n")
            f.write(f"- **Readable**: {r['readable']}\n")
            f.write(f"- **Copy Status**: {r['copy_status']}\n")
            f.write(f"- **English Safe Name**: `{r['english_safe_file_name']}`\n\n")

    # Write original_file_paths.csv
    with open(MANIFEST_DIR / "original_file_paths.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'paper_id', 'original_file_path', 'original_file_name', 'original_folder',
            'relative_path', 'file_size', 'modified_time', 'is_pdf', 'readable',
            'copy_status', 'is_english_original'
        ])
        writer.writeheader()
        for r in records:
            writer.writerow({k: r[k] for k in writer.fieldnames})

    # Write file_path_mapping.csv
    with open(MANIFEST_DIR / "file_path_mapping.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'paper_id', 'original_file_path', 'original_file_name', 'original_folder',
            'english_safe_file_path', 'english_safe_file_name', 'file_size',
            'modified_time', 'readable_status', 'detected_title', 'detected_year',
            'detected_doi', 'notes'
        ])
        writer.writeheader()
        for r in records:
            writer.writerow({
                'paper_id': r['paper_id'],
                'original_file_path': r['original_file_path'],
                'original_file_name': r['original_file_name'],
                'original_folder': r['original_folder'],
                'english_safe_file_path': r['english_safe_file_path'],
                'english_safe_file_name': r['english_safe_file_name'],
                'file_size': r['file_size'],
                'modified_time': r['modified_time'],
                'readable_status': 'readable' if r['readable'] else 'unreadable',
                'detected_title': '',
                'detected_year': '',
                'detected_doi': '',
                'notes': f"Copy: {r['copy_status']}",
            })

    # Write JSON for frontend
    with open(PROJECT_DIR / "07_frontend" / "src" / "data" / "papers_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(records)} files processed.")
    print(f"Files copied to: {ENGLISH_DIR}")

    # Summary
    success = sum(1 for r in records if r['copy_status'] == 'success')
    errors = sum(1 for r in records if r['copy_status'] != 'success')
    print(f"Copy success: {success}, errors: {errors}")

    # List subfolders
    folders = set(r['original_folder'] for r in records)
    print(f"\nSubfolders found: {len(folders)}")
    for f in sorted(folders):
        count = sum(1 for r in records if r['original_folder'] == f)
        print(f"  {f}: {count} files")

if __name__ == "__main__":
    main()
