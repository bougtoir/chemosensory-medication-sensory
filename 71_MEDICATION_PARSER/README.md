# Medication free-text parser — frozen v1.0.0

Deterministic Japanese medication-string parser for ToMMo questionnaire free-text
(e.g. `アダラートCR錠20mg`). Codebook-parsable only: no ML, no imputation.

## Files
- `medication_parser.py` — the frozen parser (`VERSION = "1.0.0"`).
- `gold_corpus.csv` — genotype-blind adjudicated validation corpus (146 strings,
  constructed from public formulary knowledge; no participant data).
- `validation_output.csv` — parser output on `gold_corpus.csv` (frozen artifact).

## Usage
`python3 medication_parser.py < input.csv > output.csv` (first column = raw text),
or `from medication_parser import parse`.

## Versioning
Any dictionary/rule edit bumps VERSION and re-runs the validation in
`69_MEDICATION_PARSER_VALIDATION.md`. See `88_AMENDMENT_POLICY_FINAL.md`.
