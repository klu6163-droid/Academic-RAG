# Project Status v1 — Polyurethane Literature RAG System

**Date**: 2026-05-23
**Version**: v1.0 (v2.1 concise mode)

## Current Data Scale

| Metric | Value |
|--------|-------|
| Evidence rows | 1858 |
| Unique papers | 179 |
| Manual check flagged | 647 |
| ML feature candidates | 214 |
| High relevance PU | 101 |
| FAISS vectors | 1858 |
| Embedding dimension | 384 (all-MiniLM-L6-v2) |

## Core Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Evidence mode | **Enabled** | Default mode, 1858 curated rows |
| Full paper mode | **Disabled** | No 37043-chunk FAISS index built |
| Hybrid mode | **Available** | Evidence first, full paper fallback (requires full paper index) |
| Ask Corpus | **Enabled** | Full RAG: retrieve + LLM answer |
| Retrieve Only | **Enabled** | No LLM, returns evidence cards |
| Dashboard | **Enabled** | Corpus statistics and visualizations |
| Knowledge Graph | **Enabled** | Interactive node-edge graph |
| No-answer gate | **Enabled** | Score threshold 0.017 |
| Support level badges | **Enabled** | direct, equivalent_concept, partial, insufficient |
| Concise answer mode | **Default** | 300-600 chars, 3 conclusions, top-5 evidence |
| Detailed answer mode | **Available** | Full analysis, top-8 evidence |
| Complex query auto-degrade | **Enabled** | Detailed → concise for complex queries |
| Diversity rerank | **Enabled** | Max 2 chunks per paper |
| Domain equivalent hints | **Enabled** | 8 categories in domain_equivalents.yaml |
| System override | **Enabled** | Restores answers with substantive evidence analysis |
| Query expansion | **Disabled** | Requires LLM, off by default |
| Timeout fallback | **Enabled** | Returns evidence with warning on LLM timeout |

## Retrieval Pipeline

```
Question → Query Expansion (optional) → FAISS Dense + BM25 Sparse → RRF Fusion → Diversity Rerank → No-Answer Gate → LLM Answer
```

- **Dense**: FAISS IndexFlatIP, all-MiniLM-L6-v2 (384 dim)
- **Sparse**: BM25 (k1=1.5, b=0.75)
- **Fusion**: Reciprocal Rank Fusion (k=60)
- **LLM**: Kimi-K2.6 via Silicon Flow API (OpenAI-compatible)

## Performance

| Query Type | Typical Latency | Notes |
|------------|-----------------|-------|
| Simple evidence lookup | 60–80s | LLM-bound |
| Complex cross-reference | 80–110s | Concise mode prevents timeout |
| Out-of-domain | 2–5s | No-answer gate blocks before LLM |
| Retrieve only | <1s | No LLM call |

Bottleneck: LLM response time (~90% of latency). Retrieval is <500ms.

## Start Commands

```bash
# Backend (port 8001)
cd literature_project
python -m src.api.server

# Frontend (port 5173)
cd frontend
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/stats` | Pipeline statistics |
| POST | `/api/ask` | Ask question (retrieve + answer) |
| POST | `/api/retrieve` | Retrieve evidence only |

## Known Limitations

1. **Full paper mode disabled**: No chunk index built. Only evidence mode available.
2. **LLM latency**: 60–110s per query. Dominated by LLM API response time.
3. **647 manual check rows**: ~35% of evidence needs human verification before citing.
4. **No streaming**: Answer appears only after full generation completes.
5. **No conversation history**: Each query is independent, no follow-up support.
6. **Chinese-only prompts**: LLM prompt is optimized for Chinese answers.

## Recommended Usage

1. Start backend and frontend
2. Open Ask Corpus page
3. Default: Curated Evidence + Concise mode
4. For complex questions: use Retrieve Only first to inspect evidence, then Ask
5. Check support level badges on evidence cards
6. Manual check warnings require human verification against original PDF
7. No-answer means insufficient evidence in corpus, not that the answer doesn't exist

## Next Steps (Priority Order)

1. **Streaming responses**: Show answer tokens as generated (SSE or WebSocket)
2. **Faster LLM**: Switch to a faster model or self-hosted inference
3. **Full paper index**: Build 37043-chunk FAISS index from extracted PDFs
4. **Conversation memory**: Support follow-up questions
5. **Batch query mode**: Process multiple questions from CSV
6. **Evidence export**: Download selected evidence as CSV/BibTeX
7. **Chinese embedding model**: Replace all-MiniLM-L6-v2 with a CJK-optimized model
