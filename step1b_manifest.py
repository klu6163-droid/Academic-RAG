#!/usr/bin/env python3
"""Generate literature_manifest.md from metadata."""

import csv
import json
from pathlib import Path
from collections import Counter

MANIFEST_DIR = Path(r"D:\Academic-RAG\00_manifest")

def main():
    # Load metadata
    with open(MANIFEST_DIR / "literature_metadata.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    # Load original paths
    orig_paths = {}
    with open(MANIFEST_DIR / "file_path_mapping.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            orig_paths[row['paper_id']] = row

    with open(MANIFEST_DIR / "literature_manifest.md", 'w', encoding='utf-8') as f:
        f.write("# Literature Manifest\n\n")
        f.write("## Overview\n\n")
        f.write(f"- **Total PDF files**: {len(records)}\n")

        readable = sum(1 for r in records if r['readable_status'] == 'readable')
        f.write(f"- **Readable papers**: {readable}\n")

        supp = sum(1 for r in records if r['preliminary_category'] == 'supplementary')
        f.write(f"- **Supplementary materials**: {supp}\n")

        main_papers = [r for r in records if r['preliminary_category'] != 'supplementary']
        f.write(f"- **Main research papers**: {len(main_papers)}\n\n")

        # Category summary
        f.write("## Research Categories\n\n")
        cats = Counter(r['preliminary_category'] for r in records)
        for cat, count in cats.most_common():
            f.write(f"- **{cat}**: {count} papers\n")

        f.write("\n## Year Distribution\n\n")
        years = Counter(r['year'] for r in records if r['year'])
        for year, count in sorted(years.items()):
            f.write(f"- {year}: {count} papers\n")

        f.write("\n## Subfolder Distribution\n\n")
        folders = Counter()
        for r in records:
            pid = r['paper_id']
            if pid in orig_paths:
                folder = orig_paths[pid].get('original_folder', '')
                # Simplify folder name
                parts = folder.split('\\')
                if len(parts) > 4:
                    folder = parts[-1] if parts[-1] != 'paper' else '(root)'
                folders[folder] += 1
        for folder, count in folders.most_common():
            f.write(f"- `{folder}`: {count} files\n")

        f.write("\n## Paper List by Category\n\n")
        for cat in sorted(set(r['preliminary_category'] for r in records)):
            f.write(f"### {cat}\n\n")
            cat_papers = [r for r in records if r['preliminary_category'] == cat]
            for r in cat_papers:
                title = r['title'][:80] if r['title'] else r['original_file_name'][:80]
                year = r['year'] if r['year'] else 'N/A'
                journal = r['journal'] if r['journal'] else 'N/A'
                f.write(f"- **{r['paper_id']}**: {title} ({year}, {journal})\n")
            f.write("\n")

    print("literature_manifest.md generated!")

if __name__ == "__main__":
    main()
