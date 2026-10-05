# 06 — Longitudinal medication-change endpoint freeze

Status: FINAL PRE-RECEIPT FREEZE. Implemented in `offline_pipeline/chemotommo/_common.py::compute_endpoints` and `08_cross_wave_medication_change.py`; verified on synthetic cases in `17`.

## Primary phenotype
The primary medication phenotype is LONGITUDINAL MEDICATION CHANGE between phase 1 and phase 2, as defined in the approved plan (dose change, medication change, switch, addition, deletion). Current/recent medication exposure is a secondary cross-sectional analysis only (AMENDMENT_LOG AM01 supersedes the legacy ordering in 34/83).

## Unit of analysis and risk set
- Population: participants with the medication section answered at both waves (medication-any item non-missing at ph1 and ph2), age ≥20 at ph1, ≥1 Level-A variant passing QC (D16). Missing phase → excluded, never imputed as "no medication".
- Scope: prescription rows (rx flag) with a resolved active ingredient (D17). OTC/supplement rows enter only S11 and control N12.
- Ingredient set per wave: union of active ingredients after combination products are expanded (`05`) and duplicate rows of the same ingredient are summed (`07`).

## Endpoint algorithms (participant level)
Let I1, I2 be the ph1/ph2 ingredient sets; A = I2 \ I1 (added), R = I1 \ I2 (removed), S = I1 ∩ I2 (shared); class(i) = ATC level-4 set of ingredient i from the frozen KEGG snapshot (`08`); r_i = standardized daily dose ratio ph2/ph1 for i ∈ S when both doses share a harmonized basis (`07`).

| Endpoint | Y = 1 | Y = 0 | Missing (not in risk set) |
|---|---|---|---|
| MEDICATION_ADDITION | A ≠ ∅ | A = ∅ | never (all both-wave participants) |
| MEDICATION_REMOVAL | R ≠ ∅ | R = ∅ | I1 = ∅ |
| ACTIVE_INGREDIENT_CHANGE | A ≠ ∅ and R ≠ ∅ | otherwise | I1 = ∅ or I2 = ∅ |
| WITHIN_CLASS_SWITCH | ∃ a∈A, r∈R with class(a) ∩ class(r) ≠ ∅ | otherwise | I1 = ∅ or I2 = ∅ |
| STANDARDIZED_DOSE_INCREASE | ∃ i∈S with r_i ≥ 1.25 | ≥1 comparable i, none ≥ 1.25 | no comparable shared ingredient |
| STANDARDIZED_DOSE_DECREASE | ∃ i∈S with r_i ≤ 0.80 | ≥1 comparable i, none ≤ 0.80 | no comparable shared ingredient |
| ANY_MEDICATION_CHANGE | A ≠ ∅ or R ≠ ∅ or any r_i ≥ 1.25 or ≤ 0.80 | none of these | I1 = ∅ and I2 = ∅ |

Brand change with the same active ingredient and comparable dose is NOT a change. Frequency change enters only through the standardized daily dose. Formulation change of the same ingredient is not an endpoint; it is used by the formulation module (`11`).

## Drug-specific endpoint (Families A, AS, F)
DRUG_SPECIFIC_CHANGE_AWAY for drug set d: risk set = participants with ≥1 ph1 row matching d; Y = 1 if a matching ph1 ingredient has no matching row at ph2 (removal, switch-out, or formulation-out for formulation-defined sets) or its daily dose ratio ≤ 0.80; else 0 (D03).

## Terminology (neutral, data-derived)
Allowed: addition, removal, active-ingredient change, within-class switch, standardized dose increase/decrease, change-away. Prohibited: "discontinuation due to intolerance", "switch due to taste", adherence, persistence, non-compliance, intent (legacy 78). The two-week questionnaire does not establish adherence, persistence, discontinuation intent, taste-driven switching, medication response or intervention effects.

## Rule
These definitions were fixed with synthetic examples before receipt. They may not be changed after real outcome frequencies are seen.
