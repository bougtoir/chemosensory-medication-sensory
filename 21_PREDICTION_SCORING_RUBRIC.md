# 21 — Prediction Scoring Rubric (FROZEN before candidate scoring)

Inputs: `13_LOCKED_PREDICTIONS.csv`, `docs/17_GO_NOGO_DECISION.md` (summaries
in `22_PREDICTION_EXPANSION_SEARCH.md`).

## Eligibility tiers (pre-registered)

- **Tier A** — direct human genotype × pharmaceutical sensory evidence.
- **Tier B** — human genotype→sensory AND (human or functional)
  receptor→drug evidence.
- **Tier C** — well-replicated functional variant AND strong
  receptor–drug agonist/antagonist evidence AND plausible oral sensory
  exposure.
- **Tier D** — negative control with mechanistic rationale.

Excluded: in-silico docking alone; single unreplicated candidate-gene
reports; non-human-only evidence; "drug is bitter" anecdotes; marketing
formulation claims; non-oral drugs except as negative controls.

## Score components (integer each)

| Component | Range | Anchor points |
|---|---|---|
| G — human genotype→sensory | 0–3 | 3=GWAS-level/multi-cohort replicated; 2=replicated candidate; 1=single cohort; 0=none |
| H — human drug sensory evidence | 0–3 | 3=human panel on the drug itself; 2=panel on close analog/probe; 1=sensor/indirect human; 0=none |
| R — functional receptor–drug | 0–3 | 3=curated agonism/antagonism at the predicted receptor (BitterDB/heterologous); 2=broad family evidence; 1=inferred; 0=none |
| V — variant function evidence | 0–3 | 3=cloned functional haplotype w/ dose-response; 2=GWAS lead w/ mechanism support; 1=association only; 0=none |
| Rep — replication | 0–2 | 2=independent replication; 1=multiple reports same group/mixed; 0=single |
| F — formulation/oral exposure relevance | 0–2 | 2=liquid/dissolving oral exposure documented; 1=oral solid with known bitter API; 0=masked/non-oral |
| O — observability in cohort data | 0–2 | 2=outcome plausibly captured by questionnaire brand-name/duration fields; 1=needs proxy; 0=requires unavailable variable |
| A — alternative-explanation burden | 0–3 (penalty) | 0=validated causal chain; 1=some confounds addressable; 2=heavy indication/adherence confounding; 3=near-fatal |

**evidence_score = G+H+R+V+Rep+F+O−A** (positive max 18).

Negative controls are scored only on mechanistic validity
(G×R mismatch, masking documentation, route) — not included in the
positive ranking.

## Rules

- Score computed by `scripts/09_expansion.py` from per-component columns
  in `23_CANDIDATE_PREDICTIONS_ALL.csv`; components hand-set from the
  curated evidence files (no fabrication; every component cites its
  support in `24_PREDICTION_EVIDENCE_AUDIT.csv`).
- Preserve all existing locked predictions unless a factual error is
  found → `PREDICTION_ERRATA.md`.
