# 67 — Oral sensory exposure classification freeze

Status: **FINAL FREEZE**. Defines how each parsed medication exposure is
assigned an orosensory contact class. Genotype-blind; depends only on the
medication label text.

## Classes (frozen)

| Class | Name | Formulations | Mechanistic meaning |
|---|---|---|---|
| EX3 | Direct / sustained orosensory contact | syrup, suspension, oral solution, dry syrup (reconstituted), powder, fine granules, granules, chewable tablet, lozenge | active ingredient dissolves in the oral cavity; taste/irritation unavoidable before swallowing |
| EX2 | Transient orosensory contact | OD (orally disintegrating) tablet, tablet of unspecified coating, sublingual/buccal | brief mucosal contact; coating status indeterminate for unspecified tablets |
| EX1 | Masked contact | film-coated tablet, sugar-coated tablet, capsule, enteric-coated tablet, controlled-release tablet | barrier layer or delayed release; minimal taste contact in normal use |
| EX0 | No orosensory contact | injection, transdermal, topical, ophthalmic, rectal | bypasses the oral cavity |
| — | Inhaled/intranasal | inhaler, aerosol, nasal spray | partial oropharyngeal deposition possible; **evaluated separately**, never pooled into EX1–EX3 |

## Frozen rules
1. Assignment derives ONLY from the formulation string produced by the frozen
   parser (`71_MEDICATION_PARSER/medication_parser.py` v1.0.0,
   sha256 `c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de`).
2. EX3 vs EX1 contrasts are the primary formulation-based test of the
   chemosensory pathway (C1–C5 contrasts, `25_FORMULATION_ROUTE_CONTRASTS.csv`).
3. "Unspecified tablet" (錠 with no coating cue) is coded EX2 and is NOT
   reclassifiable post hoc; sensitivity analysis may re-assign it to EX1 as a
   bound check (pre-specified here, `84_SENSITIVITY_FREEZE_FINAL.md`).
4. A medication report with `formulation = unknown` carries
   `oral_sensory_exposure = null` and is excluded from exposure-class analyses
   (never imputed).
5. Exposure is defined per (participant, wave, medication-row). Cross-wave
   transitions use the terminology frozen in `78_OUTCOME_TERMINOLOGY_FREEZE.md`.
6. Chewing/crushing behaviour is not observable and is not assumed; analyses
   assume label-directed use.

## Boundary notes
- Dry syrup (ドライシロップ) → EX3 (reconstituted before administration).
- Enteric coating exists specifically to delay release past the mouth/stomach
  interface → EX1, not EX2.
- Combination products take the formulation of the reported dosage form.
