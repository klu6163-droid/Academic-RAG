# Project Synthesis: Machine Learning for Polyurethane Properties

Generated: 2026-05-22

## 1. Research Question

如何利用机器学习预测聚氨酯的力学性能？
SAXS/FTIR/DSC特征作为ML输入的有效性如何？
小数据集下如何实现可靠的模型训练和预测？

## 2. Existing Evidence from Corpus

### ML架构
- P182: "TransPolymer: a Transformer-based language model for polymer property prediction" (file: P182.txt, confidence: medium)
- P186: "Periodicity-aware deep learning for polymers" (file: P186.txt, confidence: medium)
- P187: "Structure-Aware Machine Learning for Polymers" (file: P187.txt, confidence: medium)
- P183: "A Machine Learning Interatomic Potential Data Set and Model" (file: P183.txt, confidence: medium)

### ML特征候选（from Batch 4-5 evidence）
- SAXS peak position: 20 evidence rows
- SAXS FWHM: 10 evidence rows
- WAXS peak: 12 evidence rows
- FTIR peak / band ratio: 10 evidence rows
- DSC Tg/Tm/delta-H: 15 evidence rows
- Mechanical properties: 8 evidence rows
- Total ML feature candidates: 214 rows

### 光谱特征作为ML输入
- P260: Multi-technique (SAXS/FTIR/BDS/DSC/rheology) characterization framework (file: P260.txt, abstract, confidence: high)
- P369: SAXS + DMA for polyurea microstructure (file: P369.txt, confidence: high)

## 3. Mechanistic Chain

PU chemical structure
    -> SAXS: domain size, long period, FWHM
    -> FTIR: H-bond index, phase separation index
    -> DSC: Tg, Tm, crystallinity
    -> ML model (RF, NN, GNN, Transformer)
    -> predicted: tensile strength, elongation, toughness, modulus

## 4. Key Papers

1. P182: TransPolymer — Transformer for polymer properties
2. P186: Periodicity-aware deep learning
3. P187: Structure-aware ML for polymers
4. P260: Multi-technique characterization framework
5. P369: SAXS + DMA for polyurea

## 5. Best Evidence Excerpts

- P182: "TransPolymer: a Transformer-based language model for polymer property prediction"
- P186: "Periodicity-aware deep learning for polymers"
- P260 abstract: "Combining X-ray scattering, Fourier transform infrared spectroscopy (FT-IR), broadband dielectric spectroscopy (BDS), rheology, and differential scanning calorimetry (DSC)"

## 6. Missing Evidence

1. 使用SAXS/FTIR/DSC特征预测PU力学性能的直接研究 — evidence_missing
2. 聚合物ML数据集规模和泛化能力评估 — partial evidence from P182, P186
3. 特征重要性分析：哪些SAXS/FTIR/DSC特征对力学预测最关键 — evidence_missing
4. 小数据集下的迁移学习或数据增强策略 — evidence_missing

## 7. Recommended Experiments or Simulations

1. 构建PU力学性能数据集：从文献中提取SAXS/FTIR/DSC特征 + 力学标签
2. 特征工程：SAXS peak position, FWHM, domain size; FTIR HBI; DSC Tg, Tm, delta-H
3. 模型训练：Random Forest (baseline), XGBoost, Neural Network
4. 可解释性：SHAP分析特征重要性
5. 迁移学习：从大分子数据集预训练，微调到PU数据集

## 8. How to Use in Paper/Grant Writing

- 引言：用P182/P186/P187建立聚合物ML的研究背景
- 方法：特征工程策略（SAXS/FTIR/DSC -> ML features）
- 讨论：小数据集风险和缓解策略
- 创新点：SAXS/FTIR/DSC特征直接用于PU力学预测是文献空白
