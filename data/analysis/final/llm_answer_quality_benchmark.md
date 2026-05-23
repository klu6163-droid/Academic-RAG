# LLM Answer Quality Benchmark

Generated: 2026-05-23 10:14
Model: Kimi-K2.6 (Silicon Flow API)
Retrieval: FAISS+BM25+RRF hybrid, evidence mode (1858 rows)

## Summary

| Metric | Value |
|--------|-------|
| Total queries | 10 |
| Passed deterministic gate (score ≥ 0.017) | 6/10 |
| Blocked by deterministic gate | 4/10 (Q5, Q8, Q9, Q10) |
| LLM returned no_answer=true | 10/10 |
| With paper_id citation | 1/10 (Q1 only) |
| Avg response time | 34.4s |
| Hallucinated paper IDs | 0 |

## Two-Layer No-Answer Gate

This system uses a **two-layer** no-answer mechanism:

1. **Deterministic gate** (score < 0.017): Blocks before LLM is called
2. **LLM self-assessment**: LLM returns `no_answer: true` in JSON when evidence is insufficient

| Query | Score | Gate Result | LLM Result | Final |
|-------|-------|-------------|------------|-------|
| Q1: 微相分离 | 0.0262 | PASS | no_answer | no_answer |
| Q2: PCL活死染色 | 0.0303 | PASS | no_answer | no_answer |
| Q3: TPU SAXS | 0.0278 | PASS | no_answer | no_answer |
| Q4: PVDF蛋白吸附 | 0.0237 | PASS | no_answer | no_answer |
| Q5: ML数据来源 | 0.0164 | BLOCKED | — | no_answer |
| Q6: FeCl4+PU | 0.0241 | PASS | no_answer | no_answer |
| Q7: FTIR C=O | 0.0267 | PASS | no_answer | no_answer |
| Q8: SAXS FWHM | 0.0164 | BLOCKED | — | no_answer |
| Q9: 火星土壤PU | 0.0164 | BLOCKED | — | no_answer |
| Q10: PU治癌症 | 0.0164 | BLOCKED | — | no_answer |

## Per-Query Evaluation

### Q1: 哪些论文提到了聚氨酯微相分离？
- **Score**: 0.0262 | **Confidence**: High | **Time**: 68.4s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: paper_id=P003 ✓, page ✓
- **Evaluation**: LLM correctly identifies that P003 discusses TPU soft/hard segment structure (which IS microphase separation) but the excerpt doesn't contain the exact term "微相分离". The LLM is being **overly conservative** — soft/hard segment phase separation IS microphase separation.
- **Quality**: Good reasoning, honest about evidence limitations, cites P003
- **Issue**: LLM should recognize domain synonyms (soft/hard segment structure ≈ microphase separation)

### Q2: PCL基聚氨酯有没有做活死细胞染色？
- **Score**: 0.0303 | **Confidence**: Low | **Time**: 28.4s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: none
- **Evaluation**: Correct no-answer. Evidence only covers PCL synthesis and physical properties, no biological experiments.
- **Quality**: Good — clearly explains what evidence DOES contain and what's missing
- **Issue**: None — this is a correct "not in corpus" judgment

### Q3: 哪些文献报道了TPU的SAXS long period？
- **Score**: 0.0278 | **Confidence**: High | **Time**: 47.0s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: none
- **Evaluation**: Correct no-answer. Retrieved SAXS papers are about other polymers (PVA, polyester), not TPU.
- **Quality**: Good — distinguishes between "SAXS papers exist" and "TPU SAXS papers exist"
- **Issue**: None — honest assessment

### Q4: PVDF压电材料是否影响蛋白吸附？
- **Score**: 0.0237 | **Confidence**: High | **Time**: 31.5s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: none
- **Evaluation**: Correct no-answer. Evidence covers PVDF electrolytes and piezoelectric properties, not protein adsorption.
- **Quality**: Good — concise and accurate
- **Issue**: None

### Q5: 哪些文献适合作为聚氨酯力学性能机器学习预测的数据来源？
- **Score**: 0.0164 | **Confidence**: Low | **Time**: 2.1s
- **Gate**: BLOCKED (score < 0.017) | **LLM**: not called
- **Citations**: none
- **Evaluation**: Correctly blocked. This is a meta-question about data suitability, not a specific literature query.
- **Quality**: Gate response is terse ("当前知识库中没有足够证据支持该回答")
- **Issue**: Could provide a more helpful message for meta-questions

### Q6: FeCl4 和 PU 可能有哪些相互作用？
- **Score**: 0.0241 | **Confidence**: Low | **Time**: 107.0s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: [4] for FeCl4 in PMMA system, [1][2][5][7] for PU properties
- **Evaluation**: Excellent reasoning. LLM correctly identifies that FeCl4 appears in non-PU systems and PU evidence doesn't mention FeCl4. No hallucinated connections.
- **Quality**: Best response in the benchmark — detailed cross-referencing, honest about evidence gaps
- **Issue**: None — this is the gold standard for "evidence exists but doesn't answer the question"

