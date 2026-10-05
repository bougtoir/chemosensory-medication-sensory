# 81 — Calibration final lock

Status: **FINAL FREEZE**. Whether the ordered evidence scores predict
observed support across the prediction panel.

## Frozen protocol (amended — continuous calibration is PRIMARY, `96`)
1. Unit of calibration = the 12 directional predictions (P01–P12) plus the
   5 formulation contrasts; controls are excluded from the correlation and
   shown in a separate diagnostic display (expected near zero).
2. Predictor = frozen `evidence_score` (rubric `21`, values in
   `13_LOCKED_PREDICTIONS_v2_FINAL.csv`).
3. Outcome per prediction = **signed standardized effect**
   `Z_i = s_i × β_i / SE(β_i)`, where s_i = ±1 orients the observed effect
   to the pre-frozen predicted direction (positive = as predicted). The
   sign s_i is fixed by `13_v2_FINAL`, never reoriented after data.
   UNDEFINED predictions are excluded and reported separately.
4. **Primary test: Spearman ρ** between evidence_score rank and Z_i;
   permutation null with **≥10,000 permutations**, seed 42, two-sided.
5. **Secondary**: weighted regression of signed effect on score;
   rank correlation on signed raw β where scales are comparable; the
   former binary SUPPORTED/NOT SUPPORTED calibration.
6. **Anti-precision artefact rule**: report BOTH signed Z_i and signed raw
   β_i, and assess whether the correlation persists after accounting for
   precision/sample size — a calibration driven only by N is not success.
7. Calibration is run ONCE after all family tests are closed. No score
   recalibration from observed results — scores stay frozen; a low ρ is a
   finding about the evidence framework, not a license to rescore.
8. Reported: ρ, permutation p, regression slope + CI, per-tier support
   rates (≥12 / 9–11 / ≤8), and the negative-control diagnostic cloud.
