# Batch 4 Quality Gate Report

Generated: 2026-05-22

## 1. Evidence CSV Field Quality

### PVDF_piezoelectric_biomaterials_evidence.csv
- Total rows: 256
- Unique papers: 23
- Empty claim_type: 0
- Empty relevance: 0
- Empty ml_feature_candidate: 0
- Empty evidence_text: 0
- Empty page_est: 103 (mostly figure captions and performance data — expected)
- Claim types: general(126), measurement(105), finding(14), method(8), interpretation(3)
- Relevance: standard(241), high_relevance_pu(15)
- ML feature candidates: TRUE(17), FALSE(239)

### SAXS_WAXS_FTIR_DSC_characterization_evidence.csv
- Total rows: 332
- Unique papers: 25
- Empty claim_type: 0
- Empty relevance: 0
- Empty ml_feature_candidate: 0
- Empty evidence_text: 0
- Empty page_est: 146 (mostly figure captions — expected)
- Claim types: measurement(157), general(134), finding(27), method(8), interpretation(6)
- Relevance: standard(282), high_relevance_pu(50)
- ML feature candidates: TRUE(73), FALSE(259)

### Quality Assessment
- **PASS**: All rows have populated claim_type, relevance, ml_feature_candidate, evidence_text
- **PASS**: No empty evidence_text
- **PASS**: ML feature candidates reasonably distributed (17 + 73 = 90 total)
- **PASS**: High-relevance-to-PU entries identified (15 + 50 = 65 total)
- **NOTE**: Some page_est values missing for figure captions and performance data (expected)
- **ISSUE**: Some titles are journal info rather than paper titles (see Section 3)

## 2. Manual Check Paper Audit (30 papers)

All 30 manual check papers have **usable evidence** despite abstract/conclusion extraction failures.
Root cause: PDF two-column layout causes regex-based abstract/conclusion extraction to fail.
All papers still have: keyword-matched excerpts, figure captions, and/or performance data.

### PVDF_piezoelectric_biomaterials (20 papers)

| Paper ID | Title | Extraction Issue | Usable | Keep | Downgrade | Reason |
|----------|-------|-----------------|--------|------|-----------|--------|
| P069 | Journal of Science: Advanced Materials... | no abstract; no conclusion | Yes | Yes | No | 14 evidence rows, excerpts+figures+perf |
| P083 | Chem Soc Rev | no abstract | Yes | Yes | No | 8 rows, excerpts+perf, review article |
| P104 | J.Am.Ceram.Soc. | no abstract; no conclusion | Yes | Yes | No | 19 rows, excerpts+figures |
| P105 | PHYSICAL REVIEW B | no abstract; no conclusion | Yes | Yes | No | 9 rows, excerpts+figures |
| P106 | Vol.14,No.2(2024) | no abstract | Yes | Yes | No | 12 rows, excerpts+figures+perf |
| P107 | REVIEW SUMMARY | no abstract | Yes | Yes | No | 10 rows, excerpts+figures+perf, large review |
| P108 | 压电效应—百岁铁电的守护者 | no conclusion | Yes | Yes | No | 15 rows, excerpts+figures, Chinese review |
| P110 | Nano Energy 59 (2019) | no abstract; no conclusion | Yes | Yes | No | 10 rows, excerpts+figures |
| P111 | NanoEnergy102(2022) | no abstract | Yes | Yes | No | 10 rows, excerpts+figures |
| P113 | NanoEnergy118(2023) | no abstract; no conclusion | Yes | Yes | No | 15 rows, excerpts+figures+perf |
| P115 | Materials Today Communications | no abstract; no conclusion | Yes | Yes | No | 10 rows, excerpts+figures |
| P122 | HYDROGELS | no abstract; no conclusion | Yes | Yes | No | 8 rows, excerpts+figures |
| P123 | Piezoelectric Nanomaterial-Mediated... | no abstract; no conclusion | Yes | Yes | No | 9 rows, excerpts+figures |
| P140 | Biocompatible Piezoelectric Elastomer... | no conclusion | Yes | Yes | No | 9 rows, excerpts+figures, medium priority |
| P145 | PHYSICAL REVIEW LETTERS | no abstract; no conclusion | Yes | Yes | No | 8 rows, excerpts+figures+perf |
| P146 | Design and Manufacturing of Piezo... | no abstract | Yes | Yes | No | 13 rows, excerpts+figures+perf |
| P147 | Ultra-soft organic combined... | no abstract; no conclusion | Yes | Yes | No | 7 rows, excerpts+figures |
| P177 | The tribo-piezoelectric microscopic... | no conclusion | Yes | Yes | No | 10 rows, excerpts+figures |
| P298 | Cellulose sulfate lithium... | no abstract; no conclusion | Yes | Yes | No | 10 rows, excerpts+figures |
| P379 | A Close Look at the Local Structure... | no abstract | Yes | Yes | No | 10 rows, excerpts+figures+perf |

