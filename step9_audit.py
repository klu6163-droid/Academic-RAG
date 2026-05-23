#!/usr/bin/env python3
"""
Phase 1 Audit: Count, deduplicate, audit irrelevant, check extraction quality.
Outputs: phase1_audit.md, duplicates.csv, deduplicated_paper_cards.jsonl,
         irrelevant_audit.csv, poor_extraction_papers.csv
"""

import json
import csv
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher

# Paths
PDF_DIR = Path(r"D:\Academic-RAG\paper")
EXTRACTED_DIR = Path(r"D:\Academic-RAG\06_logs\extracted_texts")
METADATA_CSV = Path(r"D:\Academic-RAG\00_manifest\literature_metadata.csv")
CARDS_FILE = Path(r"D:\Academic-RAG\data\analysis\paper_cards.jsonl")
OUT_DIR = Path(r"D:\Academic-RAG\data\analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_metadata():
    metadata = {}
    with open(METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get("paper_id", "").strip()
            if pid:
                metadata[pid] = row
    return metadata


def load_cards():
    cards = []
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))
    return cards


def similar(a, b, threshold=0.75):
    """Check if two strings are similar above threshold."""
    if not a or not b:
        return False
    a_clean = re.sub(r'\s+', ' ', a.lower().strip())
    b_clean = re.sub(r'\s+', ' ', b.lower().strip())
    if a_clean == b_clean:
        return True
    return SequenceMatcher(None, a_clean, b_clean).ratio() >= threshold


def step1_count_pdfs(metadata):
    """Count all PDFs and their status."""
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    total_pdfs = len(pdf_files)

    # Map PDFs to paper IDs
    pdf_to_pid = {}
    pid_to_pdf = {}
    for row in metadata.values():
        pid = row.get("paper_id", "")
        fname = row.get("original_file_name", "") or row.get("english_safe_file_name", "")
        if pid and fname:
            pdf_to_pid[fname] = pid
            pid_to_pdf[pid] = fname

    # Count extracted texts
    extracted_files = sorted(EXTRACTED_DIR.glob("P*.txt"))
    extracted_count = len(extracted_files)
    non_empty_extracted = sum(1 for f in extracted_files if f.stat().st_size > 50)

    # Count paper cards
    cards = load_cards()
    total_cards = len(cards)

    # Identify supplementary materials
    supplementary = [c for c in cards if c.get("primary_category") == "irrelevant_or_low_priority"
                     and any(kw in c.get("title", "").lower() for kw in ["supplementary", "supporting", "supplemental", "si_"])]

    # Identify course/exam material
    course_material = set(f"P{i:03d}" for i in range(305, 319))

    # Count by category
    cat_counts = Counter(c["primary_category"] for c in cards)
    prio_counts = Counter(c["priority"] for c in cards)

    return {
        "total_pdfs": total_pdfs,
        "extracted_count": extracted_count,
        "non_empty_extracted": non_empty_extracted,
        "total_cards": total_cards,
        "supplementary_count": len(supplementary),
        "course_material_count": len(course_material),
        "cat_counts": cat_counts,
        "prio_counts": prio_counts,
        "cards": cards,
        "metadata": metadata,
        "pdf_to_pid": pdf_to_pid,
        "pid_to_pdf": pid_to_pdf,
    }


