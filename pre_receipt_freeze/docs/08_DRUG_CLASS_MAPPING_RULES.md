# 08 — Drug identification and class mapping rules

Status: FINAL PRE-RECEIPT FREEZE. Config: `offline_pipeline/config/drug_dictionary.yaml`. Modules 04–06.

## Identification hierarchy (D10)
1. Drug ID (if valid in the delivered Drug ID master).
2. KEDD ID (if valid in the delivered KEDD master).
3. Free text, parsed by the frozen medication parser v1.0.0 (`71_MEDICATION_PARSER/medication_parser.py`, SHA-256 c722341a…a99de), used only when no valid structured ID exists.
Conflicts between Drug ID and KEDD ID: Drug ID wins; conflict flagged. Unknown IDs are flagged (`drug_id_unknown`, `kedd_unknown`) and the row falls through to the next level; unresolved rows are excluded from ingredient-based endpoints and counted. NLP/free-text parsing is never the primary method when structured IDs are available.

## Uses of free text
QC (genotype-blind), brand resolution, formulation and release-form identification, route inference, reconciliation when structured IDs are absent.

## Ingredient normalization
Ingredients from masters (`;`-separated INN, lower case) or the parser are canonicalized through `ingredient_aliases` (e.g., methimazole → thiamazole, acetaminophen → paracetamol, chlorpheniramine → chlorphenamine). Same ingredient under different brands maps to one ingredient.

## Classification database
KEGG ATC hierarchy br08303, stored offline at `data/raw_atc_20261004/br08303.json` (1,170,593 bytes, SHA-256 69c3d45d9131312b005b5bd7db9a86b6bf27f63bbdccf713427eca89977e672a; release info `kegg_info.txt` 3b2e7698…ace3; ledger `LEDGER.csv`). The pipeline refuses to run if the hash differs. Use is academic, offline, and the snapshot is not redistributed in the public registration (`20`). ATC codes given by the delivered master take precedence; otherwise by-name lookup (with `atc_name_synonyms`).

## Class rules
- Same therapeutic class = shared ATC level-4 code (used by WITHIN_CLASS_SWITCH).
- Revised-plan categories (Family C2): antihypertensive C02/C03/C07/C08/C09; statin C10AA; NSAID M01A; digestive A02/A03/A06/A07; metformin A10BA02.
- Supplement/health food = non-prescription row with no ATC code (N12, S11).
- Prediction and control drug sets are fixed in `prediction_drugs` / `negative_control_drugs`; formulation terms use the parser vocabulary exactly (test `test_parser_vocabulary`).

## Real-string QC gate (post-receipt, genotype-blind)
Before outcome models: draw 300–500 real medication strings blind to genotype, adjudicate, require ≥95% field accuracy for parser fields (92). Failure → formulation module not testable (`11`); primary analyses unaffected because they use structured IDs.
