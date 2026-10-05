# 98 — Final opening decision (v2, supersedes `89`)

Status: **FINAL**. Issued after pre-opening amendments 91/92/95/96.

## Decision: **OPEN PRIMARY DATA WITH RESTRICTIONS**

## Ten-criterion checklist (open-data criteria)

| # | Criterion | State | Evidence |
|---|---|---|---|
| 1 | P01/P10 hierarchy unambiguous | PASS | `91`; collapse/rescue language removed from `72`, `74`, `76`, `87` |
| 2 | Real ToMMo-string parser validation meets thresholds | **NOT YET EXECUTED — binding restriction** | `92`: real strings require authorized data access; frozen gate before any association run |
| 3 | Primary genotypes implementable | CONDITIONAL | `63`: TAS2R38 haplotype + rs10772420/rs11988795/rs12033832 ready; rs3741845 via proxy rule; TAS2R4 UNRESOLVED → P10 genotype-dependent leg may be UNTESTABLE |
| 4 | Adequate genotype-blind exposure counts | CONDITIONAL | `73` floors set; counts themselves are a permitted QC at access time |
| 5 | Mechanistic-gradient model frozen | PASS | `95` (1-df G×E test + categorical + order-restricted) |
| 6 | Continuous calibration model frozen | PASS | `96` (signed Z_i, Spearman ρ, ≥10,000 permutations, seed 42) |
| 7 | Negative controls pre-specified | PASS | `79` |
| 8 | Indication-confounding strategy frozen | PASS | `76`, `77` |
| 9 | Multiple-testing hierarchy frozen | PASS | `82` incl. F-GRADIENT, F-CALIBRATION |
| 10 | No unresolved analytical choice | PASS except #2/#3 gates | — |

## Binding restrictions (unchanged + amendment additions)
1. **Real-string parser gate (`92`)**: sample 300–500 unique genotype-blind
   medication strings, adjudicate, re-validate parser v1.0.0 against the
   frozen thresholds. Any unmet threshold → parser revision, re-validation
   on a fresh sample, and primary analysis stays CLOSED until it passes.
2. Variant availability + observability floors per `89` restrictions 1–2.
3. P01/P10 separation per `91`.
4. Denominator reporting: frozen / testable / untestable / evaluated
   counts must appear in all result summaries.
5. Instrument, claims-level, and authorization limits per `89`/`87`.
6. Isolated significant associations are never framed as proof of the
   general framework (`85`, `86` convergence criteria).

## Sign-off
Amendments strengthened pre-specification without touching outcomes.
No genotype–medication association has been estimated. Primary data may
be opened under the stated restrictions; the real-string parser gate and
variant-availability check execute first, still genotype-blind.
