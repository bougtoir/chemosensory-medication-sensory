# 02 — Actual distribution scope

Status: FINAL PRE-RECEIPT FREEZE. Derived from the distribution specification (data dictionary only; no participant-level values). Machine-readable extract: `../../reconciliation/distributed_scope.json`.

## Release
リリース 3.1.1 地域住民・三世代コホート 宮城（20歳以上）ベースライン・第2段階調査 86K.

## Selected file families
| Logical key (`config/variable_map.yaml`) | Family | Wave |
|---|---|---|
| demographics | demographics | — |
| cohort_profile | cohort_profile | — |
| laboratory_ph1 / laboratory_ph2 | laboratory_test | ph1 / ph2 |
| lifestyle_ph1 / lifestyle_ph2 | qa_lifestyle (incl. medication section) | ph1 / ph2 |
| ffq_ph1 / ffq_ph2 | qa_ffq | ph1 / ph2 |
| physiological_ph1 / physiological_ph2 | physiological_test | ph1 / ph2 |
| snp_genotypes + snp_manifest | taste-related SNP information within the approved gene scope (separate delivery stated by the PI) | — |

## Not in the distribution (frozen assumptions)
- NO CLAIMS DATA IN THE PRIMARY DISTRIBUTION; no long-term prescription claims. Claims supplied later → data-availability amendment (`24`), never required by the primary manuscript.
- No metabolomics (all metabolomics rows in the specification are not selected).
- No WGS or unrestricted genome-wide genotypes; therefore no genome-wide ancestry principal components (D08).
- No direct psychophysical taste test. Self-reported taste items exist (口の健康状態「味覚について」, ph1 only) and are not used as confirmatory phenotypes.

## Medication section (both waves)
Past-two-week use; up to 45 slots; per slot: product/ingredient text, KEDD ID, Drug ID, prescription vs other acquisition, duration and unit, frequency and unit, amount per administration and unit. Normalization hierarchy: PRIMARY Drug ID / KEDD ID; SECONDARY structured fields; TERTIARY free text (QC, brand, formulation, release form, route, fallback identification only) (`08`).

## SNP delivery
The SNP list is taken only from the delivered SNP file/manifest. SNP availability is not invented and no dry-frozen SNP is assumed to be delivered; testability states are assigned deterministically at receipt (`05`).

## Acceptable unknowns at timestamp
File paths, exact column names, codebook values, SNP availability, event counts. All are bound through `config/variable_map.yaml` as logged technical changes before any outcome model runs (`16`, `23`).
