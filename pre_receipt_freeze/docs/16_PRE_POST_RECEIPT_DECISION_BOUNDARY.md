# 16 — Pre/post-receipt decision boundary

## Before receipt (fixed here)
Theory, hypotheses, prediction set and signs, SNP hierarchy and fallback rules, endpoints and algorithms, dose rules, class database, FFQ lock, controls and failure rule, gradient, calibration, families and corrections, covariates, sensitivity list, ML plan, interpretation matrix, code and tests.

## At receipt (technical only, logged; `23`)
Record receipt time and file hashes; store offline; bind delivered column names, codebook values and file paths in `config/variable_map.yaml` / `ffq_lock.yaml` (technical change log entry with hash); run `--stage qc` (inventory, variable mapping, SNP harmonization, ID resolution, long format, class mapping, dose harmonization, endpoint counts without genotype); genotype-blind parser real-string QC; write analysis-set lock; sign `receipt/RECEIPT_SIGNOFF.json`.

## After sign-off
Run `--stage analysis` exactly as frozen. Any deviation → amendment (`24`) before results are inspected; analytic amendments are prohibited after genotype–outcome results are seen.

## Never allowed after receipt
Changing endpoints, thresholds, families, signs, variants (no favorable SNP substitution), controls, interpretation patterns; adding predictions.

Participant-level ToMMo data were not received, inspected or analysed at the time of this freeze.