def step2_find_duplicates(cards, metadata):
    """Find duplicate papers by title, DOI, abstract similarity."""
    duplicates = []
    seen = {}

    for card in cards:
        pid = card["paper_id"]
        title = card.get("title", "").strip()
        doi = card.get("doi", "").strip()
        abstract = card.get("abstract_preview", "").strip()
        fname = card.get("file_name", "")

        # Check by DOI first
        if doi and doi in seen:
            duplicates.append({
                "group_id": f"DOI_{doi[:30]}",
                "paper_id": pid,
                "file_name": fname,
                "title": title,
                "doi": doi,
                "keep_or_remove": "remove",
                "reason": f"Duplicate DOI with {seen[doi]}",
            })
            continue

        # Check by title similarity
        matched = False
        for seen_pid, seen_info in seen.items():
            if similar(title, seen_info["title"], 0.80):
                duplicates.append({
                    "group_id": f"TITLE_{seen_pid}",
                    "paper_id": pid,
                    "file_name": fname,
                    "title": title,
                    "doi": doi,
                    "keep_or_remove": "remove",
                    "reason": f"Similar title to {seen_pid}: '{seen_info['title'][:50]}'",
                })
                matched = True
                break

        if not matched:
            # Check by abstract similarity
            for seen_pid, seen_info in seen.items():
                if abstract and seen_info["abstract"] and similar(abstract, seen_info["abstract"], 0.85):
                    duplicates.append({
                        "group_id": f"ABSTRACT_{seen_pid}",
                        "paper_id": pid,
                        "file_name": fname,
                        "title": title,
                        "doi": doi,
                        "keep_or_remove": "remove",
                        "reason": f"Similar abstract to {seen_pid}",
                    })
                    matched = True
                    break

        if not matched:
            seen[pid] = {"title": title, "doi": doi, "abstract": abstract}

    # Mark known duplicates from prior analysis
    known_dupes = {
        "P019": ("P016", "Known duplicate"),
        "P059": ("P060", "Known duplicate"),
        "P120": ("P115", "Known duplicate"),
        "P124": ("P114", "Known duplicate"),
        "P130": ("P126", "Known duplicate"),
        "P131": ("P127", "Known duplicate"),
        "P132": ("P128", "Known duplicate"),
        "P133": ("P129", "Known duplicate"),
        "P134": ("P122", "Known duplicate"),
        "P135": ("P129", "Known duplicate"),
        "P141": ("P139", "Known duplicate"),
        "P142": ("P121", "Known duplicate"),
        "P144": ("P143", "Known duplicate"),
        "P158": ("P159", "Known duplicate"),
        "P255": ("P242", "Known duplicate"),
        "P292": ("P284", "Known duplicate"),
        "P295": ("P291", "Known duplicate"),
        "P296": ("P293", "Known duplicate"),
        "P324": ("P217", "Known duplicate"),
        "P325": ("P221", "Known duplicate"),
        "P328": ("P308", "Known duplicate"),
        "P388": ("P376", "Known duplicate"),
        "P389": ("P381", "Known duplicate"),
        "P421": ("P418", "Known duplicate"),
        "P432": ("P347", "Known duplicate"),
        "P436": ("P351", "Known duplicate"),
        "P445": ("P383", "Known duplicate"),
        "P453": ("P454", "Known duplicate"),
    }

    existing_dup_ids = set(d["paper_id"] for d in duplicates)
    for pid, (canonical, reason) in known_dupes.items():
        if pid not in existing_dup_ids:
            # Find the card info
            card_info = next((c for c in cards if c["paper_id"] == pid), None)
            duplicates.append({
                "group_id": f"KNOWN_{canonical}",
                "paper_id": pid,
                "file_name": card_info["file_name"] if card_info else "",
                "title": card_info["title"] if card_info else "",
                "doi": card_info.get("doi", "") if card_info else "",
                "keep_or_remove": "remove",
                "reason": f"Known duplicate of {canonical}: {reason}",
            })

    # Also check supplementary materials
    supplementary_pids = set()
    for card in cards:
        title = card.get("title", "").lower()
        fname = card.get("file_name", "").lower()
        if any(kw in title for kw in ["supplementary", "supporting information", "supplemental"]):
            supplementary_pids.add(card["paper_id"])
        elif any(kw in fname for kw in ["_sup", "suppmat", "si_", "mmc", "supplemental"]):
            supplementary_pids.add(card["paper_id"])

    for pid in supplementary_pids:
        if pid not in set(d["paper_id"] for d in duplicates):
            card_info = next((c for c in cards if c["paper_id"] == pid), None)
            duplicates.append({
                "group_id": "SUPPLEMENTARY",
                "paper_id": pid,
                "file_name": card_info["file_name"] if card_info else "",
                "title": card_info["title"] if card_info else "",
                "doi": card_info.get("doi", "") if card_info else "",
                "keep_or_remove": "remove",
                "reason": "Supplementary material",
            })

    return duplicates


