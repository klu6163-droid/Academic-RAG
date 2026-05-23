#!/usr/bin/env python3
"""
Phase 1 Audit - Step 5-6: Generate refined category summary and Phase 2 plan.
Uses deduplicated + reclassified paper cards.
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

INPUT = Path(r"D:\Academic-RAG\data\analysis\refined_paper_cards.jsonl")
AUDIT_DIR = Path(r"D:\Academic-RAG\data\analysis")

CAT_NAMES = {
    "polyurethane_microphase_separation": "Polyurethane Microphase Separation",
    "shape_memory_polyurethane": "Shape Memory Polyurethane",
    "biodegradable_polyurethane": "Biodegradable Polyurethane",
    "PCL_based_polyurethane": "PCL-Based Polyurethane",
    "TPU_mechanics": "TPU Mechanics",
    "PVDF_piezoelectric_biomaterials": "PVDF/Piezo Biomaterials",
    "protein_adsorption_cell_response": "Protein Adsorption & Cell Response",
    "SAXS_WAXS_FTIR_DSC_characterization": "SAXS/WAXS/FTIR/DSC Characterization",
    "machine_learning_polymer_properties": "ML for Polymer Properties",
    "ionogel_or_magnetic_ionogel": "Ionogel / Magnetic Ionogel",
    "review_or_background": "Review / Background",
    "irrelevant_or_low_priority": "Irrelevant / Low Priority",
    "self_healing_elastomer": "Self-Healing Elastomer",
    "supramolecular_polymer": "Supramolecular Polymer",
    "bio_based_polymer": "Bio-Based Polymer",
    "polymer_nanocomposite": "Polymer Nanocomposite",
    "polymer_blend": "Polymer Blend",
}

# Phase 2 recommended order
PHASE2_ORDER = [
    ("polyurethane_microphase_separation", "deep_read", "Core research topic: PU microphase separation is central to the thesis"),
    ("TPU_mechanics", "deep_read", "Core research topic: TPU mechanical properties, fatigue, fracture"),
    ("self_healing_elastomer", "deep_read", "Directly relevant: self-healing PU/elastomer is a key research direction"),
    ("shape_memory_polyurethane", "deep_read", "Core research topic: shape memory PU is the main application"),
    ("PCL_based_polyurethane", "deep_read", "Core research topic: PCL-based PU for biocompatibility"),
    ("biodegradable_polyurethane", "deep_read", "Core research topic: biodegradable PU for biomedical applications"),
    ("PVDF_piezoelectric_biomaterials", "skim", "Related: PVDF piezoelectric biomaterials, may inform PU design"),
    ("SAXS_WAXS_FTIR_DSC_characterization", "skim", "Methods reference: characterization techniques for PU analysis"),
    ("protein_adsorption_cell_response", "skim", "Related: protein/cell response for biomedical PU evaluation"),
    ("polymer_nanocomposite", "skim", "Related: nanocomposite reinforcement strategies"),
    ("supramolecular_polymer", "skim", "Related: supramolecular interactions in PU"),
    ("bio_based_polymer", "skim", "Related: bio-based raw materials for sustainable PU"),
    ("polymer_blend", "skim", "Related: polymer blending for property tuning"),
    ("ionogel_or_magnetic_ionogel", "skip", "Low relevance to core PU research"),
    ("machine_learning_polymer_properties", "skip", "Low relevance unless doing computational work"),
    ("review_or_background", "skip", "Already covered in prior deep reading session"),
    ("irrelevant_or_low_priority", "skip", "Not relevant to research topic"),
]


def load_cards():
    cards = []
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))
    return cards


def load_duplicates():
    dupes = []
    with open(AUDIT_DIR / "duplicates.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dupes.append(row)
    return dupes


def load_poor_extraction():
    poor = []
    with open(AUDIT_DIR / "poor_extraction_papers.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            poor.append(row)
    return poor


def generate_refined_summary(cards, duplicates, poor_extraction):
    """Generate refined category summary."""
    total = len(cards)
    cat_counts = Counter(c["primary_category"] for c in cards)
    prio_counts = defaultdict(lambda: Counter())
    for c in cards:
        prio_counts[c["primary_category"]][c["priority"]] += 1

    # Per-category stats
    cat_stats = {}
    for cat in cat_counts:
        cat_cards = [c for c in cards if c["primary_category"] == cat]

        mat_counter = Counter()
        meth_counter = Counter()
        prop_counter = Counter()
        for c in cat_cards:
            for m in c.get("material_system", []):
                mat_counter[m] += 1
            for m in c.get("methods", []):
                meth_counter[m] += 1
            for p in c.get("properties", []):
                prop_counter[p] += 1

        # Top papers (high > medium > by confidence)
        sorted_papers = sorted(
            cat_cards,
            key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 2),
                {"high": 0, "medium": 1, "low": 2}.get(x["confidence"], 2),
            )
        )[:10]

        cat_stats[cat] = {
            "count": cat_counts[cat],
            "prio": prio_counts[cat],
            "top_materials": mat_counter.most_common(8),
            "top_methods": meth_counter.most_common(8),
            "top_properties": prop_counter.most_common(8),
            "top_papers": sorted_papers,
        }

    return cat_counts, cat_stats, total


def write_refined_md(cat_counts, cat_stats, total, duplicates, poor_extraction):
    """Write category_summary_refined.md."""
    lines = []
    lines.append("# Refined Category Summary - Phase 1 Audit Results")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append("")

    dup_count = len(duplicates)
    needs_check = [p for p in poor_extraction if p.get("suggested_action") == "needs_manual_check"]

    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Papers before dedup | {total + dup_count} |")
    lines.append(f"| Duplicates removed | {dup_count} |")
    lines.append(f"| Papers after dedup | {total} |")
    lines.append(f"| Needs manual check (poor extraction) | {len(needs_check)} |")
    lines.append("")

    # Category table
    lines.append("## Category Distribution (After Dedup & Reclassification)")
    lines.append("")
    lines.append("| Category | Count | High | Medium | Low | % |")
    lines.append("|----------|-------|------|--------|-----|---|")
    research_cats = []
    for cat, count in cat_counts.most_common():
        stats = cat_stats[cat]
        p = stats["prio"]
        pct = f"{count/total*100:.1f}%"
        name = CAT_NAMES.get(cat, cat)
        lines.append(f"| {name} | {count} | {p.get('high',0)} | {p.get('medium',0)} | {p.get('low',0)} | {pct} |")
        if cat not in ("irrelevant_or_low_priority", "review_or_background"):
            research_cats.append((cat, stats))
    lines.append("")

    # Per-category details (research categories only)
    lines.append("---")
    lines.append("")
    lines.append("## Research Category Details")
    lines.append("")

    for cat, stats in research_cats:
        name = CAT_NAMES.get(cat, cat)
        lines.append(f"### {name} ({stats['count']} papers)")
        lines.append("")

        if stats["top_materials"]:
            lines.append("**Top Materials:** " + ", ".join(f"{m}({c})" for m, c in stats["top_materials"][:5]))
            lines.append("")

        if stats["top_methods"]:
            lines.append("**Top Methods:** " + ", ".join(f"{m}({c})" for m, c in stats["top_methods"][:5]))
            lines.append("")

        if stats["top_properties"]:
            lines.append("**Top Properties:** " + ", ".join(f"{p}({c})" for p, c in stats["top_properties"][:5]))
            lines.append("")

        lines.append("**Top Papers:**")
        lines.append("")
        lines.append("| ID | Title | Year | Priority | Confidence |")
        lines.append("|----|-------|------|----------|------------|")
        for p in stats["top_papers"]:
            title = p["title"][:65] + ("..." if len(p["title"]) > 65 else "")
            lines.append(f"| {p['paper_id']} | {title} | {p.get('year','-')} | {p['priority']} | {p['confidence']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Needs manual check
    if needs_check:
        lines.append("## Papers Needing Manual Check")
        lines.append("")
        lines.append("These papers have poor text extraction but may be relevant based on filename/title:")
        lines.append("")
        lines.append("| Paper ID | Title | Extraction Problem |")
        lines.append("|----------|-------|--------------------|")
        for p in needs_check:
            lines.append(f"| {p['paper_id']} | {p['title'][:50]} | {p['extraction_problem'][:60]} |")
        lines.append("")

    return "\n".join(lines)


def write_phase2_plan(cat_counts, cat_stats, total):
    """Write Phase 2 reading plan."""
    lines = []
    lines.append("# Phase 2 Grouped Deep Reading Plan")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append("")
    lines.append("## Recommended Reading Order")
    lines.append("")
    lines.append("| Priority | Category | Papers | High | Medium | Action | Reason |")
    lines.append("|----------|----------|--------|------|--------|--------|--------|")

    for i, (cat, action, reason) in enumerate(PHASE2_ORDER, 1):
        if cat not in cat_stats:
            continue
        stats = cat_stats[cat]
        name = CAT_NAMES.get(cat, cat)
        h = stats["prio"].get("high", 0)
        m = stats["prio"].get("medium", 0)
        lines.append(f"| {i} | {name} | {stats['count']} | {h} | {m} | **{action}** | {reason} |")

    lines.append("")
    lines.append("## Action Definitions")
    lines.append("")
    lines.append("- **deep_read**: Read full paper, extract structured findings, add to knowledge graph")
    lines.append("- **skim**: Read abstract + conclusion + key figures, extract main findings")
    lines.append("- **skip**: Do not read in Phase 2 (may revisit later if needed)")
    lines.append("")

    lines.append("## Phase 2 Execution Plan")
    lines.append("")

    for i, (cat, action, reason) in enumerate(PHASE2_ORDER, 1):
        if cat not in cat_stats or action == "skip":
            continue
        stats = cat_stats[cat]
        name = CAT_NAMES.get(cat, cat)
        lines.append(f"### Group {i}: {name}")
        lines.append(f"- **Action**: {action}")
        lines.append(f"- **Paper count**: {stats['count']}")
        lines.append(f"- **High priority**: {stats['prio'].get('high', 0)}")
        lines.append(f"- **Medium priority**: {stats['prio'].get('medium', 0)}")
        lines.append(f"- **Reason**: {reason}")
        lines.append("")

        if action == "deep_read":
            lines.append("**Papers to deep read:**")
            lines.append("")
            for p in stats["top_papers"]:
                lines.append(f"- {p['paper_id']}: {p['title'][:70]}")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## Estimated Total Effort")
    lines.append("")
    deep_read_cats = [(cat, stats) for cat, action, reason in PHASE2_ORDER
                      if action == "deep_read" and cat in cat_stats]
    skim_cats = [(cat, stats) for cat, action, reason in PHASE2_ORDER
                 if action == "skim" and cat in cat_stats]

    deep_read_total = sum(stats["count"] for _, stats in deep_read_cats)
    skim_total = sum(stats["count"] for _, stats in skim_cats)

    lines.append(f"- Deep read: ~{deep_read_total} papers across {len(deep_read_cats)} categories")
    lines.append(f"- Skim: ~{skim_total} papers across {len(skim_cats)} categories")
    lines.append(f"- Total active: ~{deep_read_total + skim_total} papers")
    lines.append(f"- Skipped: ~{total - deep_read_total - skim_total} papers")
    lines.append("")
    lines.append("## Output Format per Category")
    lines.append("")
    lines.append("Each category review will be saved to:")
    lines.append("`data/analysis/category_reviews/{category_name}.md`")
    lines.append("")
    lines.append("Each review includes:")
    lines.append("1. Research background")
    lines.append("2. Key material systems")
    lines.append("3. Experimental design & methods")
    lines.append("4. Key characterization evidence")
    lines.append("5. Key performance data")
    lines.append("6. Structure-property relationships")
    lines.append("7. Consensus across papers")
    lines.append("8. Contradictions across papers")
    lines.append("9. Research gaps")
    lines.append("10. Implications for user's research")
    lines.append("11. Evidence table with paper_id, title, file_name, page, excerpt")
    lines.append("")

    return "\n".join(lines)


def main():
    print(f"[{datetime.now():%H:%M:%S}] Generating refined summary and Phase 2 plan...")

    cards = load_cards()
    duplicates = load_duplicates()
    poor_extraction = load_poor_extraction()

    print(f"  Refined cards: {len(cards)}")
    print(f"  Duplicates: {len(duplicates)}")
    print(f"  Poor extraction: {len(poor_extraction)}")

    cat_counts, cat_stats, total = generate_refined_summary(cards, duplicates, poor_extraction)

    # Write refined summary
    md = write_refined_md(cat_counts, cat_stats, total, duplicates, poor_extraction)
    (AUDIT_DIR / "category_summary_refined.md").write_text(md, encoding="utf-8")
    print(f"  Written: category_summary_refined.md")

    # Write refined CSV
    rows = []
    for cat in cat_counts:
        stats = cat_stats[cat]
        p = stats["prio"]
        rows.append({
            "category": cat,
            "display_name": CAT_NAMES.get(cat, cat),
            "count": cat_counts[cat],
            "high_priority": p.get("high", 0),
            "medium_priority": p.get("medium", 0),
            "low_priority": p.get("low", 0),
            "pct_of_total": f"{cat_counts[cat]/total*100:.1f}%",
        })
    with open(AUDIT_DIR / "category_summary_refined.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written: category_summary_refined.csv")

    # Write Phase 2 plan
    plan = write_phase2_plan(cat_counts, cat_stats, total)
    (AUDIT_DIR / "phase2_plan.md").write_text(plan, encoding="utf-8")
    print(f"  Written: phase2_plan.md")

    # Print summary
    print()
    print("=== REFINED CATEGORY DISTRIBUTION ===")
    for cat, count in cat_counts.most_common():
        name = CAT_NAMES.get(cat, cat)
        p = cat_stats[cat]["prio"]
        print(f"  {name}: {count} (H:{p.get('high',0)} M:{p.get('medium',0)} L:{p.get('low',0)})")

    print()
    print(f"[{datetime.now():%H:%M:%S}] Done. Awaiting user confirmation before Phase 2.")


if __name__ == "__main__":
    main()
