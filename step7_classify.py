#!/usr/bin/env python3
"""
Phase 1: Lightweight classification of all papers (v2 - improved rules).
Reads extracted texts, extracts title/abstract/keywords/conclusion/captions,
classifies into categories, saves paper_cards.jsonl with checkpoints.
"""

import json
import re
import csv
import os
from pathlib import Path
from datetime import datetime

# Paths
EXTRACTED_DIR = Path(r"D:\Academic-RAG\06_logs\extracted_texts")
METADATA_CSV = Path(r"D:\Academic-RAG\00_manifest\literature_metadata.csv")
OUTPUT_DIR = Path(r"D:\Academic-RAG\data\analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path(r"D:\Academic-RAG\data\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

CARDS_FILE = OUTPUT_DIR / "paper_cards.jsonl"
FAILED_FILE = LOG_DIR / "failed_analysis.csv"
CHECKPOINT_EVERY = 20

# ─── Category definitions ────────────────────────────────────────────────
# Each category has:
#   required: keywords that MUST be present (at least one)
#   boost: additional keywords that increase score
#   min_score: minimum score to assign this category

CATEGORIES = {
    "polyurethane_microphase_separation": {
        "required": ["polyurethane", "tpu", "thermoplastic polyurethane", "pu "],
        "boost": ["microphase separation", "hard segment", "soft segment", "domain", "phase separation", "hydrogen bond", "h-bond", "urethane", "nanophase", "hard domain", "soft domain"],
        "min_score": 1.5,
    },
    "shape_memory_polyurethane": {
        "required": ["shape memory", "shape-memory"],
        "boost": ["polyurethane", "tpu", "recovery ratio", "fixity ratio", "switching temperature", "programming", "recovery stress", "two-way", "triple shape", "multi-shape"],
        "min_score": 1.0,
    },
    "biodegradable_polyurethane": {
        "required": ["polyurethane", "tpu", "thermoplastic polyurethane"],
        "boost": ["biodegradable", "degradation", "biocompatible", "scaffold", "tissue engineering", "cell", "cytotoxic", "in vivo", "in vitro", "implant", "wound healing", "biomedical"],
        "min_score": 1.5,
    },
    "PCL_based_polyurethane": {
        "required": ["polycaprolactone", "pcl", "caprolactone", "pcl-pu", "pclu"],
        "boost": ["polyurethane", "tpu", "soft segment", "elastomer", "shape memory", "biodegradable"],
        "min_score": 1.0,
    },
    "TPU_mechanics": {
        "required": ["polyurethane", "tpu", "thermoplastic polyurethane"],
        "boost": ["tensile strength", "elongation at break", "fracture", "fatigue", "tear", "modulus", "toughness", "resilience", "cyclic", "stress-strain", "notch", "crack", "mechanical properties", "strain hardening", "self-healing", "elastomer"],
        "min_score": 1.5,
    },
    "PVDF_piezoelectric_biomaterials": {
        "required": ["pvdf", "polyvinylidene fluoride", "piezoelectric"],
        "boost": ["ferroelectric", "beta phase", "electroactive", "polarization", "poling", "biomaterial", "scaffold", "tissue", "cell", "sensor"],
        "min_score": 1.0,
    },
    "protein_adsorption_cell_response": {
        "required": ["protein adsorption", "cell adhesion", "cell response", "fibroblast", "osteoblast", "stem cell", "proliferation", "differentiation", "hemocompatibility", "blood compatibility"],
        "boost": ["biocompatibility", "surface", "biomaterial", "scaffold", "polyurethane"],
        "min_score": 1.0,
    },
    "SAXS_WAXS_FTIR_DSC_characterization": {
        "required": ["saxs", "small-angle x-ray scattering", "waxs", "wide-angle x-ray", "waxd"],
        "boost": ["ftir", "ft-ir", "infrared", "dsc", "differential scanning", "dma", "dynamic mechanical", "thermogravimetric", "tga", "polyurethane", "crystallization", "phase separation"],
        "min_score": 1.0,
    },
    "machine_learning_polymer_properties": {
        "required": ["machine learning", "neural network", "deep learning", "random forest", "support vector", "gradient boosting", "artificial intelligence", "convolutional neural", "recurrent neural"],
        "boost": ["prediction", "training", "regression", "classification", "feature", "dataset", "polymer", "property prediction", "structure-property"],
        "min_score": 1.5,  # Higher threshold to avoid false positives
    },
    "ionogel_or_magnetic_ionogel": {
        "required": ["ionogel", "ionic liquid", "ionic gel", "ionic conductor"],
        "boost": ["ionic conductivity", "electrolyte", "magnetic", "ferrofluid", "gel", "polymer", "polyurethane"],
        "min_score": 1.0,
    },
    "review_or_background": {
        "required": ["review", "perspective", "overview", "progress", "recent advances", "state of the art", "comprehensive review", "50th anniversary"],
        "boost": [],
        "min_score": 0.5,
    },
    "self_healing_elastomer": {
        "required": ["self-heal", "self-healing", "healable"],
        "boost": ["polyurethane", "tpu", "elastomer", "dynamic bond", "reversible", "hydrogen bond", "disulfide", "diels-alder"],
        "min_score": 1.0,
    },
    "supramolecular_polymer": {
        "required": ["supramolecular", "host-guest", "cyclodextrin", "cucurbituril", "inclusion complex"],
        "boost": ["polyurethane", "elastomer", "self-assembly", "hydrogen bond", "non-covalent"],
        "min_score": 1.0,
    },
    "bio_based_polymer": {
        "required": ["bio-based", "biobased", "renewable", "natural oil", "castor", "soybean", "vegetable oil", "biomass", "cellulose", "chitosan", "collagen", "gelatin", "silk", "keratin"],
        "boost": ["polyurethane", "elastomer", "sustainable", "green chemistry"],
        "min_score": 1.0,
    },
    "polymer_nanocomposite": {
        "required": ["nanocomposite", "nanoparticle", "nanofiber", "nanotube", "graphene", "carbon nanotube", "clay", "montmorillonite", "silica nanoparticle"],
        "boost": ["polyurethane", "elastomer", "mechanical", "thermal", "reinforcement", "filler"],
        "min_score": 1.0,
    },
    "polymer_blend": {
        "required": ["blend", "polymer blend", "miscibility", "compatibiliz"],
        "boost": ["polyurethane", "elastomer", "phase behavior", "interfacial"],
        "min_score": 1.0,
    },
}


def load_metadata():
    """Load paper metadata from CSV."""
    metadata = {}
    with open(METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get("paper_id", "").strip()
            if pid:
                metadata[pid] = row
    return metadata


def extract_sections(text):
    """Extract lightweight sections from paper text."""
    result = {
        "title": "",
        "abstract": "",
        "keywords": "",
        "intro_snippet": "",
        "conclusion": "",
        "figure_captions": "",
    }

    lines = text.split("\n")
    if not lines:
        return result

    # Title: first substantive line (skip headers, journal info)
    skip_patterns = [
        "pubs.acs", "cite this", "access", "metrics", "supporting",
        "journal", "doi", "read online", "article", "research article",
        "perspective", "communication", "view article", "this article",
        "corrected", "open access", "acs", "wiley", "springer", "nature",
        "rsc", "elsevier", "royal society", "american chemical",
        "received", "revised", "accepted", "published", "copyright",
    ]
    for line in lines[:15]:
        line = line.strip()
        if not line or len(line) < 8:
            continue
        if any(p in line.lower() for p in skip_patterns):
            continue
        if re.match(r"^\d+$", line):  # Just a number
            continue
        result["title"] = line
        break

    # Abstract
    abstract_patterns = [
        r"(?:ABSTRACT|Abstract)[:\s]+(.+?)(?:\n\s*(?:INTRODUCTION|Introduction|KEYWORDS|Keywords|■|\n\n\n))",
        r"(?:ABSTRACT|Abstract)[:\s]+(.+?)(?:\n\s*\n)",
    ]
    for pat in abstract_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 50:
            result["abstract"] = m.group(1).strip()[:2000]
            break

    # Keywords
    kw_match = re.search(
        r"(?:KEYWORDS|Keywords)[:\s]+(.+?)(?:\n\s*\n|\n\s*(?:INTRODUCTION|■))",
        text, re.DOTALL | re.IGNORECASE
    )
    if kw_match:
        result["keywords"] = kw_match.group(1).strip()[:500]

    # Introduction snippet
    intro_match = re.search(
        r"(?:INTRODUCTION|Introduction)[:\s]+(.+?)(?:\n\s*\n\s*\n|\n\s*(?:RESULTS|EXPERIMENTAL|METHODS|THEORY|■))",
        text, re.DOTALL | re.IGNORECASE
    )
    if intro_match:
        result["intro_snippet"] = intro_match.group(1).strip()[:800]

    # Conclusion
    conclusion_match = re.search(
        r"(?:CONCLUSIONS?|CONCLUDING|SUMMARY|DISCUSSION\s+(?:AND|&)\s+CONCLUSIONS?)[:\s]+(.+?)(?:\n\s*(?:REFERENCES|ACKNOWLEDG|AUTHOR|ASSOCIATED|■|$))",
        text, re.DOTALL | re.IGNORECASE
    )
    if conclusion_match:
        result["conclusion"] = conclusion_match.group(1).strip()[:2000]

    # Figure captions
    fig_captions = re.findall(
        r"(?:Figure|Fig\.?)\s*\d+[.:]\s*(.+?)(?:\n\s*\n|\n\s*(?:Figure|Fig\.?))",
        text, re.DOTALL | re.IGNORECASE
    )
    if fig_captions:
        result["figure_captions"] = " | ".join(c.strip()[:200] for c in fig_captions[:10])

    return result


def classify_paper(title, abstract, keywords, intro, conclusion, fig_captions):
    """Classify paper into categories based on required+boost keyword matching."""
    combined = f"{title} {abstract} {keywords} {intro} {conclusion} {fig_captions}".lower()

    scores = {}
    for cat, info in CATEGORIES.items():
        # Check required keywords
        has_required = any(rk in combined for rk in info["required"])
        if not has_required:
            continue

        # Base score for having required keywords
        score = 1.0

        # Boost score
        for bk in info["boost"]:
            if bk in combined:
                score += 0.5

        if score >= info["min_score"]:
            scores[cat] = score

    # Build result
    if not scores:
        # Try supplementary detection
        if any(kw in combined for kw in ["supplementary", "supporting information", "supplemental"]):
            return "irrelevant_or_low_priority", [], "low", "Supplementary material", "high"
        return "irrelevant_or_low_priority", [], "low", "No category keywords matched", "low"

    sorted_cats = sorted(scores.items(), key=lambda x: -x[1])
    primary = sorted_cats[0][0]
    secondary = [c for c, _ in sorted_cats[1:4]]  # Top 3 secondary

    # Confidence based on score gap
    if len(sorted_cats) >= 2:
        gap = sorted_cats[0][1] - sorted_cats[1][1]
        if gap >= 2:
            confidence = "high"
        elif gap >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "high" if sorted_cats[0][1] >= 3 else "medium"

    # Priority
    priority, reason = determine_priority(primary, scores, combined)

    return primary, secondary, priority, reason, confidence


def determine_priority(primary, scores, combined):
    """Determine reading priority."""
    high_keywords = [
        "thermoplastic polyurethane", "tpu", "microphase separation",
        "shape memory", "polycaprolactone", "pcl",
        "biodegradable", "scaffold", "tissue engineering",
        "fatigue", "fracture toughness", "self-healing",
        "saxs", "waxs", "ftir",
    ]
    high_count = sum(1 for kw in high_keywords if kw in combined)

    if primary == "irrelevant_or_low_priority":
        return "low", "Not directly relevant to core research topics"
    elif primary == "review_or_background":
        return "medium", "Review/background paper for context"
    elif high_count >= 4:
        return "high", f"Highly relevant: {high_count} core keywords matched"
    elif high_count >= 2:
        return "medium", f"Related: {high_count} core keywords matched"
    elif scores.get(primary, 0) >= 3:
        return "medium", f"Strong category match (score={scores[primary]:.1f})"
    else:
        return "low", f"Weak category match (score={scores.get(primary, 0):.1f})"


def extract_materials(text):
    """Extract material system mentions."""
    text_lower = text.lower()
    materials = []
    material_keywords = [
        "polyurethane", "tpu", "thermoplastic polyurethane",
        "polycaprolactone", "pcl", "poly(caprolactone)",
        "polyvinylidene fluoride", "pvdf",
        "polyethylene", "pe ", "hdpe", "ldpe", "lldpe",
        "polypropylene", "pp ",
        "polystyrene", "ps ",
        "polyamide", "nylon", "pa6", "pa66",
        "polyacrylate", "polyacrylamide", "pam",
        "polyvinyl alcohol", "pva",
        "poly(methyl methacrylate)", "pmma",
        "polydimethylsiloxane", "pdms",
        "polyethylene glycol", "peg",
        "polyimide", "pi ",
        "polylactic acid", "pla",
        "polyglycolic acid", "pga",
        "polylactic-co-glycolic", "plga",
        "chitosan", "collagen", "gelatin", "cellulose", "silk",
        "keratin", "hyaluronic acid", "alginate",
        "hydrogel", "elastomer", "rubber", "foam",
        "ionic liquid", "ionogel", "organogel",
        "block copolymer", "graft copolymer", "random copolymer",
        "nanocomposite", "composite", "filler",
        "graphene", "carbon nanotube", "cnt", "silica", "clay",
        "tio2", "zno", "fe3o4", "batio3",
    ]
    for mk in material_keywords:
        if mk in text_lower:
            materials.append(mk.strip())
    return list(set(materials))[:10]


def extract_methods(text):
    """Extract method mentions."""
    text_lower = text.lower()
    methods = []
    method_keywords = [
        "saxs", "small-angle x-ray scattering",
        "waxs", "wide-angle x-ray scattering", "waxd",
        "ftir", "ft-ir", "fourier transform infrared",
        "dsc", "differential scanning calorimetry",
        "dma", "dynamic mechanical analysis",
        "tga", "thermogravimetric analysis",
        "tensile test", "stress-strain", "mechanical test",
        "sem", "scanning electron microscopy",
        "tem", "transmission electron microscopy",
        "afm", "atomic force microscopy",
        "nmr", "nuclear magnetic resonance",
        "xrd", "x-ray diffraction",
        "rheology", "rheometer", "viscoelastic",
        "uv-vis", "fluorescence spectroscopy",
        "cell culture", "mtt assay", "cytotoxicity",
        "3d printing", "electrospinning", "electrospun",
        "molecular dynamics", "md simulation", "dft",
        "gpc", "sec", "size exclusion",
        "contact angle", "water contact angle",
        "impedance spectroscopy", "dielectric",
    ]
    for mk in method_keywords:
        if mk in text_lower:
            methods.append(mk)
    return list(set(methods))[:10]


def extract_properties(text):
    """Extract property mentions."""
    text_lower = text.lower()
    properties = []
    prop_keywords = [
        "tensile strength", "elongation at break", "young's modulus",
        "toughness", "resilience", "hardness", "compressive strength",
        "glass transition temperature", "melting temperature", "tg", "tm",
        "crystallization temperature", "tc",
        "thermal stability", "decomposition temperature",
        "biocompatibility", "cytotoxicity", "cell viability",
        "ionic conductivity", "conductivity",
        "piezoelectric coefficient", "piezoelectric",
        "shape memory ratio", "recovery ratio", "fixity ratio",
        "self-healing efficiency", "healing efficiency",
        "water absorption", "swelling ratio",
        "degradation rate", "biodegradation",
        "fatigue life", "crack propagation", "tear strength",
        "protein adsorption", "cell adhesion", "hemolysis",
        "contact angle", "hydrophilicity", "hydrophobicity",
    ]
    for pk in prop_keywords:
        if pk in text_lower:
            properties.append(pk)
    return list(set(properties))[:10]


def extract_applications(text):
    """Extract application mentions."""
    text_lower = text.lower()
    applications = []
    app_keywords = [
        "tissue engineering", "scaffold", "implant", "drug delivery",
        "wound healing", "bone regeneration", "cartilage repair",
        "sensor", "actuator", "energy harvesting", "energy storage",
        "coating", "adhesive", "sealant",
        "packaging", "membrane", "filtration",
        "3d printing", "additive manufacturing",
        "soft robotics", "wearable device", "flexible electronics",
        "biomedical", "medical device", "catheter", "stent",
        "automotive", "footwear", "textile",
    ]
    for ak in app_keywords:
        if ak in text_lower:
            applications.append(ak)
    return list(set(applications))[:8]


def process_paper(pid, metadata):
    """Process a single paper."""
    txt_file = EXTRACTED_DIR / f"{pid}.txt"
    if not txt_file.exists():
        return None, f"File not found: {txt_file}"

    text = txt_file.read_text(encoding="utf-8", errors="replace").strip()
    if not text or len(text) < 50:
        return None, f"File too short or empty ({len(text)} chars)"

    # Extract sections
    sections = extract_sections(text)

    # Get metadata
    meta = metadata.get(pid, {})
    title = sections["title"] or meta.get("title", "")
    year = meta.get("year", "")
    doi = meta.get("DOI", "")
    file_name = meta.get("english_safe_file_name", meta.get("original_file_name", ""))

    # If title from metadata is better, use it
    meta_title = meta.get("title", "")
    if meta_title and len(meta_title) > len(title) and not any(x in meta_title.lower() for x in ["research article", "view article", "supporting"]):
        title = meta_title

    # Classify
    primary, secondary, priority, reason, confidence = classify_paper(
        title, sections["abstract"], sections["keywords"],
        sections["intro_snippet"], sections["conclusion"],
        sections["figure_captions"]
    )

    # Extract entities
    full_text = f"{title} {sections['abstract']} {sections['keywords']} {sections['intro_snippet']} {sections['conclusion']}"
    materials = extract_materials(full_text)
    methods = extract_methods(full_text)
    properties = extract_properties(full_text)
    applications = extract_applications(full_text)

    card = {
        "paper_id": pid,
        "file_name": file_name,
        "title": title,
        "year": year,
        "doi": doi,
        "primary_category": primary,
        "secondary_categories": secondary,
        "material_system": materials,
        "methods": methods,
        "properties": properties,
        "application": applications,
        "priority": priority,
        "reason": reason,
        "key_pages": [],
        "confidence": confidence,
        "abstract_preview": sections["abstract"][:300] if sections["abstract"] else "",
    }

    return card, None


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 1: Lightweight Classification (v2)")
    print(f"  Extracted texts: {EXTRACTED_DIR}")
    print(f"  Output: {CARDS_FILE}")
    print()

    # Load metadata
    metadata = load_metadata()
    print(f"  Loaded metadata for {len(metadata)} papers")

    # Get all paper IDs
    all_pids = sorted([
        f.stem for f in EXTRACTED_DIR.glob("P*.txt")
        if f.stat().st_size > 0
    ])
    print(f"  Found {len(all_pids)} non-empty extracted text files")

    # Clear previous output (v2 rewrite)
    if CARDS_FILE.exists():
        CARDS_FILE.unlink()

    # Process
    processed = 0
    failed = 0
    failed_records = []

    with open(CARDS_FILE, "w", encoding="utf-8") as out_f:
        for i, pid in enumerate(all_pids):
            card, error = process_paper(pid, metadata)

            if error:
                failed += 1
                failed_records.append({"paper_id": pid, "error": error})
            else:
                out_f.write(json.dumps(card, ensure_ascii=False) + "\n")
                processed += 1

            # Checkpoint
            if (processed + failed) % CHECKPOINT_EVERY == 0:
                out_f.flush()
                print(f"  [{datetime.now():%H:%M:%S}] Checkpoint: {processed} processed, {failed} failed")

    # Write failed records
    if failed_records:
        with open(FAILED_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["paper_id", "error"])
            writer.writeheader()
            writer.writerows(failed_records)

    print()
    print(f"[{datetime.now():%H:%M:%S}] Phase 1 Complete")
    print(f"  Total processed: {processed}")
    print(f"  Failed: {failed}")
    print(f"  Output: {CARDS_FILE}")
    if failed_records:
        print(f"  Failed log: {FAILED_FILE}")


if __name__ == "__main__":
    main()
