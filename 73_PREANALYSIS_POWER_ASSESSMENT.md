# 73 — Pre-analysis power assessment

Status: **FINAL FREEZE**. Genotype-blind: every input below is an ASSUMPTION
(prevalence, genotype frequency, effect size); nothing observed in ToMMo or
any individual-level dataset was used. Method: analytic Wald approximation,
`scripts/10_power_assessment.py` (seed 42) → `build/power_assessment.csv`.

## Assumptions (frozen as planning priors, not data)
- Effective cohort N ≈ 50,000 (order-of-magnitude for a community biobank
  survey wave; no observed number).
- TAS2R38 PAV-carrier frequency ≈ 0.4; rare-variant scenario 0.10
  (literature-derived East Asian priors, NOT ToMMo counts).
- Exposure prevalence grid: 5% (common), 1% (uncommon), 0.5% (rare).
- Effect sizes: OR 1.15 / 1.30 / 1.50 on any-exposure or
  formulation-transition outcomes.

## Results (two-sided α = 0.05)

| Scenario | Expected exposed n | Power | Verdict |
|---|---|---|---|
| Common drug (5%), common variant, OR 1.30 | 2,500 | 1.000 | ADEQUATE |
| Common drug, common variant, OR 1.15 | 2,500 | 0.928 | ADEQUATE |
| Uncommon drug (1%), common variant, OR 1.30 | 500 | 0.852 | ADEQUATE |
| Uncommon drug, OR 1.50 | 500 | 0.998 | ADEQUATE |
| Rare drug (0.5%), common variant, OR 1.50 | 250 | 0.923 | ADEQUATE |
| Rare drug, **rare variant (10%)**, OR 1.50 | 250 | 0.502 | MARGINAL |
| Common drug, rare variant, OR 1.50 | 2,500 | 1.000 | ADEQUATE |
| EX3-class aggregate (10%), common variant, OR 1.20 | 5,000 | 1.000 | ADEQUATE |
| Within-drug formulation contrast (2%), OR 1.40 | 1,000 | 1.000 | ADEQUATE |

## Frozen interpretation rules
1. Power is adequate for single-variant tests whenever the exposure has
   ≥1% prevalence and the variant is common — this covers P01, P02, P04,
   P07, P10, P12, C1, C4.
2. Rare-drug × rare-variant cells (P05 if proxy unavailable, P10 standalone,
   N11-like cells) are MARGINAL at best → such tests are declared
   **underpowered a priori**; a null there is reported as uninformative,
   never as falsification.
3. An outcome with expected exposed-n < 200 is DO NOT OPEN for association
   testing (cell-size and power floor); it may still be used descriptively.
4. This assessment fixes the analysis plan (logistic/ordinal models,
   α=0.05, multiplicity per `82_MULTIPLE_TESTING_FINAL.md`); it does not
   constrain which predictions are opened — that is decided by `72` and `89`.
