#!/usr/bin/env python3
"""Phase 4: Build knowledge graph from all analysis data."""

import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_DIR = Path(r"D:\Academic-RAG")
EVIDENCE_DIR = PROJECT_DIR / "02_evidence_database"
KG_DIR = PROJECT_DIR / "03_knowledge_graph"
SYNTHESIS_DIR = PROJECT_DIR / "04_synthesis"
FRONTEND_DATA = PROJECT_DIR / "07_frontend" / "src" / "data"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def build_knowledge_graph():
    """Build knowledge graph nodes and edges."""
    # Load data
    papers = load_csv(PROJECT_DIR / "00_manifest" / "literature_metadata.csv")
    methods_data = load_json(EVIDENCE_DIR / "method_matrix.json")
    materials_data = load_json(EVIDENCE_DIR / "material_system_matrix.json")

    nodes = []
    edges = []
    node_ids = set()

    def add_node(node_id, node_type, label, **kwargs):
        if node_id not in node_ids:
            node_ids.add(node_id)
            nodes.append({
                'id': node_id,
                'type': node_type,
                'label': label,
                **kwargs
            })

    def add_edge(source, target, relation, **kwargs):
        edges.append({
            'source': source,
            'target': target,
            'relation': relation,
            **kwargs
        })

    # Add paper nodes
    for p in papers:
        pid = p['paper_id']
        cat = p.get('preliminary_category', 'other')
        if cat == 'supplementary':
            continue
        add_node(pid, 'Paper', p.get('title', '')[:60], category=cat,
                year=p.get('year', ''), journal=p.get('journal', ''))

    # Add material system nodes and edges
    material_papers = defaultdict(set)
    for m in materials_data:
        mat = m['material_system']
        pid = m['paper_id']
        if mat and pid in node_ids:
            mat_id = f"MAT_{mat.replace(' ', '_')}"
            add_node(mat_id, 'Material_System', mat)
            add_edge(pid, mat_id, 'studies')
            material_papers[mat].add(pid)

    # Add method nodes and edges
    method_papers = defaultdict(set)
    for m in methods_data:
        method = m['method_name']
        pid = m['paper_id']
        if method and pid in node_ids:
            method_id = f"METHOD_{method.replace(' ', '_')}"
            add_node(method_id, 'Characterization_Method', method)
            add_edge(pid, method_id, 'uses')
            method_papers[method].add(pid)

    # Add category nodes
    categories = set()
    for p in papers:
        cat = p.get('preliminary_category', 'other')
        if cat != 'supplementary':
            categories.add(cat)
    for cat in categories:
        cat_id = f"CAT_{cat}"
        add_node(cat_id, 'Research_Topic', cat.replace('_', ' ').title())

    # Link papers to categories
    for p in papers:
        cat = p.get('preliminary_category', 'other')
        if cat != 'supplementary' and p['paper_id'] in node_ids:
            add_edge(p['paper_id'], f"CAT_{cat}", 'belongs_to')

    # Add mechanism nodes based on content analysis
    mechanisms = {
        'Hydrogen_Bonding': 'Hydrogen Bonding',
        'Ionic_Interaction': 'Ionic Interaction',
        'Phase_Separation': 'Phase Separation',
        'Microphase_Separation': 'Microphase Separation',
        'Dynamic_Covalent': 'Dynamic Covalent Bond',
        'Entanglement': 'Chain Entanglement',
        'Crosslinking': 'Crosslinking',
        'Crystallization': 'Crystallization',
        'Supramolecular': 'Supramolecular Interaction',
        'Coordination': 'Metal Coordination',
    }
    for mech_id, mech_name in mechanisms.items():
        add_node(f"MECH_{mech_id}", 'Mechanism', mech_name)

    # Add property nodes
    properties = {
        'Toughness': 'Toughness',
        'Self_Healing': 'Self-Healing',
        'Stretchability': 'Stretchability',
        'Ionic_Conductivity': 'Ionic Conductivity',
        'Piezoelectric': 'Piezoelectric Response',
        'Shape_Memory': 'Shape Memory',
        'Fatigue_Resistance': 'Fatigue Resistance',
        'Biocompatibility': 'Biocompatibility',
        'Transparency': 'Transparency',
        'Adhesion': 'Adhesion',
        'Crystallinity': 'Crystallinity',
        'Viscoelasticity': 'Viscoelasticity',
    }
    for prop_id, prop_name in properties.items():
        add_node(f"PROP_{prop_id}", 'Property', prop_name)

    # Add application nodes
    applications = {
        'Flexible_Electronics': 'Flexible Electronics',
        'Biomedical': 'Biomedical',
        'Energy_Harvesting': 'Energy Harvesting',
        'Sensors': 'Sensors',
        'Actuators': 'Actuators',
        'Coatings': 'Coatings',
        'Textiles': 'Textiles',
        'Packaging': 'Packaging',
    }
    for app_id, app_name in applications.items():
        add_node(f"APP_{app_id}", 'Application', app_name)

    # Add scientific question nodes
    questions = [
        ('SQ1', 'How do molecular architecture and processing control microphase separation?'),
        ('SQ2', 'What governs the balance between mechanical toughness and self-healing?'),
        ('SQ3', 'How do ionic interactions affect both mechanical and electrical properties?'),
        ('SQ4', 'What controls crystallization kinetics in dynamic polymer networks?'),
        ('SQ5', 'How can piezoelectric response be enhanced in soft polymers?'),
        ('SQ6', 'What is the role of chain entanglement in toughening hydrogels/ionogels?'),
        ('SQ7', 'How do dynamic bonds influence viscoelastic behavior?'),
        ('SQ8', 'Can machine learning predict polymer structure-property relationships?'),
    ]
    for qid, qtext in questions:
        add_node(qid, 'Scientific_Question', qtext)

    # Build relationship edges between materials and properties
    material_property_links = {
        'Polyurethane': ['Toughness', 'Self_Healing', 'Stretchability', 'Fatigue_Resistance'],
        'Hydrogel': ['Stretchability', 'Self_Healing', 'Biocompatibility'],
        'Ionogel': ['Ionic_Conductivity', 'Stretchability', 'Transparency'],
        'Elastomer': ['Stretchability', 'Toughness', 'Fatigue_Resistance'],
        'PVDF': ['Piezoelectric'],
        'PVDF-TrFE': ['Piezoelectric'],
        'PEDOT:PSS': ['Ionic_Conductivity', 'Flexible_Electronics'],
        'Vitrimer': ['Self_Healing', 'Toughness'],
        'Ionic liquid': ['Ionic_Conductivity'],
        'Block copolymer': ['Microphase_Separation'],
        'Shape memory polymer': ['Shape_Memory'],
    }
    for mat, props in material_property_links.items():
        mat_id = f"MAT_{mat.replace(' ', '_')}"
        if mat_id in node_ids:
            for prop in props:
                prop_id = f"PROP_{prop}" if f"PROP_{prop}" in node_ids else f"APP_{prop}"
                if prop_id in node_ids:
                    add_edge(mat_id, prop_id, 'exhibits')

    # Write outputs
    # Nodes
    with open(KG_DIR / "nodes.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'type', 'label'])
        writer.writeheader()
        for n in nodes:
            writer.writerow({'id': n['id'], 'type': n['type'], 'label': n['label']})

    with open(KG_DIR / "nodes.json", 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    # Edges
    with open(KG_DIR / "edges.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['source', 'target', 'relation'])
        writer.writeheader()
        for e in edges:
            writer.writerow({'source': e['source'], 'target': e['target'], 'relation': e['relation']})

    with open(KG_DIR / "edges.json", 'w', encoding='utf-8') as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)

    # Frontend data
    with open(FRONTEND_DATA / "nodes.json", 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    with open(FRONTEND_DATA / "edges.json", 'w', encoding='utf-8') as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)

    # Generate Mermaid diagrams
    generate_mermaid(nodes, edges, material_papers, method_papers)

    # Generate knowledge_graph.md
    generate_kg_markdown(nodes, edges)

    print(f"Knowledge graph built: {len(nodes)} nodes, {len(edges)} edges")
    return nodes, edges

def generate_mermaid(nodes, edges, material_papers, method_papers):
    """Generate Mermaid diagram files."""
    kg_dir = KG_DIR

    # 1. Research topic overview
    with open(kg_dir / "knowledge_graph_mermaid.md", 'w', encoding='utf-8') as f:
        f.write("# Knowledge Graph - Mermaid Diagrams\n\n")

        # Research topic overview
        f.write("## 1. Research Topic Overview\n\n")
        f.write("```mermaid\ngraph TD\n")
        topic_nodes = [n for n in nodes if n['type'] == 'Research_Topic']
        for n in topic_nodes[:15]:
            safe_id = n['id'].replace(' ', '_')
            f.write(f"    {safe_id}[\"{n['label']}\"]\n")
        f.write("```\n\n")

        # 2. Material-Property relationships
        f.write("## 2. Material System Relationships\n\n")
        f.write("```mermaid\ngraph LR\n")
        mat_nodes = [n for n in nodes if n['type'] == 'Material_System']
        prop_nodes = [n for n in nodes if n['type'] in ('Property', 'Application')]
        for n in mat_nodes[:12]:
            safe_id = n['id'].replace(' ', '_').replace('-', '_')
            f.write(f"    {safe_id}[\"{n['label']}\"]\n")
        for n in prop_nodes[:10]:
            safe_id = n['id'].replace(' ', '_').replace('-', '_')
            f.write(f"    {safe_id}[\"{n['label']}\"]\n")
        for e in edges[:30]:
            if e['relation'] in ('exhibits', 'studies'):
                s = e['source'].replace(' ', '_').replace('-', '_')
                t = e['target'].replace(' ', '_').replace('-', '_')
                f.write(f"    {s} -->|{e['relation']}| {t}\n")
        f.write("```\n\n")

        # 3. Method network
        f.write("## 3. Characterization Method Network\n\n")
        f.write("```mermaid\ngraph TD\n")
        method_nodes = [n for n in nodes if n['type'] == 'Characterization_Method']
        for n in method_nodes[:15]:
            safe_id = n['id'].replace(' ', '_').replace('-', '_')
            f.write(f"    {safe_id}[\"{n['label']}\"]\n")
        f.write("```\n\n")

        # 4. Scientific questions
        f.write("## 4. Scientific Questions Network\n\n")
        f.write("```mermaid\ngraph TD\n")
        sq_nodes = [n for n in nodes if n['type'] == 'Scientific_Question']
        for n in sq_nodes:
            safe_id = n['id']
            label = n['label'][:50]
            f.write(f"    {safe_id}[\"{label}\"]\n")
        f.write("```\n\n")

def generate_kg_markdown(nodes, edges):
    """Generate knowledge graph markdown document."""
    with open(KG_DIR / "knowledge_graph.md", 'w', encoding='utf-8') as f:
        f.write("# Knowledge Graph\n\n")
        f.write(f"## Statistics\n\n")
        f.write(f"- **Total nodes**: {len(nodes)}\n")
        f.write(f"- **Total edges**: {len(edges)}\n\n")

        # Node type distribution
        node_types = Counter(n['type'] for n in nodes)
        f.write("## Node Types\n\n")
        for ntype, count in node_types.most_common():
            f.write(f"- **{ntype}**: {count}\n")

        f.write("\n## Edge Types\n\n")
        edge_types = Counter(e['relation'] for e in edges)
        for etype, count in edge_types.most_common():
            f.write(f"- **{etype}**: {count}\n")

        # Material systems
        f.write("\n## Material Systems\n\n")
        mat_nodes = [n for n in nodes if n['type'] == 'Material_System']
        for n in mat_nodes:
            f.write(f"- {n['label']} ({n['id']})\n")

        # Methods
        f.write("\n## Characterization Methods\n\n")
        method_nodes = [n for n in nodes if n['type'] == 'Characterization_Method']
        for n in method_nodes:
            f.write(f"- {n['label']}\n")

        # Scientific questions
        f.write("\n## Scientific Questions\n\n")
        sq_nodes = [n for n in nodes if n['type'] == 'Scientific_Question']
        for n in sq_nodes:
            f.write(f"- **{n['id']}**: {n['label']}\n")

if __name__ == "__main__":
    build_knowledge_graph()
