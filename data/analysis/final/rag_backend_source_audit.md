# RAG Backend Source Audit

Generated: 2026-05-23

## Current Retrieval Mode

| Field | Value |
|-------|-------|
| Default mode | evidence |
| Vector count | 1858 |
| Source data | `frontend/public/data/evidence.json` |
| Source index | `data/cache/faiss_index/evidence.index` |
| Embedding cache | `data/cache/embeddings/evidence_embeddings.npy` |
| Embedding model | all-MiniLM-L6-v2 (384 dim) |
| Index type | FAISS IndexFlatIP (inner product on normalized vectors) |
| BM25 | Enabled, k1=1.5, b=0.75 |
| Fusion method | RRF (k=60) |

## Data Source Confirmation

The current backend retrieves from the **cleaned evidence table** (1858 rows), NOT from raw PDF chunks.

- Source CSV: `data/analysis/final/global_evidence_table_cleaned.csv` (5471 lines including header, 1858 unique evidence rows after dedup/cleaning)
- Source JSON: `frontend/public/data/evidence.json` (1858 rows)
- Each row contains: paper_id, title, file_name, category, year, evidence_type, claim_type, evidence_text, page_est, keyword, confidence, relevance, ml_feature_candidate, needs_manual_check

## Citation Traceability

| Field | Available | Source |
|-------|-----------|--------|
| paper_id | Yes | evidence table |
| title | Yes | evidence table (display_title or title) |
| file_name | Yes | evidence table |
| PDF page | Partial | `page_est` field — 1103 rows have page info, 755 missing |
| category | Yes | evidence table |
| claim_type | Yes | evidence table |
| confidence | Yes | evidence table |
| excerpt | Yes | `evidence_text` field |

## 37043 Chunk Index Status

**NOT FOUND.** No FAISS index with 37043 vectors exists in the project.

Search locations checked:
- `data/cache/faiss_index/` — only `evidence.index` (1858 vectors)
- legacy source workspace - no other `.index` files
- `D:/paper_rag_data/` — directory does not exist

Available raw data for building a full-paper index:
- `06_logs/extracted_texts/` — 456 `.txt` files (full extracted text per PDF)
- These could be chunked and indexed to create a ~37K chunk index

## Available Modes

| Mode | Status | Vector Count | Source |
|------|--------|-------------|--------|
| evidence | **Active** | 1858 | Cleaned evidence table |
| full_paper | **Not configured** | N/A | No chunk index exists |
| hybrid | **Fallback only** | 1858 | Falls back to evidence mode |

## Recommendation

To enable `full_paper` mode:
1. Chunk the 456 extracted text files (e.g., 512-token windows with 128-token overlap)
2. Compute embeddings for ~37K chunks
3. Build FAISS index
4. Store chunk metadata (paper_id, file_name, page_est, chunk_text)
5. This would require a new build step, not just configuration
