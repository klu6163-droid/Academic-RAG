# Polyurethane Literature RAG System

A retrieval-augmented generation (RAG) system for querying a polyurethane materials science literature corpus. Uses hybrid FAISS+BM25 retrieval with RRF fusion, domain-aware equivalent concept recognition, and strict evidence-based answering.

## Quick Start

### 1. Configure LLM

Edit `.env` with your API key:

```bash
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Pro/moonshotai/Kimi-K2.6
```

### 2. Start Backend

```bash
cd D:\Academic-RAG
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Backend runs at `http://localhost:8001` by default.

Stop it with:

```bash
powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
```

Backend logs are written to `data/logs/backend_uvicorn.out.log` and `data/logs/backend_uvicorn.err.log`.

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Recommended Daily Workflow

1. Start backend: `powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1`
2. Start frontend: `cd frontend && npm run dev`
3. Open Ask Corpus at `http://localhost:5173`
4. Default settings: **Curated Evidence + Concise** mode
5. For complex questions: use **Retrieve Only** first to inspect evidence, then **Ask**
6. Check **support level badges** on evidence cards (direct, equivalent_concept, partial, insufficient)
7. **Manual check warnings** require verification against the original PDF before citing
8. **No-answer** means insufficient evidence in the current corpus — it does not mean the answer doesn't exist in reality

## Adding New Literature

This is a RAG system, not model fine-tuning. To make it "learn" new papers, add
new evidence rows to the corpus, regenerate frontend JSON, and rebuild the local
embedding/FAISS cache.

### Fast Path: Add Curated Evidence Rows

Use this when you already know which claims, methods, figures, or results should
be searchable.

1. Add rows to `data/analysis/final/global_evidence_table_frontend.csv`.
2. Keep `paper_id` unique for new papers, for example continue after the current
   IDs instead of reusing an existing one.
3. Fill the retrieval-critical fields: `paper_id`, `title`, `file_name`,
   `category`, `claim_type`, `evidence_text`, `page_est`, `keyword`,
   `confidence`, `relevance`, `needs_manual_check`.
4. Regenerate frontend JSON:

   ```bash
   python convert_to_json.py
   ```

5. Rebuild the local RAG index:

   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\rebuild_rag_index.ps1
   ```

6. Restart the backend:

   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
   powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
   ```

### Full Path: Add PDFs and Reprocess

Use this when you want to add PDF files directly. The import script copies each
PDF to `00_manifest/english_pdf_copies/` with an ASCII-safe filename, removing
Chinese characters and special characters from the working filename while
keeping the original path in `00_manifest/file_path_mapping.csv`.

1. Put new PDFs in a source folder.
2. Import the PDFs:

   ```bash
   python scripts\ingest_new_pdfs.py "D:\path\to\new_pdfs"
   ```

   By default, this also extracts text and appends low-confidence,
   `needs_manual_check=TRUE` evidence chunks to
   `data/analysis/final/global_evidence_table_frontend.csv`, so the new PDFs are
   searchable immediately but clearly marked as unreviewed.

3. Regenerate frontend JSON and rebuild the RAG index:

   ```bash
   python convert_to_json.py
   powershell -ExecutionPolicy Bypass -File scripts\rebuild_rag_index.ps1
   ```

4. Restart the backend:

   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
   powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
   ```

Useful import options:

```bash
# Copy/extract only; do not add evidence rows yet
python scripts\ingest_new_pdfs.py "D:\path\to\new_pdfs" --no-evidence

