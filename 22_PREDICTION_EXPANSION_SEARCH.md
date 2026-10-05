# 22 — Prediction Expansion Search (Phase A1–A2 record)

## Summary of the pre-existing state (inspection of v1 files)

**Locked predictions (13_LOCKED_PREDICTIONS.csv, 9 rows):**
- Positive/directional: TAS2R38×thiourea/PROP (tier 1, large);
  TAS2R38×chloramphenicol (tier 1); TAS2R9×ofloxacin (tier 2);
  TAS2R38×liquid oral meds (tier 2); TAS1R2×sweetened formulations (tier 3);
  TRPA1×chemesthetic liquids (tier 3).
- Negative controls (tier 4): clindamycin (published null), insulin
  (route), enteric-coated omeprazole (masking).

**GO rationale (docs/17):** CONDITIONAL GO — coherent mechanistic
architecture and replicated G→S1 anchor, thin genotype×drug and adult
S1→S2 links; conditions: β3 interaction estimand, embedded negative
controls, claims capped at Levels 1–2.

**Claim ceiling:** Level 2 supported; Levels 3–5 aspirational.

All v1 predictions are preserved in v2 (P01/P03/P05/P07/P08/P09 =
direct carries; N01/N05/N09 = direct carries).

## Eligibility tiers

Defined before searching — see `21_PREDICTION_SCORING_RUBRIC.md`.

## Search strategy (this pass)

Sources already acquired under raw-data persistence:
- `evidence/bitterdb_receptor_ligands.csv` — 1,108 human receptor→ligand
  edges; joined to the 197-drug list (scripts/07) and to the
  variant-function matrix (scripts/09).
- `evidence/search_pool.csv` — 5,125 PMIDs; mined for functional
  variants (TAS2R19 quinine GWAS, TAS2R4 rescue, TAS2R43/46 acesulfame-K)
  and formulation/palatability contrasts.
- PubChem chemical space — exposure plausibility.

New evidence surfaced: methimazole is a **curated TAS2R38 ligand**
(BitterDB + Behrens 2013 lists it among ligands) and a routinely used
oral drug in Japan → strongest single addition (P02).

## Inclusion outcome

12 positive/directional predictions (within the 10–20 target), 12
negative controls (4 classes: route, masking, receptor-mismatch,
adherence), 5 formulation/route contrasts. Quality cap: candidates
below evidence_score 6 or failing eligibility tiers were not added.
