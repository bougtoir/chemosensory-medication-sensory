# 32 — Prediction Calibration Plan (FROZEN pre-validation)

The strongest validation is a calibration test, not "some SNPs were
significant".

## Design

- x-axis: **pre-registered predicted sensory effect score** per
  prediction — the `evidence_score` in `13_LOCKED_PREDICTIONS_v2_FINAL.csv`
  (frozen; formula fixed in `21_PREDICTION_SCORING_RUBRIC.md`).
- y-axis: **observed genotype-associated medication-use effect** in the
  future validation — the β3 genotype×exposure interaction estimate per
  prediction (primary estimand; see `34_PRIMARY_VALIDATION_FREEZE.md`).

## Primary calibration hypothesis

Higher predicted sensory effect → larger observed β3 in the predicted
direction.

## Statistics (fixed)

- Rank correlation: Spearman ρ between predicted score and observed
  standardized β3 across predictions; primary test is one-sided
  (direction frozen by the prediction).
- Signed concordance: proportion of predictions whose observed β3 sign
  matches the predicted direction, vs binomial null p=0.5.
- Null framework: permutation of prediction↔observation pairing
  (≥10,000 permutations) — not an asymptotic assumption.
- Uncertainty: bootstrap over predictions (cluster on receptor family
  to respect correlated predictions).
- The calibration metric (Spearman ρ + signed concordance) will NOT be
  chosen or re-specified after seeing results.

## Ordered gradient extension (Phase H)

Where formulation contrasts are testable (25_FORMULATION_ROUTE_CONTRASTS):
ordinal formulation exposure score 0=non-oral, 1=masked oral, 2=unmasked
oral is defensible for the listed pairs only. Trend test = linear-by-
linear association on the ordinal score; key result is the ordered
trend, not per-stratum significance.
