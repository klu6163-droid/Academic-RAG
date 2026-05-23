#!/usr/bin/env python3
"""
Phase 2 Batch 4: Deep read PVDF/Piezo Biomaterials + SAXS/WAXS/FTIR/DSC.
Enhanced evidence CSV with claim_type, relevance, ML_feature_candidate tagging.
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

BATCH4_CATEGORIES = [
    "PVDF_piezoelectric_biomaterials",
    "SAXS_WAXS_FTIR_DSC_characterization",
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
        "waxs": "WAXS", "wide-angle x-ray": "WAXS", "waxd": "WAXD",
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
        "xrd": "XRD", "x-ray diffraction": "XRD",
        "piezoelectric": "Piezoelectric Measurement",
        "ferroelectric": "Ferroelectric Measurement",
        "d33": "Piezoelectric Measurement",
        "polarization": "Polarization Measurement",
        "impedance": "Impedance Spectroscopy",
        "uv-vis": "UV-Vis Spectroscopy",
        "raman": "Raman Spectroscopy",
        "gel permeation": "GPC",
        "neutron": "Neutron Scattering",
        "synchrotron": "Synchrotron Characterization",
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
        (r"melting (?:temperature|point)[^.]*?(\-?\d+[\.\d]*)\s*°?C", "Tm"),
        (r"degradation[^.]*?(\d+[\.\d]*)\s*%", "Degradation"),
        (r"molecular weight[^.]*?(\d+[\.\d]*)\s*(kDa|Da|g/mol)", "Molecular weight"),
        (r"crystallinity[^.]*?(\d+[\.\d]*)\s*%", "Crystallinity"),
        (r"water uptake[^.]*?(\d+[\.\d]*)\s*%", "Water uptake"),
        # Piezoelectric specific
        (r"d33[^.]*?(\d+[\.\d]*)\s*(pC/N|pm/V)", "d33"),
        (r"d31[^.]*?(\d+[\.\d]*)\s*(pC/N|pm/V)", "d31"),
        (r"piezoelectric coefficient[^.]*?(\d+[\.\d]*)\s*(pC/N|pm/V)", "Piezoelectric coefficient"),
        (r"dielectric constant[^.]*?(\d+[\.\d]*)", "Dielectric constant"),
        (r"curie temperature[^.]*?(\d+[\.\d]*)\s*°?C", "Curie temperature"),
        # SAXS/WAXS specific
        (r"(?:long period|long-spacing)[^.]*?(\d+[\.\d]*)\s*(nm|A|angstrom)", "Long period"),
        (r"peak position[^.]*?(\d+[\.\d]*)\s*(nm|A|angstrom|degrees)", "SAXS peak position"),
        (r"fwhm[^.]*?(\d+[\.\d]*)", "FWHM"),
        (r"domain size[^.]*?(\d+[\.\d]*)\s*(nm|A)", "Domain size"),
        (r"d-spacing[^.]*?(\d+[\.\d]*)\s*(nm|A|angstrom)", "d-spacing"),
        # FTIR specific
        (r"hydrogen bond[^.]*?(\d+[\.\d]*)\s*(cm|%)", "H-bond metric"),
        (r"carbonyl[^.]*?(\d+[\.\d]*)\s*cm", "Carbonyl shift"),
        (r"absorbance ratio[^.]*?(\d+[\.\d]*)", "FTIR absorbance ratio"),
    ]
    text_lower = text.lower()
    for pat, label in patterns:
        m = re.search(pat, text_lower)
        if m:
            val = m.group(1)
            unit = m.group(2) if m.lastindex >= 2 else ""
            data.append(f"{label}: {val} {unit}".strip())
    return data[:10]


def extract_evidence_excerpts(text, category):
    excerpts = []
    lines = text.split("\n")

    if category == "PVDF_piezoelectric_biomaterials":
        keywords = ["pvdf", "poly(vinylidene", "piezoelectric", "beta-phase", "β-phase",
                    "d33", "d31", "polarization", "ferroelectric", "electroactive",
                    "cell response", "proliferation", "differentiation", "scaffold"]
    else:  # SAXS_WAXS_FTIR_DSC_characterization
        keywords = ["saxs", "waxs", "small-angle", "wide-angle", "ftir",
                    "dsc", "differential scanning", "crystalliz", "microphase",
                    "hydrogen bond", "melting", "glass transition", "long period",
                    "peak position", "fwhm", "domain size", "lamellar"]

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
        if len(excerpts) >= 6:
            break

    return excerpts


def classify_evidence_relevance(text, category):
    """Classify evidence relevance to user's research topics."""
    text_lower = text.lower()
    # High relevance to PU microphase separation and mechanics
    pu_keywords = ["polyurethane", "microphase separation", "hard segment",
                   "soft segment", "phase separation", "hydrogen bond",
                   "elastomer", "toughness", "fatigue", "strain-induced"]
    # ML feature candidate keywords
    ml_keywords = ["peak position", "fwhm", "domain size", "crystallinity",
                   "glass transition", "melting", "modulus", "tensile strength",
                   "elongation", "toughness", "d-spacing", "long period"]

    relevance = "standard"
    for kw in pu_keywords:
        if kw in text_lower:
            relevance = "high_relevance_pu"
            break

    ml_feature = False
    for kw in ml_keywords:
        if kw in text_lower:
            ml_feature = True
            break

    return relevance, ml_feature


