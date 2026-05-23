# Literature RAG Dashboard

React+Vite+TypeScript frontend for browsing and querying the polyurethane literature knowledge base.

## Quick Start

```bash
cd frontend
npm install
npm run dev        # dev server at http://localhost:5173
```

## Build & Preview

```bash
npm run build      # outputs to dist/
npm run preview    # preview build at http://localhost:4173
```

## RAG API (Ask Corpus)

The Ask Corpus page uses a full RAG pipeline backend with FAISS + BM25 hybrid retrieval.

### 1. Configure LLM API Key

```bash
cd ..   # project root
cp .env.example .env
# Edit .env and set LLM_API_KEY (OpenAI-compatible)
```

### 2. Start Backend

```bash
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Backend runs at http://localhost:8001. On first start it builds the FAISS index if no cache exists.
Stop it from the project root with `powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1`.

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

### 4. Configure API URL (optional)

```bash
cp .env.example .env
# VITE_RAG_API_BASE_URL=http://localhost:8001
```

Default is `http://localhost:8001`.

### RAG Pipeline Architecture

- **Retrieval**: FAISS dense (sentence-transformers all-MiniLM-L6-v2) + BM25 sparse, fused with RRF
- **Query Expansion**: LLM-based (when API key configured)
- **Answer Generation**: OpenAI-compatible LLM with evidence-grounded prompting
- **No-Answer Gate**: Deterministic checks (score threshold, min evidence chunks) before LLM call
- **Configuration**: Unified via `src/config.py` + `.env`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/stats` | GET | Corpus + pipeline statistics |
| `/api/ask` | POST | Full RAG: retrieve + generate answer |
| `/api/retrieve` | POST | Retrieve evidence only (no LLM) |

### Test Queries

```bash
# Health check
curl http://localhost:8001/health

# Pipeline stats
curl http://localhost:8001/api/stats

# Retrieve evidence (works without LLM key)
curl -X POST http://localhost:8001/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"question":"polyurethane microphase separation SAXS","top_k":8}'

# Full RAG ask (requires LLM_API_KEY)
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"哪些论文提到了聚氨酯微相分离？","top_k":8}'
```

## Data Files

All static data lives in `public/data/`:

| File | Content | Count |
|------|---------|-------|
| `evidence.json` | Cleaned evidence rows | 1858 |
| `kg_nodes.json` | Knowledge graph nodes | 228 |
| `kg_edges.json` | Knowledge graph edges | 820 |
| `dashboard_stats.json` | Summary statistics | — |
| `project_syntheses.json` | 5 project-specific syntheses | 5 |
| `global_synthesis.json` | Global synthesis sections | 13 |
| `data_quality_report.json` | QA report | — |

To regenerate these JSON files from the source CSV/MD files:

```bash
cd ..
python convert_to_json.py
```

## Pages

1. **Dashboard** — stat cards, category bar chart, claim type pie chart, manual check warning
2. **Ask Corpus** — RAG Q&A with FAISS+BM25 hybrid retrieval and LLM answer generation
3. **Evidence Explorer** — search, filters, ML feature toggle, manual check toggle, pagination
4. **Knowledge Graph** — force-directed graph, node coloring, search/filter, click-to-inspect
5. **Project Views** — 5 project syntheses with expandable sections
6. **Citation Browser** — high-relevance papers grouped by category
7. **ML Features** — ML feature candidate rows filtered by category
8. **Data Quality** — quality distribution, manual check queue, uncertain titles

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend unreachable | Start backend from the project root: `powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1` |
| "LLM API key not configured" | Set `LLM_API_KEY` in `.env` at project root |
| CORS error | Backend allows all origins; check if port 8000 is in use |
| "No Answer" | Question outside corpus scope or evidence too weak |
| Evidence missing page | Some rows lack PDF page info; check `page_est` field |
| Manual check warning | Evidence from partial-extraction papers; verify before citing |
| Slow first startup | First run builds FAISS index and computes embeddings (~15s) |

## Tech Stack

- React 19 + TypeScript + Vite 6 + Tailwind CSS 3
- Recharts, react-force-graph-2d, lucide-react
- FastAPI + sentence-transformers + FAISS + BM25 + OpenAI-compatible LLM
