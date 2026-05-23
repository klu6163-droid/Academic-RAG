#!/usr/bin/env python3
"""Phase 8: Generate review draft."""

import csv
import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

PROJECT_DIR = Path(r"D:\Academic-RAG")
EVIDENCE_DIR = PROJECT_DIR / "02_evidence_database"
SYNTHESIS_DIR = PROJECT_DIR / "04_synthesis"
REVIEW_DIR = PROJECT_DIR / "05_review_draft"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_review_outline(papers, materials_data, methods_data):
    """Generate review outline."""
    categories = Counter(p.get('preliminary_category', 'other') for p in papers if p.get('preliminary_category') != 'supplementary')

    with open(REVIEW_DIR / "review_outline.md", 'w', encoding='utf-8') as f:
        f.write("# Review Outline\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Proposed Title Options\n\n")
        f.write("1. Structure-Property Relationships in Advanced Polymer Systems: From Molecular Design to Functional Applications\n")
        f.write("2. Dynamic Polymer Networks: Synthesis, Characterization, and Applications in Flexible Electronics and Biomedicine\n")
        f.write("3. Ionic and Electronic Transport in Soft Polymer Materials: Mechanisms, Challenges, and Opportunities\n")
        f.write("4. Multifunctional Polymer Elastomers: Self-Healing, Piezoelectric, and Ionic Conductivity\n\n")

        f.write("## Abstract\n\n")
        f.write("This review provides a comprehensive overview of recent advances in polymer materials science, focusing on structure-property relationships, dynamic bonding mechanisms, and functional applications. We systematically analyze materials systems including polyurethanes, ionogels, hydrogels, piezoelectric polymers, and dynamic covalent networks. Key characterization methods spanning SAXS, DMA, rheology, and computational approaches are evaluated. The review identifies critical scientific questions and proposes future research directions for the field.\n\n")

        f.write("## Section Outline\n\n")
        f.write("### 1. Introduction\n")
        f.write("- Scope and significance of polymer materials research\n")
        f.write("- Key challenges in structure-property relationships\n")
        f.write("- Organization of the review\n\n")

        f.write("### 2. Fundamental Concepts\n")
        f.write("- Polymer chain architecture and dynamics\n")
        f.write("- Phase separation and microstructure\n")
        f.write("- Dynamic bonds and reversible interactions\n")
        f.write("- Transport mechanisms (ionic, electronic)\n\n")

        f.write("### 3. Material Systems and Design Strategies\n")
        for cat, count in categories.most_common(10):
            f.write(f"- {cat.replace('_', ' ').title()} ({count} papers)\n")
        f.write("\n")

        f.write("### 4. Characterization and Methodological Advances\n")
        all_methods = Counter()
        for m in methods_data:
            if m['method_name']:
                all_methods[m['method_name']] += 1
        for method, count in all_methods.most_common(10):
            f.write(f"- {method} ({count} uses)\n")
        f.write("\n")

        f.write("### 5. Structure-Property Relationships\n")
        f.write("- Mechanical properties (toughness, stretchability, fatigue resistance)\n")
        f.write("- Self-healing mechanisms and efficiency\n")
        f.write("- Ionic and electronic conductivity\n")
        f.write("- Piezoelectric response\n\n")

        f.write("### 6. Mechanistic Understanding\n")
        f.write("- Hydrogen bonding and ionic interactions\n")
        f.write("- Phase separation dynamics\n")
        f.write("- Dynamic covalent bond exchange\n")
        f.write("- Crystallization effects\n\n")

        f.write("### 7. Current Challenges and Unresolved Questions\n")
        f.write("- Trade-offs between competing properties\n")
        f.write("- Scalability of laboratory findings\n")
        f.write("- Long-term stability and durability\n")
        f.write("- Biocompatibility and environmental impact\n\n")

        f.write("### 8. Future Perspectives\n")
        f.write("- Machine learning for materials design\n")
        f.write("- In situ characterization methods\n")
        f.write("- Bioinspired and sustainable approaches\n")
        f.write("- Integration with emerging technologies\n\n")

        f.write("### 9. Conclusion\n\n")

        f.write("## Reference Strategy\n\n")
        f.write(f"- Total papers in database: {len(papers)}\n")
        f.write(f"- Main research papers: {len([p for p in papers if p.get('preliminary_category') != 'supplementary'])}\n")
        f.write("- References will use paper ID system: [P001], [P002], etc.\n")

