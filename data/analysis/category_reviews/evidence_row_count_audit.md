# Evidence Row Count Audit

Generated: 2026-05-22

## Actual Row Counts (including header)

| CSV File | Total Lines | Data Rows | Unique Papers |
|----------|-------------|-----------|---------------|
| polyurethane_microphase_separation_evidence.csv | 386 | 385 | 12 |
| TPU_mechanics_evidence.csv | 774 | 773 | 27 |
| self_healing_elastomer_evidence.csv | 620 | 619 | 20 |
| shape_memory_polyurethane_evidence.csv | 83 | 82 | 4 |
| **Total** | **1863** | **1859** | **63** |

## Discrepancy with Quality Gate Report

The Batch 1 quality gate report (batch1_quality_gate.md) stated:
- polyurethane_microphase_separation: 126 rows
- TPU_mechanics: 258 rows

**Actual counts are 385 and 773 respectively.** The quality gate report was generated before the final evidence CSVs were written — it appears to have used preliminary counts. The actual file counts are correct and significantly higher.

## P437 Conclusion Fix

**Issue**: P437's conclusion was mixed with reference text due to 2-column PDF layout.

**Clean conclusion extracted manually**:
"In conclusion, this study presents an ultra-strong and tough bio-based polyurethane elastomer with multiple hydrogen bonds. Through the modulation of FDHA content, which acts as the network builder for the dynamic hydrogen bonding-induced confinement effect, the polyurethane micro-network transitioned from a weak isolated structure to a robust 'soft-hard' layered dual-continuous microphase separation structure. This distinctive microstructure endows the elastomer with remarkable mechanical properties, including ultra-high tensile strength (76.54 MPa), exceptional toughness (589.75 MJ m−3), significant fracture true stress (1.45 GPa), and superior fatigue and damage resistance. Beyond these outstanding mechanical attributes, PFPU demonstrates favorable biocompatibility and can be precisely fabricated using 3D printing technology to produce artificial ligaments, which shows great application prospects in the biomedical field."

**Source**: P437.txt, section "3.Conclusion", page ~11 (Adv. Funct. Mater. 2026, 36, e10461)

**Action**: P437 updated from needs_manual_check to confirmed — conclusion now available for synthesis.

## Status

- [x] Row counts verified
- [x] P437 conclusion fixed
- [x] Ready for Batch 3
