# 14 — Future ToMMo Validation Plan (WRITE ONLY — NOT EXECUTED)

No individual-level ToMMo data were accessed in this project. This plan is
written from public knowledge of what a cohort questionnaire typically
contains. Before execution, a separate, independently frozen analysis plan
would be required.

## Outcome availability tiers

**A. Plausible from questionnaire data (usable):**
current medication use; specific drug / drug-class exposure; food intake;
alcohol; smoking; lifestyle and health phenotypes. Formulation-level
behavior (liquid vs solid preference, reported taste complaints, switching
between formulation types) may exist only indirectly — to be confirmed
against the actual ToMMo instruments.

**B. Possible, requires ToMMo confirmation:**
exact product/formulation; repeated medication measures across survey
waves; indication; duration; medication changes over waves.

**C. Unavailable unless specifically documented:**
claims-like longitudinal history (initiation dates, discontinuation,
switching times, MPR/refill). This plan does NOT assume any category-C data.

## Design that remains useful without C

Primary inference uses **cross-sectional exposure × genotype**:

```
Outcome ~ β0 + β1 Genotype + β2 DrugChemProperty + β3 Genotype × DrugChemProperty + covariates
```

β3 is the key estimand: genotype should predict outcome **only within
exposure classes the receptor biology predicts** (e.g. TAS2R38 effects in
thiourea-class/bitter liquid exposures but not masked/non-oral exposures —
interaction with the frozen drug-prioritization tiers, file 13).

## Covariate policy (pre-specified DAG)

Confounders: age, sex, ancestry PCs, disease indication, major
comorbidities, smoking, alcohol, diet, SES where available.
Mediators (e.g. sensory phenotype itself, adherence propensity) are NOT
adjusted for. A DAG will be drawn and frozen before analysis.

## Negative controls (embedded)

- TAS2R38 should not predict outcomes for **non-oral drugs** (insulin,
  gentamicin) or fully masked formulations (enteric-coated PPIs).
- A positive finding in negative controls signals indication/ancestry
  confounding, not sensory biology.

## Latent chemical approach–avoidance phenotype

A latent factor across bitter/sweet foods, coffee, tea, alcohol, smoking,
supplements, medicines is evaluated — not assumed. Required evidence:
cross-domain covariance, measurement coherence, biological plausibility,
adequate fit. Competing structures (single-factor, multi-factor, bifactor,
network) compared; if no coherent latent trait, report that clearly.

## Multiple testing

Tests are limited to the locked prediction table (13_LOCKED_PREDICTIONS.csv),
~9 pre-specified rows → Bonferroni/FDR control across that table, not the
genome. Exploratory findings are labeled exploratory.
