# 84 — Sensitivity analysis freeze (final)

Status: **FINAL FREEZE**. The complete, bounded set of robustness checks.
Nothing may be added post hoc.

| ID | Check | Specification |
|---|---|---|
| S1 | Unspecified-tablet reclassification | reassign `tablet (unspecified coating)` from EX2 to EX1; repeat primary family |
| S2 | Proxy-variant swap | P05 run with rs3741845 AND with the best pre-specified proxy (`64`); concordance reported |
| S3 | A49P-only haplotype | TAS2R38 predictions repeated with the single-SNP fallback (`65`) |
| S4 | Age restriction | primary tests in age≥40 subset (antithyroid/antibiotic selection differs by age) |
| S5 | Prescription-only | restrict exposures to 入手方法=prescription rows (drops OTC behavior channel) |
| S6 | Claims-defined exposure | if claims linkage available (`75`): replicate primary on dispense-defined exposure |
| S7 | Allelic vs diplotype coding | TAS2R38 as PAV-carrier binary vs dosage |
| S8 | Additional health-behavior adjustment | add smoking + alcohol (FFQ) to primary models |
| S9 | E-value reporting | per significant primary result, E-value for unmeasured confounding |
| S10 | Multiple imputation | MAR imputation of missing exposure rows; compare direction/significance |

## Rules
1. Sensitivity results are supportive evidence; they never override the
   primary verdict. Discordance is reported and interpreted via `85`.
2. No sensitivity check may rescue a non-significant primary into a claim.
3. Checks needing unavailable variables are marked NOT RUN, not dropped
   silently.