def classify_claim_type(text):
    """Classify the type of scientific claim."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["we found", "results show", "demonstrate", "reveal", "observe"]):
        return "finding"
    elif any(kw in text_lower for kw in ["method", "procedure", "protocol", "characterized by"]):
        return "method"
    elif any(kw in text_lower for kw in ["property", "value", "measured", "obtained"]):
        return "measurement"
    elif any(kw in text_lower for kw in ["suggest", "propose", "indicate", "imply"]):
        return "interpretation"
    else:
        return "general"


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
    quality_notes = []
    if not abstract:
        quality = "partial"
        quality_notes.append("no abstract extracted")
    if len(text) < 500:
        quality = "poor"
        quality_notes.append("text too short")
    if not conclusion and quality != "poor":
        if quality == "good":
            quality = "partial"
        quality_notes.append("no conclusion extracted")
    if not methods:
        quality_notes.append("no methods detected")

    return {
        "paper_id": pid, "title": card.get("title", ""),
        "file_name": card.get("file_name", ""), "year": card.get("year", ""),
        "priority": card.get("priority", ""),
        "abstract": abstract if abstract else "evidence_missing",
        "conclusion": conclusion if conclusion else "evidence_missing",
        "methods": methods, "performance_data": performance,
        "figures": figures, "evidence_excerpts": excerpts,
        "extraction_quality": quality,
        "notes": "; ".join(quality_notes) if quality_notes else "",
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
    if category == "PVDF_piezoelectric_biomaterials":
        lines.append("Poly(vinylidene fluoride) (PVDF) and its copolymers exhibit piezoelectric properties源于极性β相晶型。PVDF基压电生物材料在组织工程、自供电传感器、药物递送等领域有广泛应用。关键参数包括β相含量、压电系数(d33/d31)、极化方式、生物相容性、以及力-电耦合对细胞行为的影响。")
    else:
        lines.append("SAXS/WAXS/FTIR/DSC是聚合物微结构表征的核心技术组合。SAXS提供纳米尺度结构信息（长周期、domain size、界面）；WAXS/XRD提供晶体结构和结晶度；FTIR揭示化学键状态和氢键相互作用；DSC测量热转变（Tg、Tm、Tc、ΔH）。这些表征手段对理解PU微相分离、结晶行为、结构-性能关系至关重要。")
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

    # 3. Core Mechanisms / Characterization Techniques
    lines.append("## 3. Core Mechanisms / Characterization Techniques")
    lines.append("")
    if category == "PVDF_piezoelectric_biomaterials":
        lines.append("**Piezoelectric Phase and Poling:**")
        lines.append("- α-phase to β-phase transition (mechanical stretching, electrical poling, electrospinning)")
        lines.append("- Piezoelectric coefficient d33 measurement (Berlincourt method, AFM-PFM)")
        lines.append("- Ferroelectric polarization hysteresis")
        lines.append("")
        lines.append("**Bioelectric Coupling:**")
        lines.append("- Piezoelectric signal → cell membrane potential change → proliferation/differentiation")
        lines.append("- Mechanical stimulation → electrical signal → osteogenic/neurogenic response")
        lines.append("- Self-powered implantable devices")
    else:
        lines.append("**SAXS Analysis Methods:**")
        lines.append("- Lorentz-corrected I(q) vs q plots")
        lines.append("- Long period from peak position: L = 2π/q*")
        lines.append("- Domain size, interface thickness from correlation function")
        lines.append("- FWHM → size distribution / disorder")
        lines.append("")
        lines.append("**FTIR Characterization:**")
        lines.append("- Hydrogen bonding index (HBI) from N-H / C=O peak shifts")
        lines.append("- Phase separation index from hard/soft segment absorbance ratios")
        lines.append("- Peak deconvolution for ordered vs disordered domains")
        lines.append("")
        lines.append("**DSC Analysis:**")
        lines.append("- Tg (soft segment), Tm (hard/soft segment), Tc")
        lines.append("- Crystallinity from ΔHf")
        lines.append("- Multiple endotherms → microphase mixing")
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
                if r["notes"]:
                    lines.append(f"- Notes: {r['notes']}")
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
        "extraction_quality", "evidence_type", "claim_type",
        "evidence_text", "figure_table_source", "page_est",
        "keyword", "confidence", "relevance", "ml_feature_candidate"
    ]

    rows = []
    for r in results:
        quality = r["extraction_quality"]
        conf_base = "high" if quality == "good" else ("medium" if quality == "partial" else "low")

        if r["abstract"] != "evidence_missing":
            relevance, ml_flag = classify_evidence_relevance(r["abstract"], category)
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": quality,
                "evidence_type": "abstract",
                "claim_type": classify_claim_type(r["abstract"]),
                "evidence_text": r["abstract"][:500],
                "figure_table_source": "abstract section",
                "page_est": 1, "keyword": "abstract",
                "confidence": conf_base,
                "relevance": relevance,
                "ml_feature_candidate": "TRUE" if ml_flag else "FALSE",
            })
        if r["conclusion"] != "evidence_missing":
            relevance, ml_flag = classify_evidence_relevance(r["conclusion"], category)
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": quality,
                "evidence_type": "conclusion",
                "claim_type": classify_claim_type(r["conclusion"]),
                "evidence_text": r["conclusion"][:500],
                "figure_table_source": "conclusion section",
                "page_est": "end", "keyword": "conclusion",
                "confidence": conf_base,
                "relevance": relevance,
                "ml_feature_candidate": "TRUE" if ml_flag else "FALSE",
            })
        for exc in r.get("evidence_excerpts", []):
            relevance, ml_flag = classify_evidence_relevance(exc["text"], category)
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": quality,
                "evidence_type": "excerpt",
                "claim_type": classify_claim_type(exc["text"]),
                "evidence_text": exc["text"],
                "figure_table_source": f"line {exc['line_num']}",
                "page_est": exc["page_est"], "keyword": exc["keyword"],
                "confidence": "medium",
                "relevance": relevance,
                "ml_feature_candidate": "TRUE" if ml_flag else "FALSE",
            })
        for pd in r.get("performance_data", []):
            relevance, ml_flag = classify_evidence_relevance(pd, category)
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": quality,
                "evidence_type": "performance_data",
                "claim_type": "measurement",
                "evidence_text": pd,
                "figure_table_source": "text extraction",
                "page_est": "", "keyword": "performance",
                "confidence": "medium",
                "relevance": relevance,
                "ml_feature_candidate": "TRUE",
            })
        for num, cap in r.get("figures", []):
            relevance, ml_flag = classify_evidence_relevance(cap, category)
            rows.append({
                "paper_id": r["paper_id"], "title": r["title"],
                "file_name": r["file_name"], "year": r["year"],
                "priority": r["priority"], "extraction_quality": quality,
                "evidence_type": "figure_caption",
                "claim_type": "measurement",
                "evidence_text": cap[:300],
                "figure_table_source": f"Figure {num}",
                "page_est": "", "keyword": f"Figure {num}",
                "confidence": "medium",
                "relevance": relevance,
                "ml_feature_candidate": "TRUE" if ml_flag else "FALSE",
            })

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return csv_file


def write_manual_check_list(category, results, cards):
    """Write manual check list for papers needing attention."""
    needs_check = []
    for r in results:
        if r["extraction_quality"] in ("poor", "partial"):
            card = next((c for c in cards if c["paper_id"] == r["paper_id"]), {})
            needs_check.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "quality": r["extraction_quality"],
                "reason": r["notes"] if r["notes"] else "see review",
                "priority": r["priority"],
            })
    return needs_check


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 2 Batch 4: Deep Reading")
    print()

    cards = load_cards()
    print(f"  Loaded {len(cards)} refined cards")

    total_processed = 0
    all_needs_manual = []

    for category in BATCH4_CATEGORIES:
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
                print(f" [POOR]")
            elif result["extraction_quality"] == "partial":
                print(f" [PARTIAL]")
            else:
                print(f" [OK]")

            total_processed += 1

        # Write review
        review_file = write_category_review(category, results, cards)
        print(f"    Written: {review_file}")

        # Write evidence CSV
        evidence_file = write_evidence_csv(category, results)
        print(f"    Written: {evidence_file}")

        # Collect manual check items
        manual_items = write_manual_check_list(category, results, cards)
        for item in manual_items:
            item["category"] = category
        all_needs_manual.extend(manual_items)

        good = sum(1 for r in results if r["extraction_quality"] == "good")
        partial = sum(1 for r in results if r["extraction_quality"] == "partial")
        poor = sum(1 for r in results if r["extraction_quality"] == "poor")
        print(f"    Quality: {good} good, {partial} partial, {poor} poor")

    # Write manual check list
    if all_needs_manual:
        manual_file = REVIEW_DIR / "batch4_manual_check_list.md"
        lines = []
        lines.append("# Batch 4 Manual Check List")
        lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
        lines.append(f"Papers needing attention: {len(all_needs_manual)}")
        lines.append("")
        lines.append("| Paper ID | Category | Title | Quality | Reason | Priority |")
        lines.append("|----------|----------|-------|---------|--------|----------|")
        for item in all_needs_manual:
            title_short = item['title'][:40] + ("..." if len(item['title']) > 40 else "")
            lines.append(f"| {item['paper_id']} | {item['category']} | {title_short} | {item['quality']} | {item['reason']} | {item['priority']} |")
        lines.append("")
        manual_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n    Written: {manual_file}")

    print()
    print(f"[{datetime.now():%H:%M:%S}] Batch 4 Complete")
    print(f"  Total processed: {total_processed}")
    print(f"  Needs manual check: {len(all_needs_manual)}")
    print()
    print("  Output files:")
    for category in BATCH4_CATEGORIES:
        print(f"    data/analysis/category_reviews/{category}.md")
        print(f"    data/analysis/category_reviews/{category}_evidence.csv")
    if all_needs_manual:
        print(f"    data/analysis/category_reviews/batch4_manual_check_list.md")


if __name__ == "__main__":
    main()
