# 19 — Data Provenance

All raw external data persisted locally under `data/raw/` with hashes in
ledger files (see `data/raw/*/…ledger*.csv`). Third-party record-level
data are not republished; aggregates and code only.

## Retrieval log

| Source | What | Date (UTC) | Raw location | Ledger |
|--------|------|-----------|--------------|--------|
| PubMed eutils | 20-query Stage 1 battery + 10 seed queries + anchor fetches (XML) | 2026-10-04 | `data/raw/pubmed/*.xml` | `search_ledger.csv`, `seed_ledger.csv` (sha256 per response) |
| BitterDB | 236 receptor pages scraped; 26 human receptors, 1,108 receptor→ligand edges, 644 compounds | 2026-10-04 | `data/raw/bitterdb/receptor_*.html` | `bitterdb_ledger.csv` |
| PubChem PUG-REST | 197 oral/parenteral compounds × 11 descriptors | 2026-10-04 | `data/raw/pubchem/*.json` | `pubchem_ledger.csv` |

## Processing chain

```
scripts/01_pubmed_search.py     -> evidence/search_pool.csv (5,125 PMIDs)
scripts/02_bitterdb_scrape.py   -> evidence/bitterdb_receptor_ligands.csv
scripts/03_pubchem_drug_space.py -> prediction/drug_chemical_space.csv
scripts/04_curate_evidence.py   -> 03/04/05/06 evidence CSVs (78 studies)
scripts/05_evidence_graph.py    -> 07/08 graph (163 nodes, 150 edges)
scripts/06_meta_analysis.py     -> 09_META_ANALYSIS/
scripts/07_matrices_predictions.py -> 11/12/13
scripts/08_figures.py           -> figures/fig1..7.png
```

Deterministic seed: 20261004. Python 3.10, pandas 2.3.3, scipy 1.15.3,
matplotlib (system). No random components in the pipeline.

## Curation policy

Extracted fields (n, effect, P) are transcribed from abstracts only;
fields not in abstracts are left empty. Bibliographic metadata
(title/journal/year/DOI) is pulled programmatically from PubMed records —
never hand-typed — so citations are verifiable by construction.

## Known limits

- Five Stage-1 queries hit the retmax=400 cap; the pool is a rich sample,
  not an exhaustive census. Flagged in `search_ledger.csv` (n_ids=400).
- Abstract-level extraction understates effect-size capture vs full-text
  review; flagged fields are empty rather than estimated.
- BitterDB aggregates heterogeneous assays; per-edge assay detail was not
  retrieved beyond the receptor-page level.
