# 74 — Repeated-wave outcome structure freeze

Status: **FINAL FREEZE**.

## Documented instrument facts (public questionnaire only)
- ToMMo health-survey medication section 【５】asks: any medication in the
  **past two weeks** → free-text rows per drug with 商品名や成分等, 入手方法
  (prescription/OTC), 使用期間, 使用頻度, 1回の使用量. Example printed on the
  form: 「アダラートCR錠20mg」.
- The same section wording appears in both Wave 1 and Wave 2 instruments
  (public PDFs persisted in `data/raw/tommo_public/` with ledger).
- The exposure window is therefore a **2-week point exposure per wave**, not
  a continuous exposure history.

## Frozen consequences
1. Primary unit of analysis = participant × wave exposure state
   (any-exposure indicator per drug/class, exposure class EX0–EX3).
2. A "past two weeks" instrument CANNOT measure adherence, persistence,
   discontinuation, or switching intent. Outcomes built from it are limited
   to: presence/absence of an exposure; formulation/route class of the
   exposure; and cross-wave exposure transition / discordance indicators
   (terminology frozen in `78`).
3. Cross-wave analyses are restricted to participants observed in both waves
   and are secondary/supportive — never the primary test, because the
   interval between waves and interim therapy changes are unobserved.
4. Sparse-cell rule (pre-registered, amended by `91`): if a drug-level
   exposed count falls below the `73` floor (n<200), the prediction is
   marked PRE-SPECIFIED BUT UNTESTABLE. Class-level predictions (P07, P10,
   formulation contrasts) were independently frozen at the class level and
   are evaluated there regardless of any drug-level test's fate — a
   drug-specific prediction is never merged into, replaced by, or declared
   supported through a class-level prediction (e.g. P12 evaluates its own
   suspension-vs-tablet contrast only if its own cell meets the floor).
5. Waves are analyzed as repeated measures with within-participant
   correlation (GEE or participant-clustered SEs), never pooled naively.
6. Indication confounding is wave-varying; confounder availability per wave
   is part of the permitted genotype-blind QC.
