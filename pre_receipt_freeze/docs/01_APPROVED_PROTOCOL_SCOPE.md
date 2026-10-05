# 01 — Approved protocol scope

Status: FINAL PRE-RECEIPT FREEZE. Source documents are restricted; only scope summaries and hashes appear here (see `22_RESTRICTED_SOURCE_HASH_INDEX.md`).

## Governing documents
| Rank | Document | Role |
|---|---|---|
| 1 | `tommo研究計画.docx` (research plan, study 2025-0057) | highest-priority scientific constraint |
| 1 | `tommo申請書.docx` (application) | highest-priority administrative constraint |
| 2 | `tommoデータセット.xlsx` (distribution specification) | defines what data can exist (`02`) |
| 3 | `CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip` | formal pre-ToMMo scientific history (`04`) |

Approved title: 味蕾関連遺伝子多型が処方変更に与える影響の解明 (effect of taste-bud-related gene polymorphisms on prescription change).

## Protocol version rule (D01)
The attached plan/application (text identical to the 2026-03-13 submission) governs. A 2026-06-13 revision exists in the monorepo (`tommo_taste_receptor_2025-0057/revised/`) with four differences: (1) analysis restricted to participants present in both waves; (2) five drug categories (antihypertensives, statins, NSAIDs, digestive drugs, metformin) named as main analysis targets; (3) GWAS wording replaced by candidate-region analysis; (4) gene list moved to an appendix. The frozen plan is constructed to be valid under either version:
- both-wave restriction is applied to every analysis (D16) — compatible with both;
- no GWAS in any confirmatory family (D15) — compatible with both;
- the gene universe is identical (20 genes) under both;
- the five-category family C2 is secondary under the attached version and is promoted to confirmatory (Holm, α=0.05, 15 tests) if, before the independent timestamp, the PI records that the 2026-06-13 revision is the approved version. This is an administrative fact, not a data-dependent choice; the switch is recorded in `DECISION_LOG.md` D01 and cannot be exercised after receipt.

## Scope summary
- Objective: whether taste/chemosensory-related genetic polymorphisms are associated with prescription change (dose change, medication change, switch, addition, deletion) between baseline (phase 1) and second-stage (phase 2) surveys of the TMM Community-Based and Birth and Three-Generation Cohorts (Miyagi, age ≥20).
- Approved gene universe (20): TAS1R1, TAS1R2, TAS1R3, TAS2R8, TAS2R9, TAS2R10, TAS2R14, TAS2R16, TAS2R38, TAS2R46, SCNN1A, SCNN1B, SCNN1G, SCNN1D, OTOP1, GNAT3, GNG13, PLCB2, ITPR3, TRPM5. The plan text writes `AS2R8`; this is read as TAS2R8 (clerical, AMENDMENT_LOG AM02).
- Methods named in the plan: regression with covariate adjustment, regularized regression and gradient boosting (permitted; secondary only here), GWAS as an option if data volume permits (not used; D15), claims information (not in the distribution; D15).
- Background in the plan frames taste receptors as extending beyond tongue perception (gut, airway, innate immunity, nutrient sensing, glucose metabolism). This makes a chemical-surveillance discussion compatible with the protocol, but immune mediation is NOT directly tested (`25`, `03`).

## Out of protocol scope (never run without an approved amendment, `24`)
Variants or genes outside the 20-gene universe (TAS2R19, TRPA1, TAS2R4, TAS2R43); genome-wide association; metabolomics; claims-based outcomes; any intervention, health-economic or global-health inference.
