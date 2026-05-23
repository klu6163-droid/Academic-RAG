#!/usr/bin/env python3
"""Generate frontend data JSON files."""

import csv
import json
from pathlib import Path

PROJECT_DIR = Path(r"D:\Academic-RAG")
EVIDENCE_DIR = PROJECT_DIR / "02_evidence_database"
FRONTEND_DATA = PROJECT_DIR / "07_frontend" / "src" / "data"

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Papers - already exists from step1_metadata.py
    # Evidence - copy from evidence_matrix.json
    evidence = load_json(EVIDENCE_DIR / "evidence_matrix.json")
    with open(FRONTEND_DATA / "evidence.json", 'w', encoding='utf-8') as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)

    # Methods - copy from method_matrix.json
    methods = load_json(EVIDENCE_DIR / "method_matrix.json")
    with open(FRONTEND_DATA / "methods.json", 'w', encoding='utf-8') as f:
        json.dump(methods, f, ensure_ascii=False, indent=2)

    # Materials - copy from material_system_matrix.json
    materials = load_json(EVIDENCE_DIR / "material_system_matrix.json")
    with open(FRONTEND_DATA / "materials.json", 'w', encoding='utf-8') as f:
        json.dump(materials, f, ensure_ascii=False, indent=2)

    # Figures - copy from key_figures_table.json
    figures = load_json(EVIDENCE_DIR / "key_figures_table.json")
    with open(FRONTEND_DATA / "figures.json", 'w', encoding='utf-8') as f:
        json.dump(figures, f, ensure_ascii=False, indent=2)

    # Nodes and edges already exist from step3_knowledge_graph.py
    # Questions and directions already exist from step4_synthesis.py

    print("Frontend data files generated!")
    print(f"  evidence.json: {len(evidence)} items")
    print(f"  methods.json: {len(methods)} items")
    print(f"  materials.json: {len(materials)} items")
    print(f"  figures.json: {len(figures)} items")

    # Verify all required files exist
    required = ['papers.json', 'evidence.json', 'methods.json', 'materials.json',
                'figures.json', 'nodes.json', 'edges.json', 'questions.json', 'directions.json']
    for f in required:
        path = FRONTEND_DATA / f
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {f} ({size:,} bytes)")
        else:
            print(f"  ✗ {f} MISSING")

if __name__ == "__main__":
    main()
