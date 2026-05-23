#!/usr/bin/env python3
"""Parse deep_reading_notes.md and build comprehensive knowledge graph JSON files."""

import json
import re
from pathlib import Path
from collections import defaultdict

NOTES_PATH = Path(r"D:\Academic-RAG\06_logs\deep_reading_notes.md")
OUT_DIR = Path(r"D:\Academic-RAG\03_knowledge_graph")
FRONTEND_DATA = Path(r"D:\Academic-RAG\07_frontend\src\data")

# --- Duplicate map from summary ---
DUPLICATES = {
    "P292": "P284", "P295": "P291", "P296": "P293",
    "P324": "P217", "P325": "P221", "P328": "P308",
    "P388": "P376", "P389": "P381", "P255": "P242",
    "P019": "P016", "P059": "P060", "P120": "P115",
    "P124": "P114", "P130": "P126", "P131": "P127",
    "P132": "P128", "P133": "P129", "P134": "P122",
    "P135": "P129", "P141": "P139", "P142": "P121",
    "P144": "P143", "P158": "P159",
    "P421": "P418", "P432": "P347", "P436": "P351",
    "P445": "P383", "P453": "P454",
}

# Course material IDs (not research papers)
COURSE_MATERIALS = set(f"P{i:03d}" for i in range(305, 319))  # P305-P318
EMPTY_PAPERS = {"P125", "P137", "P138"}


def parse_notes(path):
    """Parse deep_reading_notes.md into structured entries."""
    text = path.read_text(encoding="utf-8")
    entries = {}

    # Split by ## PXXX pattern
    pattern = r"^## (P\d{3})\s*[-–]\s*(.+?)$"
    sections = re.split(pattern, text, flags=re.MULTILINE)

    # sections[0] is preamble, then groups of (ID, title, content)
    for i in range(1, len(sections), 3):
        pid = sections[i].strip()
        title_hint = sections[i + 1].strip()
        content = sections[i + 2].strip() if i + 2 < len(sections) else ""

        if pid in EMPTY_PAPERS or "empty" in content.lower()[:50]:
            continue

        entry = parse_entry(pid, title_hint, content)
        if entry:
            entries[pid] = entry

    return entries


def parse_entry(pid, title_hint, content):
    """Parse a single entry's content into structured fields."""
    entry = {"id": pid}

    # Check if it's a duplicate reference
    if re.match(r"(?i)duplicate\s+of\s+P\d{3}", content):
        return None

    # Check if it's just a stub (prior session, not deep-read)
    if "not yet deep-read" in content.lower() or "read in prior session" in content.lower():
        # Still record it but with limited info
        entry["title"] = title_hint
        entry["stub"] = True
        return entry

    entry["stub"] = False

    # Extract fields
    field_patterns = {
        "title": r"\*\*Title\*\*:\s*(.+)",
        "authors": r"\*\*Authors\*\*:\s*(.+)",
        "institution": r"\*\*Institution\*\*:\s*(.+)",
        "journal": r"\*\*Journal\*\*:\s*(.+)",
        "materials": r"\*\*Materials\*\*:\s*(.+)",
        "methods": r"\*\*Methods\*\*:\s*(.+)",
        "key_findings": r"\*\*Key Findings\*\*:\s*(.+)",
        "scientific_questions": r"\*\*Scientific Questions\*\*:\s*(.+)",
    }

    for field, pattern in field_patterns.items():
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            entry[field] = m.group(1).strip()
        else:
            entry[field] = ""

    # Use title_hint as fallback
    if not entry["title"]:
        entry["title"] = title_hint

    return entry


def extract_materials(materials_str):
    """Extract material keywords from materials string."""
    if not materials_str:
        return []

    # Split by common delimiters
    materials = []

    # Extract key material terms
    # Common patterns: "Material1, Material2", "Material1 (description)"
    parts = re.split(r"[,;]", materials_str)
    for part in parts:
        part = part.strip()
        if not part or len(part) < 3:
            continue
        # Remove parenthetical descriptions for categorization
        clean = re.sub(r"\(.*?\)", "", part).strip()
        if clean and len(clean) > 2:
            materials.append(clean)

    return materials[:10]  # Limit to top 10


def extract_methods(methods_str):
    """Extract method keywords from methods string."""
    if not methods_str:
        return []

    methods = []
    parts = re.split(r"[,;]", methods_str)
    for part in parts:
        part = part.strip()
        if not part or len(part) < 3:
            continue
        clean = re.sub(r"\(.*?\)", "", part).strip()
        if clean and len(clean) > 2:
            methods.append(clean)

    return methods[:10]


