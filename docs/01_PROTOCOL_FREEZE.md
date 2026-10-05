# 01 — Protocol Freeze (Stage 0)

Project: **Ancient chemosensory variation shapes human responses to modern medicines**
Freeze date (UTC): 2026-10-04
Status: **FROZEN before substantive evidence synthesis.** No individual-level ToMMo data were accessed, inspected, requested, inferred from, or used at any point in this project. This file was written before the Stage 1 search results were examined.

## 0. Scope rule

Dry/public evidence only. Stages 0–2 only. STOP after Stage 2. The output is a GO / CONDITIONAL GO / NO-GO decision on whether a *separately locked* population-validation phase (e.g. ToMMo) is justified.

## 1. Terminology lock

| Code | Concept | Examples | Role |
|------|---------|----------|------|
| S1 | sensory sensitivity | bitterness, sweetness, sourness, metallic taste, oral irritation, aversive intensity | primary |
| S2 | behavioral sensitivity | acceptance, refusal, adherence-adjacent choice, formulation preference, willingness to continue | primary |
| S3 | pharmacological sensitivity | efficacy, toxicity, ADRs, pharmacodynamics | exploratory only |

S3 is **never** inferred from S1 or S2 without direct evidence. "Drug sensitivity" unqualified is banned.

## 2. Central model (frozen)

```
Chemosensory genotype → sensory phenotype (S1) → behavioral response (S2) → medication-related phenotype
                                          ↑
                    diet / repeated exposure / sensory training → ΔS1
```

Each arrow is falsified separately. The model is not assumed true.

## 3. Frozen hypotheses

- **H1 (primary):** Common or functionally relevant variation in human chemosensory receptor genes produces reproducible differences in sensory response to pharmaceutical compounds or chemically analogous ligands. `G_chemosensory → S1_drug`
- **H2 (primary):** The sensory effects associated with chemosensory genotype are not restricted to foods but extend to evolutionarily novel orally encountered compounds, including medicines. `G_chemosensory × drug chemical property → S1_drug`
- **H3 (primary):** Chemosensory phenotype is environmentally plastic. `dietary exposure / repeated exposure / training → ΔS1`
- **H4 (primary):** There is credible evidence that S1 influences medication-related behavior. `S1 → S2`
- **H5 (translational, NOT claimed demonstrated):** Because S1 is genetically influenced and environmentally modifiable, an intervention pathway `E → ΔS1 → ΔS2` is biologically plausible. H5 requires direct interventional evidence to be *demonstrated*; plausibility ≠ demonstration.

## 4. Falsification criteria (frozen NO-GO triggers)

| ID | Trigger | Verdict (filled after Stage 1) |
|----|---------|-------------------------------|
| F1 | No reproducible genotype → S1 associations in humans | see 17_GO_NOGO_DECISION.md |
| F2 | Genotype effects limited to canonical lab tastants; no generalization to pharmaceutical/analogous compounds | see decision doc |
| F3 | S1 effectively fixed in adults; credible interventional plasticity absent | see decision doc |
| F4 | Drug S1 has no credible association with S2 after obvious confounders | see decision doc |
| F5 | Published genotype–drug associations better explained by PK, disease, ancestry, or linkage mechanisms unrelated to sensory biology | see decision doc |
| F6 | Evidence dominated by isolated candidate-gene reports, poor replication, no coherent architecture | see decision doc |
| F7 | Receptor–drug links mostly in silico docking without experimental receptor/sensory validation | see decision doc |
| F8 | Future ToMMo-relevant outcomes cannot plausibly distinguish sensory mechanisms from general health behavior / indication / treatment choice / adherence | see decision doc |

Each criterion is scored **Supported / Partially supported / Not supported** in `17_GO_NOGO_DECISION.md` (the criterion is "supported" when the failure condition holds).

## 5. Evidence grading (frozen)

For drug → chemosensory evidence: A human sensory > B human receptor functional assay > C non-human receptor assay > D indirect chemical prediction > E purely computational. Grades are never merged.

For genotype → drug sensory: direct replicated human > direct single-cohort human > indirect > mechanistic inference only.

## 6. Gene universe (frozen tiers)

- **Tier A (direct receptors):** TAS1R1, TAS1R2, TAS1R3, TAS2R family (TAS2R1–TAS2R60 incl. pseudogene-aware handling), OTOP1.
- **Tier B (canonical transduction):** GNAT3, GNG13, PLCB2, ITPR3, TRPM5.
- **Tier C (other oral chemosensory, strong evidence):** SCNN1A, SCNN1B, SCNN1G, SCNN1D (ENaC salt-sensing subunits).
- **Tier D (exploratory):** additional genes admitted only with explicit human chemosensory justification, logged in the evidence tables.

Olfactory receptors are kept analytically separate; they may serve as a parallel positive-control chemosensory system.

## 7. Prediction freeze rule

The Stage 2 score `PredictedSensoryResponse(g,d)` and the locked prediction table (file 13) are frozen **before** any validation data exist. No post hoc modification after seeing population data is permitted. Missing evidence ⇒ `unknown`, never imputed to a direction.

## 8. Analysis commitments

- P values, effect sizes, and 95% CIs retained wherever published; missing fields recorded as missing, not guessed.
- Pediatric and adult S1→S2 evidence kept separate; pediatric formulation behavior never generalized to adults unqualified.
- Meta-analysis only where ≥3 reasonably comparable studies; otherwise structured effect-direction synthesis.
- Deterministic seeds (seed = 20261004); package versions and all retrieval dates logged in `19_DATA_PROVENANCE.md`.
- Third-party record-level data (e.g. OpenAlex-derived individual records) are not republished; aggregates and code only, per project policy.
