# 83 — Primary statistical analysis plan (final freeze)

Status: **FINAL FREEZE**. This SAP governs every genotype–medication
analysis if, and only if, the opening decision in `89` authorizes it.

## 1. Analysis population
- Participants with valid genotype (post-QC), Wave-1 medication section
  answered; Wave-2 analyses use the both-waves subset.
- No outcome-based exclusions. Medication-parse failures are retained with
  exposure=null.

## 2. Exposures (genotype)
- TAS2R38 PAV diplotype: dosage 0/1/2 (A49P-proxy fallback labelled per `65`).
- Other variants: dosage of the effect allele per `63`.
- Genotype QC (MAF, HWE, missingness, relatedness, ancestry PCs) performed
  genotype-blind w.r.t. outcomes per `87`.

## 3. Outcomes (terminology per `78`)
- O1: exposure presence (drug/class) — binary.
- O2: exposure class EX3 vs EX1 within drug — binary (stratum-restricted).
- O3: cross-wave transition/discordance — secondary.
- O4: EX3 share — ordinal/continuous.

## 4. Models (frozen)
- O1, O2: logistic regression, exposure ~ genotype_dosage + age + sex +
  wave + 10 ancestry PCs (+ indication proxy where the DAG requires).
- O3: logistic on transition indicator; participant-clustered SEs.
- O4: linear/ordinal as appropriate.
- Odds ratios + 95% CIs reported for every test; direction checked against
  the frozen sign in `13_v2_FINAL` BEFORE p-value interpretation.

## 4-G. Mechanistic gradient (primary test of the general mechanism, `95`)
- E = 0–3 ordinal exposure score (EX0–EX3, `67`).
- Primary: logit[P(Y=1)] = β0 + β1G + β2E + β3G×E + covariates; H1: β3 in
  the frozen direction; 1-df test.
- Secondary: categorical E model (per-stratum genotype effects);
  order-restricted check |β_EX3|≥|β_EX2|≥|β_EX1|≥|β_EX0|.

## 5. Estimands
- Population-average genotype-associated difference in past-two-week
  reported exposure (per 1-dosage-unit). Explicitly NOT an effect on
  adherence or on sensory perception.

## 6. Missing data
- Complete-case per test; missingness patterns described genotype-blind.
- No multiple imputation in primary analysis (sensitivity only, `84`).

## 7. Ordered execution
1. Genotype-blind QC + parser run + exposure counts (authorized, `87`).
2. Analysis-set lock (codebook + participant list), hash recorded.
3. Primary family tests → mechanistic gradient test (`95`) → controls →
   contrasts → continuous calibration (`81`, `96`).
4. Interpretation through matrix `85` only.

## 8. Software freeze
- Analysis code versioned in-repo; seed 42 wherever randomness exists;
  environment pinned (requirements.txt); every output hash-logged.
