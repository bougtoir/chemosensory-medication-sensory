# 88 — Amendment policy (final)

Status: **FINAL FREEZE**. How the frozen package may change after this
commit.

## Amendment classes
1. **Clerical** — typos, formatting, dead links, README drift. Allowed
   freely; logged in `61_PREOPENING_ERRATA.md`.
2. **Technical** — parser dictionary additions, bug fixes in build scripts.
   Allowed ONLY with: version bump (`70`), re-run of the frozen validation,
   errata entry with reason + hash diff. Never changes thresholds or gold
   labels to fit results.
3. **Analytic** — any change to predictions, exposures, outcomes, models,
   families, interpretation, or opening conditions. **PROHIBITED after
   genotype–outcome results have been inspected.** Before that point,
   allowed only through a written amendment: new file, explicit diff from
   the frozen item, justification referencing only non-outcome evidence.

## Hard prohibitions (cannot be amended away)
- No adding/removing/reordering predictions after opening.
- No threshold lowering (parser accuracy, power floors, r² proxy cutoff).
- No renaming outcomes toward banned terminology (`78`).
- No changing interpretation patterns (`85`) to fit observed results.
- No deletion of negative controls or falsifying-condition rows.

## Process
1. Every amendment gets a sequential entry in `61_PREOPENING_ERRATA.md`
   (or a new dated errata file) with: file, field, old, new, reason class,
   and SHA-256 of the changed file.
2. Analytic amendments require a fresh opening decision (`89`) re-checklist
   sign-off before any result inspection resumes.
3. This policy file itself may only be amended as class 3 with a written
   justification stronger than convenience.
