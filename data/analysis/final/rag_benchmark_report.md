# RAG Benchmark Report

Generated: 2026-05-23

## Configuration

- Evidence rows: 1858
- FAISS vectors: 1858 (IndexFlatIP, normalized)
- BM25: k1=1.5, b=0.75
- RRF k: 60
- Embedding model: all-MiniLM-L6-v2 (384 dim)
- Retrieval mode: evidence (hybrid FAISS+BM25+RRF)

## Score Distribution

| Group | Queries | Score Range | Mean |
|-------|---------|-------------|------|
| Clearly relevant (Q1-4,6,7) | 6 | 0.0237 – 0.0303 | 0.0265 |
| Marginally relevant (Q5,8) | 2 | 0.0164 | 0.0164 |
| Clearly irrelevant (Q9,10) | 2 | 0.0164 | 0.0164 |

## Per-Query Results

| # | Query | Score | Top Papers | Relevant? |
|---|-------|-------|------------|-----------|
| 1 | 哪些论文提到了聚氨酯微相分离？ | 0.0262 | P339, P151, P219 | Yes |
| 2 | PCL基聚氨酯有没有做活死细胞染色？ | 0.0303 | P151, P339, P166 | Yes |
| 3 | 哪些文献报道了TPU的SAXS long period？ | 0.0278 | P286, P425, P372 | Yes |
| 4 | PVDF压电材料是否影响蛋白吸附？ | 0.0237 | P069, P151 | Yes |
| 5 | 哪些文献适合做PU力学性能ML预测？ | 0.0164 | P151, P074, P219 | Weak |
| 6 | FeCl4和PU可能有哪些相互作用？ | 0.0241 | P258, P439, P089 | Yes |
| 7 | 哪些文献提到了FTIR中C=O氢键？ | 0.0267 | P339, P151 | Yes |
| 8 | 哪些论文使用SAXS峰位置/FWHM？ | 0.0164 | P151, P425, P372 | Weak |
| 9 | 有没有关于火星土壤种植聚氨酯的？ | 0.0164 | P151, P219, P003 | No |
| 10 | 有没有论文证明PU可以治疗癌症？ | 0.0164 | P151, P219, P003 | No |

## Threshold Analysis

| Threshold | Pass | Filtered | Assessment |
|-----------|------|----------|------------|
| 0.015 | 10 | 0 | Too permissive — irrelevant queries pass |
| 0.016 | 10 | 0 | Same as 0.015 (all scores ≥ 0.0164) |
| **0.017** | **6** | **4** | **Best: filters Q5,8,9,10; keeps all clearly relevant** |
| 0.020 | 6 | 4 | Same as 0.017 for this test set |
| 0.024 | 5 | 5 | Too aggressive — filters Q4 (PVDF/protein) |

## Recommended Thresholds

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `no_answer_threshold` | 0.017 | Separates relevant (≥0.0237) from irrelevant (0.0164) |
| `min_retrieval_score` | 0.017 | Same as no_answer_threshold |
| `min_evidence_chunks` | 1 | Keep as-is |

## Known Limitations

1. **P151 dominance**: P151 appears in top results for 8/10 queries because it has many evidence rows. BM25 matches "polyurethane" across all queries.
2. **Score compression**: RRF scores are compressed to 0.016-0.030 range, making fine-grained discrimination difficult.
3. **Q5/Q8 false negatives**: Marginally relevant queries (ML data sources, SAXS FWHM) score same as irrelevant ones. These need query expansion or better embeddings to resolve.
4. **Chinese tokenization**: BM25 uses character-level matching for CJK, which may miss multi-character terms.

## Full Paper Mode

Not yet available. To enable:
1. Chunk 456 extracted text files (512-token windows, 128-token overlap)
2. Compute embeddings (~37K chunks)
3. Build FAISS index
4. Store chunk metadata (paper_id, file_name, page_est)

## Next Steps

1. Set `LLM_API_KEY` in `.env` to test answer quality
2. Build full-paper chunk index for broader coverage
3. Consider query expansion for marginal queries (Q5, Q8)
4. Consider hybrid scoring that uses claim_type and confidence as signals
