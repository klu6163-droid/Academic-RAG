#!/usr/bin/env python3
"""Phase 2: Deep analysis of each PDF - extract text and generate reports."""

import os
import csv
import json
import re
from pathlib import Path
from datetime import datetime
import pdfplumber

PROJECT_DIR = Path(r"D:\Academic-RAG")
ENGLISH_DIR = PROJECT_DIR / "00_manifest" / "english_pdf_copies"
REPORTS_DIR = PROJECT_DIR / "01_single_paper_reports"
METADATA_FILE = PROJECT_DIR / "00_manifest" / "literature_metadata.csv"
EVIDENCE_DIR = PROJECT_DIR / "02_evidence_database"
LOGS_DIR = PROJECT_DIR / "06_logs"

def extract_full_text(pdf_path, max_pages=15):
    """Extract text from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n--- PAGE BREAK ---\n"
            return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def extract_abstract(text):
    """Extract abstract from text."""
    # Look for abstract section
    patterns = [
        r'(?:ABSTRACT|Abstract)[:\s]*\n(.*?)(?:\n\s*(?:KEYWORDS|Keywords|INTRODUCTION|Introduction|1\.|I\.))',
        r'(?:ABSTRACT|Abstract)[:\s]*(.*?)(?:\n\n|\n\s*\n)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()[:1000]
    # Fallback: first substantial paragraph after title
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if len(line) > 100 and ('polymer' in line.lower() or 'material' in line.lower() or 'study' in line.lower()):
            return line.strip()[:1000]
    return ""

def extract_keywords(text):
    """Extract keywords from text."""
    patterns = [
        r'(?:KEYWORDS|Keywords|Key words)[:\s]*(.*?)(?:\n\n|\n\s*\n)',
        r'(?:KEYWORDS|Keywords)[:\s]*(.*?)(?:\n)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            kw = m.group(1).strip()
            kw = re.sub(r'\s+', ' ', kw)
            return kw[:500]
    return ""

def extract_figures_tables(text):
    """Extract figure and table references."""
    figs = re.findall(r'(?:Fig\.|Figure|FIG\.?)\s*(\d+[a-z]?)', text)
    tables = re.findall(r'(?:Table|TABLE)\s*(\d+)', text)
    return list(set(figs)), list(set(tables))

def extract_methods(text):
    """Extract characterization and experimental methods mentioned."""
    methods = []
    method_keywords = {
        'SAXS': ['SAXS', 'small-angle X-ray scattering', 'small angle X-ray'],
        'WAXD': ['WAXD', 'WAXS', 'wide-angle X-ray', 'wide angle X-ray'],
        'DSC': ['DSC', 'differential scanning calorimetry'],
        'DMA': ['DMA', 'dynamic mechanical analysis', 'dynamic mechanical'],
        'FTIR': ['FTIR', 'FT-IR', 'Fourier transform infrared', 'infrared spectroscopy'],
        'NMR': ['NMR', 'nuclear magnetic resonance'],
        'Rheology': ['rheolog', 'viscoelastic', 'storage modulus', "G'", "G''", 'loss modulus'],
        'Tensile': ['tensile', 'stress-strain', 'elongation at break', 'tensile strength'],
        'AFM': ['AFM', 'atomic force microscop'],
        'SEM': ['SEM', 'scanning electron microscop'],
        'TEM': ['TEM', 'transmission electron microscop'],
        'XPS': ['XPS', 'X-ray photoelectron spectroscopy'],
        'Dielectric': ['dielectric', 'impedance spectroscopy'],
        'DLS': ['DLS', 'dynamic light scattering'],
        'Neutron Scattering': ['neutron scattering', 'SANS', 'small-angle neutron'],
        'MD Simulation': ['molecular dynamics', 'MD simulation', 'coarse-grain'],
        'DFT': ['DFT', 'density functional theory', 'first-principles'],
        'GPC': ['GPC', 'gel permeation chromatography', 'size exclusion'],
        'TGA': ['TGA', 'thermogravimetric analysis'],
        'UV-Vis': ['UV-Vis', 'UV-vis', 'ultraviolet-visible'],
        'Fluorescence': ['fluorescence spectroscopy', 'photoluminescence'],
        'Piezoelectric': ['piezoelectric', 'd33', 'piezoresponse'],
        'Cyclic Voltammetry': ['cyclic voltammetry', 'CV', 'electrochemical'],
    }
    text_lower = text.lower()
    for method, keywords in method_keywords.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                methods.append(method)
                break
    return list(set(methods))

def extract_materials(text):
    """Extract material systems mentioned."""
    materials = []
    material_keywords = {
        'Polyurethane': ['polyurethane', 'TPU', 'PU'],
        'Polyethylene': ['polyethylene', 'PE'],
        'Polylactic acid': ['polylactic acid', 'PLA', 'poly(lactic acid)'],
        'PDMS': ['PDMS', 'polydimethylsiloxane'],
        'PEDOT:PSS': ['PEDOT:PSS', 'PEDOT-PSS', 'PEDOT'],
        'PVDF': ['PVDF', 'polyvinylidene fluoride'],
        'PCL': ['PCL', 'polycaprolactone', 'poly(caprolactone)'],
        'Hydrogel': ['hydrogel', 'polyacrylamide', 'PAAm'],
        'Ionogel': ['ionogel', 'ionic gel'],
        'Elastomer': ['elastomer', 'rubber', 'elastic'],
        'Vitrimer': ['vitrimer', 'dynamic covalent network'],
        'Ionic liquid': ['ionic liquid', '[BMIM]', '[EMIM]', '[Pyrr'],
        'Block copolymer': ['block copolymer', 'block copolymer', 'BCP'],
        'Polyelectrolyte': ['polyelectrolyte', 'poly(ionic liquid)'],
        'Shape memory polymer': ['shape memory', 'SMP'],
        'Self-healing': ['self-heal', 'self-repair'],
        'Ferrocene': ['ferrocene'],
        'BaTiO3': ['BaTiO3', 'barium titanate'],
        'PVDF-TrFE': ['PVDF-TrFE', 'P(VDF-TrFE)'],
        'Polythiophene': ['polythiophene', 'P3HT'],
        'Polyacrylate': ['polyacrylate', 'PMMA', 'poly(methyl methacrylate)'],
        'Chitosan': ['chitosan'],
        'Alginate': ['alginate'],
        'Gelatin': ['gelatin'],
        'PEG': ['PEG', 'polyethylene glycol', 'PEO', 'poly(ethylene oxide)'],
        'Polyimide': ['polyimide', 'PI'],
        'Polysiloxane': ['polysiloxane', 'silicone'],
        'SBR': ['SBR', 'styrene-butadiene'],
        'Natural rubber': ['natural rubber'],
        'Polyester': ['polyester'],
        'Polyamide': ['polyamide', 'nylon'],
        'Polysulfide': ['polysulfide', 'polythioether'],
        'Thiourea': ['thiourea', 'thiourethane'],
        'Oxime-carbamate': ['oxime-carbamate', 'oxime carbamate'],
        'Boronic ester': ['boronic ester', 'boronate'],
        'Furan': ['furan', 'FDCA', 'furandicarboxylic'],
        'Lipoic acid': ['lipoic acid', 'thioctic'],
    }
    text_lower = text.lower()
    for mat, keywords in material_keywords.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                materials.append(mat)
                break
    return list(set(materials))

def extract_key_findings(text):
    """Extract key findings from text."""
    findings = []
    # Look for conclusion-like sentences
    patterns = [
        r'(?:Our results|We demonstrate|We show|We find|We report|Here we|In this work|This study)',
        r'(?:These results|Our findings|This work|The results)',
        r'(?:In conclusion|To summarize|In summary)',
    ]
    sentences = re.split(r'[.!?]', text[:5000])
    for sent in sentences:
        for pat in patterns:
            if re.search(pat, sent, re.IGNORECASE):
                sent = sent.strip()
                if len(sent) > 20:
                    findings.append(sent[:200])
                break
    return findings[:5]

def generate_report(paper_id, meta, text, orig_name):
    """Generate a single paper analysis report."""
    abstract = extract_abstract(text)
    keywords = extract_keywords(text)
    figs, tables = extract_figures_tables(text)
    methods = extract_methods(text)
    materials = extract_materials(text)
    findings = extract_key_findings(text)

    title = meta.get('title', '')
    if not title or len(title) < 5:
        title = orig_name.replace('.pdf', '')

    authors = meta.get('authors', '')
    journal = meta.get('journal', '')
    year = meta.get('year', '')
    doi = meta.get('DOI', '')

    report = f"""# {paper_id} Literature Deep Analysis Report