def step3_audit_irrelevant(cards, metadata):
    """Re-audit irrelevant papers to check for misclassifications."""
    irrelevant = [c for c in cards if c["primary_category"] == "irrelevant_or_low_priority"]

    # Keywords for re-checking
    recheck_keywords = {
        "polyurethane_microphase_separation": ["polyurethane", "tpu", "thermoplastic polyurethane", "hard segment", "soft segment", "microphase"],
        "TPU_mechanics": ["polyurethane", "tpu", "tensile", "fracture", "fatigue", "elastomer", "mechanical"],
        "shape_memory_polyurethane": ["shape memory", "shape-memory", "recovery", "fixity"],
        "biodegradable_polyurethane": ["biodegradable", "scaffold", "tissue", "cell", "biocompat"],
        "PCL_based_polyurethane": ["polycaprolactone", "pcl", "caprolactone"],
        "PVDF_piezoelectric_biomaterials": ["pvdf", "piezoelectric", "ferroelectric"],
        "protein_adsorption_cell_response": ["protein", "cell adhesion", "cell response", "fibroblast", "osteoblast"],
        "SAXS_WAXS_FTIR_DSC_characterization": ["saxs", "waxs", "ftir", "dsc", "dma", "x-ray"],
        "machine_learning_polymer_properties": ["machine learning", "neural network", "deep learning"],
        "ionogel_or_magnetic_ionogel": ["ionogel", "ionic liquid", "ionic gel"],
        "self_healing_elastomer": ["self-heal", "self-healing", "healable"],
        "supramolecular_polymer": ["supramolecular", "host-guest"],
        "bio_based_polymer": ["bio-based", "biobased", "renewable", "cellulose", "chitosan"],
        "polymer_nanocomposite": ["nanocomposite", "nanoparticle", "graphene", "carbon nanotube"],
    }

    audit_results = []
    for card in irrelevant:
        pid = card["paper_id"]
        title = card.get("title", "").lower()
        abstract = card.get("abstract_preview", "").lower()

        # Try to read full text for better classification
        txt_file = EXTRACTED_DIR / f"{pid}.txt"
        full_text = ""
        if txt_file.exists():
            full_text = txt_file.read_text(encoding="utf-8", errors="replace").lower()

        combined = f"{title} {abstract} {full_text[:3000]}"

        # Check for supplementary
        is_supplementary = any(kw in title for kw in ["supplementary", "supporting", "supplemental"])

        # Check for course material
        course_pids = set(f"P{i:03d}" for i in range(305, 319))
        is_course = pid in course_pids

        # Check against each category
        best_match = None
        best_score = 0
        for cat, keywords in recheck_keywords.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > best_score:
                best_score = score
                best_match = cat

        if is_supplementary:
            revised = "irrelevant_or_low_priority"
            keep_irrelevant = True
            reason = "Supplementary material"
            confidence = "high"
        elif is_course:
            revised = "irrelevant_or_low_priority"
            keep_irrelevant = True
            reason = "Course/exam material"
            confidence = "high"
        elif best_score >= 3 and best_match:
            revised = best_match
            keep_irrelevant = False
            reason = f"Re-classified: {best_score} keywords matched for {best_match}"
            confidence = "medium" if best_score >= 4 else "low"
        elif best_score >= 2 and best_match:
            revised = best_match
            keep_irrelevant = False
            reason = f"Possible match: {best_score} keywords for {best_match} (needs review)"
            confidence = "low"
        else:
            revised = "irrelevant_or_low_priority"
            keep_irrelevant = True
            reason = "No relevant keywords found"
            confidence = "medium"

        audit_results.append({
            "paper_id": pid,
            "title": card.get("title", "")[:80],
            "original_category": "irrelevant_or_low_priority",
            "revised_category": revised,
            "keep_irrelevant": keep_irrelevant,
            "reason": reason,
            "confidence": confidence,
        })

    return audit_results


def step4_poor_extraction(cards, metadata):
    """Identify papers with poor text extraction."""
    poor = []
    for card in cards:
        pid = card["paper_id"]
        txt_file = EXTRACTED_DIR / f"{pid}.txt"

        if not txt_file.exists():
            poor.append({
                "paper_id": pid,
                "file_name": card.get("file_name", ""),
                "title": card.get("title", ""),
                "extraction_problem": "File not found",
                "missing_abstract": True,
                "text_length": 0,
                "classification_confidence": card.get("confidence", ""),
                "suggested_action": "needs_manual_check",
            })
            continue

        text = txt_file.read_text(encoding="utf-8", errors="replace")
        text_len = len(text)

        has_abstract = bool(re.search(r"ABSTRACT|Abstract", text[:5000]))
        has_introduction = bool(re.search(r"INTRODUCTION|Introduction", text[:10000]))
        has_conclusion = bool(re.search(r"CONCLUSIONS?|CONCLUDING", text, re.IGNORECASE))

        problems = []
        if text_len < 200:
            problems.append("Very short text (<200 chars)")
        if not has_abstract:
            problems.append("No abstract found")
        if not has_introduction and text_len > 500:
            problems.append("No introduction found")
        if text_len < 1000:
            problems.append("Short text (<1000 chars)")

        # Check if title is meaningful
        title = card.get("title", "")
        if not title or len(title) < 10 or any(kw in title.lower() for kw in ["research article", "view article", "citethis", "supporting"]):
            problems.append("Poor title extraction")

        if problems:
            # Check if potentially relevant despite poor extraction
            fname = card.get("file_name", "").lower()
            title_lower = title.lower()
            potentially_relevant = any(kw in fname or kw in title_lower for kw in [
                "polyurethane", "tpu", "elastomer", "shape memory", "pcl",
                "pvdf", "piezo", "biomaterial", "scaffold", "saxs", "ftir",
            ])

            poor.append({
                "paper_id": pid,
                "file_name": card.get("file_name", ""),
                "title": title[:80],
                "extraction_problem": "; ".join(problems),
                "missing_abstract": not has_abstract,
                "text_length": text_len,
                "classification_confidence": card.get("confidence", ""),
                "suggested_action": "needs_manual_check" if potentially_relevant else "skip",
            })

    return poor