### SAXS_WAXS_FTIR_DSC_characterization (10 papers)

| Paper ID | Title | Extraction Issue | Usable | Keep | Downgrade | Reason |
|----------|-------|-----------------|--------|------|-----------|--------|
| P003 | www.advmat.de | no abstract | Yes | Yes | No | 10 rows, excerpts+figures, medium prio |
| P064 | HYDROGELS | no abstract | Yes | Yes | No | 9 rows, excerpts+figures, medium prio |
| P159 | Mechano-responsive H-bonding... | no abstract; no conclusion | Yes | Yes | No | 8 rows, excerpts+figures+perf |
| P240 | Programmable Liquid Crystal Elastomers... | no abstract; no conclusion | Yes | Yes | No | 8 rows, excerpts+figures |
| P284 | Multiscale Flow-Induced Nucleation... | no abstract | Yes | Yes | No | 20 rows, excerpts+figures+perf |
| P365 | SAXS OF POLYMER | no abstract; no conclusion | Yes | Yes | No | 18 rows, excerpts+figures |
| P366 | Tao Li, Andrew J. Senesi... | no abstract | Yes | Yes | No | 20 rows, excerpts+figures+perf |
| P372 | Polymer Vol.38 No.18... | no abstract | Yes | Yes | No | 9 rows, excerpts+figures |
| P380 | How to Characterize Supramolecular... | no conclusion | Yes | Yes | No | 23 rows, excerpts+figures+perf |
| P414 | Dynamic pathways in energy... | no abstract; no conclusion | Yes | Yes | No | 7 rows, excerpts+figures |

### Summary
- **30/30 papers**: usable evidence (excerpts, figures, performance data)
- **30/30 papers**: keep for synthesis
- **0 papers**: need full manual re-extraction
- **0 papers**: should be excluded from synthesis
- **All 30**: partial extraction due to PDF layout, not content absence

## 3. Title-as-Journal-Info Issue

The following papers have titles that are journal metadata rather than actual paper titles.
This is a classification/extraction artifact from the original PDF metadata.

| Paper ID | Title (as stored) | Category | Impact |
|----------|-------------------|----------|--------|
| P069 | JournalofScience:AdvancedMaterialsandDevices3(2018)1e17 | PVDF | Low — paper still has usable evidence |
| P083 | Chem Soc Rev | PVDF | Low — review article, still usable |
| P104 | J.Am.Ceram.Soc.,88[10]2663–2676(2005) | PVDF | Low |
| P105 | PHYSICALREVIEWB73,174106(cid:1)2006(cid:2) | PVDF | Low |
| P106 | Vol.14,No.2(2024)2340002(9pages) | PVDF | Low |
| P107 | REVIEW SUMMARY | PVDF | Low — large review, 124KB text |
| P110 | Nano Energy 59 (2019) 730–744 | PVDF | Low |
| P111 | NanoEnergy102(2022)107690 | PVDF | Low |
| P113 | NanoEnergy118(2023)108987 | PVDF | Low |
| P115 | MaterialsTodayCommunications31(2022)103491 | PVDF | Low |
| P003 | www.advmat.de | SAXS | Low |
| P372 | Polymer Vol.38No.18,pp.4571-4575,1997 | SAXS | Low |

**Recommendation**: These titles should be corrected from PDF first-page text if possible in a future cleanup pass. For now, paper_id serves as the primary identifier.

## 4. Overall Assessment

- **PASS**: All 48 papers processed with usable evidence
- **PASS**: Enhanced CSV fields (claim_type, relevance, ml_feature_candidate) all populated
- **PASS**: 90 ML feature candidates identified
- **PASS**: 65 high-relevance-to-PU entries identified
- **NOTE**: 30 papers have partial extraction (abstract/conclusion missing) but retain excerpts/figures/perf
- **NOTE**: 12 papers have journal-info titles — cosmetic issue, does not affect synthesis
- **READY**: Proceed to Batch 4 synthesis and Batch 5
