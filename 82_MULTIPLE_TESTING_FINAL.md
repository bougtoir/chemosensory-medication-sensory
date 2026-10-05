# 82 — Multiple testing final freeze

Status: **FINAL FREEZE**.

## Testing families (fixed structure)

| Family | Contents | Error control | α |
|---|---|---|---|
| F-PRIMARY | P01, P02, P05, P10 (biological-primary subset per `62`) | Holm | 0.05 |
| F-SECONDARY | remaining directional predictions | Benjamini–Hochberg FDR | q=0.10 |
| F-CONTROL | N01–N12 negative controls | no correction; each read as "expected null" | descriptive |
| F-CONTRAST | C1–C5 formulation/route contrasts | Holm within family | 0.05 |
| F-GRADIENT | genotype × ordinal-exposure 1-df interaction (`95`) — the principal mechanistic test | single test | 0.05 |
| F-CALIBRATION | continuous calibration Spearman ρ (`96`) — principal calibration test | single test | 0.05 |
| F-EXPLORATORY | any S3/pharmacological-sensitivity or unlisted test | reported as exploratory, unadjusted p with explicit label | — |

## Frozen rules
1. Family membership is fixed by `62_PREDICTION_HIERARCHY_FREEZE.csv`; tests
   cannot be moved between families after opening.
2. A test that is UNDEFINED (unobservable/underpowered) is removed from the
   denominator BEFORE correction and listed; it is not counted as a
   rejection or a failure.
3. The mechanistic-ordering comparison (EX-class gradient, `80`) is a
   secondary descriptive claim — no additional inferential multiplicity.
4. The continuous calibration test (`96`) is the single test in
   F-CALIBRATION; the older binary supported/not-supported calibration is
   secondary within it (no extra multiplicity).
5. Sub-group/sensitivity runs in `84` never generate new families; they are
   reported as robustness checks with the same adjusted references.
6. No interim looks: all tests run once, on the finalized analysis set.
