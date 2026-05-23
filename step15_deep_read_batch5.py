#!/usr/bin/env python3
"""
Phase 2 Batch 5: Deep read Ionogel + ML for Polymer + Review/Background skim.
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

BATCH5_CATEGORIES = [
    "ionogel_or_magnetic_ionogel",
    "machine_learning_polymer_properties",
    "review_or_background",
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
        "impedance": "Impedance Spectroscopy",
        "neutron": "Neutron Scattering",
        # ML specific
        "random forest": "Random Forest",
        "neural network": "Neural Network",
        "deep learning": "Deep Learning",
        "transformer": "Transformer",
        "graph neural": "GNN",
        "support vector": "SVM",
        "gradient boosting": "Gradient Boosting",
        "cross-validation": "Cross-Validation",
        "machine learning": "Machine Learning",
        # Ionogel specific
        "ionic liquid": "Ionic Liquid",
        "ionic conductivity": "Ionic Conductivity",
        "self-heal": "Self-Healing",
        "stretchable": "Stretchability Test",
    }
    for kw, method in method_keywords.items():
        if kw in text_lower and method not in methods:
            methods.append(method)
    return methods[:12]


def extract_performance_data(text):
    data = []
    patterns = [
        (r"tensile strength[^.]*?(\d+[\.\d]*)\s*(MPa|GPa)", "Tensile strength"),
        (r"elongation at break[^.]*?(\d+[\.\d]*)\s*%", "Elongation at break"),
        (r"young'?s modulus[^.]*?(\d+[\.\d]*)\s*(MPa|GPa|kPa)", "Young's modulus"),
        (r"ionic conductivity[^.]*?(\d+[\.\d]*)\s*(S/m|mS|S/cm)", "Ionic conductivity"),
        (r"stretchab[^.]*?(\d+[\.\d]*)\s*%", "Stretchability"),
        (r"self-heal[^.]*?(\d+[\.\d]*)\s*%", "Self-healing efficiency"),
        (r"toughness[^.]*?(\d+[\.\d]*)\s*(MJ/m|kJ/m|J/m)", "Toughness"),
        (r"glass transition[^.]*?(\-?\d+[\.\d]*)\s*°?C", "Tg"),
        (r"r[\s_]?[²2][^.]*?(\d+[\.\d]*)", "R-squared"),
        (r"root mean square error[^.]*?(\d+[\.\d]*)", "RMSE"),
        (r"mean absolute error[^.]*?(\d+[\.\d]*)", "MAE"),
        (r"accuracy[^.]*?(\d+[\.\d]*)\s*%", "Accuracy"),
        (r"dielectric constant[^.]*?(\d+[\.\d]*)", "Dielectric constant"),
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

    if category == "ionogel_or_magnetic_ionogel":
        keywords = ["ionogel", "ionic liquid", "ionic gel", "ion gel",
                    "conductivity", "self-heal", "stretchable", "mechanical",
                    "metal salt", "coordination", "fecl", "magnetic",
                    "polyurethane", "hydrogen bond", "crosslink", "network"]
    elif category == "machine_learning_polymer_properties":
        keywords = ["machine learning", "neural network", "deep learning", "model",
                    "prediction", "feature", "descriptor", "training", "dataset",
                    "polymer", "property", "regression", "classification",
                    "transformer", "graph neural", "random forest"]
    else:  # review_or_background
        keywords = ["review", "overview", "progress", "recent advance",
                    "polyurethane", "microphase separation", "mechanical",
                    "self-heal", "shape memory", "biomaterial", "scaffold",
                    "piezoelectric", "ionic", "elastomer"]

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
    text_lower = text.lower()
    pu_keywords = ["polyurethane", "microphase separation", "hard segment",
                   "soft segment", "phase separation", "hydrogen bond",
                   "elastomer", "toughness", "fatigue", "strain-induced"]
    ml_keywords = ["peak position", "fwhm", "domain size", "crystallinity",
                   "glass transition", "melting", "modulus", "tensile strength",
                   "elongation", "toughness", "d-spacing", "long period",
                   "descriptor", "feature", "prediction"]

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


def skim_review_paper(card):
    """High-value skim for review/background papers — extract key arguments only."""
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
    figures = extract_figures(text)
    excerpts = extract_evidence_excerpts(text, "review_or_background")

    quality = "good"
    quality_notes = ["skim only"]
    if not abstract:
        quality = "partial"
        quality_notes.append("no abstract extracted")
    if len(text) < 500:
        quality = "poor"
        quality_notes.append("text too short")

    return {
        "paper_id": pid, "title": card.get("title", ""),
        "file_name": card.get("file_name", ""), "year": card.get("year", ""),
        "priority": card.get("priority", ""),
        "abstract": abstract if abstract else "evidence_missing",
        "conclusion": conclusion if conclusion else "evidence_missing",
        "methods": [], "performance_data": [],
        "figures": figures[:5], "evidence_excerpts": excerpts[:3],
        "extraction_quality": quality,
        "notes": "; ".join(quality_notes),
    }


def write_ionogel_review(results, cards):
    lines = []
    lines.append("# Category Review: Ionogel / Magnetic Ionogel")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Papers reviewed: {len(results)}")
    lines.append("")

    prio_order = {"high": 0, "medium": 1, "low": 2}
    results_sorted = sorted(results, key=lambda x: prio_order.get(x["priority"], 2))

    lines.append("## 1. Research Background")
    lines.append("")
    lines.append("Ionogels are polymer networks swollen with ionic liquids (ILs), combining the mechanical properties of gels with the ionic conductivity of ILs. Magnetic ionogels incorporate magnetic nanoparticles or paramagnetic ions (e.g., FeCl4-) for magneto-responsive behavior. Key applications include stretchable electronics, sensors, actuators, and energy storage devices.")
    lines.append("")

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

    lines.append("## 3. Ionic/Metal Salt/Ionic Liquid Components")
    lines.append("")
    lines.append("**Common Ionic Liquids:**")
    lines.append("- EMIM-TFSI, BMIM-TFSI, EMIM-BF4")
    lines.append("- Pyrrolidinium-based ILs")
    lines.append("- Protic ionic liquids (PILs)")
    lines.append("")
    lines.append("**Metal Salt / Magnetic Components:**")
    lines.append("- FeCl3 / FeCl4- based paramagnetic ILs")
    lines.append("- LiTFSI for lithium ion conduction")
    lines.append("- Metal-organic framework (MOF) fillers")
    lines.append("")

    lines.append("## 4. Polymer Network")
    lines.append("")
    lines.append("**Common Polymer Matrices:**")
    lines.append("- PVDF and copolymers")
    lines.append("- PMMA, PVA, PEG")
    lines.append("- Polyurethane-based ionogels")
    lines.append("- Silicone (PDMS)")
    lines.append("")

    lines.append("## 5. Interaction Mechanisms")
    lines.append("")
    lines.append("- Ion-dipole interactions between IL and polymer")
    lines.append("- Hydrogen bonding in PU-based ionogels")
    lines.append("- Coordination bonds with metal ions")
    lines.append("- Physical entanglement and crosslinking")
    lines.append("")

    for section_title, section_content in [
        ("6. Mechanical Properties", None),
        ("7. Electrical/Magnetic/Sensing Properties", None),
        ("8. Self-Healing or Stretchable Mechanisms", None),
        ("9. Relevance to PU and FeCl4/PU Simulation", None),
        ("10. Research Gaps", "(To be synthesized)"),
    ]:
        lines.append(f"## {section_title}")
        lines.append("")
        if section_content:
            lines.append(section_content)
            lines.append("")
        elif "6." in section_title:
            for r in results_sorted:
                if r.get("performance_data"):
                    lines.append(f"**{r['paper_id']}**:")
                    for pd in r["performance_data"]:
                        lines.append(f"- {pd}")
                    lines.append("")
        elif "9." in section_title:
            lines.append("**Direct PU relevance:**")
            for r in results:
                card = next((c for c in cards if c["paper_id"] == r["paper_id"]), {})
                mat = card.get("material_system", [])
                if "polyurethane" in mat or "tpu" in mat:
                    lines.append(f"- {r['paper_id']}: {r['title'][:60]}")
            lines.append("")
            lines.append("**FeCl4-/magnetic relevance:**")
            for r in results:
                for exc in r.get("evidence_excerpts", []):
                    if "fecl" in exc["text"].lower() or "magnetic" in exc["text"].lower() or "paramagnetic" in exc["text"].lower():
                        lines.append(f"- {r['paper_id']}: {exc['text'][:200]}")
                        break
            lines.append("")

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

    review_file = REVIEW_DIR / "ionogel_magnetic_ionogel.md"
    review_file.write_text("\n".join(lines), encoding="utf-8")
    return review_file


def write_ml_review(results, cards):
    lines = []
    lines.append("# Category Review: Machine Learning for Polymer Properties")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Papers reviewed: {len(results)}")
    lines.append("")

    prio_order = {"high": 0, "medium": 1, "low": 2}
    results_sorted = sorted(results, key=lambda x: prio_order.get(x["priority"], 2))

    lines.append("## 1. Research Background")
    lines.append("")
    lines.append("Machine learning (ML) is increasingly applied to polymer science for property prediction, materials discovery, and structure-property relationship modeling. Key challenges include limited training data, need for interpretable descriptors, and domain-specific feature engineering (e.g., SAXS/FTIR/DSC spectral features as ML inputs).")
    lines.append("")

    lines.append("## 2. Dataset Sources")
    lines.append("")
    for r in results_sorted:
        if r["abstract"] != "evidence_missing":
            lines.append(f"- **{r['paper_id']}**: {r['abstract'][:200]}...")
        elif r.get("evidence_excerpts"):
            lines.append(f"- **{r['paper_id']}**: {r['evidence_excerpts'][0]['text'][:200]}...")
        lines.append("")

    lines.append("## 3. Input Feature Types")
    lines.append("")
    lines.append("**Common polymer descriptors:**")
    lines.append("- SMILES / molecular fingerprints")
    lines.append("- Monomer composition and sequence")
    lines.append("- Molecular weight and distribution")
    lines.append("- Topological features (branching, crosslink density)")
    lines.append("")
    lines.append("**Spectroscopy features:**")
    lines.append("- FTIR peak positions and intensities")
    lines.append("- SAXS/WAXS peak positions and FWHM")
    lines.append("- DSC thermal transitions (Tg, Tm, ΔH)")
    lines.append("- Dielectric relaxation parameters")
    lines.append("")

    for section_title, section_content in [
        ("4. Model Types", None),
        ("5. Prediction Targets", None),
        ("6. Evaluation Metrics", None),
        ("7. Interpretability Methods", None),
        ("8. Suitability for PU Mechanical Property Prediction", None),
        ("9. Transferable Techniques", None),
        ("10. Data Gaps and Risks", None),
    ]:
        lines.append(f"## {section_title}")
        lines.append("")
        if section_content:
            lines.append(section_content)
            lines.append("")
        elif "4." in section_title:
            for r in results_sorted:
                methods = [m for m in r.get("methods", []) if m in
                          ["Random Forest", "Neural Network", "Deep Learning", "Transformer",
                           "GNN", "SVM", "Gradient Boosting", "Machine Learning"]]
                if methods:
                    lines.append(f"- **{r['paper_id']}**: {', '.join(methods)}")
            lines.append("")
        elif "8." in section_title:
            lines.append("**Assessment:**")
            for r in results_sorted:
                if r.get("evidence_excerpts"):
                    exc = r["evidence_excerpts"][0]
                    lines.append(f"- {r['paper_id']}: {exc['text'][:200]}")
                lines.append("")

    lines.append("## Evidence Table")
    lines.append("")
    lines.append("| Paper ID | Title | Year | Priority | Quality | ML Methods | Key Contribution |")
    lines.append("|----------|-------|------|----------|---------|------------|------------------|")
    for r in results_sorted:
        methods_str = ", ".join(r.get("methods", [])[:3]) if r.get("methods") else "-"
        title_short = r["title"][:40] + ("..." if len(r["title"]) > 40 else "")
        contrib = r["evidence_excerpts"][0]["text"][:80] if r.get("evidence_excerpts") else "-"
        lines.append(f"| {r['paper_id']} | {title_short} | {r['year']} | {r['priority']} | {r['extraction_quality']} | {methods_str} | {contrib} |")
    lines.append("")

    review_file = REVIEW_DIR / "ML_for_polymer_properties.md"
    review_file.write_text("\n".join(lines), encoding="utf-8")
    return review_file


def write_review_background(results, cards):
    lines = []
    lines.append("# High-Value Review / Background Papers")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Papers skimmed: {len(results)}")
    lines.append("")

    prio_order = {"high": 0, "medium": 1, "low": 2}
    results_sorted = sorted(results, key=lambda x: prio_order.get(x["priority"], 2))

    lines.append("## 1. High-Value Reviews")
    lines.append("")
    for r in results_sorted:
        if r["extraction_quality"] == "poor":
            continue
        lines.append(f"### {r['paper_id']}: {r['title'][:60]}")
        lines.append(f"- Priority: {r['priority']} | Year: {r['year']} | Quality: {r['extraction_quality']}")
        if r["abstract"] != "evidence_missing":
            lines.append(f"- **Key argument**: {r['abstract'][:300]}...")
        if r["conclusion"] != "evidence_missing":
            lines.append(f"- **Conclusion**: {r['conclusion'][:300]}...")
        if r.get("evidence_excerpts"):
            lines.append(f"- **Excerpt**: {r['evidence_excerpts'][0]['text'][:200]}...")
        lines.append("")

    lines.append("## 2. Relevance by Topic")
    lines.append("")

    topic_map = {
        "PU microphase separation": ["polyurethane", "microphase", "hard segment", "soft segment"],
        "Mechanical properties": ["mechanical", "toughness", "fatigue", "elastomer", "strength"],
        "PVDF / Piezoelectric": ["piezoelectric", "pvdf", "ferroelectric"],
        "Characterization methods": ["saxs", "ftir", "dsc", "characterization"],
        "Machine learning": ["machine learning", "neural network", "prediction"],
        "Ionogel / Ionic": ["ionogel", "ionic liquid", "conductivity"],
        "Biomaterials": ["biomaterial", "scaffold", "tissue", "cell"],
    }

    for topic, keywords in topic_map.items():
        relevant = []
        for r in results:
            text = (r.get("abstract", "") + " " + r.get("conclusion", "") + " " +
                    " ".join(e["text"] for e in r.get("evidence_excerpts", []))).lower()
            if any(kw in text for kw in keywords):
                relevant.append(r["paper_id"])
        if relevant:
            lines.append(f"**{topic}**: {', '.join(relevant)}")
            lines.append("")

    lines.append("## 3. Not Worth Further Processing")
    lines.append("")
    for r in results_sorted:
        if r["extraction_quality"] == "poor":
            lines.append(f"- {r['paper_id']}: {r['title'][:50]} — {r['notes']}")
    lines.append("")

    lines.append("## Evidence Table")
    lines.append("")
    lines.append("| Paper ID | Title | Year | Priority | Quality | Key Topics |")
    lines.append("|----------|-------|------|----------|---------|------------|")
    for r in results_sorted:
        title_short = r["title"][:45] + ("..." if len(r["title"]) > 45 else "")
        topics = []
        text = (r.get("abstract", "") + " " + " ".join(e["text"] for e in r.get("evidence_excerpts", []))).lower()
        for topic, keywords in topic_map.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        lines.append(f"| {r['paper_id']} | {title_short} | {r['year']} | {r['priority']} | {r['extraction_quality']} | {', '.join(topics[:3])} |")
    lines.append("")

    review_file = REVIEW_DIR / "review_background_high_value.md"
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
                "relevance": "standard",
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


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 2 Batch 5: Deep Reading + Skim")
    print()

    cards = load_cards()
    print(f"  Loaded {len(cards)} refined cards")

    total_processed = 0
    all_needs_manual = []

    for category in BATCH5_CATEGORIES:
        cat_cards = [c for c in cards if c["primary_category"] == category]
        cat_display = category.replace("_", " ").title()
        print(f"\n  === {cat_display}: {len(cat_cards)} papers ===")

        results = []
        for i, card in enumerate(cat_cards):
            pid = card["paper_id"]
            title_safe = card['title'][:50].encode('ascii', 'replace').decode('ascii')

            if category == "review_or_background":
                print(f"    [{i+1}/{len(cat_cards)}] {pid}: {title_safe}... [SKIM]", end="")
                result = skim_review_paper(card)
            else:
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

        # Write category-specific reviews
        if category == "ionogel_or_magnetic_ionogel":
            review_file = write_ionogel_review(results, cards)
        elif category == "machine_learning_polymer_properties":
            review_file = write_ml_review(results, cards)
        else:
            review_file = write_review_background(results, cards)
        print(f"    Written: {review_file}")

        # Write evidence CSV
        evidence_file = write_evidence_csv(category, results)
        print(f"    Written: {evidence_file}")

        # Collect manual check items
        for r in results:
            if r["extraction_quality"] in ("poor", "partial"):
                all_needs_manual.append({
                    "paper_id": r["paper_id"],
                    "category": category,
                    "title": r["title"],
                    "quality": r["extraction_quality"],
                    "reason": r["notes"] if r["notes"] else "see review",
                    "priority": r["priority"],
                })

        good = sum(1 for r in results if r["extraction_quality"] == "good")
        partial = sum(1 for r in results if r["extraction_quality"] == "partial")
        poor = sum(1 for r in results if r["extraction_quality"] == "poor")
        print(f"    Quality: {good} good, {partial} partial, {poor} poor")

    # Write manual check list
    if all_needs_manual:
        manual_file = REVIEW_DIR / "batch5_manual_check_list.md"
        lines = []
        lines.append("# Batch 5 Manual Check List")
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
    print(f"[{datetime.now():%H:%M:%S}] Batch 5 Complete")
    print(f"  Total processed: {total_processed}")
    print(f"  Needs manual check: {len(all_needs_manual)}")
    print()
    print("  Output files:")
    print(f"    data/analysis/category_reviews/ionogel_magnetic_ionogel.md")
    print(f"    data/analysis/category_reviews/ionogel_magnetic_ionogel_evidence.csv")
    print(f"    data/analysis/category_reviews/ML_for_polymer_properties.md")
    print(f"    data/analysis/category_reviews/ML_for_polymer_properties_evidence.csv")
    print(f"    data/analysis/category_reviews/review_background_high_value.md")
    print(f"    data/analysis/category_reviews/review_background_high_value_evidence.csv")
    if all_needs_manual:
        print(f"    data/analysis/category_reviews/batch5_manual_check_list.md")


if __name__ == "__main__":
    main()
