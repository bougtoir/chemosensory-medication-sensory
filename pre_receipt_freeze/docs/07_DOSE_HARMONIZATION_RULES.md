# 07 — Dose harmonization rules

Status: FINAL PRE-RECEIPT FREEZE. Implemented in `_common.py::harmonize_dose` and `07_dose_harmonization.py`; tests `test_dose_harmonization`, `test_dose_thresholds_boundary`.

## Derived quantities
- dose_per_administration = amount × unit factor (mass units → mg).
- administrations_per_day = frequency ÷ frequency-unit days (日=1, 週=7, 月=30; 回/日 forms normalized).
- estimated_daily_dose = dose_per_administration × administrations_per_day.
- Primary dose quantity: standardized daily dose ratio ph2/ph1 per shared ingredient.

## Unit rules
1. Mass units (g, mg, µg/μg/mcg, ng) convert to mg.
2. Count units (錠, カプセル, 包, 本, 枚, 個, 滴, 回分 …) convert to mg only if the Drug ID/KEDD master gives strength_mg per unit for that ingredient; otherwise the basis is `count:<unit>` and is comparable only with the same count unit at the other wave.
3. Volume units (mL, L) have basis `volume:mL` and are comparable only with volume at the other wave (no concentration is assumed).
4. Unknown, free-form or incompatible units (e.g., 適量, missing unit, missing frequency) → no daily dose; the ingredient is not dose-comparable. Nothing is imputed.
5. Combination products: a mass amount entered for a multi-ingredient product cannot be attributed to an ingredient → no daily dose unless the master gives per-ingredient strengths for count units.
6. Duplicate rows of one ingredient within a wave are summed only if all rows share one non-null basis; otherwise the ingredient's daily dose is missing.
7. No conversion across incompatible formulations or bases (e.g., mg vs count, oral vs injection).

## Thresholds (D11)
Increase: ratio ≥ 1.25. Decrease: ratio ≤ 0.80 (the reciprocal of 1.25). Sensitivity: any difference (S12) and ±50% (S12b). Dose ratio as a continuous outcome (log ratio, linear model, robust SE) is secondary (`14`).

## Rule
Unit factor tables may receive dictionary additions only as technical amendments (`24`), never to change which participants count as changed after outcome inspection.
