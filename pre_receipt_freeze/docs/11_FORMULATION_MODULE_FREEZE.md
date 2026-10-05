# 11 — Formulation / route / oral-sensory module freeze (Family E)

Status: FINAL PRE-RECEIPT FREEZE. CONDITIONAL CONFIRMATORY: executed only if the gates below pass; failure yields `MECHANISTIC GRADIENT NOT TESTABLE` and does not invalidate the primary genotype–medication-change analysis. Module 15.

## Sources of formulation information
Drug ID / KEDD master formulation fields (preferred), then parser v1.0.0 on product text (brand, formulation, release form, route).

## Oral sensory exposure classes (legacy 67)
| Class | Meaning | Formulations |
|---|---|---|
| EX3 | direct/sustained oral contact | syrup/suspension, dry syrup, oral solution, powder, fine granules, granules, chewable tablet, lozenge |
| EX2 | transient | OD tablet, tablet (unspecified coating), sublingual/buccal |
| EX1 | masked | film-coated, sugar-coated, enteric-coated, controlled-release tablet, capsule |
| EX0 | no oral contact | injection, transdermal, topical, ophthalmic, rectal |
| separate | inhaled/intranasal | excluded from EX0–EX3 analyses |

## Gates (all required)
1. Post-receipt genotype-blind real-string QC: 300–500 strings, ≥95% accuracy per field (legacy 92).
2. EX coverage: ≥70% of ph1 prescription rows have an EX class (D14).
3. Testability floors (200 exposed / 20 events) for each test.

## Tests
- GR1 formal gradient (legacy 95; D06): row-level GEE logistic, exchangeable, clustered by participant. Rows = ph1 prescription rows whose ingredient is a human bitter-receptor ligand in the frozen BitterDB extract (`evidence/bitterdb_receptor_ligands.csv`), inhaled excluded. Y = DRUG_SPECIFIC_CHANGE_AWAY at row level (ingredient absent at ph2 or daily dose ratio ≤ 0.80). G = TAS2R38 PAV dosage (0/1/2). E = EX class 0–3 (ordinal). Model: logit P(Y=1) = β0 + β1G + β2E + β3G×E + covariates. Estimand β3; predicted β3 > 0. Categorical-E and order-restricted versions are sensitivity analyses.
- C1–C4 drug-specific contrasts (legacy 25; D05): erythromycin suspension vs enteric/film tablet; paracetamol liquid vs film tablet; theophylline liquid vs controlled-release tablet; potassium chloride liquid vs controlled-release tablet. Each: G×(high vs low formulation) interaction on change-away among ph1 users of that ingredient.
- C5 route null (insulin, parenteral): genotype effect expected absent; reported, not in the Holm set.
- Family E multiplicity: Holm across {GR1, C1, C2, C3, C4}, α = 0.05.

## Historical discrepancy
Legacy 72 lists different C1–C5 labels. They are retained in the legacy package and AMENDMENT_LOG AM05 but not executed.