def generate_audit_md(stats, duplicates, irrelevant_audit, poor_extraction):
    """Generate phase1_audit.md."""
    lines = []
    lines.append("# Phase 1 Audit Report")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append("")

    lines.append("## 1. Paper Count Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Original PDF files | {stats['total_pdfs']} |")
    lines.append(f"| Successfully extracted text files | {stats['extracted_count']} |")
    lines.append(f"| Non-empty extracted texts | {stats['non_empty_extracted']} |")
    lines.append(f"| Paper cards generated | {stats['total_cards']} |")
    lines.append(f"| Supplementary materials identified | {stats['supplementary_count']} |")
    lines.append(f"| Course/exam material (P305-P318) | {stats['course_material_count']} |")
    lines.append(f"| Duplicate papers found | {len(duplicates)} |")
    lines.append(f"| Irrelevant/low priority | {stats['cat_counts'].get('irrelevant_or_low_priority', 0)} |")
    lines.append("")

    lines.append("## 2. Why 452 instead of 412?")
    lines.append("")
    lines.append("The previous deep reading session identified 412 unique entries from P002-P456.")
    lines.append("The current classification processed 452 non-empty extracted text files.")
    lines.append("The difference is because:")
    lines.append("- The previous session skipped P001 (empty file), P003/P009/P015/P017/P018 (not deep-read), and some supplementary files")
    lines.append("- The current classification includes ALL non-empty extracted texts, including supplementary materials")
    lines.append("- Some papers were identified as duplicates in the previous session but are still counted as separate files")
    lines.append("")

    lines.append("## 3. Category Distribution (Before Dedup)")
    lines.append("")
    lines.append("| Category | Count | High | Medium | Low |")
    lines.append("|----------|-------|------|--------|-----|")
    for cat, count in stats["cat_counts"].most_common():
        # Count priorities per category
        cat_cards = [c for c in stats["cards"] if c["primary_category"] == cat]
        h = sum(1 for c in cat_cards if c["priority"] == "high")
        m = sum(1 for c in cat_cards if c["priority"] == "medium")
        l = sum(1 for c in cat_cards if c["priority"] == "low")
        lines.append(f"| {cat} | {count} | {h} | {m} | {l} |")
    lines.append("")

    lines.append("## 4. Duplicate Summary")
    lines.append("")
    dup_groups = defaultdict(list)
    for d in duplicates:
        dup_groups[d["group_id"]].append(d["paper_id"])
    lines.append(f"Total duplicate entries: {len(duplicates)}")
    lines.append(f"Duplicate groups: {len(dup_groups)}")
    lines.append("")

    lines.append("## 5. Irrelevant Audit Summary")
    lines.append("")
    reclassified = [a for a in irrelevant_audit if not a["keep_irrelevant"]]
    lines.append(f"Originally irrelevant: {len(irrelevant_audit)}")
    lines.append(f"Re-classified to a real category: {len(reclassified)}")
    lines.append(f"Confirmed irrelevant: {len(irrelevant_audit) - len(reclassified)}")
    lines.append("")

    lines.append("## 6. Poor Extraction Summary")
    lines.append("")
    needs_check = [p for p in poor_extraction if p["suggested_action"] == "needs_manual_check"]
    lines.append(f"Papers with extraction issues: {len(poor_extraction)}")
    lines.append(f"Needs manual check: {len(needs_check)}")
    lines.append(f"Can skip: {len(poor_extraction) - len(needs_check)}")
    lines.append("")

    return "\n".join(lines)


