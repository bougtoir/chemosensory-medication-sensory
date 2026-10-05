# 04 — Gate history and locks

Status: FINAL PRE-RECEIPT FREEZE. Historical gates are preserved verbatim in the legacy package; this file records their order and present meaning.

| Order | Gate / lock | Source | Decision | Meaning now |
|---|---|---|---|---|
| 1 | Theory and dry evidence synthesis | 03–12 | evidence graph, receptor–drug matrix | historical input |
| 2 | Prediction freeze v2 | 13_LOCKED_PREDICTIONS_v2_FINAL.csv | P01–P12, N01–N12 locked; evidence scores P01=15 … P12=10 | retained; regenerated exactly (DRY_REPRODUCTION_AUDIT) |
| 3 | Gate decision | 36_GATE_DECISION.md | CONDITIONAL GO TO PRIMARY VALIDATION | historical |
| 4 | Pre-opening lock 60–90 | 60–90 | 89: OPEN WITH RESTRICTIONS | superseded by 98 |
| 5 | Pre-opening amendments | 91, 92, 95, 96 | P01/P10 separation; real-string parser QC gate; formal 1-df gradient; continuous calibration | retained |
| 6 | Final opening decision v2 | 98_FINAL_OPENING_DECISION_V2.md | OPEN PRIMARY DATA WITH RESTRICTIONS | historical gate decision only |
| 7 | Protocol/distribution/freeze reconciliation | ../../PROTOCOL_DISTRIBUTION_FREEZE_RECONCILIATION.md | 118 items classified | governs carry-forward |
| 8 | Dry reproduction audit | ../../DRY_REPRODUCTION_AUDIT.md | predictions, scores, controls regenerated without participant data | retained |
| 9 | Final pre-receipt freeze | this package | see 29 | pending independent timestamp |

## Binding interpretation of the historical OPEN decision
`OPEN PRIMARY DATA WITH RESTRICTIONS` (98) is a historical gate decision of the legacy session. It does NOT authorize participant-level analysis in this session. The binding order is:

old freeze → protocol/data reconciliation → final pre-receipt freeze → independent timestamp → ToMMo data receipt → offline validation.

Participant-level analysis requires, in addition, the receipt log (`23`), the genotype-blind QC stage, the analysis-set lock and `receipt/RECEIPT_SIGNOFF.json` (enforced by `offline_pipeline/run_pipeline.py --mode real`).

The reconciliation (order 7) was completed and committed before any new pre-receipt analytic decision (D-series in `DECISION_LOG.md`) was drafted.

## Locks carried forward
Predictions and evidence scores (13); negative controls (79, labels per AMENDMENT_LOG AM09); hierarchy (62 governs; P10 not in Family A, AM04); parser v1.0.0 SHA-256 c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de (70/94); EX0–EX3 (67); formal gradient (95); continuous calibration (96); interpretation matrix (85); amendment classes (88 → `24`).
