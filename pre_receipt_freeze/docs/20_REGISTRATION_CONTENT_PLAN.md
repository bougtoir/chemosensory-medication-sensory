# 20 — Registration content plan

## Public layer (registration + public mirror)
Theory and hypotheses; approved-protocol mapping at scope-summary level; SNP hierarchy (gene/variant/prediction level); endpoint algorithms; dose rules; class rules; FFQ lock (food items, derivation, direction, gene); negative controls; SAP; multiple testing; calibration; formulation rules; interpretation matrix; offline code; synthetic generator and tests; environment specification; manifest; SHA-256 checksums; amendment policy; instruction register, decision log, amendment log, completeness audit.

## Restricted layer (never redistributed)
`tommo申請書.docx`, `tommo研究計画.docx`, `tommoデータセット.xlsx`, any ToMMo participant-level data, KEGG br08303 snapshot body and other third-party record-level raw downloads (PubMed XML, PubChem/BitterDB responses, Ensembl responses). They are represented only by filename, SHA-256, document date and scope summary (`22`). Public-mirror sync must list them in EXCLUDE_MAP.

## Registration fields
Hypothesis; theory; primary/secondary endpoints; variant hierarchy; controls; multiple testing; calibration; formulation module; interpretation rules; success/refutation criteria (`26`, legacy 85); amendment policy (`24`); timestamp evidence (archive SHA-256 + independent timestamp record).