def main():
    print(f"[{datetime.now():%H:%M:%S}] Phase 1 Audit")
    print()

    # Load data
    metadata = load_metadata()
    print(f"  Loaded metadata: {len(metadata)} entries")

    # Step 1: Count
    print("  Step 1: Counting papers...")
    stats = step1_count_pdfs(metadata)
    print(f"    PDFs: {stats['total_pdfs']}, Extracted: {stats['extracted_count']}, Cards: {stats['total_cards']}")

    # Step 2: Deduplicate
    print("  Step 2: Finding duplicates...")
    duplicates = step2_find_duplicates(stats["cards"], metadata)
    dup_pids = set(d["paper_id"] for d in duplicates)
    print(f"    Found {len(duplicates)} duplicate entries")

    # Generate deduplicated cards
    deduped = [c for c in stats["cards"] if c["paper_id"] not in dup_pids]
    with open(OUT_DIR / "deduplicated_paper_cards.jsonl", "w", encoding="utf-8") as f:
        for card in deduped:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    print(f"    Deduplicated cards: {len(deduped)} (removed {len(dup_pids)})")

    # Write duplicates.csv
    with open(OUT_DIR / "duplicates.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["group_id", "paper_id", "file_name", "title", "doi", "keep_or_remove", "reason"])
        writer.writeheader()
        writer.writerows(duplicates)

    # Step 3: Audit irrelevant
    print("  Step 3: Auditing irrelevant papers...")
    irrelevant_audit = step3_audit_irrelevant(stats["cards"], metadata)
    reclassified = [a for a in irrelevant_audit if not a["keep_irrelevant"]]
    print(f"    Re-classified: {len(reclassified)} papers")

    with open(OUT_DIR / "irrelevant_audit.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["paper_id", "title", "original_category", "revised_category", "keep_irrelevant", "reason", "confidence"])
        writer.writeheader()
        writer.writerows(irrelevant_audit)

    # Step 4: Poor extraction
    print("  Step 4: Checking extraction quality...")
    poor_extraction = step4_poor_extraction(stats["cards"], metadata)
    needs_check = [p for p in poor_extraction if p["suggested_action"] == "needs_manual_check"]
    print(f"    Poor extraction: {len(poor_extraction)}, Needs manual check: {len(needs_check)}")

    with open(OUT_DIR / "poor_extraction_papers.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["paper_id", "file_name", "title", "extraction_problem", "missing_abstract", "text_length", "classification_confidence", "suggested_action"])
        writer.writeheader()
        writer.writerows(poor_extraction)

    # Step 5: Generate audit report
    print("  Step 5: Generating audit report...")
    audit_md = generate_audit_md(stats, duplicates, irrelevant_audit, poor_extraction)
    (OUT_DIR / "phase1_audit.md").write_text(audit_md, encoding="utf-8")

    # Apply irrelevant audit to create refined cards
    reclass_map = {a["paper_id"]: a["revised_category"] for a in irrelevant_audit if not a["keep_irrelevant"]}

    refined_cards = []
    for card in deduped:  # Use deduplicated cards
        pid = card["paper_id"]
        if pid in reclass_map:
            card = dict(card)
            card["primary_category"] = reclass_map[pid]
            card["original_category"] = "irrelevant_or_low_priority"
        refined_cards.append(card)

    with open(OUT_DIR / "refined_paper_cards.jsonl", "w", encoding="utf-8") as f:
        for card in refined_cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    print(f"    Refined cards: {len(refined_cards)}")

    # Print summary
    print()
    print("=== RESULTS ===")
    print(f"  phase1_audit.md: {OUT_DIR / 'phase1_audit.md'}")
    print(f"  duplicates.csv: {OUT_DIR / 'duplicates.csv'}")
    print(f"  deduplicated_paper_cards.jsonl: {OUT_DIR / 'deduplicated_paper_cards.jsonl'}")
    print(f"  irrelevant_audit.csv: {OUT_DIR / 'irrelevant_audit.csv'}")
    print(f"  poor_extraction_papers.csv: {OUT_DIR / 'poor_extraction_papers.csv'}")
    print(f"  refined_paper_cards.jsonl: {OUT_DIR / 'refined_paper_cards.jsonl'}")
    print()
    print(f"  Before dedup: {stats['total_cards']} cards")
    print(f"  After dedup: {len(deduped)} cards")
    print(f"  Irrelevant re-classified: {len(reclassified)}")
    print(f"  Final refined: {len(refined_cards)} cards")

    # Print reclassified papers
    if reclassified:
        print()
        print("=== RE-CLASSIFIED PAPERS ===")
        for a in reclassified:
            print(f"  {a['paper_id']}: {a['original_category']} -> {a['revised_category']} ({a['reason']})")

    print()
    print(f"[{datetime.now():%H:%M:%S}] Audit complete.")


if __name__ == "__main__":
    main()
