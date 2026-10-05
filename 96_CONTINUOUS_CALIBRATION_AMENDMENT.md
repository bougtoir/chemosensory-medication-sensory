# 96 — Continuous calibration amendment

Status: **FINAL PRE-OUTCOME AMENDMENT** (class 3 analytic, pre-result).

## Change
The binary SUPPORTED/NOT SUPPORTED calibration in `81` is demoted to
secondary; a continuous directional calibration becomes PRIMARY within
the calibration family (F-CALIBRATION, `82`).

## Frozen specification
1. Directional harmonization: every testable directional prediction has a
   pre-frozen expected sign s_i ∈ {+1,−1} from `13_v2_FINAL`. After the
   analysis, observed effects are oriented so positive = in predicted
   direction. Signs are never re-oriented after seeing data.
2. Primary quantity: signed standardized effect
   `Z_i = s_i × β_i / SE(β_i)`.
3. Primary test: **Spearman ρ** between the frozen evidence_score rank and
   Z_i; permutation null, **≥10,000 permutations**, seed 42, two-sided.
4. Secondary: weighted regression of signed effect on score; rank
   correlation on signed raw β (where scales comparable); the original
   binary calibration.
5. Negative controls: separate diagnostic display, expected near zero —
   not part of the ρ computation.
6. Anti-precision artefact: report both Z_i and signed raw β_i; assess
   whether calibration persists after accounting for precision/N. A ρ
   driven only by larger-N predictions is explicitly not success.
7. UNDEFINED predictions are excluded and reported; they are not zeros.

## Files updated
`81` (protocol rewritten), `82` (F-CALIBRATION row), `83` (execution
order), `85`, `86` (convergence criterion 2).
