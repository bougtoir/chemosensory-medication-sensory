# 95 — Formal mechanistic-gradient amendment

Status: **FINAL PRE-OUTCOME AMENDMENT** (class 3 analytic, pre-result).

## Change
The EX0→EX3 exposure ordering in `80` is promoted from a descriptive
pattern to a formal primary statistical test.

## Frozen specification
- Exposure score: `E ∈ {0,1,2,3}` = EX0–EX3 (`67`); higher = more direct
  oral chemosensory contact. Inhaled/intranasal excluded (per `67`).
- Primary model: `logit[P(Y=1)] = β0 + β1·G + β2·E + β3·G×E + covariates`
  (age, sex, wave, ancestry PCs; indication proxy where the DAG requires).
- H1: β3 has the pre-specified sign (genotype effect increasing with E).
  H0: β3 = 0. **1-degree-of-freedom interaction/trend test.** Report β3,
  95% CI, p. Individual stratum significance is never the primary claim.
- Secondary categorical: E as factor; genotype effect estimated within
  each EX class.
- Secondary order-restricted sensitivity: |β_EX3| ≥ |β_EX2| ≥ |β_EX1| ≥
  |β_EX0| under the frozen direction — the order is committed here and
  may not be re-derived from observed estimates.

## Multiplicity
The 1-df interaction is the single test of new family F-GRADIENT
(α=0.05, `82`). It is the principal mechanistic test.

## Interpretation binding (`85`)
- Strong mechanistic support = directionally consistent G×E interaction
  AND broadly compatible categorical ordering.
- A significant drug-specific genotype association WITHOUT the gradient
  is not evidence for the general chemosensory mechanism.

## Files updated
`80`, `83` (§4-G), `82` (F-GRADIENT row), `85` (pattern A + rule 1b),
`87` (authorization row).
