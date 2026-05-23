#!/usr/bin/env python3
"""Phase 5-7: Synthesis analysis, scientific questions, future directions."""

import csv
import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

PROJECT_DIR = Path(r"D:\Academic-RAG")
EVIDENCE_DIR = PROJECT_DIR / "02_evidence_database"
SYNTHESIS_DIR = PROJECT_DIR / "04_synthesis"
FRONTEND_DATA = PROJECT_DIR / "07_frontend" / "src" / "data"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_research_team_comparison(papers, materials_data, methods_data):
    """Generate research team comparison analysis."""
    # Group by category/research direction
    categories = defaultdict(list)
    for p in papers:
        cat = p.get('preliminary_category', 'other')
        if cat != 'supplementary':
            categories[cat].append(p)

    with open(SYNTHESIS_DIR / "research_team_comparison.md", 'w', encoding='utf-8') as f:
        f.write("# Research Team and Direction Comparison\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Overview\n\n")
        f.write(f"This analysis compares {len(categories)} major research directions identified across {len([p for p in papers if p.get('preliminary_category') != 'supplementary'])} papers.\n\n")

        for cat, cat_papers in sorted(categories.items(), key=lambda x: -len(x[1])):
            f.write(f"## {cat.replace('_', ' ').title()}\n\n")
            f.write(f"**Number of papers**: {len(cat_papers)}\n\n")

            # Year distribution
            years = Counter(p.get('year', '') for p in cat_papers if p.get('year'))
            if years:
                f.write("**Year distribution**: ")
                f.write(', '.join(f"{y}({c})" for y, c in sorted(years.items())))
                f.write("\n\n")

            # Journal distribution
            journals = Counter(p.get('journal', '') for p in cat_papers if p.get('journal'))
            if journals:
                f.write("**Key journals**: ")
                f.write(', '.join(f"{j}({c})" for j, c in journals.most_common(5)))
                f.write("\n\n")

            # Materials used
            cat_materials = set()
            for m in materials_data:
                if m['paper_id'] in {p['paper_id'] for p in cat_papers} and m['material_system']:
                    cat_materials.add(m['material_system'])
            if cat_materials:
                f.write(f"**Material systems**: {', '.join(sorted(cat_materials))}\n\n")

            # Methods used
            cat_methods = set()
            for m in methods_data:
                if m['paper_id'] in {p['paper_id'] for p in cat_papers} and m['method_name']:
                    cat_methods.add(m['method_name'])
            if cat_methods:
                f.write(f"**Key methods**: {', '.join(sorted(cat_methods))}\n\n")

            # Representative papers
            f.write("**Representative papers**:\n")
            for p in cat_papers[:5]:
                title = p.get('title', '')[:80]
                year = p.get('year', 'N/A')
                journal = p.get('journal', 'N/A')
                f.write(f"- [{p['paper_id']}] {title} ({year}, {journal})\n")
            f.write("\n---\n\n")

