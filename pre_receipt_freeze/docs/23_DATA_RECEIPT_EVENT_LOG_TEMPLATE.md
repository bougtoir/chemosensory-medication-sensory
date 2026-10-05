# 23 — Data receipt event log (template)

Fill in at receipt. No association model may run before every row of section B is complete and section C is signed.

## A. Receipt
| Field | Value |
|---|---|
| Receipt timestamp (UTC) | |
| Received by | |
| Delivery medium / channel | |
| Offline storage location (no network) | |
| Freeze archive SHA-256 verified before opening (yes/no) | |
| Independent timestamp reference of the freeze archive | |

## B. Files received
| File | Bytes | SHA-256 | Family key bound in variable_map.yaml |
|---|---|---|---|
| | | | |

## C. Genotype-blind QC (`run_pipeline.py --mode real --stage qc`, then `--stage lock`)
| Check | Result | Output |
|---|---|---|
| 1 file inventory | | 01_inventory.csv |
| 2 variable mapping (technical change log entry + hash) | | 02_variable_mapping.csv |
| 3 participant counts / both-wave set | | 11_analysis_set_lock.json |
| 4 SNP availability, QC, testability states | | 03_snp_status.csv |
| 5 medication field / ID resolution coverage | | 04_id_resolution_qc.csv |
| 6 parser real-string QC (300–500 strings, blind) | | receipt/parser_realstring_qc.csv |
| 7 missingness and endpoint counts without genotype | | 08_endpoint_counts.csv |

## D. Sign-off
`receipt/RECEIPT_SIGNOFF.json`: {"signed_by": "", "signed_utc": "", "freeze_archive_sha256": "", "parser_realstring_gate": "PASS|FAIL|NOT RUN", "variable_map_sha256": "", "analysis_set_lock_sha256": "", "technical_changes": []}

`run_pipeline.py --mode real --stage analysis` refuses to run unless this file exists, `variable_map_sha256` equals the current `config/variable_map.yaml` hash, and `analysis_set_lock_sha256` equals the lock written at `--stage lock`; the recomputed lock (participant set, config, parser, ATC snapshot and code hashes) must also match.

## E. Deviations
| Time | Deviation | Class (clerical/technical/analytic) | Amendment ID |
|---|---|---|---|