def categorize_paper(entry):
    """Assign a research category based on content."""
    text = " ".join([
        entry.get("title", ""),
        entry.get("materials", ""),
        entry.get("methods", ""),
        entry.get("key_findings", ""),
    ]).lower()

    categories = []

    category_keywords = {
        "tpu_elastomer": ["thermoplastic polyurethane", "tpu", "polyurethane elastomer"],
        "hydrogel": ["hydrogel", "gel electrolyte", "ionic gel"],
        "self_healing": ["self-heal", "self-healing", "healable"],
        "vitrimers": ["vitrimer", "dynamic covalent network", "dcpn"],
        "block_copolymer": ["block copolymer", "bcps", "self-assembly"],
        "polymer_brush": ["polymer brush", "brush"],
        "ionic_material": ["ionic", "ionogel", "ionene", "ionic liquid"],
        "piezoelectric": ["piezoelectric", "ferroelectric", "piezocatal"],
        "shape_memory": ["shape memory", "shape-memory", "smp"],
        "polymer_crystallization": ["crystalliz", "crystalline", "saxs", "waxd"],
        "glass_transition": ["glass transition", "glass-forming", "gardner"],
        "supramolecular": ["supramolecular", "hydrogen bond", "h-bond"],
        "triboelectric": ["triboelectric", "teng"],
        "biomaterial": ["biomaterial", "tissue engineering", "scaffold", "bioelast"],
        "polymer_simulation": ["simulation", "molecular dynamics", "dft", "scft"],
        "conducting_polymer": ["conducting polymer", "pedot", "polyaniline", "pani"],
        "polymerization": ["polymerization", "atrp", "raft", "living"],
        "rheology": ["rheolog", "viscoelastic", "relaxation"],
        "mechanochromic": ["mechanochrom", "color-change"],
        "copolyester": ["copolyester", "polyester", "fdca", "bio-based"],
        "lce": ["liquid crystal elastomer", "lce"],
    }

    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text:
                categories.append(cat)
                break

    if not categories:
        categories.append("other")

    return categories[0]  # Primary category


def extract_institution(entry):
    """Extract primary institution."""
    inst = entry.get("institution", "")
    if not inst or inst.startswith("(") or "not" in inst.lower()[:20]:
        return "Unknown"
    # Take first institution
    parts = re.split(r"[;,]", inst)
    return parts[0].strip()[:80]


def extract_year(entry):
    """Extract publication year from journal field."""
    journal = entry.get("journal", "")
    m = re.search(r"(\d{4})", journal)
    if m:
        return m.group(1)
    return ""


