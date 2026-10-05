# 20 — Final Handoff

## What this package is

A complete Stage 0–2 dry-analysis for *"Ancient chemosensory variation
shapes human responses to modern medicines"*: frozen hypotheses, a
machine-readable evidence base (78 curated studies, 5,125-PMID search
pool, 1,108 BitterDB receptor–ligand edges, 197-compound drug chemical
space), an evidence graph, a meta-analytic pass, and a locked prediction
table for any future validation.

## Decision

**CONDITIONAL GO** — see `docs/17_GO_NOGO_DECISION.md` for the scorecard,
conditions, and explicit flip-to-NO-GO triggers. Bottleneck: adult
genotype→drug-perception→behavior (domains D/E).

## File map (spec-numbered files at project root)

- `01_PROTOCOL_FREEZE.md` → docs/01_PROTOCOL_FREEZE.md
- `02_SEARCH_STRATEGY.md` → docs/02_SEARCH_STRATEGY.md
- `03_STUDY_INVENTORY.csv` — 78 studies × layers
- `04_VARIANT_EVIDENCE.csv` — genotype→S1 (incl. 1D drug-sensory)
- `05_DRUG_SENSORY_EVIDENCE.csv` — drug→receptor/sensory evidence A–E graded
- `06_PLASTICITY_EVIDENCE.csv` — diet/training→ΔS1
- `07_EVIDENCE_GRAPH.csv` / `08_EVIDENCE_GRAPH.json` — 163 nodes / 150 edges
- `09_META_ANALYSIS/` — Fisher combined P (TAS2R38→PROP/PTC: chi2=588.7, df=16, P≈0);
  direction synthesis (24 positive / 4 null)
- `10_DRUG_CHEMICAL_SPACE.csv` → prediction/drug_chemical_space.csv
- `11_RECEPTOR_DRUG_MATRIX.csv` — 4,531 R×D cells, 76 known agonism edges
- `12_VARIANT_FUNCTION_MATRIX.csv` — 13 variant–function records
- `13_LOCKED_PREDICTIONS.csv` — 9 frozen predictions incl. negative controls
- `14_TOMMO_FUTURE_VALIDATION_PLAN.md` → docs/14 (write-only)
- `15_INTERVENTION_FUTURE_PLAN.md` → docs/15 (design-only)
- `16_NATURE_CLAIM_AUDIT.md` → docs/16 (Levels 1–2 supported)
- `17_GO_NOGO_DECISION.md` → docs/17
- `18_REFERENCES.bib` — 78 verified BibTeX records
- `19_DATA_PROVENANCE.md` → docs/19
- `20_FINAL_HANDOFF.md` — this file

Auxiliary: `evidence/` (search pool, sensory→behavior, extraoral,
evolution, BitterDB tables), `figures/fig1–7`, `scripts/01–08`,
`data/raw/` (raw XML/HTML/JSON + sha256 ledgers).

## To regenerate

`make all` in this directory (requires network for 01–03; curated
downstream steps are deterministic).

## Hard rules honored

- No ToMMo individual-level data touched at any point.
- Stopped after Stage 2; predictions frozen, not outcome-fitted.
- No fabricated values: abstract-missing fields left empty; all citations
  machine-verified against PubMed.
