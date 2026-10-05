# Final pre-receipt protocol — ToMMo study 2025-0057 (chemosensory genotype and longitudinal medication change)

Status: FINAL PRE-RECEIPT FREEZE (gate `29`). This is the governing index. All pre-receipt instructions of the session are consolidated here, in the decision log (`DECISION_LOG.md`), the amendment log (`AMENDMENT_LOG.md`) and the timestamp package; their chronology and classification are in `INSTRUCTION_REGISTER.csv` and verified by `COMPLETENESS_AUDIT.md`.

| Section | Document |
|---|---|
| Approved protocol scope and version rule | 01 |
| Distribution scope | 02 |
| Theory → protocol map | 03 |
| Gate history and locks | 04 |
| SNP hierarchy | 05 |
| Longitudinal endpoints | 06 |
| Dose harmonization | 07 |
| Drug identification/class | 08 |
| FFQ lock | 09 |
| Negative controls | 10 |
| Formulation module | 11 |
| Calibration | 12 |
| Multiple testing | 13 |
| Confirmatory SAP | 14 |
| ML secondary | 15 |
| Pre/post-receipt boundary | 16 |
| Synthetic validation | 17 |
| Manifest / checksums | 18 / 19 |
| Registration plan / public summary | 20 / 21 |
| Restricted-source hash index | 22 |
| Data receipt log template | 23 |
| Amendment policy | 24 |
| Manuscript architecture / success criteria | 25 / 26 |
| Future intervention / economic models (not tested) | 27 / 28 |
| Final handoff and gate | 29 |

## Core frozen design (summary; documents govern)
- Population: both-wave participants, age ≥20, genotype QC pass.
- Primary: Family A — TAS2R38 PAV (P01 propylthiouracil, P02 thiamazole) and TAS2R9 V187A (P05 ofloxacin) × drug-specific longitudinal change-away; Holm α = 0.05.
- Confirmatory-secondary: Family AS (P03, P04, P07, P08, P12; BH q = 0.10); Family C (3 Level-A variants × 7 longitudinal endpoints; Holm).
- Secondary: C2 five drug categories; B gene-constrained SNPs; D FFQ triangulation; H ML. Conditional confirmatory: E formulation gradient. Controls: F. Calibration: G.
- Structured Drug ID / KEDD ID first; KEGG ATC snapshot hash-guarded; parser v1.0.0 for free text.
- Not assumed: claims, genome-wide data, ancestry PCs, metabolomics; not claimed: adherence, persistence, taste-driven switching, intervention efficacy, immune mediation, economic or global-health benefit.