def build_graph(entries):
    """Build nodes and edges from parsed entries."""
    nodes = []
    edges = []
    node_ids = set()

    # Material taxonomy - map raw mentions to canonical names
    MATERIAL_TAXONOMY = {
        "tpu": "TPU (Thermoplastic Polyurethane)",
        "thermoplastic polyurethane": "TPU (Thermoplastic Polyurethane)",
        "polyurethane": "Polyurethane",
        "polyimide": "Polyimide",
        "polyimides": "Polyimide",
        "block copolymer": "Block Copolymers",
        "block copolymers": "Block Copolymers",
        "bcps": "Block Copolymers",
        "hydrogel": "Hydrogels",
        "hydrogels": "Hydrogels",
        "ionogel": "Ionogels",
        "ionogels": "Ionogels",
        "organogel": "Organogels",
        "organogels": "Organogels",
        "vitrimer": "Vitrimers",
        "vitrimers": "Vitrimers",
        "dynamic covalent network": "Dynamic Covalent Networks",
        "dcpn": "Dynamic Covalent Networks",
        "polymer brush": "Polymer Brushes",
        "polymer brushes": "Polymer Brushes",
        "ionic liquid": "Ionic Liquids",
        "ionic liquids": "Ionic Liquids",
        "pedot": "PEDOT:PSS",
        "pedot:pss": "PEDOT:PSS",
        "pvdf": "PVDF",
        "polyvinylidene fluoride": "PVDF",
        "polyacrylonitrile": "PAN",
        "pan": "PAN",
        "polyethylene": "Polyethylene",
        "polyethylene glycol": "PEG",
        "peg": "PEG",
        "polylactic acid": "PLA",
        "pla": "PLA",
        "pcl": "PCL",
        "polycaprolactone": "PCL",
        "polyvinyl alcohol": "PVA",
        "pva": "PVA",
        "poly(methyl methacrylate)": "PMMA",
        "pmma": "PMMA",
        "polyacrylamide": "PAM",
        "pam": "PAM",
        "polydimethylsiloxane": "PDMS",
        "pdms": "PDMS",
        "chitosan": "Chitosan",
        "cellulose": "Cellulose",
        "collagen": "Collagen",
        "keratin": "Keratin",
        "silk": "Silk",
        "ionene": "Ionomers",
        "ionomer": "Ionomers",
        "ionomers": "Ionomers",
        "polyelectrolyte": "Polyelectrolytes",
        "polyelectrolytes": "Polyelectrolytes",
        "polyurea": "Polyurea",
        "polyurethane urea": "Polyurea",
        "polylipoate": "Polylipoates",
        "poly(disulfide)": "Poly(disulfide)s",
        "polyester": "Polyesters",
        "polyesters": "Polyesters",
        "polyacrylate": "Polyacrylates",
        "acrylate": "Polyacrylates",
        "liquid crystal elastomer": "Liquid Crystal Elastomers",
        "lce": "Liquid Crystal Elastomers",
        "lces": "Liquid Crystal Elastomers",
        "shape memory": "Shape Memory Polymers",
        "shape-memory": "Shape Memory Polymers",
        "smp": "Shape Memory Polymers",
        "elastomer": "Elastomers",
        "elastomers": "Elastomers",
        "mxene": "MXenes",
        "mxenes": "MXenes",
        "cnt": "Carbon Nanotubes",
        "carbon nanotube": "Carbon Nanotubes",
        "graphene": "Graphene",
        "rGO": "Graphene",
        "GO": "Graphene",
        "BaTiO3": "BaTiO₃",
        "barium titanate": "BaTiO₃",
        "ZnO": "ZnO",
        "zinc oxide": "ZnO",
        "MoS2": "MoS₂",
        "nanocellulose": "Nanocellulose",
        "carrageenan": "Carrageenan",
        "alginate": "Alginate",
        "gelatin": "Gelatin",
        "polyacrylonitrile": "PAN",
        "Nylon": "Nylon",
        "polyamide": "Nylon",
        "polyamide (PA)": "Nylon",
    }

    # Method taxonomy
    METHOD_TAXONOMY = {
        "saxs": "SAXS",
        "waxs": "WAXS",
        "waxd": "WAXD",
        "small-angle x-ray": "SAXS",
        "wide-angle": "WAXS/WAXD",
        "dsc": "DSC",
        "differential scanning calorimetry": "DSC",
        "dma": "DMA",
        "dynamic mechanical analysis": "DMA",
        "tensile testing": "Tensile Testing",
        "mechanical testing": "Mechanical Testing",
        "rheology": "Rheology",
        "rheological": "Rheology",
        "ft-ir": "FTIR",
        "ftir": "FTIR",
        "afm": "AFM",
        "atomic force microscopy": "AFM",
        "sem": "SEM",
        "tem": "TEM",
        "xps": "XPS",
        "nmr": "NMR",
        "molecular dynamics": "MD Simulation",
        "md simulation": "MD Simulation",
        "dft": "DFT",
        "density functional theory": "DFT",
        "scft": "SCFT",
        "self-consistent field": "SCFT",
        "atrp": "ATRP",
        "raft": "RAFT",
        "living polymerization": "Living Polymerization",
        "anionic polymerization": "Anionic Polymerization",
        "romp": "ROMP",
        "3d printing": "3D Printing",
        "electrospinning": "Electrospinning",
        "dielectric spectroscopy": "Dielectric Spectroscopy",
        "pfm": "PFM",
        "piezoresponse force microscopy": "PFM",
        "neutron scattering": "Neutron Scattering",
        "neutron diffuse scattering": "Neutron Scattering",
        "sec": "SEC/GPC",
        "sec-malls": "SEC/GPC",
        "tga": "TGA",
        "thermogravimetric": "TGA",
        "frap": "FRAP",
        "itc": "ITC",
        "calorimetry": "Calorimetry",
        "gel permeation": "SEC/GPC",
        "pals": "PALS",
        "positron annihilation": "PALS",
        "shg": "SHG",
        "second harmonic generation": "SHG",
        "conductivity": "Conductivity Measurement",
        "four-point probe": "Conductivity Measurement",
        "eis": "EIS",
        "impedance spectroscopy": "EIS",
        "comsol": "COMSOL FEM",
        "finite element": "FEM",
        "phase-field": "Phase-Field Simulation",
        "first-principles": "First-Principles Calculation",
    }

    # Concept keywords for theme extraction
    CONCEPT_KEYWORDS = {
        "self-assembly": "Self-Assembly",
        "phase separation": "Phase Separation",
        "microphase separation": "Microphase Separation",
        "crystallization": "Crystallization",
        "glass transition": "Glass Transition",
        "energy landscape": "Energy Landscape",
        "gardner transition": "Gardner Transition",
        "dynamic covalent": "Dynamic Covalent Chemistry",
        "hydrogen bond": "Hydrogen Bonding",
        "h-bond": "Hydrogen Bonding",
        "supramolecular": "Supramolecular Chemistry",
        "ionic interaction": "Ionic Interactions",
        "coordination bond": "Coordination Bonds",
        "shape memory": "Shape Memory Effect",
        "self-healing": "Self-Healing",
        "recyclab": "Recyclability",
        "toughness": "Toughness",
        "fracture": "Fracture Mechanics",
        "fatigue": "Fatigue Resistance",
        "viscoelastic": "Viscoelasticity",
        "rheolog": "Rheology",
        "topological": "Topology",
        "entanglement": "Entanglement",
        "crosslink": "Crosslinking",
        "cross-link": "Crosslinking",
        "piezoelectric": "Piezoelectricity",
        "ferroelectric": "Ferroelectricity",
        "triboelectric": "Triboelectricity",
        "mechanochrom": "Mechanochromism",
        "fluorescen": "Fluorescence",
        "phosphorescen": "Phosphorescence",
        "clusteroluminescen": "Clusteroluminescence",
        "biocompatib": "Biocompatibility",
        "biodegrad": "Biodegradability",
        "sustainab": "Sustainability",
        "bio-based": "Bio-based Materials",
        "chain dynamics": "Chain Dynamics",
        "cooperative motion": "Cooperative Motion",
        "relaxation": "Relaxation Dynamics",
        "segmental dynamics": "Segmental Dynamics",
        "free volume": "Free Volume",
        "percolation": "Percolation",
        "network": "Polymer Networks",
        "graft": "Grafting",
        "brush": "Polymer Brushes",
        "copolymer": "Copolymers",
        "block copolymer": "Block Copolymers",
        "homopolymer": "Homopolymers",
        "blending": "Polymer Blending",
        "nanocomposite": "Nanocomposites",
        "filler": "Fillers",
        "reinforcement": "Reinforcement",
        "interface": "Interfaces",
        "surface": "Surface Properties",
        "wetting": "Wetting",
        "adhesion": "Adhesion",
        "diffusion": "Diffusion",
        "transport": "Transport Properties",
        "conductivity": "Ionic/Electronic Conductivity",
        "ion transport": "Ion Transport",
        "membrane": "Membranes",
        "actuat": "Actuation",
        "soft robotics": "Soft Robotics",
        "sensor": "Sensing",
        "energy harvest": "Energy Harvesting",
        "tissue engineering": "Tissue Engineering",
        "wound healing": "Wound Healing",
        "drug delivery": "Drug Delivery",
        "4d print": "4D Printing",
        "additive manufacturing": "Additive Manufacturing",
    }

    # Build paper nodes
    for pid, entry in entries.items():
        if entry.get("stub"):
            continue

        cat = categorize_paper(entry)
        year = extract_year(entry)
        inst = extract_institution(entry)

        paper_node = {
            "id": pid,
            "type": "Paper",
            "label": entry.get("title", "")[:100],
            "full_title": entry.get("title", ""),
            "category": cat,
            "year": year,
            "journal": entry.get("journal", ""),
            "authors": entry.get("authors", ""),
            "institution": inst,
            "materials_raw": entry.get("materials", ""),
            "methods_raw": entry.get("methods", ""),
            "key_findings": entry.get("key_findings", ""),
            "scientific_questions": entry.get("scientific_questions", ""),
        }
        nodes.append(paper_node)
        node_ids.add(pid)

        # Extract and link materials
        raw_materials = extract_materials(entry.get("materials", ""))
        for mat in raw_materials:
            mat_lower = mat.lower().strip()
            # Find canonical name
            canonical = None
            for key, val in MATERIAL_TAXONOMY.items():
                if key in mat_lower:
                    canonical = val
                    break
            if not canonical:
                canonical = mat[:60]

            mat_id = "MAT_" + re.sub(r"[^a-zA-Z0-9]", "_", canonical)[:40]
            if mat_id not in node_ids:
                nodes.append({
                    "id": mat_id,
                    "type": "Material",
                    "label": canonical,
                    "category": "material",
                })
                node_ids.add(mat_id)

            edges.append({
                "source": pid,
                "target": mat_id,
                "relation": "studies",
            })

        # Extract and link methods
        raw_methods = extract_methods(entry.get("methods", ""))
        for method in raw_methods:
            method_lower = method.lower().strip()
            canonical = None
            for key, val in METHOD_TAXONOMY.items():
                if key in method_lower:
                    canonical = val
                    break
            if not canonical:
                canonical = method[:50]

            method_id = "METH_" + re.sub(r"[^a-zA-Z0-9]", "_", canonical)[:40]
            if method_id not in node_ids:
                nodes.append({
                    "id": method_id,
                    "type": "Method",
                    "label": canonical,
                    "category": "method",
                })
                node_ids.add(method_id)

            edges.append({
                "source": pid,
                "target": method_id,
                "relation": "uses",
            })

        # Extract and link concepts from key_findings and scientific_questions
        full_text = (entry.get("key_findings", "") + " " + entry.get("scientific_questions", "")).lower()
        for kw, concept in CONCEPT_KEYWORDS.items():
            if kw in full_text:
                concept_id = "CONC_" + re.sub(r"[^a-zA-Z0-9]", "_", concept)[:40]
                if concept_id not in node_ids:
                    nodes.append({
                        "id": concept_id,
                        "type": "Concept",
                        "label": concept,
                        "category": "concept",
                    })
                    node_ids.add(concept_id)

                edges.append({
                    "source": pid,
                    "target": concept_id,
                    "relation": "addresses",
                })

        # Link to institution
        if inst and inst != "Unknown":
            inst_id = "INST_" + re.sub(r"[^a-zA-Z0-9]", "_", inst)[:40]
            if inst_id not in node_ids:
                nodes.append({
                    "id": inst_id,
                    "type": "Institution",
                    "label": inst,
                    "category": "institution",
                })
                node_ids.add(inst_id)

            edges.append({
                "source": pid,
                "target": inst_id,
                "relation": "from",
            })

    # Build cross-paper edges based on shared materials, methods, concepts
    paper_nodes = [n for n in nodes if n["type"] == "Paper"]
    paper_materials = defaultdict(set)
    paper_methods = defaultdict(set)
    paper_concepts = defaultdict(set)

    for e in edges:
        if e["relation"] == "studies":
            paper_materials[e["source"]].add(e["target"])
        elif e["relation"] == "uses":
            paper_methods[e["source"]].add(e["target"])
        elif e["relation"] == "addresses":
            paper_concepts[e["source"]].add(e["target"])

    paper_ids = [n["id"] for n in paper_nodes]
    cross_links = set()

    for i, p1 in enumerate(paper_ids):
        for p2 in paper_ids[i+1:]:
            shared_mats = paper_materials[p1] & paper_materials[p2]
            shared_methods = paper_methods[p1] & paper_methods[p2]
            shared_concepts = paper_concepts[p1] & paper_concepts[p2]

            if len(shared_mats) >= 2 or (len(shared_mats) >= 1 and len(shared_concepts) >= 2):
                key = tuple(sorted([p1, p2]))
                if key not in cross_links:
                    edges.append({
                        "source": p1,
                        "target": p2,
                        "relation": "related_material",
                        "weight": len(shared_mats),
                    })
                    cross_links.add(key)

            if len(shared_methods) >= 3:
                key = tuple(sorted([p1, p2]))
                if key not in cross_links:
                    edges.append({
                        "source": p1,
                        "target": p2,
                        "relation": "related_method",
                        "weight": len(shared_methods),
                    })
                    cross_links.add(key)

            if len(shared_concepts) >= 4:
                key = tuple(sorted([p1, p2]))
                if key not in cross_links:
                    edges.append({
                        "source": p1,
                        "target": p2,
                        "relation": "related_concept",
                        "weight": len(shared_concepts),
                    })
                    cross_links.add(key)

    return nodes, edges