### Q7: 哪些文献提到了FTIR中C=O氢键？
- **Score**: 0.0267 | **Confidence**: Low | **Time**: 27.1s
- **Gate**: PASS | **LLM no_answer**: True
- **Citations**: none
- **Evaluation**: Correct no-answer. Evidence mentions "FTIR-ATR spectra" but not C=O hydrogen bonding specifically.
- **Quality**: Good — notes the partial match (FTIR mentioned, but not the specific topic)
- **Issue**: None

### Q8: 哪些论文使用SAXS峰位置或FWHM作为结构特征？
- **Score**: 0.0164 | **Confidence**: Low | **Time**: 2.1s
- **Gate**: BLOCKED (score < 0.017) | **LLM**: not called
- **Evaluation**: Correctly blocked. This is a methodological question that the evidence table doesn't directly address.
- **Issue**: Same as Q5 — terse gate response

### Q9: 这个知识库里有没有关于火星土壤种植聚氨酯的论文？
- **Score**: 0.0164 | **Confidence**: Low | **Time**: 2.1s
- **Gate**: BLOCKED (score < 0.017) | **LLM**: not called
- **Evaluation**: Correctly blocked — nonsense/out-of-scope query. Low score confirms no relevant evidence.
- **Issue**: None — gate works correctly for out-of-scope queries

### Q10: 有没有论文证明聚氨酯可以治疗癌症？
- **Score**: 0.0164 | **Confidence**: Low | **Time**: 2.1s
- **Gate**: BLOCKED (score < 0.017) | **LLM**: not called
- **Evaluation**: Correctly blocked — nonsense/out-of-scope query.
- **Issue**: None

## Hallucination Check

| Check | Result |
|-------|--------|
| Fabricated paper IDs | 0/10 queries |
| Fabricated page numbers | 0/10 queries |
| Fabricated data/figures | 0/10 queries |
| Cited evidence not in retrieval | 0/10 queries |

**Verdict: Zero hallucination.** The LLM strictly adheres to provided evidence and never fabricates citations.

## Key Findings

### Strengths
1. **Zero hallucination**: LLM never fabricates paper IDs, pages, or data
2. **Honest no-answer**: When evidence is insufficient, LLM clearly says so with reasoning
3. **Good reasoning**: Q1 and Q6 show the LLM can analyze evidence relationships and explain gaps
4. **Gate catches nonsense**: Q9, Q10 (out-of-scope) correctly blocked by score threshold
5. **Manual check warnings**: Consistently flagged for flagged evidence rows
6. **Language matching**: Responds in Chinese for Chinese queries

### Issues
1. **100% no-answer rate**: All queries return no_answer=True. The LLM is overly conservative — it requires exact keyword matches in excerpts rather than recognizing domain equivalences.
2. **Q1 false negative**: Soft/hard segment structure IS microphase separation, but LLM says "term not found"
3. **Q7 false negative**: FTIR evidence exists but LLM requires exact "C=O hydrogen bonding" mention
4. **Citation inconsistency**: Only Q1 cites paper_id; Q6 uses [number] format but doesn't map to paper_ids
5. **Terse gate responses**: Q5, Q8 blocked by gate with generic message — no domain-specific guidance
6. **P151 dominance**: 7/10 queries have P151 in top-3, suggesting BM25 over-indexes on this paper
7. **Slow responses**: Q6 took 107s, Q1 took 68s — LLM latency is high

## Recommendations

### High Priority
1. **Refine no-answer prompt**: The prompt "If the evidence is insufficient, say so clearly" is too strict. Add guidance: "If evidence discusses the CONCEPT even without using the exact term, consider it relevant. For example, 'soft/hard segment structure' IS 'microphase separation'."
2. **Add synonym guidance to prompt**: Include domain-specific synonym mappings (微相分离 ≈ 软硬段分离, C=O氢键 ≈ 羰基氢键)
3. **Improve citation format**: Standardize on [paper_id] format instead of [number] for consistency

### Medium Priority
4. **Tune deterministic threshold**: Current 0.017 blocks Q5/Q8 which are legitimate queries. Consider 0.015 for broader recall.
5. **P151 debiasing**: P151 has too many evidence rows, dominating BM25 results. Consider TF-IDF weighting or per-paper result caps.
6. **Gate response enhancement**: For blocked queries, provide more helpful messages (e.g., "No matching evidence found. Try rephrasing or check if the topic is in the corpus.")

### Low Priority
7. **Response latency**: 30-107s is slow. Consider streaming or async response.
8. **Add confidence calibration**: LLM returns "High" confidence even when setting no_answer=true — these should be "Low".

## Benchmark Configuration

```
Backend: http://localhost:8000
Endpoint: POST /api/ask
Mode: evidence
Top K: 8
LLM: Pro/moonshotai/Kimi-K2.6 (Silicon Flow)
Embedding: all-MiniLM-L6-v2 (local)
Retrieval: FAISS+BM25+RRF hybrid
No-answer threshold: 0.017
Evidence rows: 1858
```
