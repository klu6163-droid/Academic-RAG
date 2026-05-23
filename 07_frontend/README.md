# Academic Literature Research Dashboard

Evidence-based knowledge system for literature analysis, research synthesis, and review drafting.

## Features

- **Dashboard**: Overview with statistics, year distribution, category breakdown
- **Literature Library**: Browse, search, and filter all 456 papers
- **Evidence Matrix**: Searchable evidence database with reliability ratings
- **Knowledge Graph**: Explore relationships between papers, materials, methods, and properties
- **Scientific Questions**: Ranked research questions with priority scores
- **Future Directions**: 8 research directions with detailed roadmaps
- **Review Draft**: Complete review manuscript with outline and references
- **Global Search**: Search across all content simultaneously

## Quick Start

```bash
cd literature_project/07_frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Recharts (charts)

## Project Structure

```
src/
├── main.tsx           # Entry point
├── App.tsx            # Main application
├── styles.css         # Global styles
├── data/              # JSON data files
│   ├── papers.json    # 456 papers metadata
│   ├── evidence.json  # Evidence items
│   ├── methods.json   # Characterization methods
│   ├── materials.json # Material systems
│   ├── figures.json   # Key figures
│   ├── nodes.json     # Knowledge graph nodes
│   ├── edges.json     # Knowledge graph edges
│   ├── questions.json # Scientific questions
│   └── directions.json# Future directions
└── components/
    ├── Sidebar.tsx
    ├── Dashboard.tsx
    ├── PaperTable.tsx
    ├── PaperDetail.tsx
    ├── EvidenceMatrix.tsx
    ├── KnowledgeGraph.tsx
    ├── ScientificQuestions.tsx
    ├── FutureDirections.tsx
    ├── ReviewDraft.tsx
    └── SearchPanel.tsx
```

## Data Sources

All data is generated from the analysis of 456 academic PDFs in the paper collection. See the parent project directories for:

- `00_manifest/` - File paths and metadata
- `01_single_paper_reports/` - Individual paper analysis
- `02_evidence_database/` - Structured evidence matrices
- `03_knowledge_graph/` - Knowledge graph data
- `04_synthesis/` - Cross-paper analysis
- `05_review_draft/` - Review manuscript
