# 13 — Multiple-testing hierarchy (final)

Status: FINAL PRE-RECEIPT FREEZE. Config `analysis_config.yaml::families`. Legacy 82 families mapped as recorded in AMENDMENT_LOG AM10.

| Family | Content | Correction | Status |
|---|---|---|---|
| A | P01, P02, P05 (legacy F-PRIMARY per 62; P10 excluded, AM04) | Holm, α = 0.05 | confirmatory |
| AS | P03, P04, P07, P08, P12 | BH, q = 0.10 | confirmatory-secondary (legacy F-SECONDARY) |
| C | 3 Level-A variants × 7 longitudinal endpoints (21 tests) | Holm, α = 0.05 | confirmatory-secondary |
| C2 | 3 Level-A variants × 5 revised-plan categories, ANY change within category users (15 tests) | BH q = 0.05; Holm α = 0.05 confirmatory if D01 switch exercised | secondary |
| B | Level-B: every QC-passing delivered SNP in the 20-gene regions × ANY_MEDICATION_CHANGE | BH, q = 0.05 | secondary, gene-constrained |
| D | FFQ F01–F08, ph1 primary (ph2 replication reported) | BH, q = 0.05 | secondary triangulation |
| E | GR1 + C1–C4 (C5 reported) | Holm, α = 0.05 | conditional confirmatory |
| F | N01–N10, N12 | none; failure rule `10` | negative control |
| G | calibration ρ | single test, α = 0.05 | confirmatory calibration |
| H | ML | no p-values; ΔAUC with bootstrap CI | secondary |
| X | anything else | unadjusted, labelled exploratory | exploratory |

Rules: no test moves between families after receipt; untestable tests are removed from the family denominator and reported with reasons (family denominators exported in `20_family_denominators.csv`); a novel Level-B SNP cannot be promoted to confirmatory; no hierarchical gatekeeping between families.