# Assign a category to generated evidence rows
python scripts\ingest_new_pdfs.py "D:\path\to\new_pdfs" --category PU_Microphase_Separation
```

The current production backend retrieves from `frontend/public/data/evidence.json`.
Full-paper retrieval is still disabled until a separate PDF chunk index is built.

### Performance Notes

- Simple queries: ~60–80s (LLM-bound)
- Complex queries: ~80–110s (concise mode prevents timeout)
- Out-of-domain queries: ~2–5s (no-answer gate blocks before LLM)
- Retrieval only: <500ms (no LLM call)
- Bottleneck is LLM API response time (~90% of latency)
- Future optimizations: faster model, streaming responses, retrieve-first UI

## Architecture

```
Question → Hybrid Retrieval (FAISS + BM25 + RRF) → Diversity Rerank → No-Answer Gate → LLM Answer
```

### Retrieval Pipeline

1. **Dense retrieval**: FAISS IndexFlatIP with all-MiniLM-L6-v2 embeddings (384 dim)
2. **Sparse retrieval**: BM25 with CJK-aware tokenization (k1=1.5, b=0.75)
3. **Fusion**: Reciprocal Rank Fusion (RRF, k=60)
4. **Diversity rerank**: Max 2 chunks per paper in top-k results
5. **Query expansion**: Optional LLM-based query expansion (disabled by default)

### Answer Generation

- **Evidence mode** (default): Uses 1858 curated evidence rows
- **Full paper mode**: Disabled (no chunk index built)
- **Hybrid mode**: Evidence first, full paper fallback
- **Concise mode** (default): 300-600 chars, 3 conclusions, top-5 evidence
- **Detailed mode**: Full analysis, top-8 evidence
- Complex queries auto-degrade from detailed to concise to prevent timeout

### No-Answer Gate

Deterministic gate blocks before LLM is called:
- `top_score < 0.017`: Evidence too weak → no_answer
- `retrieved_count == 0`: No evidence → no_answer
- LLM can still set `no_answer=true` if evidence is insufficient

### Evidence Support Levels

Each evidence row is classified:

| Level | Meaning |
|-------|---------|
| `direct` | Excerpt explicitly contains query terms |
| `equivalent_concept` | Domain-equivalent concept (e.g., soft/hard segment = microphase separation) |
| `partial` | Supports part of the question |
| `insufficient` | Not relevant |

Domain equivalents are defined in `config/domain_equivalents.yaml`.

### System Override

When the LLM sets `no_answer=true` but provides a substantive evidence analysis (>100 chars), the system may override to `no_answer=false`. Guardrails:
- Only overrides when evidence has valid paper_id and excerpt
- Only overrides when answer contains evidence discussion keywords
- Never overrides when score < 0.017 (blocked by gate)
- Never overrides nonsense queries (blocked by gate)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/stats` | Pipeline statistics |
| POST | `/api/ask` | Ask a question (retrieves + generates answer) |
| POST | `/api/retrieve` | Retrieve evidence only (no LLM) |

### POST /api/ask

```json
{
  "question": "哪些论文提到了聚氨酯微相分离？",
  "top_k": 8,
  "mode": "evidence",
  "answer_style": "concise",
  "filters": {
    "category": ["structure"],
    "exclude_manual_check": true
  }
}
```

Response includes `evidence_levels` and `support_level` per evidence row.

## Running Benchmarks

```bash
# LLM answer quality benchmark
python scripts/benchmark_llm.py

# Retrieval benchmark
python scripts/benchmark_rag.py
```

Results saved to `data/analysis/final/`.

## Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | — | LLM API key (required for answer generation) |
| `LLM_BASE_URL` | — | OpenAI-compatible API base URL |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `LLM_TEMPERATURE` | `0.1` | Generation temperature |
| `LLM_MAX_TOKENS` | `2000` | Max response tokens |
| `EMBEDDING_PROVIDER` | `local` | `local` or `api` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `HYBRID_RETRIEVAL` | `true` | Enable BM25+RRF hybrid |

### Pipeline Config (src/config.py)

| Setting | Value | Description |
|---------|-------|-------------|
| `no_answer_threshold` | 0.017 | Score gate for no-answer |
| `max_context_chunks` | 8 | Max evidence rows sent to LLM |
| `max_excerpt_chars` | 500 | Truncate excerpts for LLM |
| `max_chunks_per_paper` | 2 | Diversity rerank cap |
| `diversity_rerank` | True | Enable per-paper diversity |
| `LLM timeout` | 120s | LLM request timeout |

## Evidence Table

- **1858** cleaned evidence rows
- **179** unique papers
- **647** manual check flagged
- **214** ML feature candidates
- **101** high relevance PU

## Project Structure

```
D:\Academic-RAG/
  config/
    domain_equivalents.yaml    # Domain synonym/equivalent tables
  src/
    api/
      server.py                # FastAPI server
      schemas.py               # Pydantic models
    rag/
      answer_generator.py      # No-answer gate + LLM generation
      citation.py              # Evidence formatting
      llm_client.py            # OpenAI-compatible LLM client
      prompt_builder.py        # Prompt construction
      retriever.py             # BM25 + HybridRetriever
      service.py               # Full pipeline orchestrator
    ingest/
      index_builder.py         # Embedding engine
    storage/
      vector_store.py          # FAISS vector store
    config.py                  # Unified configuration
  frontend/
    src/
      pages/
        AskCorpus.tsx          # Q&A page with support level badges
      lib/
        api.ts                 # API client
  scripts/
    benchmark_llm.py           # LLM answer quality benchmark
    benchmark_rag.py           # Retrieval benchmark
  data/
    analysis/final/            # Benchmark results
  .env                         # Configuration (not committed)
```

## Manual Check Warnings

Evidence rows flagged with `needs_manual_check` require verification against the original PDF before citing. These are typically OCR artifacts or ambiguous excerpts.

## Known Limitations

1. **Full paper mode disabled**: No 37043-chunk FAISS index exists. Only evidence mode is available.
2. **LLM latency**: 60–110s per query. Dominated by LLM API response time.
3. **647 manual check rows**: ~35% of evidence needs human verification before citing.
4. **No streaming**: Answer appears only after full generation completes.
5. **No conversation history**: Each query is independent, no follow-up support.
