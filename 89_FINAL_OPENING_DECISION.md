# 89 — Final pre-opening decision

Status: **FINAL**. The decision state before any genotype-associated ToMMo
result is inspected.

## Decision: **OPEN WITH RESTRICTIONS**

Neither fully open (unverified pre-conditions remain) nor DO NOT OPEN
(the dry-evidence case is strong enough to proceed under restriction).

## Twelve-criterion checklist

| # | Criterion | State | Evidence |
|---|---|---|---|
| 1 | Hypothesis independently derived & frozen | PASS | `01`, `13_v2_FINAL` (sha256 in `60`) |
| 2 | Predictions locked, directional, falsifiable | PASS | `13_v2_FINAL`, `62` (24 rows incl. controls) |
| 3 | Scoring rubric fixed before outcomes seen | PASS | `21`, `24` |
| 4 | Negative controls pre-specified | PASS | `26`, `79` |
| 5 | Genotype implementation & haplotype locked | PASS | `63`, `64`, `65`; TAS2R4 flagged UNRESOLVED |
| 6 | Medication parsing validated genotype-blind | PASS | `69`: all thresholds exceeded on 146-string corpus |
| 7 | Exposure/formulation/masking classes frozen | PASS | `66`–`68` |
| 8 | Outcome construct & wave structure resolved | PASS | `74`, `78` |
| 9 | Confounding structure documented | PASS | `76`, `77` |
| 10 | Statistical plan & multiplicity frozen | PASS | `82`, `83`, `84` |
| 11 | Interpretation committed pre-result | PASS | `80`, `85` |
| 12 | Sufficient assumed power for primary tests | CONDITIONAL | `73`: adequate ≥1% prevalence; rare×rare marginal |

## Restrictions (binding at open)
1. **Variant availability gate**: confirm the rsIDs/haplotype tags in `63`
   exist in the dbTMM variable catalog BEFORE any association run;
   absent variants fall back per `64`/`65` or the prediction is marked
   PRE-SPECIFIED BUT UNTESTABLE — never silently substituted.
2. **Observability gate**: predictions marked UNTESTABLE in `72`
   (P03, P06, P11, N02, N03, N09, N10) are not executed; CONDITIONAL ones
   execute only if the `73` n≥200 floor is met.
3. **Instrument limits**: results describe past-two-week reported exposure
   (`74`, `78`); adherence/persistence claims are prohibited.
4. **Sensory-link is inferential**: no taste-phenotype data exist in this
   cohort; claims capped at Level 4 (`16`, `75`, `85`).
5. **Claims data are optional secondary**: survey-only validity is the
   designed primary (`75`).
6. All authorization states per `87`; any protocol change via `88`.

## Sign-off statement
The dry-evidence package justifies a population-level validation attempt
under the above restrictions. This document is the last thing produced
before any genotype–medication inspection. **STOP condition met: no
association has been or will be estimated in this session.**
