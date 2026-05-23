#!/usr/bin/env python3
"""Import new PDFs into the literature RAG corpus.

The script copies PDFs to ASCII-safe filenames, extracts text, appends basic
metadata, and optionally adds low-confidence text chunks to the RAG evidence
table so the new papers become searchable immediately.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

import pdfplumber


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = PROJECT_ROOT / "00_manifest"
PDF_OUT_DIR = MANIFEST_DIR / "english_pdf_copies"
TEXT_OUT_DIR = PROJECT_ROOT / "06_logs" / "extracted_texts"
FINAL_DIR = PROJECT_ROOT / "data" / "analysis" / "final"
MAPPING_CSV = MANIFEST_DIR / "file_path_mapping.csv"
METADATA_CSV = MANIFEST_DIR / "literature_metadata.csv"
EVIDENCE_CSV = FINAL_DIR / "global_evidence_table_frontend.csv"


def sanitize_stem(name: str, max_len: int = 80) -> str:
    """Return an ASCII-only filename stem with CJK and special chars removed."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_text)
    ascii_text = re.sub(r"_+", "_", ascii_text).strip("._-")
    return (ascii_text[:max_len].strip("._-") or "paper")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def append_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def next_paper_number(rows: list[dict[str, str]]) -> int:
    max_id = 0
    for row in rows:
        paper_id = row.get("paper_id", "")
        m = re.fullmatch(r"P(\d{3,})", paper_id)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id + 1


def extract_text(pdf_path: Path, max_pages: int) -> tuple[str, str]:
    try:
        parts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:max_pages]:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    parts.append(page_text)
        text = "\n\n".join(parts)
        text = text.replace("\x00", "")
        text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]+", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip(), ""
    except Exception as exc:
        return "", f"{type(exc).__name__}: {exc}"


def extract_title(text: str, fallback: str) -> str:
    for raw in text.splitlines()[:40]:
        line = re.sub(r"\s+", " ", raw).strip()
        if 20 <= len(line) <= 220 and not re.search(r"^(doi|http|www\.|abstract\b|keywords\b)", line, re.I):
            return line
    return fallback


def extract_year(text: str) -> str:
    years = re.findall(r"\b(19[9]\d|20[0-3]\d)\b", text[:6000])
    return years[0] if years else ""


