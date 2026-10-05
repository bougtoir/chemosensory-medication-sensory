# 12 — Continuous calibration (Family G)

Status: FINAL PRE-RECEIPT FREEZE. Legacy 81/96. Module 17.

- For each locked prediction i that is in the approved scope and TESTED (not untestable): Z_i = s_i × β_i / SE(β_i), where s_i is the frozen sign (`analysis_config.yaml::prediction_sign`) and β_i the Family A/AS estimate.
- Statistic: Spearman ρ between frozen evidence score and Z_i.
- Inference: one-sided permutation p (ρ > 0), 10,000 permutations, seed 42.
- Minimum evaluable count (D07): ≥5 tested predictions; otherwise status `UNDEFINED (evaluable predictions below minimum)` (reported, no inference). Predictions outside the approved scope (P06, P09, P10, P11) never enter.
- Single test, α = 0.05. Calibration speaks to the evidence-weighting framework, not to any single prediction.