## 1. Literature Information
- **Paper ID**: {paper_id}
- **Title**: {title}
- **Authors**: {authors}
- **Journal**: {journal}
- **Year**: {year}
- **DOI**: {doi}
- **Original File**: {orig_name}
- **Category**: {meta.get('preliminary_category', '')}
- **Materials**: {', '.join(materials) if materials else 'To be identified'}

## 2. Research Background & Significance
{abstract if abstract else 'Abstract not reliably extracted. Please refer to the original PDF.'}

## 3. Core Scientific Questions
{generate_questions(text, materials, methods)}

## 4. Material System & Experimental Design
- **Materials identified**: {', '.join(materials) if materials else 'To be identified'}
- **Characterization methods**: {', '.join(methods) if methods else 'To be identified'}

## 5. Methodology Analysis
{generate_method_analysis(methods, text)}

## 6. Key Figures & Results
- **Figures referenced**: {', '.join(figs[:10]) if figs else 'None detected'}
- **Tables referenced**: {', '.join(tables[:5]) if tables else 'None detected'}

## 7. Mechanism Analysis
{generate_mechanism_analysis(text)}

## 8. Innovation Points
{generate_innovation(text, materials, methods)}

## 9. Limitations & Issues
{generate_limitations(text)}

## 10. Implications for Future Research
{generate_implications(text, materials, methods)}

