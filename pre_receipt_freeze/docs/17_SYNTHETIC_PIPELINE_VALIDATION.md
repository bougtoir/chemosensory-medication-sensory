# 17 — Synthetic pipeline validation

No participant-level ToMMo data were used. Synthetic data mimic the delivered structure (PH1/PH2 lifestyle with 45 medication slots, Drug ID, KEDD ID, free text, duration, frequency, dose; FFQ; laboratory; physiological; demographics; cohort profile; SNP genotypes + manifest; Drug ID/KEDD masters).

## Reproduce
```
python3 pre_receipt_freeze/tools/run_synthetic_validation.py     # generate, run twice, compare
python3 -m pytest pre_receipt_freeze/offline_pipeline/tests -q   # unit + end-to-end tests
```
Outputs: `synthetic_validation/export/` (privacy-safe export), `fixed_case_endpoints.csv`, `RUN_LEDGER.json` (input hashes, export hashes of two fresh-process runs, determinism flag).

## Fixed edge cases
| Case | Scenario | Expected |
|---|---|---|
| S00001 | same ingredient, different brand | no change |
| S00002 | dose increase | STANDARDIZED_DOSE_INCREASE = 1 |
| S00003 | within-class switch | ACTIVE_INGREDIENT_CHANGE = 1, WITHIN_CLASS_SWITCH = 1 |
| S00004 | addition | MEDICATION_ADDITION = 1 |
| S00005 | removal | MEDICATION_REMOVAL = 1 |
| S00006 | duplicate rows | collapsed to one ingredient |
| S00007 | combination → mono product | combination expanded per ingredient |
| S00008 | incompatible dose units | dose endpoints undefined |
| S00009 | missing phase | excluded from analysis set |
| S00010 | unknown Drug ID, usable free text | resolved by parser fallback, flagged |
| S00011 | unknown KEDD ID, no usable text | unresolved, counted |
| S00012 | Drug ID at ph1, KEDD only at ph2 | same ingredient resolved |
Plus SNP cases: Level-A direct, proxy, HWE failure, out-of-universe amendment-only variants.

## Results
| Family | Frozen | Tested | Untestable | Rejected |
|---|---|---|---|---|
| A | <10 | <10 | <10 | 0 |
| AS | <10 | <10 | <10 | 0 |
| B | <10 | <10 | 0 | 0 |
| C | 21 | 18 | <10 | 0 |
| C2 | 15 | 15 | 0 | 0 |
| D | 16 | 16 | 0 | <10 |
| E | <10 | <10 | <10 | 0 |
| F | 12 | <10 | 11 | 0 |

Two fresh-process runs produced identical export hashes: True. participant_level_tommo_data_used = False.

Fixed-case endpoints (blank = not in risk set / undefined; S00009 absent = excluded):

| Case | ANY_MED_CHANGE | ACTIVE_INGREDIENT_CHANGE | WITHIN_CLASS_SWITCH | MED_ADDITION | MED_REMOVAL | STD_DOSE_INCREASE | STD_DOSE_DECREASE |
|---|---|---|---|---|---|---|---|
| S00001 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| S00002 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| S00003 | 1 | 1 | 1 | 1 | 1 |  |  |
| S00004 | 1 |  |  | 1 |  |  |  |
| S00005 | 1 |  |  | 0 | 1 |  |  |
| S00006 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| S00007 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| S00008 | 0 | 0 | 0 | 0 | 0 |  |  |
| S00010 | 0 | 0 | 0 | 0 | 0 |  |  |
| S00011 |  |  |  | 0 |  |  |  |
| S00012 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Test suite
`tests/test_pipeline.py`: 33 passed in 131.79s (0:02:11). Covers all cases above, dose boundaries, structured-ID precedence, SNP QC/proxy/allele orientation (TAS2R38 forward-strand G/G/C), EM PAV inference, small-cell suppression, interpretation patterns, family denominators, N11 status, real-mode refusal without sign-off, no hard-coded delivered column names, parser/ATC hash guards, parser vocabulary, deterministic rerun.

Synthetic results have no scientific meaning; they show that every module runs end to end and that untestable tests are reported, not dropped.
