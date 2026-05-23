#!/usr/bin/env python3
"""Phase 1: Extract metadata from all PDFs using pdfplumber."""

import os
import csv
import json
import re
from pathlib import Path
from datetime import datetime

import pdfplumber

ENGLISH_DIR = Path(r"D:\Academic-RAG\00_manifest\english_pdf_copies")
MANIFEST_DIR = Path(r"D:\Academic-RAG\00_manifest")
MAPPING_FILE = MANIFEST_DIR / "file_path_mapping.csv"
LOGS_DIR = Path(r"D:\Academic-RAG\06_logs")

def extract_text_from_pdf(pdf_path, max_pages=3):
    """Extract text from first N pages of a PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def extract_doi(text):
    """Try to find DOI in text."""
    patterns = [
        r'(?:DOI|doi)[:\s]*(10\.\d{4,}/[^\s]+)',
        r'(10\.\d{4,}/[^\s]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            doi = m.group(1).rstrip('.')
            return doi
    return ""

def extract_year(text):
    """Try to find publication year."""
    # Look for common year patterns - only match 4-digit years
    patterns = [
        r'(?:©|Copyright|Published)\s*(?:in\s+)?(\d{4})',
        r'(?:Received|Accepted|Published)\s*[:\s]+\d{1,2}\s+\w+\s+(\d{4})',
        r'(\d{4})\s*(?:WILEY|Elsevier|Springer|Nature|ACS|Royal Society)',
        r'(?:Volume|Vol\.?)\s*\d+.*?(\d{4})',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            year = m.group(1)
            try:
                y = int(year)
                if 1990 <= y <= 2030:
                    return str(y)
            except ValueError:
                continue
    # Fallback: find any 4-digit year (strict word boundary)
    years = re.findall(r'\b(19[9]\d|20[0-2]\d)\b', text)
    if years:
        return years[0]
    return ""

def extract_title_from_text(text):
    """Try to extract title from first page text."""
    lines = text.split('\n')
    # Title is usually one of the first non-empty lines
    # Skip very short lines (likely headers/journal names)
    candidates = []
    for line in lines[:15]:
        line = line.strip()
        if len(line) > 10 and not line.startswith('http') and not line.startswith('DOI'):
            # Skip lines that look like journal headers
            if not re.match(r'^(Article|Communication|Research Article|Full Paper)', line):
                candidates.append(line)
    if candidates:
        # Return the first substantial line as likely title
        return candidates[0][:200]
    return ""

def extract_authors(text):
    """Try to extract authors from first page."""
    lines = text.split('\n')
    for i, line in enumerate(lines[:10]):
        # Authors often contain commas, superscript numbers, and email
        if '@' in line and (',' in line or '†' in line or '‡' in line):
            return line.strip()[:300]
    # Look for lines with many commas (author lists)
    for line in lines[:10]:
        if line.count(',') >= 2 and len(line) > 20:
            return line.strip()[:300]
    return ""

def extract_journal(text):
    """Try to identify journal name."""
    journals = {
        'Advanced Materials': 'Advanced Materials',
        'Adv. Mater.': 'Advanced Materials',
        'Advanced Functional Materials': 'Advanced Functional Materials',
        'Adv. Funct. Mater.': 'Advanced Functional Materials',
        'Nature': 'Nature',
        'Science': 'Science',
        'Macromolecules': 'Macromolecules',
        'Angewandte Chemie': 'Angewandte Chemie International Edition',
        'Angew. Chem.': 'Angewandte Chemie International Edition',
        'ACS Macro Letters': 'ACS Macro Letters',
        'Macromol. Rapid Commun.': 'Macromolecular Rapid Communications',
        'Polymer': 'Polymer',
        'Chemistry of Materials': 'Chemistry of Materials',
        'Chem. Mater.': 'Chemistry of Materials',
        'Journal of the American Chemical Society': 'Journal of the American Chemical Society',
        'J. Am. Chem. Soc.': 'Journal of the American Chemical Society',
        'Nature Materials': 'Nature Materials',
        'Nature Chemistry': 'Nature Chemistry',
        'Nature Communications': 'Nature Communications',
        'Small': 'Small',
        'Nano Letters': 'Nano Letters',
        'ACS Applied': 'ACS Applied Materials & Interfaces',
        'Physical Review': 'Physical Review',
        'Journal of Polymer Science': 'Journal of Polymer Science',
        'Soft Matter': 'Soft Matter',
        'J. Mater. Chem.': 'Journal of Materials Chemistry',
        'Cell Reports Physical Science': 'Cell Reports Physical Science',
        'Matter': 'Matter',
        'Joule': 'Joule',
        'Chemical Reviews': 'Chemical Reviews',
        'Chem. Rev.': 'Chemical Reviews',
        'Chemical Society Reviews': 'Chemical Society Reviews',
        'Chem. Soc. Rev.': 'Chemical Society Reviews',
        'Accounts of Chemical Research': 'Accounts of Chemical Research',
        'ACS Nano': 'ACS Nano',
        'Science Advances': 'Science Advances',
        'NPG Asia Materials': 'NPG Asia Materials',
        'Advanced Science': 'Advanced Science',
        'Adv. Sci.': 'Advanced Science',
        'Small Science': 'Small Science',
        'Advanced Energy Materials': 'Advanced Energy Materials',
        'Adv. Energy Mater.': 'Advanced Energy Materials',
        'Nano Energy': 'Nano Energy',
        'Energy & Environmental Science': 'Energy & Environmental Science',
        'ACS Energy Letters': 'ACS Energy Letters',
        'Macromolecular': 'Macromolecular',
        'Polymer Chemistry': 'Polymer Chemistry',
        'Polym. Chem.': 'Polymer Chemistry',
        'European Polymer Journal': 'European Polymer Journal',
        'Composites Science and Technology': 'Composites Science and Technology',
        'Chemical Engineering Journal': 'Chemical Engineering Journal',
        'Applied Surface Science': 'Applied Surface Science',
        'Journal of Physical Chemistry': 'Journal of Physical Chemistry',
        'J. Phys. Chem.': 'Journal of Physical Chemistry',
        'Physical Chemistry Chemical Physics': 'Physical Chemistry Chemical Physics',
        'Chem. Phys.': 'Physical Chemistry Chemical Physics',
        'Extreme Mechanics Letters': 'Extreme Mechanics Letters',
        'International Journal of Solids and Structures': 'International Journal of Solids and Structures',
        'Mechanics of Materials': 'Mechanics of Materials',
        'Computational Materials Science': 'Computational Materials Science',
        'The Journal of Chemical Physics': 'The Journal of Chemical Physics',
        'J. Chem. Phys.': 'The Journal of Chemical Physics',
        'Chinese Journal of Polymer Science': 'Chinese Journal of Polymer Science',
        'Science China': 'Science China',
        'Chinese Chemical Letters': 'Chinese Chemical Letters',
        'Giant': 'Giant',
        'Supramolecular': 'Supramolecular Chemistry',
        'Materials Horizons': 'Materials Horizons',
        'Mater. Horiz.': 'Materials Horizons',
        'Materials Today': 'Materials Today',
        'Mater. Today': 'Materials Today',
        'Nanoscale': 'Nanoscale',
        'Biomacromolecules': 'Biomacromolecules',
        'ACS Sustainable Chemistry & Engineering': 'ACS Sustainable Chemistry & Engineering',
        'Green Chemistry': 'Green Chemistry',
        'Green Chem.': 'Green Chemistry',
        'iScience': 'iScience',
        'PNAS': 'Proceedings of the National Academy of Sciences',
        'PNAS': 'Proceedings of the National Academy of Sciences',
    }
    text_upper = text[:2000]
    for key, journal in journals.items():
        if key.lower() in text_upper.lower():
            return journal
    return ""

def is_supplementary(filename):
    """Check if file is supplementary material."""
    indicators = ['suppmat', 'supplement', 'supporting', 'si_001', 'mmc', 'sup-0001', 'sup-0002']
    fname_lower = filename.lower()
    return any(ind in fname_lower for ind in indicators)

def main():
    # Load mapping
    records = []
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Processing {len(records)} PDFs for metadata extraction...")

    metadata_list = []
    errors = []

    for i, rec in enumerate(records):
        paper_id = rec['paper_id']
        pdf_path = Path(rec['english_safe_file_path'])
        orig_name = rec['original_file_name']

        if i % 50 == 0:
            print(f"  Processing {i}/{len(records)}...")

        # Check if supplementary
        is_supp = is_supplementary(orig_name) or is_supplementary(pdf_path.name)

        # Extract text
        text = extract_text_from_pdf(pdf_path, max_pages=3)

        if text.startswith("ERROR"):
            errors.append(f"{paper_id}: {orig_name} -> {text}")
            meta = {
                'paper_id': paper_id,
                'english_safe_file_name': pdf_path.name,
                'original_file_name': orig_name,
                'title': '',
                'authors': '',
                'journal': '',
                'year': '',
                'DOI': '',
                'keywords': '',
                'research_field': '',
                'material_system': '',
                'core_topic': '',
                'preliminary_category': 'supplementary' if is_supp else 'unreadable',
                'readable_status': 'error',
                'notes': text,
            }
        else:
            title = extract_title_from_text(text)
            authors = extract_authors(text)
            journal = extract_journal(text)
            year = extract_year(text)
            doi = extract_doi(text)

            # Try to extract title from original filename if not found
            if not title and not is_supp:
                title = orig_name.replace('.pdf', '')

            # Category based on folder and content
            category = categorize_paper(orig_name, rec.get('original_folder', ''), text)

            meta = {
                'paper_id': paper_id,
                'english_safe_file_name': pdf_path.name,
                'original_file_name': orig_name,
                'title': title[:200] if title else '',
                'authors': authors[:300] if authors else '',
                'journal': journal,
                'year': year,
                'DOI': doi,
                'keywords': '',
                'research_field': '',
                'material_system': '',
                'core_topic': '',
                'preliminary_category': 'supplementary' if is_supp else category,
                'readable_status': 'readable',
                'notes': 'supplementary_material' if is_supp else '',
            }

        metadata_list.append(meta)

    # Write metadata CSV
    fieldnames = ['paper_id', 'english_safe_file_name', 'original_file_name', 'title', 'authors',
                  'journal', 'year', 'DOI', 'keywords', 'research_field', 'material_system',
                  'core_topic', 'preliminary_category', 'readable_status', 'notes']

    with open(MANIFEST_DIR / "literature_metadata.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in metadata_list:
            writer.writerow({k: m.get(k, '') for k in fieldnames})

    # Write JSON for frontend
    with open(Path(r"D:\Academic-RAG\07_frontend\src\data") / "papers.json", 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    # Write errors
    with open(LOGS_DIR / "file_reading_errors.md", 'w', encoding='utf-8') as f:
        f.write("# File Reading Errors\n\n")
        for e in errors:
            f.write(f"- {e}\n")

    # Print summary
    print(f"\nMetadata extraction complete!")
    print(f"Total papers: {len(metadata_list)}")
    readable = sum(1 for m in metadata_list if m['readable_status'] == 'readable')
    supplementary = sum(1 for m in metadata_list if m['preliminary_category'] == 'supplementary')
    print(f"Readable: {readable}")
    print(f"Supplementary materials: {supplementary}")
    print(f"Errors: {len(errors)}")

    # Category distribution
    categories = {}
    for m in metadata_list:
        cat = m['preliminary_category']
        categories[cat] = categories.get(cat, 0) + 1
    print("\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Year distribution
    years = {}
    for m in metadata_list:
        y = m['year']
        if y:
            years[y] = years.get(y, 0) + 1
    print("\nYear distribution:")
    for y, count in sorted(years.items()):
        print(f"  {y}: {count}")

    # Journal distribution
    journals = {}
    for m in metadata_list:
        j = m['journal']
        if j:
            journals[j] = journals.get(j, 0) + 1
    print("\nJournal distribution:")
    for j, count in sorted(journals.items(), key=lambda x: -x[1])[:20]:
        print(f"  {j}: {count}")

def categorize_paper(filename, folder, text):
    """Categorize paper based on filename, folder, and content."""
    fn = filename.lower()
    fd = folder.lower() if folder else ''
    txt = text[:3000].lower()

    # Check folder-based categories
    if '压电' in fd or 'piezoelectric' in fn:
        return 'piezoelectric'
    if '离子凝胶' in fd or 'ionogel' in fn:
        return 'ionogel'
    if '流变' in fd or 'rheolog' in fn:
        return 'rheology'
    if '结晶' in fd or 'crystalliz' in fn or 'crystal' in fn:
        return 'crystallization'
    if '形状记忆' in fd or 'shape memory' in fn:
        return 'shape_memory'
    if '机器学习' in fd or 'machine learning' in fn:
        return 'machine_learning'
    if '计算化学' in fd or 'molecular dynamics' in fn or 'simulation' in fn:
        return 'computational'
    if '离聚物' in fd or 'ionomer' in fn:
        return 'ionomer'
    if '合成策略' in fd:
        return 'synthesis'
    if '弹性体' in fd or 'elastomer' in fn:
        return 'elastomer'
    if '凝胶' in fd or 'gel' in fn or 'hydrogel' in fn:
        return 'gel'
    if '离子液体' in fd or 'ionic liquid' in fn:
        return 'ionic_liquid'
    if '摩擦纳米' in fd or 'triboelectric' in fn or 'nanogenerator' in fn:
        return 'triboelectric'
    if '迈克尔' in fd or 'michael' in fn:
        return 'michael_addition'
    if '荧光' in fd or 'fluorescen' in fn or 'luminescen' in fn:
        return 'fluorescence'
    if '生物' in fd or 'biocompat' in fn or 'bio' in fn:
        return 'biocompatibility'
    if '高分子物理' in fd:
        return 'polymer_physics'
    if '生命物理' in fd:
        return 'biophysics'
    if '温度编程' in fd or 'adaptive network' in fn:
        return 'adaptive_network'
    if '脂肪族荧光' in fd:
        return 'fluorescence'
    if '胶' in fd or 'adhesive' in fn or 'adhesion' in fn:
        return 'adhesion'

    # Content-based
    if 'polyurethane' in txt or '聚氨酯' in txt:
        return 'polyurethane'
    if 'elastomer' in txt or '弹性体' in txt:
        return 'elastomer'
    if 'hydrogel' in txt or '水凝胶' in txt:
        return 'hydrogel'
    if 'ionogel' in txt or '离子凝胶' in txt:
        return 'ionogel'
    if 'piezoelectric' in txt or '压电' in txt:
        return 'piezoelectric'
    if 'self-heal' in txt or '自修复' in txt:
        return 'self_healing'
    if 'shape memory' in txt or '形状记忆' in txt:
        return 'shape_memory'
    if 'crystal' in txt or '结晶' in txt:
        return 'crystallization'
    if 'rheolog' in txt or '流变' in txt:
        return 'rheology'
    if 'ionic liquid' in txt or '离子液体' in txt:
        return 'ionic_liquid'
    if 'machine learning' in txt or '机器学习' in txt:
        return 'machine_learning'

    return 'other'

if __name__ == "__main__":
    main()