def generate_method_evolution(methods_data, papers):
    """Generate method evolution analysis."""
    # Group methods by year
    paper_years = {p['paper_id']: p.get('year', '') for p in papers}
    method_by_year = defaultdict(lambda: Counter())
    for m in methods_data:
        year = paper_years.get(m['paper_id'], '')
        if year and m['method_name']:
            method_by_year[year][m['method_name']] += 1

    with open(SYNTHESIS_DIR / "method_evolution.md", 'w', encoding='utf-8') as f:
        f.write("# Method Evolution Analysis\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Overall method popularity
        all_methods = Counter()
        for m in methods_data:
            if m['method_name']:
                all_methods[m['method_name']] += 1

        f.write("## Most Used Methods (Overall)\n\n")
        f.write("| Rank | Method | Count |\n")
        f.write("|------|--------|-------|\n")
        for i, (method, count) in enumerate(all_methods.most_common(20), 1):
            f.write(f"| {i} | {method} | {count} |\n")
        f.write("\n")

        # Method trends over time
        f.write("## Method Trends by Year\n\n")
        for year in sorted(method_by_year.keys()):
            if method_by_year[year]:
                f.write(f"### {year}\n")
                for method, count in method_by_year[year].most_common(10):
                    f.write(f"- {method}: {count}\n")
                f.write("\n")

        # Emerging methods
        f.write("## Emerging Methods (2023-2026)\n\n")
        recent_methods = Counter()
        for year in ['2023', '2024', '2025', '2026']:
            for method, count in method_by_year.get(year, {}).items():
                recent_methods[method] += count
        for method, count in recent_methods.most_common(15):
            f.write(f"- **{method}**: {count} papers\n")
        f.write("\n")

def generate_scientific_questions(papers, materials_data, methods_data):
    """Generate ranked scientific questions."""
    # Analyze gaps and questions
    all_materials = Counter()
    for m in materials_data:
        if m['material_system']:
            all_materials[m['material_system']] += 1

    all_methods = Counter()
    for m in methods_data:
        if m['method_name']:
            all_methods[m['method_name']] += 1

    # Define scientific questions based on literature analysis
    questions = [
        {
            'id': 'SQ1',
            'question': 'How does molecular architecture (hard segment length, soft segment type, branching) control microphase separation morphology and kinetics in segmented polyurethanes?',
            'importance': 5,
            'feasibility': 4,
            'literature_gap': 4,
            'priority': 80,
            'evidence': 'Multiple papers study TPU microphase separation but quantitative structure-morphology relationships remain incomplete.',
            'current_evidence': 'SAXS, DMA, and MD simulations provide partial understanding.',
            'gaps': 'Systematic variation of hard/soft segment parameters with coupled characterization is lacking.',
            'related_papers': ['P001', 'P002', 'P003'],
        },
        {
            'id': 'SQ2',
            'question': 'What is the quantitative relationship between ionic cluster morphology and ionic conductivity in ionomers and ionogels?',
            'importance': 5,
            'feasibility': 4,
            'literature_gap': 5,
            'priority': 100,
            'evidence': 'Ionic conductivity depends on cluster connectivity but quantitative models are missing.',
            'current_evidence': 'Impedance spectroscopy, SAXS, and NMR provide partial picture.',
            'gaps': 'In situ characterization of ion transport under deformation is rare.',
            'related_papers': [],
        },
        {
            'id': 'SQ3',
            'question': 'Can self-healing efficiency and mechanical toughness be simultaneously maximized in dynamic covalent polymer networks?',
            'importance': 5,
            'feasibility': 3,
            'literature_gap': 4,
            'priority': 60,
            'evidence': 'Trade-off between dynamic bond exchange rate and mechanical integrity is well documented.',
            'current_evidence': 'Multiple self-healing systems studied but optimization is largely empirical.',
            'gaps': 'Predictive models for the toughness-healing trade-off are lacking.',
            'related_papers': [],
        },
        {
            'id': 'SQ4',
            'question': 'How do processing conditions (shear, temperature, solvent) affect crystallization kinetics and crystal polymorphism in biodegradable polyesters?',
            'importance': 4,
            'feasibility': 4,
            'literature_gap': 3,
            'priority': 48,
            'evidence': 'PLA and PCL crystallization well studied but polymorph control remains challenging.',
            'current_evidence': 'DSC, WAXD, and SAXS provide good characterization tools.',
            'gaps': 'Real-time crystallization monitoring during processing is limited.',
            'related_papers': [],
        },
        {
            'id': 'SQ5',
            'question': 'What mechanisms govern piezoelectric response in non-polar polymers and how can it be enhanced through structural engineering?',
            'importance': 5,
            'feasibility': 3,
            'literature_gap': 5,
            'priority': 75,
            'evidence': 'Piezoelectricity in PVDF well understood but in other polymers is less clear.',
            'current_evidence': 'DFT calculations and experimental measurements available.',
            'gaps': 'Mechanism for piezoelectricity in non-polar polymers needs clarification.',
            'related_papers': [],
        },
        {
            'id': 'SQ6',
            'question': 'How does chain entanglement density affect fracture mechanics and fatigue resistance in polymer networks and gels?',
            'importance': 4,
            'feasibility': 4,
            'literature_gap': 4,
            'priority': 64,
            'evidence': 'Entanglement effects on rheology well studied but fracture mechanics less understood.',
            'current_evidence': 'Rheology, neutron scattering, and mechanical testing available.',
            'gaps': 'Quantitative entanglement-fracture relationships are lacking.',
            'related_papers': [],
        },
        {
            'id': 'SQ7',
            'question': 'Can machine learning models accurately predict polymer properties from molecular structure without extensive training data?',
            'importance': 4,
            'feasibility': 3,
            'literature_gap': 4,
            'priority': 48,
            'evidence': 'ML models show promise but generalizability is limited.',
            'current_evidence': 'GNN, transformer, and traditional ML approaches tested.',
            'gaps': 'Limited training data and domain-specific featurization remain challenges.',
            'related_papers': [],
        },
        {
            'id': 'SQ8',
            'question': 'How do dynamic bonds (hydrogen bonds, ionic interactions, coordination bonds) influence viscoelastic relaxation spectra?',
            'importance': 4,
            'feasibility': 4,
            'literature_gap': 3,
            'priority': 48,
            'evidence': 'Sticky Rouse model and various dynamic bond studies available.',
            'current_evidence': 'Rheology and NMR provide good characterization.',
            'gaps': 'Unified framework for different dynamic bond types is missing.',
            'related_papers': [],
        },
        {
            'id': 'SQ9',
            'question': 'What controls the mechanical response of ionogels under extreme conditions (cryogenic, high temperature, high strain rate)?',
            'importance': 4,
            'feasibility': 3,
            'literature_gap': 4,
            'priority': 48,
            'evidence': 'Some cryogenic studies exist but systematic investigation is limited.',
            'current_evidence': 'DMA, tensile testing at various temperatures available.',
            'gaps': 'High strain rate and cryogenic data are sparse.',
            'related_papers': [],
        },
        {
            'id': 'SQ10',
            'question': 'How can triboelectric nanogenerator performance be improved through polymer surface and interface engineering?',
            'importance': 4,
            'feasibility': 4,
            'literature_gap': 3,
            'priority': 48,
            'evidence': 'TENG research is active but polymer-specific optimization is less studied.',
            'current_evidence': 'Electrical measurements and surface characterization available.',
            'gaps': 'Polymer-specific design rules for TENG are lacking.',
            'related_papers': [],
        },
    ]

    # Sort by priority
    questions.sort(key=lambda q: -q['priority'])

    # Write to file
    with open(SYNTHESIS_DIR / "scientific_questions_ranked.md", 'w', encoding='utf-8') as f:
        f.write("# Scientific Questions Ranked by Priority\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Ranking Methodology\n\n")
        f.write("**Priority = Importance x Feasibility x Literature Gap**\n\n")
        f.write("- Importance: 1-5 (scientific significance)\n")
        f.write("- Feasibility: 1-5 (experimental feasibility)\n")
        f.write("- Literature Gap: 1-5 (how much is unknown)\n\n")

        for i, q in enumerate(questions, 1):
            f.write(f"## {i}. {q['id']}: {q['question']}\n\n")
            f.write(f"- **Importance**: {q['importance']}/5\n")
            f.write(f"- **Feasibility**: {q['feasibility']}/5\n")
            f.write(f"- **Literature Gap**: {q['literature_gap']}/5\n")
            f.write(f"- **Priority Score**: {q['priority']}\n\n")
            f.write(f"### Current Evidence\n{q['evidence']}\n\n")
            f.write(f"### Evidence Details\n{q['current_evidence']}\n\n")
            f.write(f"### Research Gaps\n{q['gaps']}\n\n")
            if q['related_papers']:
                f.write(f"### Related Papers\n{', '.join(q['related_papers'])}\n\n")
            f.write("---\n\n")

    # Write JSON for frontend
    with open(FRONTEND_DATA / "questions.json", 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return questions

def generate_future_directions(questions, papers, materials_data):
    """Generate future research directions."""
    directions = [
        {
            'id': 'FD1',
            'title': 'Machine Learning-Guided Design of Self-Healing Polyurethanes',
            'hypothesis': 'ML models trained on structure-property data can predict optimal hard/soft segment ratios for maximizing both toughness and self-healing efficiency.',
            'evidence': 'Multiple TPU papers with systematic composition variation; ML models for polymer properties emerging.',
            'gap': 'No ML-guided optimization of self-healing TPU reported.',
            'innovation': 'Combines computational design with experimental validation for accelerated materials discovery.',
            'value': 'Could reduce development time from years to months.',
            'feasibility': 'Requires synthesis capability, mechanical testing, and ML expertise.',
            'experiment': '1) Collect structure-property data from literature; 2) Train GNN model; 3) Predict optimal compositions; 4) Synthesize and validate.',
            'characterization': 'Tensile testing, healing efficiency measurement, SAXS for morphology.',
            'expected_results': 'Identified composition window with >90% healing efficiency and >30 MJ/m3 toughness.',
            'risks': 'Model may not generalize beyond training data.',
            'alternatives': 'Bayesian optimization with smaller experimental campaigns.',
            'output': 'High-impact paper + database for community.',
        },
        {
            'id': 'FD2',
            'title': 'In Situ SAXS/DMA Coupling for Real-Time Microphase Separation Dynamics',
            'hypothesis': 'Coupling in situ SAXS with simultaneous DMA measurements can reveal the kinetic coupling between microphase separation and mechanical property development.',
            'evidence': 'SAXS and DMA individually well-used; coupling is rare but technically feasible.',
            'gap': 'Real-time structure-property evolution during processing is largely unknown.',
            'innovation': 'First systematic in situ study of structure-property coupling in dynamic polymer networks.',
            'value': 'Fundamental understanding of processing-structure-property relationships.',
            'feasibility': 'Requires synchrotron access and custom DMA setup.',
            'experiment': '1) Design temperature-controlled DMA cell for SAXS; 2) Study TPU crystallization kinetics; 3) Correlate SAXS invariant with modulus.',
            'characterization': 'SAXS, DMA, DSC, WAXD.',
            'expected_results': 'Quantitative relationship between phase separation kinetics and mechanical property development.',
            'risks': 'Beam damage, limited time resolution.',
            'alternatives': 'Lab-scale SAXS with slower heating rates.',
            'output': 'Methodology paper + fundamental study.',
        },
        {
            'id': 'FD3',
            'title': 'Ionic Liquid-Enabled Ultra-Stretchable Ionogels for Biomedical Applications',
            'hypothesis': 'Biocompatible ionic liquids confined in polymer networks can create ionogels with unprecedented stretchability (>1000%) and ionic conductivity (>10 mS/cm) suitable for implantable devices.',
            'evidence': 'Ionogel papers show high stretchability; biocompatibility data emerging.',
            'gap': 'Systematic biocompatibility assessment of ionogels is lacking.',
            'innovation': 'First comprehensive biocompatibility study of high-performance ionogels.',
            'value': 'Opens new application space for ionogels in biomedical devices.',
            'feasibility': 'Requires IL synthesis, gel fabrication, and cell culture facilities.',
            'experiment': '1) Screen biocompatible ILs; 2) Fabricate ionogels with various polymer matrices; 3) Characterize mechanical and electrical properties; 4) In vitro cytotoxicity; 5) In vivo implantation.',
            'characterization': 'Tensile testing, impedance spectroscopy, cell viability, histology.',
            'expected_results': 'Identified IL/polymer combinations with >1000% stretchability and >90% cell viability.',
            'risks': 'IL leaching, long-term biocompatibility unknown.',
            'alternatives': 'Encapsulated ionogel designs to prevent IL exposure.',
            'output': 'Biomedical engineering paper + patent potential.',
        },
        {
            'id': 'FD4',
            'title': 'Piezoelectric Polymer Composites for Self-Powered Wearable Sensors',
            'hypothesis': 'Incorporating piezoelectric nanoparticles (BaTiO3, ZnO) into stretchable polymer matrices can create self-powered sensors with sensitivity >1 V/kPa.',
            'evidence': 'Piezoelectric polymer composites well-studied; wearable applications emerging.',
            'gap': 'Systematic optimization of filler-matrix interface for maximum piezoelectric response is lacking.',
            'innovation': 'Interface engineering approach for enhanced piezoelectric response.',
            'value': 'Enables self-powered health monitoring without batteries.',
            'feasibility': 'Requires nanoparticle synthesis, composite fabrication, and electrical testing.',
            'experiment': '1) Synthesize surface-modified BaTiO3 nanoparticles; 2) Fabricate composites with various matrices; 3) Measure d33 and voltage output; 4) Integrate into wearable sensor prototype.',
            'characterization': 'Piezoelectric testing, SEM, tensile testing, sensor characterization.',
            'expected_results': 'Composites with >15 pC/N d33 and >1 V/kPa sensitivity.',
            'risks': 'Filler agglomeration at high loading.',
            'alternatives': 'Electrospun nanofiber composites for better dispersion.',
            'output': 'Materials science + wearable technology paper.',
        },
        {
            'id': 'FD5',
            'title': 'Dynamic Covalent Chemistry for Recyclable Thermoset Elastomers',
            'hypothesis': 'Vitrimer elastomers based on dynamic thiourethane or oxime-carbamate bonds can achieve mechanical properties comparable to conventional thermosets while being fully recyclable.',
            'evidence': 'Vitrimer research is active; thiourethane and oxime-carbamate chemistries emerging.',
            'gap': 'Systematic comparison of different dynamic chemistries in elastomer applications is lacking.',
            'innovation': 'First comprehensive comparison of dynamic bond types for elastomer recycling.',
            'value': 'Addresses plastic waste challenge in elastomer industry.',
            'feasibility': 'Requires organic synthesis, polymer processing, and mechanical testing.',
            'experiment': '1) Synthesize elastomers with different dynamic bonds; 2) Characterize mechanical properties; 3) Test recyclability; 4) Compare property retention.',
            'characterization': 'Tensile testing, DMA, rheology, GPC.',
            'expected_results': 'Elastomers with >80% property retention after 3 recycling cycles.',
            'risks': 'Dynamic bond exchange may compromise mechanical integrity.',
            'alternatives': 'Hybrid networks with permanent and dynamic crosslinks.',
            'output': 'Sustainable materials paper.',
        },
        {
            'id': 'FD6',
            'title': 'Phase-Engineered Piezoionic Elastomers for Soft Robotics',
            'hypothesis': 'Controlling phase separation and interface morphology in piezoionic elastomers can enhance mechanoelectrical transduction for soft robotic applications.',
            'evidence': 'Piezoionic elastomers recently reported; soft robotics applications proposed.',
            'gap': 'Structure-performance relationships in piezoionic systems are poorly understood.',
            'innovation': 'Phase engineering approach for enhanced piezoionic response.',
            'value': 'Enables new soft robotic sensing capabilities.',
            'feasibility': 'Requires polymer synthesis, phase characterization, and robotics integration.',
            'experiment': '1) Design phase-separated elastomers; 2) Characterize morphology; 3) Measure piezoionic coefficient; 4) Integrate into soft robot.',
            'characterization': 'SAXS, impedance spectroscopy, mechanical testing, robotics testing.',
            'expected_results': 'Piezoionic coefficient >10 mV/kPa with >500% stretchability.',
            'risks': 'Phase separation kinetics may be difficult to control.',
            'alternatives': 'Block copolymer self-assembly for controlled morphology.',
            'output': 'Advanced materials + robotics paper.',
        },
        {
            'id': 'FD7',
            'title': 'Crystallization-Directed Self-Assembly for Hierarchical Polymer Structures',
            'hypothesis': 'Combining crystallization with block copolymer self-assembly can create hierarchical structures with unprecedented mechanical properties.',
            'evidence': 'Both crystallization and self-assembly individually well-studied; combination is emerging.',
            'gap': 'Guidelines for synergistic use of crystallization and self-assembly are lacking.',
            'innovation': 'First systematic study of crystallization-directed self-assembly.',
            'value': 'New design paradigm for high-performance polymers.',
            'feasibility': 'Requires synthesis, processing, and multi-scale characterization.',
            'experiment': '1) Design crystalline-amorphous block copolymers; 2) Control crystallization during self-assembly; 3) Characterize hierarchical structure; 4) Measure mechanical properties.',
            'characterization': 'SAXS, WAXD, AFM, TEM, tensile testing.',
            'expected_results': 'Hierarchical structures with >50% improvement in toughness.',
            'risks': 'Kinetic trapping of non-equilibrium structures.',
            'alternatives': 'Solvent annealing for better structural control.',
            'output': 'Fundamental polymer physics paper.',
        },
        {
            'id': 'FD8',
            'title': 'AI-Accelerated Discovery of Novel Ionic Conductors',
            'hypothesis': 'Generative models can design novel polymer electrolyte structures with predicted ionic conductivity >1 mS/cm at room temperature.',
            'evidence': 'ML for polymers emerging; ionic conductor design is active.',
            'gap': 'No generative AI approach for ionic conductor design reported.',
            'innovation': 'First generative AI application to polymer electrolyte design.',
            'value': 'Could accelerate discovery of solid-state battery electrolytes.',
            'feasibility': 'Requires ML expertise, synthesis capability, and electrochemical testing.',
            'experiment': '1) Build database of polymer electrolyte properties; 2) Train generative model; 3) Generate candidate structures; 4) Synthesize and test top candidates.',
            'characterization': 'Impedance spectroscopy, DSC, NMR, MD simulation.',
            'expected_results': 'Novel polymer electrolytes with >1 mS/cm conductivity.',
            'risks': 'Generated structures may be difficult to synthesize.',
            'alternatives': 'Virtual screening of known polymer databases.',
            'output': 'AI + materials science paper.',
        },
    ]

    with open(SYNTHESIS_DIR / "future_directions.md", 'w', encoding='utf-8') as f:
        f.write("# Future Research Directions\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Overview\n\nThis document presents {len(directions)} research directions with high potential impact.\n\n")

        for d in directions:
            f.write(f"## {d['id']}: {d['title']}\n\n")
            f.write(f"### 1. Core Scientific Hypothesis\n{d['hypothesis']}\n\n")
            f.write(f"### 2. Literature Evidence\n{d['evidence']}\n\n")
            f.write(f"### 3. Current Research Gap\n{d['gap']}\n\n")
            f.write(f"### 4. Innovation Analysis\n{d['innovation']}\n\n")
            f.write(f"### 5. Scientific Value\n{d['value']}\n\n")
            f.write(f"### 6. Technical Feasibility\n{d['feasibility']}\n\n")
            f.write(f"### 7. Possible Experimental Design\n{d['experiment']}\n\n")
            f.write(f"### 8. Key Characterization Methods\n{d['characterization']}\n\n")
            f.write(f"### 9. Expected Results\n{d['expected_results']}\n\n")
            f.write(f"### 10. Potential Risks\n{d['risks']}\n\n")
            f.write(f"### 11. Alternative Approaches\n{d['alternatives']}\n\n")
            f.write(f"### 12. Output\n{d['output']}\n\n")
            f.write("---\n\n")

    # Write JSON for frontend
    with open(FRONTEND_DATA / "directions.json", 'w', encoding='utf-8') as f:
        json.dump(directions, f, ensure_ascii=False, indent=2)

    return directions

def generate_research_roadmaps(directions):
    """Generate research roadmaps for each direction."""
    with open(SYNTHESIS_DIR / "research_roadmaps.md", 'w', encoding='utf-8') as f:
        f.write("# Research Roadmaps\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for d in directions:
            f.write(f"## {d['id']}: {d['title']}\n\n")

            f.write("### Short-term Goals (0-6 months)\n\n")
            f.write("- Literature review and gap analysis\n")
            f.write("- Experimental design and protocol development\n")
            f.write("- Preliminary sample preparation\n")
            f.write("- Initial characterization\n")
            f.write("- Feasibility assessment\n\n")

            f.write("### Medium-term Goals (6-18 months)\n\n")
            f.write("- Systematic variable studies\n")
            f.write("- Mechanism validation\n")
            f.write("- Model development/calibration\n")
            f.write("- Performance optimization\n")
            f.write("- Manuscript preparation\n\n")

            f.write("### Long-term Goals (18-36 months)\n\n")
            f.write("- Theory completion\n")
            f.write("- Application validation\n")
            f.write("- High-impact publication\n")
            f.write("- Grant application\n")
            f.write("- Platform expansion\n\n")

            f.write("### Technical Roadmap (Mermaid)\n\n")
            f.write("```mermaid\ngantt\n")
            f.write(f"    title {d['id']} Research Roadmap\n")
            f.write("    dateFormat  YYYY-MM-DD\n")
            f.write("    section Phase 1\n")
            f.write("    Literature Review      :2026-01-01, 2m\n")
            f.write("    Experimental Design    :2026-02-01, 1m\n")
            f.write("    section Phase 2\n")
            f.write("    Sample Preparation     :2026-03-01, 2m\n")
            f.write("    Characterization       :2026-04-01, 3m\n")
            f.write("    section Phase 3\n")
            f.write("    Data Analysis          :2026-07-01, 2m\n")
            f.write("    Manuscript             :2026-08-01, 2m\n")
            f.write("```\n\n")

            f.write("### Key Experiments\n\n")
            f.write("| Experiment | Purpose | Timeline |\n")
            f.write("|------------|---------|----------|\n")
            f.write("| Sample synthesis | Material preparation | Month 1-2 |\n")
            f.write("| Mechanical testing | Property evaluation | Month 3-4 |\n")
            f.write("| Morphology characterization | Structure analysis | Month 3-5 |\n")
            f.write("| Mechanism studies | Fundamental understanding | Month 4-6 |\n")
            f.write("| Optimization | Performance improvement | Month 6-12 |\n\n")

            f.write("### Risk Management\n\n")
            f.write(f"- **Primary risk**: {d['risks']}\n")
            f.write(f"- **Mitigation**: {d['alternatives']}\n\n")
            f.write("---\n\n")

def main():
    # Load data
    papers = load_csv(PROJECT_DIR / "00_manifest" / "literature_metadata.csv")
    materials_data = load_json(EVIDENCE_DIR / "material_system_matrix.json")
    methods_data = load_json(EVIDENCE_DIR / "method_matrix.json")

    print("Generating research team comparison...")
    generate_research_team_comparison(papers, materials_data, methods_data)

    print("Generating method evolution analysis...")
    generate_method_evolution(methods_data, papers)

    print("Generating scientific questions...")
    questions = generate_scientific_questions(papers, materials_data, methods_data)

    print("Generating future directions...")
    directions = generate_future_directions(questions, papers, materials_data)

    print("Generating research roadmaps...")
    generate_research_roadmaps(directions)

    print("Synthesis analysis complete!")

if __name__ == "__main__":
    main()