def chunk_text(text: str, chunk_chars: int, overlap_chars: int) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_chars, len(cleaned))
        chunk = cleaned[start:end].strip()
        if len(chunk) >= 120:
            chunks.append(chunk)
        if end == len(cleaned):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Import new PDFs into Academic-RAG.")
    parser.add_argument("source", help="PDF file or directory containing PDFs")
    parser.add_argument("--max-pages", type=int, default=30, help="pages to extract per PDF")
    parser.add_argument("--chunk-chars", type=int, default=900, help="characters per evidence chunk")
    parser.add_argument("--overlap-chars", type=int, default=120, help="chunk overlap")
    parser.add_argument("--no-evidence", action="store_true", help="copy/extract only; do not append RAG evidence")
    parser.add_argument("--category", default="New_Unclassified", help="category for generated evidence rows")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if source.is_file() and source.suffix.lower() == ".pdf":
        pdfs = [source]
    elif source.is_dir():
        pdfs = sorted(p for p in source.rglob("*.pdf") if p.is_file())
    else:
        raise SystemExit(f"PDF source not found: {source}")

    PDF_OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_OUT_DIR.mkdir(parents=True, exist_ok=True)

    mapping_fields, mapping_rows = read_csv(MAPPING_CSV)
    metadata_fields, metadata_rows = read_csv(METADATA_CSV)
    evidence_fields, _ = read_csv(EVIDENCE_CSV)

    if not mapping_fields or not metadata_fields:
        raise SystemExit("Missing manifest CSV headers. Expected files under 00_manifest/.")
    if not args.no_evidence and not evidence_fields:
        raise SystemExit("Missing evidence CSV headers. Expected data/analysis/final/global_evidence_table_frontend.csv.")

    existing_sources = {row.get("original_file_path", "") for row in mapping_rows}
    next_num = next_paper_number(mapping_rows + metadata_rows)

    new_mapping: list[dict[str, str]] = []
    new_metadata: list[dict[str, str]] = []
    new_evidence: list[dict[str, str]] = []

    for pdf in pdfs:
        original_path = str(pdf)
        if original_path in existing_sources:
            print(f"SKIP existing path: {pdf}")
            continue

        paper_id = f"P{next_num:03d}"
        next_num += 1

        safe_name = f"{paper_id}_{sanitize_stem(pdf.stem)}.pdf"
        safe_path = PDF_OUT_DIR / safe_name
        shutil.copy2(pdf, safe_path)

        text, error = extract_text(safe_path, args.max_pages)
        text_path = TEXT_OUT_DIR / f"{paper_id}.txt"
        text_path.write_text(text, encoding="utf-8")

        title = extract_title(text, pdf.stem)
        year = extract_year(text)
        modified = datetime.fromtimestamp(pdf.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        status = "readable" if text and not error else "error"

        new_mapping.append({
            "paper_id": paper_id,
            "original_file_path": original_path,
            "original_file_name": pdf.name,
            "original_folder": str(pdf.parent),
            "english_safe_file_path": str(safe_path),
            "english_safe_file_name": safe_name,
            "file_size": str(pdf.stat().st_size),
            "modified_time": modified,
            "readable_status": status,
            "detected_title": title,
            "detected_year": year,
            "detected_doi": "",
            "notes": error,
        })

        new_metadata.append({
            "paper_id": paper_id,
            "english_safe_file_name": safe_name,
            "original_file_name": pdf.name,
            "title": title,
            "authors": "",
            "journal": "",
            "year": year,
            "DOI": "",
            "keywords": "",
            "research_field": "",
            "material_system": "",
            "core_topic": "",
            "preliminary_category": args.category,
            "readable_status": status,
            "notes": "auto_ingested; ascii_safe_filename" if not error else f"auto_ingested; {error}",
        })

        if not args.no_evidence and text:
            for i, chunk in enumerate(chunk_text(text, args.chunk_chars, args.overlap_chars), 1):
                new_evidence.append({
                    "paper_id": paper_id,
                    "title": title,
                    "file_name": safe_name,
                    "category": args.category,
                    "year": year,
                    "priority": "new",
                    "extraction_quality": "auto_text",
                    "evidence_type": "pdf_text_chunk",
                    "claim_type": "general",
                    "evidence_text": chunk,
                    "figure_table_source": "",
                    "page_est": "",
                    "keyword": "auto_ingested_pdf_text",
                    "confidence": "low",
                    "relevance": "unreviewed_new_pdf",
                    "ml_feature_candidate": "FALSE",
                    "needs_manual_check": "TRUE",
                    "title_needs_cleanup": "FALSE",
                    "original_title": title,
                    "display_title": title,
                    "title_uncertain": "False",
                })

        print(f"IMPORTED {paper_id}: {safe_name} ({len(text):,} chars, status={status})")

    append_csv(MAPPING_CSV, mapping_fields, new_mapping)
    append_csv(METADATA_CSV, metadata_fields, new_metadata)
    if not args.no_evidence:
        append_csv(EVIDENCE_CSV, evidence_fields, new_evidence)

    print("")
    print(f"PDFs imported: {len(new_mapping)}")
    print(f"Evidence rows added: {len(new_evidence)}")
    print("Next steps:")
    print("  python convert_to_json.py")
    print("  powershell -ExecutionPolicy Bypass -File scripts\\rebuild_rag_index.ps1")
    print("  powershell -ExecutionPolicy Bypass -File scripts\\stop_backend.ps1")
    print("  powershell -ExecutionPolicy Bypass -File scripts\\start_backend.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
