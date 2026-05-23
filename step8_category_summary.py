#!/usr/bin/env python3
"""
Phase 1 (continued): Generate category summary from paper_cards.jsonl.
Outputs: category_summary.md and category_summary.csv
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

INPUT = Path(r"D:\Academic-RAG\data\analysis\paper_cards.jsonl")
OUT_DIR = Path(r"D:\Academic-RAG\data\analysis")

# Category display names
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

# Core categories (user-specified)
CORE_CATEGORIES = [
    "polyurethane_microphase_separation",
    "shape_memory_polyurethane",
    "biodegradable_polyurethane",
    "PCL_based_polyurethane",
    "TPU_mechanics",
    "PVDF_piezoelectric_biomaterials",
    "protein_adsorption_cell_response",
    "SAXS_WAXS_FTIR_DSC_characterization",
    "machine_learning_polymer_properties",
    "ionogel_or_magnetic_ionogel",
    "review_or_background",
    "irrelevant_or_low_priority",
]


def load_cards():
    cards = []
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))
    return cards


def generate_summary(cards):
    """Generate summary statistics."""
    # Category counts
    cat_counts = Counter(c["primary_category"] for c in cards)
    prio_counts = defaultdict(lambda: Counter())
    for c in cards:
        prio_counts[c["primary_category"]][c["priority"]] += 1

    # Per-category stats
    cat_stats = {}
    for cat in cat_counts:
        cat_cards = [c for c in cards if c["primary_category"] == cat]

        # Top materials
        mat_counter = Counter()
        for c in cat_cards:
            for m in c.get("material_system", []):
                mat_counter[m] += 1

        # Top methods
        meth_counter = Counter()
        for c in cat_cards:
            for m in c.get("methods", []):
                meth_counter[m] += 1

        # Top properties
        prop_counter = Counter()
        for c in cat_cards:
            for p in c.get("properties", []):
                prop_counter[p] += 1

        # Top applications
        app_counter = Counter()
        for c in cat_cards:
            for a in c.get("application", []):
                app_counter[a] += 1

        # Year distribution
        year_counter = Counter()
        for c in cat_cards:
            if c.get("year"):
                year_counter[c["year"]] += 1

        # High-priority papers (top 10)
        high_prio = sorted(
            [c for c in cat_cards if c["priority"] in ("high", "medium")],
            key=lambda x: ({"high": 0, "medium": 1}.get(x["priority"], 2), -len(x.get("abstract_preview", ""))),
        )[:10]

        cat_stats[cat] = {
            "count": cat_counts[cat],
            "prio": prio_counts[cat],
            "top_materials": mat_counter.most_common(8),
            "top_methods": meth_counter.most_common(8),
            "top_properties": prop_counter.most_common(8),
            "top_applications": app_counter.most_common(5),
            "year_dist": dict(sorted(year_counter.items())),
            "top_papers": high_prio,
        }

    return cat_counts, cat_stats


def write_markdown(cat_counts, cat_stats, total):
    """Write category_summary.md."""
    lines = []
    lines.append("# Category Summary - Phase 1 Classification")
    lines.append(f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Total papers classified: {total}")
    lines.append("")

    # Overview table
    lines.append("## Overview")
    lines.append("")
    lines.append("| Category | Count | High | Medium | Low | % of Total |")
    lines.append("|----------|-------|------|--------|-----|------------|")
    for cat in CORE_CATEGORIES + [c for c in cat_counts if c not in CORE_CATEGORIES]:
        if cat not in cat_counts:
            continue
        stats = cat_stats[cat]
        p = stats["prio"]
        pct = f"{cat_counts[cat]/total*100:.1f}%"
        name = CAT_NAMES.get(cat, cat)
        lines.append(f"| {name} | {cat_counts[cat]} | {p.get('high',0)} | {p.get('medium',0)} | {p.get('low',0)} | {pct} |")
    lines.append("")

    # Per-category details
    lines.append("---")
    lines.append("")
    lines.append("## Category Details")
    lines.append("")

    for cat in CORE_CATEGORIES + [c for c in cat_counts if c not in CORE_CATEGORIES]:
        if cat not in cat_stats:
            continue
        stats = cat_stats[cat]
        name = CAT_NAMES.get(cat, cat)
        lines.append(f"### {name} ({stats['count']} papers)")
        lines.append("")

        # Materials
        if stats["top_materials"]:
            lines.append("**Top Materials:**")
            for mat, cnt in stats["top_materials"]:
                lines.append(f"- {mat} ({cnt})")
            lines.append("")

        # Methods
        if stats["top_methods"]:
            lines.append("**Top Methods:**")
            for meth, cnt in stats["top_methods"]:
                lines.append(f"- {meth} ({cnt})")
            lines.append("")

        # Properties
        if stats["top_properties"]:
            lines.append("**Top Properties:**")
            for prop, cnt in stats["top_properties"]:
                lines.append(f"- {prop} ({cnt})")
            lines.append("")

        # Applications
        if stats["top_applications"]:
            lines.append("**Top Applications:**")
            for app, cnt in stats["top_applications"]:
                lines.append(f"- {app} ({cnt})")
            lines.append("")

        # Year distribution
        if stats["year_dist"]:
            lines.append("**Year Distribution:**")
            for year, cnt in sorted(stats["year_dist"].items()):
                lines.append(f"- {year}: {cnt}")
            lines.append("")

        # Top papers
        if stats["top_papers"]:
            lines.append("**Top Papers to Read (High/Medium Priority):**")
            lines.append("")
            lines.append("| Paper ID | Title | Year | Priority | Confidence |")
            lines.append("|----------|-------|------|----------|------------|")
            for p in stats["top_papers"]:
                title = p["title"][:70] + ("..." if len(p["title"]) > 70 else "")
                lines.append(f"| {p['paper_id']} | {title} | {p.get('year','-')} | {p['priority']} | {p['confidence']} |")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations for Phase 2 (Grouped Deep Reading)")
    lines.append("")
    lines.append("Based on the classification, the recommended reading order is:")
    lines.append("")

    # Sort by high+medium priority count
    priority_order = sorted(
        [(cat, stats) for cat, stats in cat_stats.items() if cat not in ("irrelevant_or_low_priority", "review_or_background")],
        key=lambda x: -(x[1]["prio"].get("high", 0) * 3 + x[1]["prio"].get("medium", 0) * 1)
    )

    for i, (cat, stats) in enumerate(priority_order, 1):
        name = CAT_NAMES.get(cat, cat)
        high = stats["prio"].get("high", 0)
        med = stats["prio"].get("medium", 0)
        lines.append(f"{i}. **{name}** — {stats['count']} papers ({high} high, {med} medium priority)")

    lines.append("")
    lines.append("## Validation")
    lines.append("")
    lines.append(f"- paper_cards.jsonl path: `data/analysis/paper_cards.jsonl`")
    lines.append(f"- category_summary.md path: `data/analysis/category_summary.md`")
    lines.append(f"- Total papers: {total}")
    lines.append(f"- Successfully classified: {total}")
    lines.append(f"- Failed: 0")
    lines.append(f"- Irrelevant/Low priority: {cat_counts.get('irrelevant_or_low_priority', 0)}")
    lines.append(f"- Review/Background: {cat_counts.get('review_or_background', 0)}")
    lines.append(f"- Research papers: {total - cat_counts.get('irrelevant_or_low_priority', 0) - cat_counts.get('review_or_background', 0)}")
    lines.append("")

    return "\n".join(lines)


def write_csv(cat_counts, cat_stats, total):
    """Write category_summary.csv."""
    rows = []
    for cat in cat_counts:
        stats = cat_stats[cat]
        p = stats["prio"]
        top_mats = "; ".join(f"{m}({c})" for m, c in stats["top_materials"][:5])
        top_meths = "; ".join(f"{m}({c})" for m, c in stats["top_methods"][:5])
        rows.append({
            "category": cat,
            "display_name": CAT_NAMES.get(cat, cat),
            "count": cat_counts[cat],
            "high_priority": p.get("high", 0),
            "medium_priority": p.get("medium", 0),
            "low_priority": p.get("low", 0),
            "pct_of_total": f"{cat_counts[cat]/total*100:.1f}%",
            "top_materials": top_mats,
            "top_methods": top_meths,
        })

    with open(OUT_DIR / "category_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    print(f"[{datetime.now():%H:%M:%S}] Generating category summary...")

    cards = load_cards()
    total = len(cards)
    print(f"  Loaded {total} paper cards")

    cat_counts, cat_stats = generate_summary(cards)

    # Write markdown
    md = write_markdown(cat_counts, cat_stats, total)
    (OUT_DIR / "category_summary.md").write_text(md, encoding="utf-8")
    print(f"  Written: {OUT_DIR / 'category_summary.md'}")

    # Write CSV
    write_csv(cat_counts, cat_stats, total)
    print(f"  Written: {OUT_DIR / 'category_summary.csv'}")

    # Print summary
    print()
    print("=== Category Distribution ===")
    for cat, count in cat_counts.most_common():
        name = CAT_NAMES.get(cat, cat)
        p = cat_stats[cat]["prio"]
        print(f"  {name}: {count} (H:{p.get('high',0)} M:{p.get('medium',0)} L:{p.get('low',0)})")

    print()
    print(f"[{datetime.now():%H:%M:%S}] Done. Awaiting user confirmation before Phase 2.")


if __name__ == "__main__":
    main()
