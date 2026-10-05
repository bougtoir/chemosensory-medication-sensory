# 29 — Final pre-receipt handoff

## Chronology
THEORY → DRY EVIDENCE → PREDICTION FREEZE → GATES → FINAL PRE-RECEIPT FREEZE → INDEPENDENT TIMESTAMP → TOMMO DATA RECEIPT → OFFLINE VALIDATION → MANUSCRIPT.
This package completes the FINAL PRE-RECEIPT FREEZE. It was built before receipt or inspection of any participant-level ToMMo data. No participant-level ToMMo data were received, inspected or analysed; no participant-level outcome result is known.

## Contents
Final protocol (`FINAL_PRE_RECEIPT_PROTOCOL.md`), documents 01–29, `DECISION_LOG.md`, `AMENDMENT_LOG.md`, `INSTRUCTION_REGISTER.csv`, `COMPLETENESS_AUDIT.md`, offline pipeline (22 modules, 5 configs, derived SNP config, synthetic generator, tests), synthetic validation outputs, environment specification, legacy frozen package files, reconciliation and dry-reproduction audit, session instruction captures, manifest (`18`) and checksums (`19`). Archive: `timestamp/CHEMOSENSORY_TOMMO_PRE_RECEIPT_FREEZE_<YYYYMMDD>.zip`; its SHA-256 is recorded outside the archive in `timestamp/ARCHIVE_SHA256.txt`. Restricted sources and third-party raw downloads are excluded and represented by hashes (`22`), which allows third-party verification without redistribution.

## Final gate
**READY WITH TECHNICAL ITEMS ONLY.**
All scientifically meaningful choices are frozen (DECISION_LOG D01–D24, every status FROZEN). Remaining items are technical and allowed by the gate rule: delivered file paths, exact column names and codebook values (bound via `config/variable_map.yaml` / `ffq_lock.yaml` as logged technical changes), actual SNP availability (deterministic fallback rules in `05`), event counts (floors in `14`), post-receipt genotype-blind parser real-string QC (`08`, `11`). Effect estimates are unknown.

## Required before the independent timestamp
1. PI review and endorsement of decisions of origin P in `DECISION_LOG.md` (agent-drafted), and the D01 record: whether the 2026-06-13 revision is the approved version (exercises the C2 confirmatory switch) or not (C2 stays secondary).
2. Recommended independent check of D18 effect-allele orientation against the delivered SNP manifest strand convention at receipt (technical).
3. Rebuild the archive if anything changes; timestamp the archive SHA-256 (e.g., OpenTimestamps/RFC 3161/OSF registration).

## Signature
| Role | Name | Date (UTC) | Statement |
|---|---|---|---|
| PI | | | I endorse DECISION_LOG D01–D24 and record the approved protocol version as: ____ |

## Next session
POST-RECEIPT OFFLINE VALIDATION: follow `23` (receipt log → `--stage qc` → `--stage lock` → sign-off → `--stage analysis`). The next session must execute the frozen analysis rather than redesign it. This package was produced by executing the main prompt after the reconciliation requested in the initial instruction.
