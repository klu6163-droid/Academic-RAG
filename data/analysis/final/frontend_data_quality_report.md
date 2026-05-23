# Frontend Data Quality Report

Generated: 2026-05-22

## File Existence Check

| File | Status |
|------|--------|
| global_evidence_table_cleaned.csv | OK |
| kg_nodes.csv | OK |
| kg_edges.csv | OK |
| final_literature_analysis_report.md | OK |

## Data Integrity

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Evidence rows | ~1858 | 1858 | PASS |
| KG nodes | ~228 | 228 | PASS |
| KG edges | ~820 | 820 | PASS |
| Edges with missing source | 0 | 0 | PASS |
| Edges with missing target | 0 | 0 | PASS |
| Empty evidence excerpt | 0 | 0 | PASS |
| Empty claim_type | 0 | 0 | PASS |
| Empty confidence | 0 | 0 | PASS |
| Evidence unique papers | 179 | 179 | PASS |
| KG paper nodes | 179 | 179 | PASS |
| Papers in evidence but not KG | 0 | 0 | PASS |
| Papers in KG but not evidence | 0 | 0 | PASS |

## Field Quality

| Field | Count | Status |
|-------|-------|--------|
| Page missing | 755 | NOTE — expected for figure captions and performance data |
| Title needs cleanup | 136 rows (12 papers) | NEEDS FIX |
| Needs manual check | 647 | NOTE — usable evidence, just partial extraction |
| ML feature candidates | 214 | OK |
| High relevance to PU | 101 | OK |

## Summary

All data files exist and are internally consistent.
All paper_ids in evidence match KG paper nodes.
All edge source/target IDs resolve to valid node IDs.
No empty evidence excerpts or missing confidence/claim_type fields.

**Action needed**: Title cleanup for 12 papers before frontend build.
