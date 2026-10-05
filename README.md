# chemosensory_medication_sensory

Dry-evidence package: **"Ancient chemosensory variation shapes human
responses to modern medicines"**. Stage 0 hypothesis freeze → Stage 1
evidence synthesis → Stage 2 locked prediction framework →
GO/CONDITIONAL GO/NO-GO for a future (separate) population validation.

**Decision: CONDITIONAL GO** — see `docs/17_GO_NOGO_DECISION.md`.

No individual-level cohort data were accessed; this package is public
evidence only.

## Layout

- `docs/` — 01 protocol freeze, 02 search strategy, 14–15 future plans
  (write-only), 16 claim audit, 17 decision, 19 provenance, 20 handoff
- Root numbered CSVs/JSON — study inventory, variant/drug/plasticity
  evidence, evidence graph, receptor–drug matrix, variant function
  matrix, locked predictions, references.bib
- `evidence/` — search pool (5,125 PMIDs), auxiliary evidence tables,
  BitterDB receptor–ligand tables
- `prediction/` — oral drug list + PubChem chemical space
- `09_META_ANALYSIS/` — Fisher p-combination + direction synthesis
- `figures/` — provisional Figures 1–7
- `scripts/` — pipeline 01–08; `make all` regenerates (network needed
  for 01–03)
- `data/raw/` — raw API responses + sha256 acquisition ledgers
- `tests/` — `python3 -m pytest tests/` or run test functions directly
- Files `21`–`36` — prediction expansion + ToMMo public feasibility gate
  (CONDITIONAL GO TO PRIMARY VALIDATION, `36`)
- Files `60`–`90` — FINAL PRE-OPENING LOCK: manifest (`60`), frozen parser
  (`71`, validated in `69`), observability (`72`), SAP (`83`), decision
  `89` = **OPEN WITH RESTRICTIONS**. No genotype–medication association
  has been estimated; analysis is authorized only after `90` opening steps.
