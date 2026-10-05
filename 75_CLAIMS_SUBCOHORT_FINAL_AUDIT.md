# 75 — Claims / subcohort final audit

Status: **FINAL**. Audit of which ToMMo-linked resources can carry which
frozen claims, based on PUBLIC documentation only.

## Audited resources
- **Community health survey (Wave 1, Wave 2)** — the only resource assumed
  available to the primary validation. Provides the medication free-text
  section, FFQ (coffee/tea/alcohol strength), smoking, demographics.
- **dbTMM release 2.3.4** — public release notes document added 服薬情報
  (medication dispense) and 医科レセプト (medical claims/receipt) tables.
  These are RESTRICTED-ACCESS resources with coverage limited to
  opt-in/consented subsamples ("健診相乗り型" linkage).
- **Genotype/imputation panel** — availability of the specific rsIDs and
  haplotype-tagging SNPs is a pre-open CONDITION (see `89`), to be verified
  against the dbTMM variable catalog, not against data.

## Claim-resource matrix (frozen)

| Claim level | Content | Required resource | Feasible? |
|---|---|---|---|
| G → S1 (genotype → sensory perception) | not testable: no taste/olfactory phenotype collected in the survey | none | NO — out of scope, claim banned |
| G → exposure presence/class | genotype → any exposure, EX class | survey + genotype | YES (primary tests) |
| G → formulation gradient | genotype → EX3 vs EX1 choice within drug | survey + parser | YES (C1–C5) |
| G → cross-wave transition | genotype → exposure discordance | 2 waves + genotype | YES, secondary |
| G → dispensed-but-not-reported discordance | claims vs questionnaire discordance | claims linkage | CONDITIONAL — only if claims coverage & consent subset confirmed at open |
| Population-level behavioral prediction (Level 4) | direction & rough magnitude of genotype-associated exposure/transition rates | survey | YES — this is the validation target |

## Frozen statements
1. Claims data are a SECONDARY, optional resource. The primary validation is
   designed to be valid with the survey instrument alone.
2. If claims linkage is used, analyses replicate primary tests on
   dispense-defined exposure as a robustness check (`84`), never replace the
   frozen primary outcome.
3. No sensory-phenotype subcohort exists in public documentation → any
   statement implying direct taste-perception measurement in this study is
   prohibited; the sensory link is inferential (BitterDB + literature).
