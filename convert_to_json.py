#!/usr/bin/env python3
"""Convert final analysis outputs to frontend JSON."""
import csv, json, sys, os, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = Path(__file__).resolve().parent
FINAL = PROJECT_DIR / 'data' / 'analysis' / 'final'
OUT = PROJECT_DIR / 'frontend' / 'public' / 'data'
OUT.mkdir(parents=True, exist_ok=True)

# 1. evidence.json
with open(FINAL / 'global_evidence_table_frontend.csv', 'r', encoding='utf-8') as f:
    evidence = list(csv.DictReader(f))
with open(OUT / 'evidence.json', 'w', encoding='utf-8') as f:
    json.dump(evidence, f, ensure_ascii=False, indent=1)
print(f'evidence.json: {len(evidence)} rows')

# 2. kg_nodes.json
with open(FINAL / 'kg_nodes_frontend.csv', 'r', encoding='utf-8') as f:
    nodes = list(csv.DictReader(f))
with open(OUT / 'kg_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(nodes, f, ensure_ascii=False, indent=1)
print(f'kg_nodes.json: {len(nodes)} nodes')

# 3. kg_edges.json
with open(FINAL / 'kg_edges.csv', 'r', encoding='utf-8') as f:
    edges = list(csv.DictReader(f))
with open(OUT / 'kg_edges.json', 'w', encoding='utf-8') as f:
    json.dump(edges, f, ensure_ascii=False, indent=1)
print(f'kg_edges.json: {len(edges)} edges')

# 4. global_synthesis.json
with open(FINAL / 'global_synthesis.md', 'r', encoding='utf-8') as f:
    content = f.read()
# Split by ## headings
sections = []
current = {'title': '', 'content': ''}
for line in content.split('\n'):
    if line.startswith('## '):
        if current['title']:
            sections.append(current)
        current = {'title': line[3:].strip(), 'content': ''}
    else:
        current['content'] += line + '\n'
if current['title']:
    sections.append(current)
with open(OUT / 'global_synthesis.json', 'w', encoding='utf-8') as f:
    json.dump(sections, f, ensure_ascii=False, indent=1)
print(f'global_synthesis.json: {len(sections)} sections')

# 5. project_syntheses.json
projects = []
project_files = [
    ('project_PU_microphase_mechanics.md', 'PU Microphase Separation and Mechanics'),
    ('project_PCL_biodegradable_PU.md', 'PCL-Based Biodegradable PU'),
    ('project_PVDF_piezo_biointerface.md', 'PVDF Piezoelectric Biointerface'),
    ('project_ionogel_FeCl4_PU.md', 'Ionogel / FeCl4-PU Interaction'),
    ('project_ML_polyurethane_properties.md', 'ML for Polyurethane Properties'),
]
for fname, title in project_files:
    path = FINAL / fname
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Parse sections
        secs = []
        cur = {'heading': '', 'content': ''}
        for line in content.split('\n'):
            if line.startswith('## '):
                if cur['heading']:
                    secs.append(cur)
                cur = {'heading': line[3:].strip(), 'content': ''}
            else:
                cur['content'] += line + '\n'
        if cur['heading']:
            secs.append(cur)
        projects.append({'title': title, 'file': fname, 'sections': secs})
with open(OUT / 'project_syntheses.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=1)
print(f'project_syntheses.json: {len(projects)} projects')

# 6. dashboard_stats.json
cats = {}
for r in evidence:
    c = r.get('category', 'Unknown')
    cats[c] = cats.get(c, 0) + 1

claim_types = {}
for r in evidence:
    ct = r.get('claim_type', 'general')
    claim_types[ct] = claim_types.get(ct, 0) + 1

stats = {
    'refined_cards': 290,
    'active_work_papers': 179,
    'cleaned_evidence_rows': len(evidence),
    'manual_check_rows': sum(1 for r in evidence if r.get('needs_manual_check') == 'TRUE'),
    'kg_nodes': len(nodes),
    'kg_edges': len(edges),
    'ml_feature_candidates': sum(1 for r in evidence if r.get('ml_feature_candidate') == 'TRUE'),
    'high_value_citations': sum(1 for r in evidence if r.get('relevance') == 'high_relevance_pu'),
    'page_missing': sum(1 for r in evidence if not r.get('page_est', '').strip()),
    'title_needs_cleanup': sum(1 for r in evidence if r.get('title_needs_cleanup') == 'TRUE'),
    'category_distribution': cats,
    'claim_type_distribution': claim_types,
}
with open(OUT / 'dashboard_stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=1)
print(f'dashboard_stats.json')

# 7. data_quality_report.json
with open(FINAL / 'frontend_data_quality_report.md', 'r', encoding='utf-8') as f:
    dq_content = f.read()
dq = {
    'content': dq_content,
    'manual_check_papers': list(set(r['paper_id'] for r in evidence if r.get('needs_manual_check') == 'TRUE')),
    'title_cleanup_papers': list(set(r['paper_id'] for r in evidence if r.get('title_needs_cleanup') == 'TRUE')),
    'page_missing_count': sum(1 for r in evidence if not r.get('page_est', '').strip()),
}
with open(OUT / 'data_quality_report.json', 'w', encoding='utf-8') as f:
    json.dump(dq, f, ensure_ascii=False, indent=1)
print(f'data_quality_report.json')

print('\nAll JSON files generated.')
