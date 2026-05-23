# Knowledge Graph Schema

Generated: 2026-05-22

## Node Types

| node_type | Description | Example |
|-----------|-------------|---------|
| Paper | A research paper in the corpus | P375, P011 |
| Material | A material system studied | polyurethane, PVDF, PCL |
| Polymer | A specific polymer type | TPU, SMPU, WPU |
| SoftSegment | Soft segment in segmented PU | PCL, PTMG, PEG |
| HardSegment | Hard segment in segmented PU | IPDI, MDI, PPDI |
| Interaction | Molecular interaction type | hydrogen bond, ionic interaction |
| Method | Characterization or synthesis method | SAXS, FTIR, DSC, MD simulation |
| Property | A measurable property | tensile strength, Tg, d33 |
| Mechanism | A mechanistic concept | microphase separation, strain-induced crystallization |
| Application | End-use application | tissue engineering, sensor, self-healing |
| MLFeature | ML input feature candidate | SAXS peak position, FTIR HBI |
| Project | User's research project | PU_microphase_mechanics |

## Edge Types

| edge_type | Source -> Target | Description |
|-----------|-----------------|-------------|
| STUDIES | Paper -> Material/Polymer/Property | Paper studies this entity |
| CONTAINS | Polymer -> SoftSegment/HardSegment | Polymer contains this segment |
| USES_METHOD | Paper -> Method | Paper uses this characterization method |
| SHOWS_PROPERTY | Paper -> Property | Paper reports this property value |
| SUPPORTS_MECHANISM | Paper -> Mechanism | Paper provides evidence for this mechanism |
| RELATED_TO_PROJECT | Paper/Mechanism -> Project | Relevant to user's project |
| CAN_BE_ML_FEATURE | Property -> MLFeature | Property can serve as ML input |
| IMPROVES | Interaction -> Property | This interaction improves this property |
| REDUCES | Interaction -> Property | This interaction reduces this property |
| CORRELATES_WITH | Property -> Property | These properties are correlated |

## Evidence Traceability

Each edge can be traced to evidence via:
- `evidence_id`: row in global_evidence_table_cleaned.csv
- `paper_id`: links to PDF source
- `page_est`: estimated PDF page (line_num / 40)
- `evidence_text`: the actual evidence excerpt

## Usage

### For Frontend Visualization
- Nodes rendered as circles with type-specific colors
- Edges rendered as lines with type-specific styles
- Click node to see all connected evidence
- Filter by node_type, edge_type, category, confidence

### For RAG Retrieval
- Query: "What mechanisms support PU toughness?"
- Retrieve: SUPPORTS_MECHANISM edges where target = "toughness"
- Return: paper_id, evidence_text, confidence
- Use evidence_text as context for LLM response

### For Knowledge Graph Construction
- Import kg_nodes.csv and kg_edges.csv into Neo4j or similar graph DB
- Create indices on node_id, paper_id
- Enable traversal queries for multi-hop reasoning
