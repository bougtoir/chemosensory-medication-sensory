# 99 — Primary validation handoff (v2, supersedes `90`)

Status: **FINAL — session endpoint**.

## Current decision state
**OPEN PRIMARY DATA WITH RESTRICTIONS** (`98`). No genotype–medication
association has been estimated in this project to date.

## Pre-opening amendments applied (`97` manifest)
- `91` — P01/P10 confirmatory separation (no collapse/rescue).
- `92`/`93`/`94` — real-ToMMo-string parser QC protocol frozen; execution
  deferred to authorized access (real free-text is participant-level and
  not publicly available); parser stays v1.0.0 pending it.
- `95` — formal 1-df G×E gradient test = principal mechanistic test
  (F-GRADIENT).
- `96` — continuous signed-effect calibration = principal calibration test
  (F-CALIBRATION); binary calibration demoted to secondary.

## Required opening order (all steps genotype-blind until step 5)
1. dbTMM catalog variant-availability check (`89`/`98` restriction).
2. Genotype-independent QC (`87` matrix).
3. Frozen parser v1.0.0 on all medication free-text → aggregate exposure
   counts → observability/floor verdicts per `72`/`73`/`91`
   (UNTESTABLE stays UNTESTABLE — no merging).
4. **Real-string parser gate (`92`)**: random 300–500 unique strings,
   seed 42, adjudicate, validate vs frozen thresholds. If it fails:
   revise (genotype-blind), re-validate on fresh sample; analysis remains
   closed until pass.
5. Lock analysis set; record hash.
6. Execute `83` in frozen family order: F-PRIMARY → F-GRADIENT (`95`) →
   controls → F-CONTRAST → F-SECONDARY → F-CALIBRATION (`96`), then the
   `85` pattern assignment. Report the frozen/testable/untestable/
   evaluated denominator.
7. Frame results only via `85`/`86` — isolated hits are never framework
   proof.

## Unchanged prohibitions
No outcome-stratified genotype inspection; no post-result amendments;
no banned terminology (`78`); no Level-5 claims; P01 never rescued by P10.

## Files of record
- Decision: `98_FINAL_OPENING_DECISION_V2.md`
- Amendments: `91`–`96`; manifest `97`; parser version `94`
- Superseded (kept for audit): `89`, `90` — read `98`/`99` instead.
