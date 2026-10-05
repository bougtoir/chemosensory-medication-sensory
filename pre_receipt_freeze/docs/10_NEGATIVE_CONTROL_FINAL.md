# 10 — Negative controls (final)

Status: FINAL PRE-RECEIPT FREEZE. Source: legacy `79_NEGATIVE_CONTROL_FINAL.csv` (IDs, genes and drugs regenerated exactly in DRY_REPRODUCTION_AUDIT; label wording normalized per AMENDMENT_LOG AM09). Config: `analysis_config.yaml::negative_controls`, `drug_dictionary.yaml::negative_control_drugs`. Module 16.

| ID | Type | Genotype | Exposure | Expected | Paired prediction (sign) | Status |
|---|---|---|---|---|---|---|
| N01 | route | TAS2R38 PAV | insulin (parenteral, ATC A10A) | null | P01 | testable if floors met |
| N02 | route | TAS2R38 PAV | gentamicin (parenteral) | null | P01 | expected UNTESTABLE (rare) |
| N03 | route | TAS2R38 PAV | remdesivir (IV) | null | P01 | expected UNTESTABLE |
| N04 | route | TAS2R38 PAV | fentanyl transdermal | null | P01 | conditional |
| N05 | masking | TAS2R38 PAV | PPIs enteric/capsule/OD | null or attenuated | P01 | conditional |
| N06 | masking | TAS2R38 PAV | erythromycin enteric/film tablet | attenuated vs suspension | P12 | conditional |
| N07 | receptor mismatch | TAS2R9 V187A | propylthiouracil | null | P05 | conditional |
| N08 | receptor mismatch | TAS2R38 PAV | ofloxacin | null | P01 | conditional |
| N09 | receptor mismatch | TAS2R38 PAV | clindamycin | null | P01 | expected UNTESTABLE |
| N10 | receptor mismatch | TAS1R2 rs12033832 | quinine | null | P08 | expected UNTESTABLE |
| N11 | masking | TRPA1 | ibuprofen film tablet | — | — | REQUIRES PROTOCOL AMENDMENT (TRPA1 outside approved universe); not analysed, not deleted |
| N12 | behavioral | TAS2R38 PAV | supplement/health-food use | null | P01 | testable |

## Model
Same outcome (DRUG_SPECIFIC_CHANGE_AWAY), covariates and testability floors as the paired prediction (`14`). Untestable controls are reported as untestable, never dropped.

## Failure rule (D13)
A control FAILS if p < 0.05 (two-sided, unadjusted) AND the estimate has the sign of its paired prediction. Controls behave only if zero tested controls fail. Any failure → interpretation pattern C ("associations observed but mechanistic interpretation not supported") regardless of positive predictions (85 rule 3). Controls are never re-labelled or removed after results.
