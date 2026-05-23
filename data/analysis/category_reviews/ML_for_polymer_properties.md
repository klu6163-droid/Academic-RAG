# Category Review: Machine Learning for Polymer Properties

Generated: 2026-05-22 19:34
Papers reviewed: 9

## 1. Research Background

Machine learning (ML) is increasingly applied to polymer science for property prediction, materials discovery, and structure-property relationship modeling. Key challenges include limited training data, need for interpretable descriptors, and domain-specific feature engineering (e.g., SAXS/FTIR/DSC spectral features as ML inputs).

## 2. Dataset Sources

- **P184**: In this work, we present a Δ-learning approach
for predicting the eigenvalues calculated with the hybrid
functional HSE06 (ϵHSE) for a set of metal and nitrogen nk
doped graphene catalysts (MNCs) from...

- **P182**: TransPolymer: a Transformer-based language model for polymer property predictions...

- **P183**: Heterogenous catalysis involves complex reactions
with dynamic changes in catalyst morphology, challenging the
capabilities of traditional density functional theory (DFT)
methods. To address this, we ...

- **P185**: Mathematical modeling has long played a crucial role in the development of macromolecular
systems, offering a framework for designing polymeric materials to achieve specific targets.
Traditionally, th...

- **P186**: Periodicity-aware deep learning for polymers Received: 4 January 2025 Yuhui Wu1,2,5, Cong Wang1,2,5, Xintian Shen1,2, Tianyi Zhang1,2, Peng Zhang 1,2,3...

- **P187**: Structure-Aware Machine Learning for Polymers: A Hierarchical Graph Network for Predicting Properties From...

- **P189**: Determining solubilities of organic molecules is critical in
various fields such as pharmaceuticals, agrochemicals, and environmental
science. Knowing how a solute will dissolve in different solvents ...

- **P192**: ANN Artificial neural network Ppy Polypyrrole BoW Bag-of-words PSC Perovskite solar cell...

- **P305**: This study showed that an optimized structural
simulationmodelforpolymermaterialsusingactualmeasurements
asanindicatorcanenabletheexpressionofionchannelstructures
as digital values that affect ion con...

## 3. Input Feature Types

**Common polymer descriptors:**
- SMILES / molecular fingerprints
- Monomer composition and sequence
- Molecular weight and distribution
- Topological features (branching, crosslink density)

**Spectroscopy features:**
- FTIR peak positions and intensities
- SAXS/WAXS peak positions and FWHM
- DSC thermal transitions (Tg, Tm, ΔH)
- Dielectric relaxation parameters

## 4. Model Types

- **P184**: Neural Network, Deep Learning, Transformer, GNN, Machine Learning
- **P182**: Random Forest, Neural Network, Deep Learning, Transformer, Gradient Boosting
- **P183**: Neural Network, Deep Learning, Transformer, GNN, Machine Learning
- **P185**: Random Forest, Neural Network, Deep Learning, Transformer, GNN
- **P186**: Random Forest, Neural Network, Deep Learning, Transformer, GNN, Machine Learning
- **P187**: Neural Network, Transformer, GNN, SVM, Machine Learning
- **P189**: Random Forest, Neural Network, GNN, Machine Learning
- **P192**: Neural Network, Deep Learning, SVM, Machine Learning
- **P305**: Machine Learning

## 5. Prediction Targets

## 6. Evaluation Metrics

## 7. Interpretability Methods

## 8. Suitability for PU Mechanical Property Prediction

**Assessment:**
- P184: Structure Using Graph Neural Networks with Modified Node-Level Features

- P182: TransPolymer: a Transformer-based language model for polymer property predictions

- P183: A Machine Learning Interatomic Potential Data Set and Model for Catalysis with Local Fine-Tuning to Chemical Accuracy

- P185: Adding Machine Learning to the Polymer Reaction Engineering Toolbox

- P186: Periodicity-aware deep learning for polymers Received: 4 January 2025 Yuhui Wu1,2,5, Cong Wang1,2,5, Xintian Shen1,2, Tianyi Zhang1,2, Peng Zhang 1,2,3

- P187: Structure-Aware Machine Learning for Polymers: A Hierarchical Graph Network for Predicting Properties From

- P189: Machine Learning, and Solvent Ensembles Emad Al Ibrahim, Nathan Morgan, Simon Müller, Saikiran Motati, and William H. Green*

- P192: ANN Artificial neural network Ppy Polypyrrole BoW Bag-of-words PSC Perovskite solar cell

- P305: Separated Structures in Graft-Type Polymer Electrolyte Membrane by Optimization Compared to Scattering Analysis

## 9. Transferable Techniques

## 10. Data Gaps and Risks

## Evidence Table

| Paper ID | Title | Year | Priority | Quality | ML Methods | Key Contribution |
|----------|-------|------|----------|---------|------------|------------------|
| P184 | Δ‑Learning of High-Fidelity Electronic | 2025 | medium | good | SEM, TEM, Neural Network | Structure Using Graph Neural Networks with Modified Node-Level Features |
| P182 | TransPolymer: a Transformer-based langua... | 2023 | low | partial | DSC, DMA, SEM | TransPolymer: a Transformer-based language model for polymer property prediction |
| P183 | A Machine Learning Interatomic Potential... | 2025 | low | good | DSC, DMA, TGA | A Machine Learning Interatomic Potential Data Set and Model for Catalysis with L |
| P185 | Adding Machine Learning to the Polymer R... | 2025 | low | partial | DSC, Stress-Strain, SEM | Adding Machine Learning to the Polymer Reaction Engineering Toolbox |
| P186 | Periodicity-aware deep learning for poly... | 2025 | low | partial | SEM, TEM, Dielectric Spectroscopy | Periodicity-aware deep learning for polymers Received: 4 January 2025 Yuhui Wu1, |
| P187 | Structure-Aware Machine Learning for Pol... | 2026 | low | partial | DMA, SEM, TEM | Structure-Aware Machine Learning for Polymers: A Hierarchical Graph Network for  |
| P189 | Accurately Predicting Solubility Curves ... | 2025 | low | good | DMA, SEM, TEM | Machine Learning, and Solvent Ensembles Emad Al Ibrahim, Nathan Morgan, Simon Mu |
| P192 | Age of Flexible Electronics: Emerging Tr... | 2024 | low | partial | DSC, DMA, SEM | ANN Artificial neural network Ppy Polypyrrole BoW Bag-of-words PSC Perovskite so |
| P305 | Separated Structures in Graft-Type Polym... | 2025 | low | good | SAXS, DSC, DMA | Separated Structures in Graft-Type Polymer Electrolyte Membrane by Optimization  |
