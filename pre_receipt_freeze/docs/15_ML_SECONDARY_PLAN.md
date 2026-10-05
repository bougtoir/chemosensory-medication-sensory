# 15 — Machine-learning secondary plan (Family H)

Status: FINAL PRE-RECEIPT FREEZE. Secondary only; never replaces prespecified genetic tests. Module 18.

- Endpoint: ANY_MEDICATION_CHANGE.
- Models: elastic-net logistic; gradient boosting.
- Feature sets: clinical (primary covariates + n_rx_ph1) vs clinical + Level-A genotypes.
- Nested cross-validation: 5 outer × 3 inner folds, seed 42; preprocessing and imputation fitted inside folds (multiple imputation 20 for S10 only).
- Outputs: AUC, ΔAUC (clinical+genotype − clinical) with 2,000-bootstrap 95% CI, calibration slope/intercept.
- Feature importance/SHAP are descriptive; no causal interpretation.
