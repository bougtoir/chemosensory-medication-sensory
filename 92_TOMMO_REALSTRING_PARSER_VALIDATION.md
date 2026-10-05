# 92 — ToMMo real-string parser validation (required pre-analysis gate)

Status: **REQUIRED — DEFERRED TO AUTHORIZED ACCESS**. This file freezes the
protocol and records why it could not be executed during the lock task.

## Why it is deferred
Amendment 2 requires validation on ACTUAL ToMMo medication free-text.
Medication free-text rows are participant-level data: they are not in the
public dbTMM catalog (the catalog publishes item names and distributions,
not raw free-text values) and not obtainable without an approved
pre-research / data-access application. No such access exists in this
project session, and the project rules forbid acquiring it here. Sampling
was therefore IMPOSSIBLE — this is recorded, not skipped silently.

## Frozen sampling protocol (executes at authorized access, before any
genotype–outcome analysis)
1. Population: all unique normalized medication free-text strings in the
   medication section(s) of the authorized wave(s).
2. Sample: random 300–500 unique strings (all if <300). Seed = 42.
   Sampling independent of genotype, prediction ID, candidate gene,
   hypothesis, and any association result.
3. Record: total unique strings in source, sampling method, seed, N.
   Output file: `93_TOMMO_REALSTRING_QC_SAMPLE.csv` (schema below —
   currently a TEMPLATE with the only publicly documented example strings;
   it is NOT a validation sample).

## Frozen adjudication
Per string: active ingredient, generic name, brand name, formulation,
route, release type, oral sensory exposure class (EX0–EX3), taste-masking
class. Unresolvable → UNKNOWN (never forced). Adjudication genotype-blind.

## Frozen pass criteria (unchanged, not lowered)
- active ingredient ≥95%, route ≥95%, formulation ≥90%, oral sensory
  exposure ≥90% — each with 95% CI reported; precision/recall/F1 and a
  confusion matrix per field.
- Taste masking: distinguish "classification error" from "information
  unavailable" (label lacks coating cue).

## Frozen failure rule
Any unmet critical threshold → genotype-associated primary analysis does
NOT begin. Parser revision allowed only while genotype-blind; re-validate
on a FRESH genotype-blind sample. Tuning on the same evaluation sample is
documented if it ever occurs.

## Status
- `69_MEDICATION_PARSER_VALIDATION.md` remains the valid FIRST validation
  (formulary corpus, PASS). This file supplements it — the original was
  not replaced.
- Final parser identity pending real-string QC: `94` (currently v1.0.0,
  unchanged — revision only via this gate).