## 11. Citable Insights
{generate_citable_insights(findings, paper_id)}

---
*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Note: This report is auto-generated from PDF text extraction. Some sections may require manual verification against the original paper.*
"""
    return report, {
        'paper_id': paper_id,
        'title': title,
        'abstract': abstract[:500],
        'keywords': keywords,
        'methods': methods,
        'materials': materials,
        'figures': figs,
        'tables': tables,
        'findings': findings,
        'journal': journal,
        'year': year,
        'doi': doi,
    }

def generate_questions(text, materials, methods):
    """Generate research questions based on content."""
    questions = []
    text_lower = text.lower()

    if 'mechanism' in text_lower or 'mechanistic' in text_lower:
        questions.append("- What is the underlying mechanism governing the observed phenomena?")
    if 'structure-property' in text_lower or 'structure–property' in text_lower:
        questions.append("- How does the molecular/nanostructure relate to macroscopic properties?")
    if 'self-heal' in text_lower:
        questions.append("- What controls the self-healing efficiency and kinetics?")
    if 'ionic' in text_lower or 'ion' in text_lower:
        questions.append("- How do ionic interactions influence material performance?")
    if 'crystal' in text_lower:
        questions.append("- What controls crystallization behavior and crystal morphology?")
    if 'dynamic' in text_lower:
        questions.append("- How do dynamic bonds affect material properties and processing?")

    if not questions:
        questions.append("- To be extracted from detailed reading of the paper")

    return '\n'.join(questions)

def generate_method_analysis(methods, text):
    """Generate methodology analysis."""
    if not methods:
        return "Methods to be identified from detailed reading."
    lines = []
    for m in methods:
        lines.append(f"- **{m}**: Used for characterization/analysis")
    return '\n'.join(lines)

def generate_mechanism_analysis(text):
    """Generate mechanism analysis."""
    text_lower = text.lower()
    mechanisms = []
    if 'hydrogen bond' in text_lower:
        mechanisms.append("- Hydrogen bonding interactions")
    if 'ionic' in text_lower and ('interaction' in text_lower or 'cluster' in text_lower):
        mechanisms.append("- Ionic interactions/clustering")
    if 'phase separ' in text_lower:
        mechanisms.append("- Phase separation behavior")
    if 'microphase' in text_lower:
        mechanisms.append("- Microphase separation")
    if 'dynamic covalent' in text_lower:
        mechanisms.append("- Dynamic covalent bond exchange")
    if 'entanglement' in text_lower:
        mechanisms.append("- Chain entanglement effects")
    if 'crosslink' in text_lower or 'cross-link' in text_lower:
        mechanisms.append("- Crosslinking mechanisms")
    if 'crystalliz' in text_lower:
        mechanisms.append("- Crystallization-driven assembly")
    if 'supramolecular' in text_lower:
        mechanisms.append("- Supramolecular interactions")
    if 'coordination' in text_lower:
        mechanisms.append("- Metal coordination bonds")

    if not mechanisms:
        return "Mechanism details to be extracted from detailed reading."
    return "Key mechanisms discussed:\n" + '\n'.join(mechanisms)

def generate_innovation(text, materials, methods):
    """Generate innovation analysis."""
    innovations = []
    text_lower = text.lower()
    if 'novel' in text_lower or 'first' in text_lower or 'new' in text_lower:
        innovations.append("- Introduces novel approach/material/method")
    if 'unprecedented' in text_lower or 'unique' in text_lower:
        innovations.append("- Reports unprecedented findings")
    if 'strategy' in text_lower or 'design' in text_lower:
        innovations.append("- Proposes new design strategy")
    if not innovations:
        return "Innovation points to be identified from detailed reading."
    return '\n'.join(innovations)

def generate_limitations(text):
    """Generate limitations analysis."""
    limitations = []
    text_lower = text.lower()
    if 'limitation' in text_lower or 'challenge' in text_lower:
        limitations.append("- Authors acknowledge limitations/challenges")
    if 'future' in text_lower:
        limitations.append("- Future work directions identified")
    if not limitations:
        return "Limitations to be identified from detailed reading."
    return '\n'.join(limitations)

def generate_implications(text, materials, methods):
    """Generate implications for future research."""
    return "- Extends understanding of " + (', '.join(materials[:3]) if materials else 'the studied system') + "\n- Provides methodological insights for related studies"

def generate_citable_insights(findings, paper_id):
    """Generate citable insights."""
    if not findings:
        return f"1. To be extracted from detailed reading of [{paper_id}]"
    lines = []
    for i, f in enumerate(findings[:5], 1):
        lines.append(f"{i}. {f}\n   Source: [{paper_id}]")
    return '\n'.join(lines)

def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load metadata
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        metadata = {row['paper_id']: row for row in reader}

    print(f"Generating analysis reports for {len(metadata)} papers...")

    evidence_items = []
    all_methods = []
    all_materials = []
    all_figures = []
    errors = []

    for i, (paper_id, meta) in enumerate(metadata.items()):
        if i % 50 == 0:
            print(f"  Processing {i}/{len(metadata)}...")

        # Skip supplementary materials for deep analysis
        if meta.get('preliminary_category') == 'supplementary':
            continue

        pdf_path = ENGLISH_DIR / f"{paper_id}_unidentified.pdf"
        if not pdf_path.exists():
            errors.append(f"{paper_id}: PDF not found")
            continue

        # Extract text
        text = extract_full_text(pdf_path)
        if text.startswith("ERROR"):
            errors.append(f"{paper_id}: {text}")
            continue

        # Generate report
        report, analysis = generate_report(paper_id, meta, text, meta.get('original_file_name', ''))

        # Write report
        report_path = REPORTS_DIR / f"{paper_id}_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        # Collect evidence items
        for finding in analysis['findings']:
            evidence_items.append({
                'evidence_id': f"E{len(evidence_items)+1:04d}",
                'paper_id': paper_id,
                'title': analysis['title'],
                'conclusion': finding,
                'evidence_type': 'experimental',
                'figure_or_table': '',
                'material_system': ', '.join(analysis['materials']),
                'method': ', '.join(analysis['methods']),
                'key_data': '',
                'mechanism': '',
                'reliability_level': 'B',
                'related_question': '',
                'possible_limitation': '',
                'notes': '',
            })

        # Collect methods and materials
        for m in analysis['methods']:
            all_methods.append({
                'paper_id': paper_id,
                'method_name': m,
                'method_type': 'characterization',
                'purpose': '',
                'measured_information': '',
                'strengths': '',
                'limitations': '',
                'key_result': '',
            })
        for m in analysis['materials']:
            all_materials.append({
                'paper_id': paper_id,
                'material_system': m,
                'composition': '',
                'structure': '',
                'processing_method': '',
                'key_property': '',
                'performance_data': '',
                'application': '',
                'limitation': '',
            })
        for fig in analysis['figures']:
            all_figures.append({
                'paper_id': paper_id,
                'figure_or_table': f"Fig. {fig}",
                'content': '',
                'key_observation': '',
                'supported_conclusion': '',
                'importance_level': '',
            })

    # Write evidence database
    with open(EVIDENCE_DIR / "evidence_matrix.csv", 'w', newline='', encoding='utf-8') as f:
        if evidence_items:
            writer = csv.DictWriter(f, fieldnames=evidence_items[0].keys())
            writer.writeheader()
            writer.writerows(evidence_items)
    with open(EVIDENCE_DIR / "evidence_matrix.json", 'w', encoding='utf-8') as f:
        json.dump(evidence_items, f, ensure_ascii=False, indent=2)

    # Write method matrix
    with open(EVIDENCE_DIR / "method_matrix.csv", 'w', newline='', encoding='utf-8') as f:
        if all_methods:
            writer = csv.DictWriter(f, fieldnames=all_methods[0].keys())
            writer.writeheader()
            writer.writerows(all_methods)
    with open(EVIDENCE_DIR / "method_matrix.json", 'w', encoding='utf-8') as f:
        json.dump(all_methods, f, ensure_ascii=False, indent=2)

    # Write material matrix
    with open(EVIDENCE_DIR / "material_system_matrix.csv", 'w', newline='', encoding='utf-8') as f:
        if all_materials:
            writer = csv.DictWriter(f, fieldnames=all_materials[0].keys())
            writer.writeheader()
            writer.writerows(all_materials)
    with open(EVIDENCE_DIR / "material_system_matrix.json", 'w', encoding='utf-8') as f:
        json.dump(all_materials, f, ensure_ascii=False, indent=2)

    # Write key figures table
    with open(EVIDENCE_DIR / "key_figures_table.csv", 'w', newline='', encoding='utf-8') as f:
        if all_figures:
            writer = csv.DictWriter(f, fieldnames=all_figures[0].keys())
            writer.writeheader()
            writer.writerows(all_figures)
    with open(EVIDENCE_DIR / "key_figures_table.json", 'w', encoding='utf-8') as f:
        json.dump(all_figures, f, ensure_ascii=False, indent=2)

    # Write errors
    if errors:
        with open(LOGS_DIR / "file_reading_errors.md", 'w', encoding='utf-8') as f:
            f.write("# File Reading Errors\n\n")
            for e in errors:
                f.write(f"- {e}\n")

    print(f"\nDone!")
    print(f"Reports generated: {len(list(REPORTS_DIR.glob('*.md')))}")
    print(f"Evidence items: {len(evidence_items)}")
    print(f"Method entries: {len(all_methods)}")
    print(f"Material entries: {len(all_materials)}")
    print(f"Figure entries: {len(all_figures)}")
    print(f"Errors: {len(errors)}")

if __name__ == "__main__":
    main()