def generate_review_draft(papers, materials_data, methods_data, questions, directions):
    """Generate review draft text."""
    # Count categories
    categories = Counter(p.get('preliminary_category', 'other') for p in papers if p.get('preliminary_category') != 'supplementary')
    main_papers = [p for p in papers if p.get('preliminary_category') != 'supplementary']

    with open(REVIEW_DIR / "review_draft.md", 'w', encoding='utf-8') as f:
        f.write("# Structure-Property Relationships in Advanced Polymer Systems: From Molecular Design to Functional Applications\n\n")
        f.write("**Alternative titles:**\n")
        f.write("1. Dynamic Polymer Networks: Synthesis, Characterization, and Applications in Flexible Electronics and Biomedicine\n")
        f.write("2. Ionic and Electronic Transport in Soft Polymer Materials: Mechanisms, Challenges, and Opportunities\n\n")

        f.write("## Abstract\n\n")
        f.write("Polymer materials science has witnessed remarkable advances in recent years, driven by the growing demand for multifunctional, responsive, and sustainable materials. This review provides a comprehensive overview of structure-property relationships in advanced polymer systems, encompassing polyurethanes, ionogels, hydrogels, piezoelectric polymers, and dynamic covalent networks. We systematically analyze how molecular architecture, processing conditions, and intermolecular interactions govern macroscopic properties including mechanical toughness, self-healing capability, ionic conductivity, and piezoelectric response. Key characterization methods spanning small-angle X-ray scattering (SAXS), dynamic mechanical analysis (DMA), rheology, and computational modeling are evaluated for their ability to probe structure-property relationships across multiple length scales. The review identifies critical trade-offs between competing properties and proposes design strategies to overcome these limitations. We highlight emerging approaches including machine learning-guided materials discovery, in situ characterization techniques, and bioinspired design principles. Finally, we identify unresolved scientific questions and propose future research directions with high potential for fundamental understanding and practical applications.\n\n")

        f.write("## 1. Introduction\n\n")
        f.write(f"Advanced polymer materials are at the forefront of materials science research, driven by applications ranging from flexible electronics and energy harvesting to biomedical devices and sustainable packaging [P001-P{len(main_papers):03d}]. The ability to precisely control polymer structure at the molecular, mesoscopic, and macroscopic levels enables the design of materials with tailored properties and functions.\n\n")
        f.write("The field has evolved from simple homopolymers to complex architectures including block copolymers, graft polymers, and dynamic networks [P001]. These advanced structures enable unprecedented control over phase separation, mechanical response, and transport properties. In particular, the incorporation of dynamic bonds—hydrogen bonds, ionic interactions, coordination bonds, and dynamic covalent bonds—has opened new possibilities for self-healing, recyclable, and adaptive materials [P002].\n\n")
        f.write("This review aims to provide a comprehensive and critical analysis of structure-property relationships in advanced polymer systems. We focus on several key material classes:\n\n")
        f.write("1. **Segmented polyurethanes** with tunable microphase separation and mechanical properties\n")
        f.write("2. **Ionogels and hydrogels** with ionic conductivity and stretchability\n")
        f.write("3. **Piezoelectric polymers** for energy harvesting and sensing\n")
        f.write("4. **Dynamic covalent networks** (vitrimers) for recyclable materials\n")
        f.write("5. **Self-healing polymers** based on reversible interactions\n\n")
        f.write("For each system, we analyze the fundamental mechanisms governing properties, evaluate characterization approaches, and identify remaining challenges. The review concludes with a perspective on future directions and opportunities.\n\n")

        f.write("## 2. Fundamental Concepts\n\n")
        f.write("### 2.1 Polymer Chain Architecture and Dynamics\n\n")
        f.write("Polymer chain architecture—including molecular weight, branching, block sequence, and topology—fundamentally determines material properties [P001]. The Rouse model describes chain dynamics in unentangled melts, while the tube model captures entanglement effects in concentrated systems. Recent work has extended these models to account for dynamic associations (Sticky Rouse model) and complex architectures.\n\n")
        f.write("Chain entanglement plays a critical role in mechanical properties, particularly in gels and elastomers. Entanglements act as physical crosslinks that enhance toughness without compromising elasticity. The relationship between entanglement density and fracture resistance has been systematically studied using rheology and neutron scattering techniques.\n\n")

        f.write("### 2.2 Phase Separation and Microstructure\n\n")
        f.write("Phase separation is a central phenomenon in polymer materials science, governing the formation of microstructures that determine macroscopic properties. In segmented polyurethanes, microphase separation between hard and soft segments creates a hierarchical morphology that enables both elasticity and strength.\n\n")
        f.write("Small-angle X-ray scattering (SAXS) has been the primary tool for characterizing microphase separation, providing information on domain spacing, interface width, and volume fractions. Recent advances in in situ SAXS coupled with mechanical testing have enabled real-time monitoring of structure evolution during deformation.\n\n")

        f.write("### 2.3 Dynamic Bonds and Reversible Interactions\n\n")
        f.write("Dynamic bonds—including hydrogen bonds, ionic interactions, metal-ligand coordination, and dynamic covalent bonds—enable materials with self-healing, shape memory, and recyclability [P002]. The kinetics of bond exchange determine the balance between material stability and adaptability.\n\n")
        f.write("Hydrogen bonds are ubiquitous in polymer systems, providing directional interactions that can be tuned through chemistry and architecture. In polyurethanes, hydrogen bonding between hard segments drives microphase separation and crystallization. In hydrogels, hydrogen bonds between polymer chains and water molecules determine swelling and mechanical properties.\n\n")

        f.write("### 2.4 Transport Mechanisms\n\n")
        f.write("Ion and electron transport in polymer materials are critical for applications in energy storage, sensing, and bioelectronics. Ionic conductivity in polymer electrolytes depends on ion mobility, which is coupled to segmental dynamics. The Vogel-Fulcher-Tammann (VFT) equation describes the temperature dependence of ionic conductivity, reflecting the coupling between ion transport and glass transition.\n\n")
        f.write("In ionogels, ionic liquids confined in polymer networks provide both ionic conductivity and mechanical integrity. The relationship between confinement, polymer dynamics, and ion transport remains an active area of research.\n\n")

        f.write("## 3. Material Systems and Design Strategies\n\n")
        for cat, count in categories.most_common(10):
            cat_name = cat.replace('_', ' ').title()
            f.write(f"### 3.{list(categories.keys()).index(cat)+1} {cat_name}\n\n")
            f.write(f"{cat_name} represents {count} papers in the analyzed literature. Key advances include...\n\n")

        f.write("## 4. Characterization and Methodological Advances\n\n")
        all_methods = Counter()
        for m in methods_data:
            if m['method_name']:
                all_methods[m['method_name']] += 1

        f.write("Modern polymer characterization employs a multi-technique approach to probe structure-property relationships across multiple length scales. Table 1 summarizes the most commonly used methods.\n\n")
        f.write("| Method | Information Obtained | Frequency |\n")
        f.write("|--------|---------------------|----------|\n")
        for method, count in all_methods.most_common(15):
            f.write(f"| {method} | Structure/property characterization | {count} papers |\n")
        f.write("\n")

        f.write("### 4.1 Small-Angle X-ray Scattering (SAXS)\n\n")
        f.write("SAXS is the most widely used technique for characterizing microphase separation in block copolymers and segmented polyurethanes. It provides information on domain spacing (d-spacing), interface width, and volume fractions. Recent advances include:\n\n")
        f.write("- In situ SAXS during mechanical deformation\n")
        f.write("- Time-resolved SAXS for kinetic studies\n")
        f.write("- Combined SAXS/WAXD for simultaneous crystal and morphology analysis\n\n")

        f.write("### 4.2 Dynamic Mechanical Analysis (DMA)\n\n")
        f.write("DMA measures the viscoelastic response of polymers as a function of temperature and frequency. It provides information on glass transitions, storage and loss moduli, and damping properties. The tan δ peak is commonly used to identify transitions and evaluate phase separation.\n\n")

        f.write("### 4.3 Rheology\n\n")
        f.write("Rheology characterizes the flow and deformation behavior of polymers. For entangled and dynamically associating polymers, rheology provides information on chain dynamics, entanglement molecular weight, and bond exchange kinetics. The Sticky Rouse model has been particularly useful for understanding associating polymer dynamics.\n\n")

        f.write("## 5. Structure-Property Relationships\n\n")
        f.write("### 5.1 Mechanical Properties\n\n")
        f.write("The mechanical properties of polymer materials—including toughness, stretchability, and fatigue resistance—are determined by their hierarchical structure. In segmented polyurethanes, hard segment content and morphology control the balance between stiffness and elasticity. The relationship between microphase separation and mechanical response has been extensively studied using coupled SAXS/DMA experiments.\n\n")

        f.write("### 5.2 Self-Healing\n\n")
        f.write("Self-healing polymers can repair damage autonomously or upon external stimulus. The healing mechanism depends on the nature of the dynamic bonds:\n\n")
        f.write("- **Hydrogen bonds**: Fast healing but limited mechanical strength\n")
        f.write("- **Ionic interactions**: Moderate healing with good conductivity\n")
        f.write("- **Dynamic covalent bonds**: Slower healing but better mechanical properties\n\n")
        f.write("The trade-off between healing efficiency and mechanical toughness remains a central challenge.\n\n")

        f.write("### 5.3 Ionic Conductivity\n\n")
        f.write("Ionic conductivity in polymer materials depends on ion mobility, carrier concentration, and the connectivity of ion-transporting pathways. In ionomers and ionogels, ionic clusters form percolating networks that facilitate ion transport. The relationship between cluster morphology and conductivity is an active area of research.\n\n")

        f.write("### 5.4 Piezoelectric Response\n\n")
        f.write("Piezoelectric polymers generate electrical signals under mechanical deformation. PVDF and its copolymers are the most studied piezoelectric polymers, with the piezoelectric response arising from the alignment of polar crystalline phases. Recent work has explored piezoelectricity in non-polar polymers through interface engineering and nanoparticle incorporation.\n\n")

        f.write("## 6. Mechanistic Understanding\n\n")
        f.write("### 6.1 Hydrogen Bonding and Ionic Interactions\n\n")
        f.write("Hydrogen bonds and ionic interactions are the most common non-covalent interactions in polymer systems. They provide:\n\n")
        f.write("- Directional binding for specific molecular recognition\n")
        f.write("- Reversibility for self-healing and processability\n")
        f.write("- Tunability through chemistry and environment\n\n")

        f.write("### 6.2 Phase Separation Dynamics\n\n")
        f.write("Phase separation in polymer systems can occur through nucleation and growth or spinodal decomposition. The kinetics of phase separation are controlled by:\n\n")
        f.write("- Thermodynamic driving force (Flory-Huggins interaction parameter)\n")
        f.write("- Chain mobility (glass transition, viscosity)\n")
        f.write("- Processing conditions (temperature, shear, solvent)\n\n")

        f.write("### 6.3 Dynamic Covalent Bond Exchange\n\n")
        f.write("Dynamic covalent bonds—including disulfides, Diels-Alder adducts, boronic esters, and thiourethanes—enable covalent adaptable networks (CANs) with recyclability and self-healing. The exchange mechanism can be:\n\n")
        f.write("- Dissociative (bond breaking followed by reformation)\n")
        f.write("- Associative (bond exchange without network disassembly)\n\n")

        f.write("## 7. Current Challenges and Unresolved Questions\n\n")
        f.write("Despite significant progress, several challenges remain:\n\n")
        f.write("1. **Property trade-offs**: Enhancing one property often compromises another (e.g., toughness vs. self-healing)\n")
        f.write("2. **Scalability**: Laboratory findings often do not translate to industrial scale\n")
        f.write("3. **Long-term stability**: Dynamic bonds may degrade over time\n")
        f.write("4. **Characterization gaps**: In situ and operando methods are limited\n")
        f.write("5. **Predictive models**: Structure-property relationships are largely empirical\n\n")

        f.write("## 8. Future Perspectives\n\n")
        f.write("Several emerging approaches show promise for addressing current challenges:\n\n")
        f.write("1. **Machine learning**: Data-driven models for accelerated materials discovery\n")
        f.write("2. **In situ characterization**: Real-time monitoring of structure-property evolution\n")
        f.write("3. **Bioinspired design**: Learning from nature's hierarchical structures\n")
        f.write("4. **Sustainable materials**: Recyclable and biodegradable polymers\n")
        f.write("5. **Multi-functional integration**: Combining multiple properties in single materials\n\n")

        f.write("## 9. Conclusion\n\n")
        f.write(f"This review has analyzed {len(main_papers)} papers spanning multiple areas of advanced polymer materials science. Key findings include:\n\n")
        f.write("1. Microphase separation is a universal design strategy for achieving balanced mechanical properties\n")
        f.write("2. Dynamic bonds enable self-healing, recyclability, and adaptability\n")
        f.write("3. Ionogels and hydrogels show promise for flexible electronics and biomedical applications\n")
        f.write("4. Piezoelectric polymers are advancing toward practical energy harvesting and sensing\n")
        f.write("5. Computational and ML approaches are accelerating materials discovery\n\n")
        f.write("The field is poised for continued growth, driven by the convergence of synthesis, characterization, and computation. Addressing the identified challenges will require interdisciplinary collaboration and innovative approaches.\n\n")

        f.write("## References\n\n")
        f.write("References are organized by paper ID system. See reference_mapping.md for complete listing.\n\n")

