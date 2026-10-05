# 34 — Primary Validation Freeze (WRITE ONLY — DO NOT EXECUTE)

Applies only to predictions marked TESTABLE WITH PROXY or FULLY TESTABLE
in `31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv`. Primary tier:
P01, P02, P05 (highest scores); all testable primaries analyzed under one
multiple-testing family.

## Population

ToMMo community-based cohort participants with genotype data and
wave-1/2 questionnaire medication sections. Exclusions and the
sub-cohort definition are fixed at data-access time and logged.

## Per-prediction specification (template)

- **Exposure:** current use (past-2-weeks item) of the predicted drug /
  formulation class, parsed from free-text product names; parse rules
  frozen in a codebook BEFORE parsing (brand→generic/formulation map
  versioned).
- **Outcome:** cross-wave exposure transition or current-use
  formulation pattern matching the prediction's `behavioral_prediction`.
- **Genotype coding:** PAV/AVI diplotype for TAS2R38 (rs713598 etc.);
  V187A genotype for TAS2R9; effect-allele counts otherwise.
- **Model:** `Outcome ~ β0 + β1 Genotype + β2 ExposureProperty +
  β3 Genotype×ExposureProperty + covariates` (logistic/ordinal as the
  outcome dictates). **β3 is the primary estimand**; main effects alone
  do not count as confirmation.
- **Covariates:** age, sex, ancestry PCs, indication (disease-history
  fields), smoking, alcohol, coffee/tea intake, SES proxies.
  Mediators (sensory phenotype proxies) are NOT adjusted.
- **Multiple testing:** one family = primary predictions only
  (FDR q<0.05); secondary predictions reported as secondary.
- **Effect measure:** OR/β with 95% CI; sensory directions never pooled
  across phenotypes.
- **Expected direction:** exactly the `predicted_direction` column.
- **Negative control paired:** per the `negative_control` column.
- **Falsifying result:** per `falsifying_result` column.

## STOP conditions

- Any positive signal on route negative controls (N01–N04) → treat the
  panel as confounded; halt interpretation.
- If brand-name parsing cannot distinguish formulation for ≥half of
  testable predictions → downgrade gate to DO NOT OPEN for formulation
  contrasts.
- Medication section non-response or coding failure → report as
  feasibility failure, do not substitute vague proxies.

## Amendment rule

This file is immutable after data opening; changes only via a formal
amendment log appended here.