def generate_summary(entries):
    """Generate summary statistics from entries."""
    categories = defaultdict(int)
    years = defaultdict(int)
    journals = defaultdict(int)
    institutions = defaultdict(int)

    for pid, entry in entries.items():
        if entry.get("stub"):
            continue
        cat = categorize_paper(entry)
        categories[cat] += 1

        year = extract_year(entry)
        if year:
            years[year] += 1

        journal = entry.get("journal", "")
        if journal:
            # Clean journal name
            j = re.sub(r"\s*\d{4}.*", "", journal).strip()
            if j:
                journals[j] += 1

        inst = extract_institution(entry)
        if inst and inst != "Unknown":
            institutions[inst] += 1

    return {
        "categories": dict(sorted(categories.items(), key=lambda x: -x[1])),
        "years": dict(sorted(years.items())),
        "journals": dict(sorted(journals.items(), key=lambda x: -x[1])[:30]),
        "institutions": dict(sorted(institutions.items(), key=lambda x: -x[1])[:30]),
    }


def main():
    print("Parsing deep_reading_notes.md...")
    entries = parse_notes(NOTES_PATH)
    print(f"Parsed {len(entries)} entries")

    # Filter out duplicates (point to canonical)
    canonical_entries = {}
    for pid, entry in entries.items():
        if pid in DUPLICATES:
            continue  # Skip duplicates
        canonical_entries[pid] = entry

    print(f"Canonical entries: {len(canonical_entries)}")

    print("Building knowledge graph...")
    nodes, edges = build_graph(canonical_entries)
    print(f"Generated {len(nodes)} nodes, {len(edges)} edges")

    # Count by type
    type_counts = defaultdict(int)
    for n in nodes:
        type_counts[n["type"]] += 1
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")

    relation_counts = defaultdict(int)
    for e in edges:
        relation_counts[e["relation"]] += 1
    for r, c in sorted(relation_counts.items()):
        print(f"  {r}: {c}")

    # Generate summary
    summary = generate_summary(canonical_entries)

    # Write outputs
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_DATA.mkdir(parents=True, exist_ok=True)

    # Knowledge graph files
    with open(OUT_DIR / "nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    with open(OUT_DIR / "edges.json", "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)

    # Frontend data files
    # Papers list
    papers = [n for n in nodes if n["type"] == "Paper"]
    with open(FRONTEND_DATA / "papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    # Materials
    materials = [n for n in nodes if n["type"] == "Material"]
    with open(FRONTEND_DATA / "materials.json", "w", encoding="utf-8") as f:
        json.dump(materials, f, ensure_ascii=False, indent=2)

    # Methods
    methods = [n for n in nodes if n["type"] == "Method"]
    with open(FRONTEND_DATA / "methods.json", "w", encoding="utf-8") as f:
        json.dump(methods, f, ensure_ascii=False, indent=2)

    # Concepts
    concepts = [n for n in nodes if n["type"] == "Concept"]
    with open(FRONTEND_DATA / "questions.json", "w", encoding="utf-8") as f:
        json.dump(concepts, f, ensure_ascii=False, indent=2)

    # Full graph for frontend
    graph_data = {
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "metadata": {
            "total_papers": len(papers),
            "total_materials": len(materials),
            "total_methods": len(methods),
            "total_concepts": len(concepts),
            "total_edges": len(edges),
        },
    }
    with open(FRONTEND_DATA / "graph.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    # Also write summary separately
    with open(FRONTEND_DATA / "evidence.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Write CSVs for external tools
    with open(OUT_DIR / "nodes.csv", "w", encoding="utf-8") as f:
        f.write("id,type,label,category,year,journal\n")
        for n in nodes:
            f.write(f'"{n["id"]}","{n["type"]}","{n.get("label","")}","{n.get("category","")}","{n.get("year","")}","{n.get("journal","")}"\n')

    with open(OUT_DIR / "edges.csv", "w", encoding="utf-8") as f:
        f.write("source,target,relation,weight\n")
        for e in edges:
            f.write(f'"{e["source"]}","{e["target"]}","{e["relation"]}","{e.get("weight", 1)}"\n')

    print(f"\nOutput written to {OUT_DIR}")
    print(f"Frontend data written to {FRONTEND_DATA}")
    print(f"Summary: {summary['categories']}")


if __name__ == "__main__":
    main()
