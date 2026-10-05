# 69 — Medication parser blind validation

Status: **FINAL — PASS**. Validation of the frozen parser before any ToMMo
inspection. Fully genotype-blind and participant-data-free: the corpus was
built from public formulary knowledge (standard Japanese brand→generic
mappings and dosage-form suffixes).

## Corpus
- `71_MEDICATION_PARSER/gold_corpus.csv` — **146 unique strings**, hand-adjudicated
  gold labels for active ingredient, formulation, route, oral sensory exposure
  class, taste masking. Corpus spans all exposure classes (EX0–EX3, inhaled,
  ophthalmic, rectal, transdermal), brand and generic spellings, strengths,
  and OTC-style strings.
- No ToMMo participant strings were used (none were accessible or permitted).

## Results (parser v1.0.0, sha256 `c722341a…a99de`)

| Metric | Threshold (frozen, may not be lowered) | Accuracy | 90% CI | Pass? |
|---|---|---|---|---|
| Active ingredient | ≥ 95% | 145/146 = **99.3%** | 0.982–1.004 | YES |
| Route | ≥ 95% | 145/146 = **99.3%** | 0.982–1.004 | YES |
| Formulation | ≥ 90% | 145/146 = **99.3%** | 0.982–1.004 | YES |
| Oral sensory exposure class | ≥ 90% | 145/146 = **99.3%** | 0.982–1.004 | YES |
| Taste masking (informational) | — | 146/146 = 100% | — | — |

## Error analysis (frozen taxonomy)
- 1 residual error: `オオサカ堂 ビタミンC` (non-standard OTC/shop-prefixed
  string; ingredient unresolved) — flagged `manual_review_flag = YES`, which is
  the designed behaviour for unmapped strings.
- Error classes observed during development, now corrected and locked:
  (a) brand-inherent formulation (ユニフィル = CR without suffix);
  (b) strength-suffix absorbing the formulation cue (ガスター10錠);
  (c) unmapped brand names (dictionary extended, not regex-guessed).
- Resolution rule: unmapped strings are ALWAYS routed to manual review, never
  imputed. The manual-review rate in real data is a quantity we are permitted
  to measure genotype-blind.

## Adjudication protocol (frozen for any real-data use)
1. Sample = all unique normalized strings, or a random 200–500 if volume
   exceeds capacity.
2. Two-pass adjudication: parser output vs public formulary (PMDA/添付文書
   conventions); disagreements resolved by formulation label, not by guess.
3. Any systematic error class found in real data triggers parser version bump
   (`88_AMENDMENT_POLICY_FINAL.md`), NOT silent dictionary edits.

## Supplement (Amendment 2)
A SECOND validation on actual ToMMo free-text is required before any
genotype–medication analysis — see `92_TOMMO_REALSTRING_PARSER_VALIDATION.md`
(REQUIRED, deferred: real strings need authorized access). This document is
supplemented, not replaced; its corpus result stands as validation #1.

## Conclusion
Parser meets all frozen acceptance thresholds on the blind corpus →
medication parsing is **AUTHORIZED** as a pre-analysis step. Parser identity
for all future runs: `medication_parser.py` v1.0.0, sha256
`c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de`.
