# Evidence Cleaning Report

Generated: 2026-05-22

## Summary

| Metric | Count |
|--------|-------|
| Raw evidence rows | 1858 |
| Cleaned evidence rows | 1858 |
| Duplicate rows removed | 0 |
| Page missing | 755 |
| Evidence missing | 0 |
| Needs manual check | 647 |
| High relevance to PU | 101 |
| ML feature candidates | 214 |
| Title needs cleanup | 136 (12 unique papers) |

## Category-wise Evidence Counts

| Category | Evidence Rows |
|----------|---------------|
| Biodegradable_Polyurethane | 39 |
| Ionogel_Magnetic_Ionogel | 271 |
| ML_Polymer_Properties | 103 |
| PCL_Based_Polyurethane | 40 |
| PU_Microphase_Separation | 126 |
| PVDF_Piezoelectric_Biomaterials | 256 |
| Review_Background | 199 |
| SAXS_WAXS_FTIR_DSC | 332 |
| Self_Healing_Elastomer | 203 |
| Shape_Memory_Polyurethane | 31 |
| TPU_Mechanics | 258 |
| **Total** | **1858** |

## Field Standardization

### Fields added to all rows
- `category`: mapped from evidence CSV filename
- `needs_manual_check`: TRUE for papers in batch4/batch5 manual check lists
- `title_needs_cleanup`: TRUE for papers with journal-info-as-title

### Fields backfilled for Batch 1-3 CSVs
Batch 1-3 evidence CSVs lacked `claim_type`, `figure_table_source`, `relevance`, `ml_feature_candidate`.
These were backfilled with defaults:
- `claim_type`: "general"
- `figure_table_source`: empty
- `relevance`: "standard"
- `ml_feature_candidate`: "FALSE"

**Note**: Batch 1-3 evidence rows do not have ML feature candidates or relevance classification.
For ML-related analysis, only Batch 4-5 evidence rows should be used.

## Title Cleanup Needed

12 papers have journal metadata as title instead of actual paper titles:

| Paper ID | Stored Title |
|----------|-------------|
| P003 | www.advmat.de |
| P069 | JournalofScience:AdvancedMaterialsandDevices3(2018)1e17 |
| P083 | Chem Soc Rev |
| P104 | J.Am.Ceram.Soc.,88[10]2663–2676(2005) |
| P105 | PHYSICALREVIEWB73,174106(cid:1)2006(cid:2) |
| P106 | Vol.14,No.2(2024)2340002(9pages) |
| P107 | REVIEW SUMMARY |
| P110 | Nano Energy 59 (2019) 730–744 |
| P111 | NanoEnergy102(2022)107690 |
| P113 | NanoEnergy118(2023)108987 |
| P115 | MaterialsTodayCommunications31(2022)103491 |
| P372 | Polymer Vol.38No.18,pp.4571-4575,1997 |

## Deduplication

No duplicate evidence rows found across all 11 category evidence CSVs.
Each evidence CSV contains unique rows from its respective category.

## Quality Notes

1. **page_est field**: 755 of 1858 rows have empty page_est. This is expected for figure captions, performance data, and some excerpts where PDF text extraction doesn't preserve page boundaries.
2. **evidence_text**: No rows have empty evidence_text. All evidence rows contain actual text content.
3. **needs_manual_check**: 647 rows from papers with partial extraction (abstract/conclusion missing due to PDF layout). These rows still contain usable excerpts, figures, and performance data.
4. **Old-format CSVs (Batch 1-3)**: Missing claim_type/relevance/ml_feature_candidate fields were backfilled with defaults. For precise ML feature analysis, only use Batch 4-5 data.
