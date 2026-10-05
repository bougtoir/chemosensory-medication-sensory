# 78 — Outcome terminology freeze

Status: **FINAL FREEZE**. Binding terminology for all analyses and outputs.
The instrument measures a 2-week point exposure (see `74`); words that
imply unobservable longitudinal processes are banned.

## Banned terms (unless explicitly justified as unobserved-process inference)
- "adherence", "non-adherence", "compliance"
- "discontinuation", "persistence", "cessation"
- "switch / switching", "switch caused by taste"
- "refusal", "avoidance" (as observed behavior — allowed only inside
  *hypothesis* phrasing, never as an outcome label)
- "preference" (as observed behavior)
- "taste-driven change", "aversive response" (as mechanism claims)

## Allowed frozen outcome labels
| Term | Definition |
|---|---|
| exposure presence | any report of the drug/class in the wave window |
| exposure class | EX0–EX3 assignment of the reported formulation |
| formulation stratum | EX3 vs EX1 within-drug contrast cell |
| cross-wave exposure transition | change in exposure presence between Wave 1 and Wave 2 (onset/offset) |
| cross-wave exposure discordance | change in formulation/class between waves for the same ingredient |
| EX3 share | proportion of a participant's oral medications in EX3 |
| dispense-report discordance | (claims secondary) drug dispensed but absent from questionnaire report |

## Naming rules
1. Outcomes are written as `exp_<drug/class>_<metric>` in analysis code.
2. Every result sentence states the instrument window ("past-two-week
   reported exposure"), so readers cannot misread it as adherence.
3. Mechanistic language ("taste", "bitterness", "sensory") appears only in
   hypothesis and interpretation framing, consistent with `16`/`85`
   claim levels — never inside variable names or result tables.