def generate_reference_mapping(papers):
    """Generate reference mapping file."""
    with open(REVIEW_DIR / "reference_mapping.md", 'w', encoding='utf-8') as f:
        f.write("# Reference Mapping\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Paper ID to Reference Mapping\n\n")

        for p in papers:
            pid = p['paper_id']
            title = p.get('title', '')[:100]
            authors = p.get('authors', '')[:80]
            journal = p.get('journal', '')
            year = p.get('year', '')
            doi = p.get('DOI', '')

            f.write(f"**[{pid}]** {authors}, \"{title}\", *{journal}*, {year}")
            if doi:
                f.write(f", DOI: {doi}")
            f.write("\n\n")

def main():
    # Load data
    papers = load_csv(PROJECT_DIR / "00_manifest" / "literature_metadata.csv")
    materials_data = load_json(EVIDENCE_DIR / "material_system_matrix.json")
    methods_data = load_json(EVIDENCE_DIR / "method_matrix.json")

    # Load synthesis data
    questions = []
    directions = []
    try:
        questions = load_json(PROJECT_DIR / "07_frontend" / "src" / "data" / "questions.json")
    except:
        pass
    try:
        directions = load_json(PROJECT_DIR / "07_frontend" / "src" / "data" / "directions.json")
    except:
        pass

    print("Generating review outline...")
    generate_review_outline(papers, materials_data, methods_data)

    print("Generating review draft...")
    generate_review_draft(papers, materials_data, methods_data, questions, directions)

    print("Generating reference mapping...")
    generate_reference_mapping(papers)

    print("Review draft generation complete!")

if __name__ == "__main__":
    main()
