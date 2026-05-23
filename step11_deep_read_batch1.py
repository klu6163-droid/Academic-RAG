#!/usr/bin/env python3
"""
Phase 2 Batch 1: Deep read PU Microphase Separation + TPU Mechanics.
Reads extracted texts, extracts structured findings, writes category reviews + evidence CSVs.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime

# Paths
EXTRACTED_DIR = Path(r"D:\Academic-RAG\06_logs\extracted_texts")
CARDS_FILE = Path(r"D:\Academic-RAG\data\analysis\refined_paper_cards.jsonl")
REVIEW_DIR = Path(r"D:\Academic-RAG\data\analysis\category_reviews")
REVIEW_DIR.mkdir(parents=True, exist_ok=True)

BATCH1_CATEGORIES = [
    "polyurethane_microphase_separation",
    "TPU_mechanics",
]


def load_cards():
    cards = []
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))
    return cards


def read_paper(pid):
    """Read extracted text for a paper."""
    txt_file = EXTRACTED_DIR / f"{pid}.txt"
    if not txt_file.exists():
        return None
    text = txt_file.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 50:
        return None
    return text


def extract_abstract(text):
    """Extract abstract from text."""
    patterns = [
        r"(?:ABSTRACT|Abstract)[:\s]+(.+?)(?:\n\s*(?:INTRODUCTION|Introduction|KEYWORDS|Keywords|■|\n\n\n))",
        r"(?:ABSTRACT|Abstract)[:\s]+(.+?)(?:\n\s*\n)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 50:
            return m.group(1).strip()[:2000]
    return ""


def extract_conclusion(text):
    """Extract conclusion from text."""
    patterns = [
        r"(?:CONCLUSIONS?|CONCLUDING|SUMMARY|DISCUSSION\s+(?:AND|&)\s+CONCLUSIONS?)[:\s]+(.+?)(?:\n\s*(?:REFERENCES|ACKNOWLEDG|AUTHOR|ASSOCIATED|■|$))",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 30:
            return m.group(1).strip()[:2000]
    return ""


def extract_figures(text):
    """Extract figure captions."""
    captions = re.findall(
        r"(?:Figure|Fig\.?)\s*(\d+)[.:]\s*(.+?)(?:\n\s*\n|\n\s*(?:Figure|Fig\.?))",
        text, re.DOTALL | re.IGNORECASE
    )
    return [(num, cap.strip()[:300]) for num, cap in captions[:15]]


def extract_methods_from_text(text):
    """Extract methods mentioned in text."""
    text_lower = text.lower()
    methods = []
    method_keywords = {
        "saxs": "SAXS (Small-Angle X-ray Scattering)",
        "small-angle x-ray": "SAXS (Small-Angle X-ray Scattering)",
        "waxs": "WAXS (Wide-Angle X-ray Scattering)",
        "wide-angle x-ray": "WAXS (Wide-Angle X-ray Scattering)",
        "waxd": "WAXD (Wide-Angle X-ray Diffraction)",
        "ftir": "FTIR (Fourier Transform Infrared Spectroscopy)",
        "fourier transform infrared": "FTIR (Fourier Transform Infrared Spectroscopy)",
        "dsc": "DSC (Differential Scanning Calorimetry)",
        "differential scanning": "DSC (Differential Scanning Calorimetry)",
        "dma": "DMA (Dynamic Mechanical Analysis)",
        "dynamic mechanical": "DMA (Dynamic Mechanical Analysis)",
        "tga": "TGA (Thermogravimetric Analysis)",
        "thermogravimetric": "TGA (Thermogravimetric Analysis)",
        "tensile test": "Tensile Testing",
        "stress-strain": "Stress-Strain Testing",
        "sem": "SEM (Scanning Electron Microscopy)",
        "scanning electron": "SEM (Scanning Electron Microscopy)",
        "tem": "TEM (Transmission Electron Microscopy)",
        "transmission electron": "TEM (Transmission Electron Microscopy)",
        "afm": "AFM (Atomic Force Microscopy)",
        "atomic force": "AFM (Atomic Force Microscopy)",
        "nmr": "NMR (Nuclear Magnetic Resonance)",
        "xrd": "XRD (X-ray Diffraction)",
        "rheology": "Rheology",
        "rheometer": "Rheology",
        "molecular dynamics": "Molecular Dynamics Simulation",
        "md simulation": "Molecular Dynamics Simulation",
        "dielectric": "Dielectric Spectroscopy",
        "impedance": "Impedance Spectroscopy",
    }
    for kw, method in method_keywords.items():
        if kw in text_lower and method not in methods:
            methods.append(method)
    return methods[:10]


def extract_performance_data(text):
    """Extract key performance numbers from text."""
    data = []
    patterns = [
        (r"tensile strength[^.]*?(\d+[\.\d]*)\s*(MPa|GPa)", "Tensile strength"),
        (r"elongation at break[^.]*?(\d+[\.\d]*)\s*%", "Elongation at break"),
        (r"young'?s modulus[^.]*?(\d+[\.\d]*)\s*(MPa|GPa|kPa)", "Young's modulus"),
        (r"fracture toughness[^.]*?(\d+[\.\d]*)\s*(kJ/m|J/m|MPa)", "Fracture toughness"),
        (r"tear strength[^.]*?(\d+[\.\d]*)\s*(kN/m|N/m)", "Tear strength"),
        (r"glass transition[^.]*?(\-?\d+[\.\d]*)\s*°?C", "Tg"),
        (r"melting (?:temperature|point)[^.]*?(\d+[\.\d]*)\s*°?C", "Tm"),
        (r"crystallization temperature[^.]*?(\d+[\.\d]*)\s*°?C", "Tc"),
        (r"hardness[^.]*?(\d+[\.\d]*)\s*(shore|Shore)", "Hardness"),
        (r"resilience[^.]*?(\d+[\.\d]*)\s*%", "Resilience"),
    ]
    text_lower = text.lower()
    for pat, label in patterns:
        m = re.search(pat, text_lower)
        if m:
            val = m.group(1)
            unit = m.group(2) if m.lastindex >= 2 else ""
            data.append(f"{label}: {val} {unit}".strip())
    return data[:8]


def extract_evidence_excerpts(text, category):
    """Extract relevant evidence excerpts from text."""
    excerpts = []
    lines = text.split("\n")

    # Keywords to search for based on category
    if category == "polyurethane_microphase_separation":
        keywords = ["microphase separation", "hard segment", "soft segment", "domain", "phase separation",
                    "hydrogen bond", "nanophase", "morphology", "saxs", "waxs"]
    else:  # TPU_mechanics
        keywords = ["tensile", "fracture", "fatigue", "tear", "toughness", "modulus", "elongation",
                    "stress-strain", "crack", "notch", "resilience", "mechanical"]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in keywords:
            if kw in line_lower and len(line.strip()) > 30:
                # Get context (this line + next line)
                context = line.strip()
                if i + 1 < len(lines):
                    context += " " + lines[i + 1].strip()
                if len(context) > 500:
                    context = context[:500] + "..."
                # Estimate page (rough: ~40 lines per page)
                page_est = max(1, i // 40 + 1)
                excerpts.append({
                    "line_num": i + 1,
                    "page_est": page_est,
                    "text": context,
                    "keyword": kw,
                })
                break  # Only one keyword per line
        if len(excerpts) >= 5:
            break

    return excerpts


def deep_read_paper(card, category):
    """Deep read a single paper and extract structured findings."""
    pid = card["paper_id"]
    text = read_paper(pid)

    if not text:
        return {
            "paper_id": pid,
            "title": card.get("title", ""),
            "file_name": card.get("file_name", ""),
            "year": card.get("year", ""),
            "priority": card.get("priority", ""),
            "abstract": "evidence_missing",
            "conclusion": "evidence_missing",
            "methods": [],
            "performance_data": [],
            "figures": [],
            "evidence_excerpts": [],
            "extraction_quality": "poor",
            "notes": "needs_manual_check - text extraction failed or too short",
        }

    abstract = extract_abstract(text)
    conclusion = extract_conclusion(text)
    methods = extract_methods_from_text(text)
    performance = extract_performance_data(text)
    figures = extract_figures(text)
    excerpts = extract_evidence_excerpts(text, category)

    # Determine extraction quality
    quality = "good"
    if not abstract:
        quality = "partial"
    if len(text) < 500:
        quality = "poor"

    return {
        "paper_id": pid,
        "title": card.get("title", ""),
        "file_name": card.get("file_name", ""),
        "year": card.get("year", ""),
        "priority": card.get("priority", ""),
        "abstract": abstract if abstract else "evidence_missing",
        "conclusion": conclusion if conclusion else "evidence_missing",
        "methods": methods,
        "performance_data": performance,
        "figures": figures,
        "evidence_excerpts": excerpts,
        "extraction_quality": quality,
        "notes": "",
    }


def write_category_review(category, results, cards):
    """Write category review markdown file."""
    cat_display = category.replace("_", " ").title()
    lines = []
    lines.append(f"# Category Review: {cat_display}")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Papers reviewed: {len(results)}")
    lines.append("")

    # Sort by priority
    prio_order = {"high": 0, "medium": 1, "low": 2}
    results_sorted = sorted(results, key=lambda x: prio_order.get(x["priority"], 2))

    # 1. Research Background
    lines.append("## 1. Research Background")
    lines.append("")
    if category == "polyurethane_microphase_separation":
        lines.append("Polyurethane (PU) is a segmented block copolymer consisting of hard segments (diisocyanate + chain extender) and soft segments (polyol). The thermodynamic incompatibility between hard and soft segments drives microphase separation, forming hard domains dispersed in a continuous soft matrix. This morphology directly governs mechanical properties, shape memory behavior, and biocompatibility.")
    else:
        lines.append("Thermoplastic polyurethane (TPU) is widely used in applications requiring elasticity, toughness, and processability. Understanding the relationship between microstructure (hard/soft domain morphology, hydrogen bonding network) and mechanical response (tensile, fatigue, fracture) is critical for material design.")
    lines.append("")

    # 2. Key Material Systems
    lines.append("## 2. Key Material Systems")
    lines.append("")
    all_materials = set()
    for r in results:
        card = next((c for c in cards if c["paper_id"] == r["paper_id"]), {})
        for m in card.get("material_system", []):
            all_materials.add(m)
    for m in sorted(all_materials):
        lines.append(f"- {m}")
    lines.append("")

    # 3. Core Experimental Design
    lines.append("## 3. Core Experimental Design")
    lines.append("")
    all_methods = set()
    for r in results:
        for m in r.get("methods", []):
            all_methods.add(m)
    for m in sorted(all_methods):
        lines.append(f"- {m}")
    lines.append("")

    # 4. Key Characterization Evidence
    lines.append("## 4. Key Characterization Evidence")
    lines.append("")
    for r in results_sorted:
        if r["extraction_quality"] == "poor":
            continue
        lines.append(f"### {r['paper_id']}: {r['title'][:60]}")
        lines.append(f"- Priority: {r['priority']} | Year: {r['year']} | Quality: {r['extraction_quality']}")
        if r["abstract"] != "evidence_missing":
            lines.append(f"- **Abstract**: {r['abstract'][:300]}...")
        if r["conclusion"] != "evidence_missing":
            lines.append(f"- **Conclusion**: {r['conclusion'][:300]}...")
        lines.append("")

    # 5. Key Performance Data
    lines.append("## 5. Key Performance Data")
    lines.append("")
    for r in results_sorted:
        if r.get("performance_data"):
            lines.append(f"**{r['paper_id']}**:")
            for pd in r["performance_data"]:
                lines.append(f"- {pd}")
            lines.append("")

    # 6. Structure-Property Relationships
    lines.append("## 6. Structure-Property Relationships")
    lines.append("")
    lines.append("(To be synthesized from individual paper findings)")
    lines.append("")

    # 7. Important Figures and Page References
    lines.append("## 7. Important Figures and Page References")
    lines.append("")
    for r in results_sorted:
        if r.get("figures"):
            lines.append(f"**{r['paper_id']}**:")
            for num, cap in r["figures"][:5]:
                lines.append(f"- Figure {num}: {cap[:150]}")
            lines.append("")

    # 8. Consensus Across Papers
    lines.append("## 8. Consensus Across Papers")
    lines.append("")
    lines.append("(To be synthesized after all papers in category are reviewed)")
    lines.append("")

    # 9. Contradictions Across Papers
    lines.append("## 9. Contradictions Across Papers")
    lines.append("")
    lines.append("(To be synthesized after all papers in category are reviewed)")
    lines.append("")

    # 10. Research Gaps
    lines.append("## 10. Research Gaps")
    lines.append("")
    lines.append("(To be synthesized after all papers in category are reviewed)")
    lines.append("")

    # 11. Implications for Research
    lines.append("## 11. Implications for Research")
    lines.append("")
    lines.append("(To be synthesized after all papers in category are reviewed)")
    lines.append("")

    # Evidence Table
    lines.append("## Evidence Table")
    lines.append("")
    lines.append("| Paper ID | Title | Year | Priority | Extraction Quality | Abstract | Conclusion | Key Methods |")
    lines.append("|----------|-------|------|----------|--------------------|----------|------------|-------------|")
    for r in results_sorted:
        has_abstract = "Yes" if r["abstract"] != "evidence_missing" else "No"
        has_conclusion = "Yes" if r["conclusion"] != "evidence_missing" else "No"
        methods_str = ", ".join(r["methods"][:3]) if r["methods"] else "-"
        title_short = r["title"][:50] + ("..." if len(r["title"]) > 50 else "")
        lines.append(f"| {r['paper_id']} | {title_short} | {r['year']} | {r['priority']} | {r['extraction_quality']} | {has_abstract} | {has_conclusion} | {methods_str} |")
    lines.append("")

    # Write
    review_file = REVIEW_DIR / f"{category}.md"
    review_file.write_text("\n".join(lines), encoding="utf-8")
    return review_file


def write_evidence_csv(category, results):
    """Write evidence CSV file."""
    csv_file = REVIEW_DIR / f"{category}_evidence.csv"
    fieldnames = [
        "paper_id", "title", "file_name", "year", "priority",
        "extraction_quality", "evidence_type", "evidence_text",
        "page_est", "keyword", "confidence"
    ]

    rows = []
    for r in results:
        # Abstract as evidence
        if r["abstract"] != "evidence_missing":
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "file_name": r["file_name"],
                "year": r["year"],
                "priority": r["priority"],
                "extraction_quality": r["extraction_quality"],
                "evidence_type": "abstract",
                "evidence_text": r["abstract"][:500],
                "page_est": 1,
                "keyword": "abstract",
                "confidence": "high" if r["extraction_quality"] == "good" else "medium",
            })

        # Conclusion as evidence
        if r["conclusion"] != "evidence_missing":
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "file_name": r["file_name"],
                "year": r["year"],
                "priority": r["priority"],
                "extraction_quality": r["extraction_quality"],
                "evidence_type": "conclusion",
                "evidence_text": r["conclusion"][:500],
                "page_est": "end",
                "keyword": "conclusion",
                "confidence": "high" if r["extraction_quality"] == "good" else "medium",
            })

        # Evidence excerpts
        for exc in r.get("evidence_excerpts", []):
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "file_name": r["file_name"],
                "year": r["year"],
                "priority": r["priority"],
                "extraction_quality": r["extraction_quality"],
                "evidence_type": "excerpt",
                "evidence_text": exc["text"],
                "page_est": exc["page_est"],
                "keyword": exc["keyword"],
                "confidence": "medium",
            })

        # Performance data
        for pd in r.get("performance_data", []):
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "file_name": r["file_name"],
                "year": r["year"],
                "priority": r["priority"],
                "extraction_quality": r["extraction_quality"],
                "evidence_type": "performance_data",
                "evidence_text": pd,
                "page_est": "",
                "keyword": "performance",
                "confidence": "medium",
            })

        # Figures
        for num, cap in r.get("figures", []):
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "file_name": r["file_name"],
                "year": r["year"],
                "priority": r["priority"],
                "extraction_quality": r["extraction_quality"],
                "evidence_type": "figure_caption",
                "evidence_text": cap[:300],
                "page_est": "",
                "keyword": f"Figure {num}",
                "confidence": "medium",
            })

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return csv_file


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 2 Batch 1: Deep Reading")
    print()

    cards = load_cards()
    print(f"  Loaded {len(cards)} refined cards")

    total_processed = 0
    total_skipped = 0
    needs_manual = []

    for category in BATCH1_CATEGORIES:
        cat_cards = [c for c in cards if c["primary_category"] == category]
        cat_display = category.replace("_", " ").title()
        print(f"\n  === {cat_display}: {len(cat_cards)} papers ===")

        results = []
        for i, card in enumerate(cat_cards):
            pid = card["paper_id"]
            title_safe = card['title'][:50].encode('ascii', 'replace').decode('ascii')
            print(f"    [{i+1}/{len(cat_cards)}] {pid}: {title_safe}...", end="")

            result = deep_read_paper(card, category)
            results.append(result)

            if result["extraction_quality"] == "poor":
                needs_manual.append({"paper_id": pid, "category": category, "title": card["title"]})
                print(f" [POOR EXTRACTION]")
            elif result["extraction_quality"] == "partial":
                print(f" [PARTIAL]")
            else:
                print(f" [OK]")

            total_processed += 1

        # Write category review
        review_file = write_category_review(category, results, cards)
        print(f"    Written: {review_file}")

        # Write evidence CSV
        evidence_file = write_evidence_csv(category, results)
        print(f"    Written: {evidence_file}")

        # Summary
        good = sum(1 for r in results if r["extraction_quality"] == "good")
        partial = sum(1 for r in results if r["extraction_quality"] == "partial")
        poor = sum(1 for r in results if r["extraction_quality"] == "poor")
        print(f"    Quality: {good} good, {partial} partial, {poor} poor")

    # Final summary
    print()
    print(f"[{datetime.now():%H:%M:%S}] Batch 1 Complete")
    print(f"  Total processed: {total_processed}")
    print(f"  Needs manual check: {len(needs_manual)}")
    print()
    print("  Output files:")
    for category in BATCH1_CATEGORIES:
        print(f"    data/analysis/category_reviews/{category}.md")
        print(f"    data/analysis/category_reviews/{category}_evidence.csv")

    if needs_manual:
        print()
        print("  Papers needing manual check:")
        for nm in needs_manual:
            print(f"    {nm['paper_id']}: {nm['title'][:60]}")


if __name__ == "__main__":
    main()
