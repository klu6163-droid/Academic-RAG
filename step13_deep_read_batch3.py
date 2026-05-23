#!/usr/bin/env python3
"""
Phase 2 Batch 3: Deep read PCL-Based PU + Biodegradable PU.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime

EXTRACTED_DIR = Path(r"D:\Academic-RAG\06_logs\extracted_texts")
CARDS_FILE = Path(r"D:\Academic-RAG\data\analysis\refined_paper_cards.jsonl")
REVIEW_DIR = Path(r"D:\Academic-RAG\data\analysis\category_reviews")
REVIEW_DIR.mkdir(parents=True, exist_ok=True)

BATCH3_CATEGORIES = [
    "PCL_based_polyurethane",
    "biodegradable_polyurethane",
]


def load_cards():
    cards = []
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))
    return cards


def read_paper(pid):
    txt_file = EXTRACTED_DIR / f"{pid}.txt"
    if not txt_file.exists():
        return None
    text = txt_file.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 50:
        return None
    return text


def extract_abstract(text):
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
    patterns = [
        r"(?:CONCLUSIONS?|CONCLUDING|SUMMARY|DISCUSSION\s+(?:AND|&)\s+CONCLUSIONS?)[:\s]+(.+?)(?:\n\s*(?:REFERENCES|ACKNOWLEDG|AUTHOR|ASSOCIATED|■|$))",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 30:
            return m.group(1).strip()[:2000]
    return ""


def extract_figures(text):
    captions = re.findall(
        r"(?:Figure|Fig\.?)\s*(\d+)[.:]\s*(.+?)(?:\n\s*\n|\n\s*(?:Figure|Fig\.?))",
        text, re.DOTALL | re.IGNORECASE
    )
    return [(num, cap.strip()[:300]) for num, cap in captions[:15]]


def extract_methods_from_text(text):
    text_lower = text.lower()
    methods = []
    method_keywords = {
        "saxs": "SAXS", "small-angle x-ray": "SAXS",
        "waxs": "WAXS", "wide-angle x-ray": "WAXS",
        "ftir": "FTIR", "fourier transform infrared": "FTIR",
        "dsc": "DSC", "differential scanning": "DSC",
        "dma": "DMA", "dynamic mechanical": "DMA",
        "tga": "TGA", "thermogravimetric": "TGA",
        "tensile test": "Tensile Testing", "stress-strain": "Stress-Strain",
        "sem": "SEM", "scanning electron": "SEM",
        "tem": "TEM", "transmission electron": "TEM",
        "afm": "AFM", "atomic force": "AFM",
        "nmr": "NMR", "rheology": "Rheology",
        "molecular dynamics": "MD Simulation",
        "dielectric": "Dielectric Spectroscopy",
        "degradation": "Degradation Test",
        "hydrolysis": "Hydrolysis Test",
        "enzymatic": "Enzymatic Degradation",
        "biocompat": "Biocompatibility Test",
        "cell culture": "Cell Culture",
        "mtt": "MTT Assay",
        "cytotoxic": "Cytotoxicity Test",
        "in vivo": "In Vivo Test",
        "implant": "Implantation Study",
        "ring-opening polymerization": "Ring-Opening Polymerization",
        "polymerization": "Polymerization",
        "gel permeation": "GPC",
        "xrd": "XRD", "x-ray diffraction": "XRD",
        "piezoelectric": "Piezoelectric Test",
        "ferroelectric": "Ferroelectric Test",
    }
    for kw, method in method_keywords.items():
        if kw in text_lower and method not in methods:
            methods.append(method)
    return methods[:10]


def extract_performance_data(text):
    data = []
    patterns = [
        (r"tensile strength[^.]*?(\d+[\.\d]*)\s*(MPa|GPa)", "Tensile strength"),
        (r"elongation at break[^.]*?(\d+[\.\d]*)\s*%", "Elongation at break"),
        (r"young'?s modulus[^.]*?(\d+[\.\d]*)\s*(MPa|GPa|kPa)", "Young's modulus"),
        (r"fracture toughness[^.]*?(\d+[\.\d]*)\s*(kJ/m|J/m|MPa)", "Fracture toughness"),
        (r"tear strength[^.]*?(\d+[\.\d]*)\s*(kN/m|N/m)", "Tear strength"),
        (r"glass transition[^.]*?(\-?\d+[\.\d]*)\s*°?C", "Tg"),
        (r"melting temperature[^.]*?(\-?\d+[\.\d]*)\s*°?C", "Tm"),
        (r"degradation[^.]*?(\d+[\.\d]*)\s*%", "Degradation"),
        (r"molecular weight[^.]*?(\d+[\.\d]*)\s*(kDa|Da|g/mol)", "Molecular weight"),
        (r"crystallinity[^.]*?(\d+[\.\d]*)\s*%", "Crystallinity"),
        (r"water uptake[^.]*?(\d+[\.\d]*)\s*%", "Water uptake"),
        (r"piezoelectric[^.]*?(\d+[\.\d]*)\s*(pC/N|pm/V)", "Piezoelectric coefficient"),
        (r"dielectric constant[^.]*?(\d+[\.\d]*)", "Dielectric constant"),
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
    excerpts = []
    lines = text.split("\n")

    if category == "PCL_based_polyurethane":
        keywords = ["polycaprolactone", "pcl", "caprolactone", "ring-opening",
                    "crystalliz", "degradation", "biocompat", "molecular weight",
                    "soft segment", "hard segment", "microphase", "mechanical"]
    else:  # biodegradable_polyurethane
        keywords = ["biodegradable", "degradation", "hydrolysis", "enzymatic",
                    "biocompat", "in vivo", "implant", "scaffold",
                    "tissue engineering", "cell", "apoptosis", "cytotoxic"]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in keywords:
            if kw in line_lower and len(line.strip()) > 30:
                context = line.strip()
                if i + 1 < len(lines):
                    context += " " + lines[i + 1].strip()
                if len(context) > 500:
                    context = context[:500] + "..."
                page_est = max(1, i // 40 + 1)
                excerpts.append({
                    "line_num": i + 1,
                    "page_est": page_est,
                    "text": context,
                    "keyword": kw,
                })
                break
        if len(excerpts) >= 5:
            break

    return excerpts


def deep_read_paper(card, category):
    pid = card["paper_id"]
    text = read_paper(pid)

    if not text:
        return {
            "paper_id": pid, "title": card.get("title", ""),
            "file_name": card.get("file_name", ""), "year": card.get("year", ""),
            "priority": card.get("priority", ""),
            "abstract": "evidence_missing", "conclusion": "evidence_missing",
            "methods": [], "performance_data": [], "figures": [],
            "evidence_excerpts": [], "extraction_quality": "poor",
            "notes": "needs_manual_check",
        }

    abstract = extract_abstract(text)
    conclusion = extract_conclusion(text)
    methods = extract_methods_from_text(text)
    performance = extract_performance_data(text)
    figures = extract_figures(text)
    excerpts = extract_evidence_excerpts(text, category)

    quality = "good"
    if not abstract:
        quality = "partial"
    if len(text) < 500:
        quality = "poor"

    return {
        "paper_id": pid, "title": card.get("title", ""),
        "file_name": card.get("file_name", ""), "year": card.get("year", ""),
        "priority": card.get("priority", ""),
        "abstract": abstract if abstract else "evidence_missing",
        "conclusion": conclusion if conclusion else "evidence_missing",
        "methods": methods, "performance_data": performance,
        "figures": figures, "evidence_excerpts": excerpts,
        "extraction_quality": quality, "notes": "",
    }


def write_category_review(category, results, cards):
    cat_display = category.replace("_", " ").title()
    lines = []
    lines.append(f"# Category Review: {cat_display}")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Papers reviewed: {len(results)}")
    lines.append("")

    prio_order = {"high": 0, "medium": 1, "low": 2}
    results_sorted = sorted(results, key=lambda x: prio_order.get(x["priority"], 2))

    # 1. Research Background
    lines.append("## 1. Research Background")
    lines.append("")
    if category == "PCL_based_polyurethane":
        lines.append("Polycaprolactone (PCL) is a biodegradable polyester widely used as the soft segment in polyurethane synthesis. PCL-based PUs combine the mechanical properties of polyurethane with the biocompatibility and degradability of PCL. Key parameters include PCL molecular weight, hard/soft segment ratio, and crystallinity, which collectively govern degradation rate, mechanical performance, and biological response.")
    else:
        lines.append("Biodegradable polyurethanes are designed to degrade in physiological conditions through hydrolytic or enzymatic pathways. They are widely used in tissue engineering scaffolds, drug delivery systems, and implantable devices. Key challenges include balancing mechanical performance with degradation rate, ensuring non-toxic degradation products, and maintaining biocompatibility throughout the degradation process.")
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

    # 3. Core Mechanisms
    lines.append("## 3. Core Mechanisms")
    lines.append("")
    if category == "PCL_based_polyurethane":
        lines.append("**PCL Synthesis and Characterization:**")
        lines.append("- Ring-opening polymerization (ROP) of caprolactone")
        lines.append("- Molecular weight control via initiator/catalyst ratio")
        lines.append("- Crystallization behavior and thermal properties")
        lines.append("")
        lines.append("**Structure-Property Relationships:**")
        lines.append("- PCL molecular weight → soft segment length → phase separation")
        lines.append("- Hard/soft segment ratio → mechanical properties")
        lines.append("- Crystallinity → degradation rate and mechanical strength")
    else:
        lines.append("**Degradation Mechanisms:**")
        lines.append("- Hydrolytic degradation (ester, urethane bonds)")
        lines.append("- Enzymatic degradation (lipase, esterase)")
        lines.append("- Surface erosion vs bulk degradation")
        lines.append("")
        lines.append("**Biological Response:**")
        lines.append("- Cell adhesion and proliferation")
        lines.append("- Cytotoxicity of degradation products")
        lines.append("- In vivo tissue response and integration")
    lines.append("")

    # 4-11: Key sections
    for section_title, section_content in [
        ("4. Key Characterization Evidence", None),
        ("5. Key Performance Data", None),
        ("6. Structure-Property Relationships", "(To be synthesized)"),
        ("7. Important Figures and Page References", None),
        ("8. Consensus Across Papers", "(To be synthesized)"),
        ("9. Contradictions Across Papers", "(To be synthesized)"),
        ("10. Research Gaps", "(To be synthesized)"),
        ("11. Implications for Research", "(To be synthesized)"),
    ]:
        lines.append(f"## {section_title}")
        lines.append("")
        if section_content:
            lines.append(section_content)
            lines.append("")
        elif "4." in section_title:
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
        elif "5." in section_title:
            for r in results_sorted:
                if r.get("performance_data"):
                    lines.append(f"**{r['paper_id']}**:")
                    for pd in r["performance_data"]:
                        lines.append(f"- {pd}")
                    lines.append("")
        elif "7." in section_title:
            for r in results_sorted:
                if r.get("figures"):
                    lines.append(f"**{r['paper_id']}**:")
                    for num, cap in r["figures"][:5]:
                        lines.append(f"- Figure {num}: {cap[:150]}")
                    lines.append("")

    # Evidence Table
    lines.append("## Evidence Table")
    lines.append("")
    lines.append("| Paper ID | Title | Year | Priority | Quality | Abstract | Conclusion | Key Methods |")
    lines.append("|----------|-------|------|----------|---------|----------|------------|-------------|")
    for r in results_sorted:
        has_abstract = "Yes" if r["abstract"] != "evidence_missing" else "No"
        has_conclusion = "Yes" if r["conclusion"] != "evidence_missing" else "No"
        methods_str = ", ".join(r["methods"][:3]) if r["methods"] else "-"
        title_short = r["title"][:50] + ("..." if len(r["title"]) > 50 else "")
        lines.append(f"| {r['paper_id']} | {title_short} | {r['year']} | {r['priority']} | {r['extraction_quality']} | {has_abstract} | {has_conclusion} | {methods_str} |")
    lines.append("")

    review_file = REVIEW_DIR / f"{category}.md"
    review_file.write_text("\n".join(lines), encoding="utf-8")
    return review_file


def write_evidence_csv(category, results):
    csv_file = REVIEW_DIR / f"{category}_evidence.csv"
    fieldnames = [
        "paper_id", "title", "file_name", "year", "priority",
        "extraction_quality", "evidence_type", "evidence_text",
        "page_est", "keyword", "confidence"
    ]

    rows = []
    for r in results:
        if r["abstract"] != "evidence_missing":
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": r["extraction_quality"],
                "evidence_type": "abstract", "evidence_text": r["abstract"][:500],
                "page_est": 1, "keyword": "abstract",
                "confidence": "high" if r["extraction_quality"] == "good" else "medium",
            })
        if r["conclusion"] != "evidence_missing":
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": r["extraction_quality"],
                "evidence_type": "conclusion", "evidence_text": r["conclusion"][:500],
                "page_est": "end", "keyword": "conclusion",
                "confidence": "high" if r["extraction_quality"] == "good" else "medium",
            })
        for exc in r.get("evidence_excerpts", []):
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": r["extraction_quality"],
                "evidence_type": "excerpt", "evidence_text": exc["text"],
                "page_est": exc["page_est"], "keyword": exc["keyword"],
                "confidence": "medium",
            })
        for pd in r.get("performance_data", []):
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": r["extraction_quality"],
                "evidence_type": "performance_data", "evidence_text": pd,
                "page_est": "", "keyword": "performance", "confidence": "medium",
            })
        for num, cap in r.get("figures", []):
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": r["extraction_quality"],
                "evidence_type": "figure_caption", "evidence_text": cap[:300],
                "page_est": "", "keyword": f"Figure {num}", "confidence": "medium",
            })

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return csv_file


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 2 Batch 3: Deep Reading")
    print()

    cards = load_cards()
    print(f"  Loaded {len(cards)} refined cards")

    total_processed = 0
    needs_manual = []

    for category in BATCH3_CATEGORIES:
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
                print(f" [POOR]")
            elif result["extraction_quality"] == "partial":
                print(f" [PARTIAL]")
            else:
                print(f" [OK]")

            total_processed += 1

        review_file = write_category_review(category, results, cards)
        print(f"    Written: {review_file}")

        evidence_file = write_evidence_csv(category, results)
        print(f"    Written: {evidence_file}")

        good = sum(1 for r in results if r["extraction_quality"] == "good")
        partial = sum(1 for r in results if r["extraction_quality"] == "partial")
        poor = sum(1 for r in results if r["extraction_quality"] == "poor")
        print(f"    Quality: {good} good, {partial} partial, {poor} poor")

    print()
    print(f"[{datetime.now():%H:%M:%S}] Batch 3 Complete")
    print(f"  Total processed: {total_processed}")
    print(f"  Needs manual check: {len(needs_manual)}")
    print()
    print("  Output files:")
    for category in BATCH3_CATEGORIES:
        print(f"    data/analysis/category_reviews/{category}.md")
        print(f"    data/analysis/category_reviews/{category}_evidence.csv")

    if needs_manual:
        print()
        print("  Papers needing manual check:")
        for nm in needs_manual:
            title_safe = nm['title'][:60].encode('ascii', 'replace').decode('ascii')
            print(f"    {nm['paper_id']}: {title_safe}")


if __name__ == "__main__":
    main()
