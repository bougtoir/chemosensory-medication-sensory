# 14 — Confirmatory statistical analysis plan (pre-receipt)

Status: FINAL PRE-RECEIPT FREEZE.

## Hypotheses
- PRIMARY: pre-specified chemosensory genetic variation (approved 20-gene universe, Level-A variants) predicts longitudinal ph1→ph2 medication-change phenotypes in drugs predicted to engage the corresponding receptor (Family A: P01 propylthiouracil, P02 thiamazole — TAS2R38 PAV; P05 ofloxacin — TAS2R9 V187A).
- SECONDARY 1: genotype effects are stronger for formulations/routes with greater oral sensory exposure (Family E).
- SECONDARY 2: the same variants predict pre-specified FFQ chemosensory phenotypes (Family D).
- SECONDARY 3: gene-constrained analysis of all delivered SNPs in approved regions (Family B).
- SECONDARY 4: clinical + genotype improves out-of-sample prediction over clinical alone (Family H).
- NEGATIVE CONTROLS: frozen N01–N10, N12 (`10`).

## Population (D16)
Both-wave participants, age ≥20 at ph1, genotype QC pass. Exclusions counted in `11_analysis_set_lock.json`.

## Genotype coding
Additive dosage of the effect allele (`05`); TAS2R38 PAV dosage from EM-phased rs713598/rs1726866/rs10246939 (A49P only if the haplotype SNPs are unavailable or fail QC → S03 as sensitivity).

## Models (no p-value-driven model selection)
1. Participant-level binary endpoints (Families A, AS, C, C2, F): logistic regression, Y ~ G + covariates; drug-specific endpoints add n_rx_ph1 and are restricted to ph1 users of the drug (indication restriction, legacy 76). Effect: OR per effect allele, 95% CI.
2. Dose change (secondary): mean log daily-dose ratio over dose-comparable shared ingredients, linear model, robust SE.
3. No count model is pre-specified (the number of changed ingredients is descriptive only).
4. Current-exposure secondary: ph1 use of the predicted drug ~ G (cross-sectional; never primary).
5. Family D: linear (log1p frequency per day) or logistic (binary) on ph1, ph2 replication.

## Covariates (D08)
Primary: age, sex, cohort type, follow-up years, BMI, smoking, alcohol, education, hypertension, diabetes, dyslipidemia. Minimal (S08): age, sex, cohort type, follow-up years. Optional covariates absent from the delivery are dropped and logged. Genome-wide ancestry PCs are not available (candidate-region SNPs only); population structure is addressed by the single-prefecture cohort, family-clustered SE and the negative controls. SE clustered by family ID if delivered, else HC1.
Lifestyle variables are confounders, never outcomes, except in Family D. Laboratory/physiological variables serve confounding control and characterization only; no laboratory phenome scan.

## Testability floors (D12)
≥200 exposed and ≥20 events and ≥20 non-events; otherwise PRE-SPECIFIED BUT UNTESTABLE.

## Interpretation (legacy 85)
Pattern A–E assigned by rule: Family A verdicts → Family E gradient → controls → EX ordering. Level-5 causal claims prohibited in all patterns.

## Sensitivity (`analysis_config.yaml::sensitivity`)
S03 A49P only; S04 age ≥40; S07 carrier coding; S08 minimal adjustment; S09 E-value; S10 multiple imputation (20); S11 all medications incl. OTC; S12 any dose difference; S12b ±50%; S13 exclude unknown-ID rows; S14 exclude combination products; S15 addition among ph1 users only.

## Not in the plan
GWAS (confirmatory or otherwise unless genome-wide data are delivered, authorized and an exploratory amendment is filed after confirmatory results are locked); claims outcomes; external validation; survival analysis (two time points only); metabolomics; tolerance/adverse-event models. All → `24`.
