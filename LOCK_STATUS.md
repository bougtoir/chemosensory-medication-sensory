# LOCK_STATUS — confirmatory history lock (as of 2026-10-04)

Binding status of every confirmatory decision in this package.
Change authority: `88_AMENDMENT_POLICY_FINAL.md` only, and only before
genotype–medication results are inspected.

## Frozen items
- `13_LOCKED_PREDICTIONS_v2_FINAL.csv` — immutable in principle
  (SHA-256 recorded in `60`; amendment log in `97`).
- Prediction hierarchy (`62`): F-PRIMARY = P01, P02, P05, P10;
  remaining directional = SECONDARY CONFIRMATORY; N01–N12 = controls.
- **P01 sparse → P10 rescue is FORBIDDEN** (`91`). P01 failing its floor
  is `PRE-SPECIFIED BUT UNTESTABLE`; P10 is an independent secondary and
  its success never confirms P01.
- **Mechanistic gradient is a formal test** (`95`): G×E 1-df interaction,
  family F-GRADIENT α=0.05; categorical + order-restricted = secondary.
- **Continuous calibration is the primary calibration** (`96`): signed
  Z_i vs frozen evidence_score, Spearman ρ, ≥10,000 permutations,
  seed 42; binary calibration is secondary (F-CALIBRATION).
- **Negative controls are never replaced after seeing results** (`79`).
- Sparse/unavailable predictions are `PRE-SPECIFIED BUT UNTESTABLE` —
  never substituted, never counted as refutations (`72`, `89`, `91`).
- Parser: v1.0.0 frozen (`94`, sha256 c722341a…a99de). Real-ToMMo-string
  validation (`92`) is a REQUIRED GATE before any association run;
  thresholds not lowered.
- Banned outcome terms (`78`): adherence/persistence/discontinuation/
  switch as constructs — forbidden.
- **Any change made after inspecting outcomes loses confirmatory status**
  and can only be exploratory (`88`, `82` F-EXPLORATORY).
- This package preserves the complete pre-specification history written
  BEFORE any ToMMo participant-level result was seen. Keep it that way:
  amendments 91–96 are documented PRE-OUTCOME amendments.

## Outstanding conditions before association analysis
1. dbTMM catalog variant-availability check (`63` variants).
2. Real-string parser QC gate (`92` protocol, frozen thresholds).
3. Exposure-count floors (`73`, n≥200) per prediction.
4. Analysis-set lock + hash, then frozen family order (`83`).

## Decision chain
docs/17: CONDITIONAL GO → 36: CONDITIONAL GO TO PRIMARY VALIDATION →
89: OPEN WITH RESTRICTIONS → **98: OPEN PRIMARY DATA WITH RESTRICTIONS**
(current). 89/90 superseded by 98/99 for operations; retained for audit.
