# 24 — Amendment policy

Carries forward legacy `88_AMENDMENT_POLICY_FINAL.md` unchanged in substance.

1. **Clerical** (typos, formatting, label wording): allowed; logged in `AMENDMENT_LOG.md`.
2. **Technical** (column binding, codebook values, dictionary additions, bug fixes): allowed with version bump, rerun of synthetic tests, log entry with old/new hash. Never changes thresholds, endpoints, signs or gold labels.
3. **Analytic** (predictions, variants, exposures, outcomes, models, families, interpretation, gates): before receipt only by a written, dated amendment with justification from non-outcome evidence; after genotype–outcome results are inspected: PROHIBITED.
4. **Data-availability** (e.g., claims, genome-wide genotypes or metabolomics delivered later; ethics approval for genes outside the 20-gene universe): new dated amendment, frozen before the corresponding data are analysed; results reported as exploratory unless the amendment predates receipt of those data.

Hard prohibitions: no adding/removing/reordering predictions after receipt; no threshold lowering; no favorable SNP substitution; no deleting controls; no changing interpretation patterns; no banned terminology.

Every amendment: ID, date (UTC), file, field, old, new, class, reason, owner, SHA-256 of old and new file.
