# 90 — Primary validation handoff

Status: **FINAL — session endpoint**. Read this first in any future session
that opens the ToMMo data.

## What exists
- Complete frozen pre-analysis package, files `01`–`89` (key hashes in `60`).
- Decision state: **OPEN WITH RESTRICTIONS** (`89`).
- Frozen parser `71_MEDICATION_PARSER/medication_parser.py` v1.0.0,
  sha256 `c722341a04419e32b8e999411d5fb4977e809fbbc3038ad519481676a5fa99de`,
  validated `69` (all thresholds passed, n=146).
- All genotype work remains UNOPENED: no genotype–medication association
  has ever been estimated for this study.

## Executing the opening (required order)
1. Verify variant availability against the dbTMM catalog per `89` restriction 1.
2. Run genotype-independent QC only (`87` matrix).
3. Run the frozen parser on the medication free-text; produce aggregate
   exposure counts; check `72`/`73` observability floors — mark any
   prediction UNDEFINED per rules, list them.
4. Lock the analysis set; record its hash.
5. Only then execute `83` in the frozen family order (`82`), then `81`
   calibration, then assign the `85` pattern.

## What must NOT happen
- No looking at genotype frequencies stratified by any outcome.
- No prediction changes after results are seen (`88`).
- No banned outcome terminology (`78`).
- No Level-5 causal claims (`85`).

## Repo/sync
- Monorepo dir: `chemosensory_medication_sensory/` in `bougtoir/wip`;
  public mirror `bougtoir/chemosensory-medication-sensory` via
  `sync-to-repos.yml` (subdir → same name; `data` excluded from mirror).
- Raw public questionnaire PDFs persist in `data/raw/tommo_public/` with
  `ledger.csv` (SHA-256 + source URL + date); they are excluded from the
  public mirror by EXCLUDE_MAP.

## STOP
Work in this session ends here per the request sequence
(dry evidence → prediction expansion → feasibility → final freeze → STOP).
