# 80 — Mechanistic gradient (final freeze)

Status: **FINAL FREEZE**. The ordered predictions implied by the causal
chain genotype → (latent) sensory phenotype → observed exposure behavior.

## Ordered gradient (must hold jointly for the sensory interpretation)

| Level | Statement | Operationalization | Required direction |
|---|---|---|---|
| G1 | receptor function differs by genotype | literature annotation (documented in `11_VARIANT_FUNCTION_MATRIX`) | — |
| S1 | perception differs | **UNMEASURED** — inferential only | — |
| G→E | exposure presence differs by genotype | per-prediction exposure indicator | direction frozen in `13_v2_FINAL` |
| G→F | formulation class differs within drug | EX3 vs EX1 strata | masked forms favored by perception-susceptible carriers |
| G→T | cross-wave transition/discordance differs | onset/offset + formulation discordance | same direction as G→E |
| Gradient | effect magnitude ordered EX3 > EX2 > EX1 > EX0 | effect-size ordering across classes | monotone |
| Control | receptor-matched > receptor-mismatched | directional vs N07–N10 | matched exceeds mismatched |

## Formal primary ordered test (Amendment 3, `95`)

The exposure gradient is now a FORMAL test, not only a descriptive ordering.

- Exposure score: E = 0,1,2,3 for EX0–EX3 (supported by the frozen class
  definitions in `67`; inhaled/intranasal excluded as per `67`).
- Primary model (per `83` §4-G):
  `logit[P(Y=1)] = β0 + β1·G + β2·E + β3·G×E + covariates`
- H1: β3 has the pre-specified sign (effect increasing with exposure).
  H0: β3 = 0. One-degree-of-freedom trend test; report β3, 95% CI, p.
- Individual stratum significance is NEVER the primary mechanistic claim.
- Secondary categorical model (E as factor): genotype effects within each
  EX class — robustness, not the primary claim.
- Secondary order-restricted sensitivity: |β_EX3| ≥ |β_EX2| ≥ |β_EX1| ≥
  |β_EX0| under the frozen direction; the order is fixed here, never
  chosen after seeing estimates.

## Frozen decision rules
1. The mechanistic reading requires the **joint pattern**: correct direction
   on directional tests AND null/attenuated controls AND the EX-class
   ordering. Any single deviating leg degrades the interpretation per `85`.
1b. A significant drug-specific genotype association WITHOUT the
   exposure gradient must NOT be described as evidence for the general
   chemosensory mechanism.
2. Because S1 is unmeasured, the design cannot reject non-sensory
   pleiotropy by itself; the EX-ordering + controls are the discriminating
   evidence. This limitation is stated verbatim in the manuscript claims.
3. The formal 1-df interaction test above is the ONLY trend test for the
   gradient (prevents post-hoc trend-test shopping); magnitudes are also
   reported as ORs with CIs.
