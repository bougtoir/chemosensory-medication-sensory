# 36 — Gate Decision

## Verdict: **CONDITIONAL GO TO PRIMARY VALIDATION**

## Phase-J checklist

| Criterion | Status |
|---|---|
| 8–10+ high-quality directional predictions | **Met** — 12 directional; 8 with evidence_score ≥ 9 (P01–P07, P09, P12) |
| Several feasible negative controls | **Met** — 12 controls across 4 classes (route, masking, mismatch, adherence) |
| ≥1 feasible formulation/route contrast | **Partially met** — contrasts exist but rely on brand-name parsing proxy (not yet demonstrated) |
| Predictions independently derived from public evidence | **Met** — BitterDB + PubMed only |
| ToMMo can test without post hoc reinterpretation | **Partially met** — outcomes are cross-wave exposure transitions & formulation patterns via free-text product names; proxy parse must be validated |
| Confounding meaningfully addressable | **Partially met** — indication/adherence residual risk (33_ALTERNATIVE_EXPLANATION_AUDIT) |
| Population calibration / ordered-gradient test feasible | **Met in principle** — frozen plan in 32 |

## What must be confirmed BEFORE opening data

1. **Genotype coverage:** rs713598 (TAS2R38), rs10772420 (TAS2R19),
   rs11988795 (TRPA1), rs12033832 (TAS1R2) and the TAS2R9 V187A variant
   present in the dbTMM variable catalog — public catalog check only.
2. **Parse feasibility:** demonstrate on a small, documented sample that
   the free-text medication field separates formulation types (錠 vs
   細粒/シロップ/OD錠/貼付剤) with reliable precision — required for
   the ordered-gradient test.
3. **Outcome resolution:** cross-wave medication discordance is
   constructible for at least the primary predictions (P01/P02/P05
   exposure classes present at ≥ minimal prevalence).

If (2) or (3) fails → **DO NOT OPEN PRIMARY DATA** for the affected
prediction class; genotype×current-use main-effect mining alone is not
a permitted fallback.

## Claim ceiling at this stage

Level 4 is the validation target; Level 5 explicitly not required.
Nature-route assessment: `35_NATURE_ROUTE_ASSESSMENT.md`.

## Files frozen by this gate

- `13_LOCKED_PREDICTIONS_v2_FINAL.csv` — immutable
- `34_PRIMARY_VALIDATION_FREEZE.md` — immutable except amendment log
- `32_PREDICTION_CALIBRATION_PLAN.md` — metric fixed pre-validation

STOP here. No ToMMo individual-level data was accessed; no genotype–
medication association was estimated.
