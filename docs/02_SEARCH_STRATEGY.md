# 02 — Search Strategy (frozen)

## Sources

| Source | Use | Access | Retrieved |
|--------|-----|--------|-----------|
| PubMed (NCBI eutils) | primary bibliographic search | https://eutils.ncbi.nlm.nih.gov/entrez/eutils | 2026-10-04 UTC |
| BitterDB (HUJI) | TAS2R–ligand evidence table | https://bitterdb.agri.huji.ac.il | 2026-10-04 UTC |
| PubChem PUG-REST | drug physicochemical descriptors | https://pubchem.ncbi.nlm.nih.gov/rest/pug | 2026-10-04 UTC |

Retrieval-date-stamped raw responses are stored under `data/raw/` with SHA-256 digests (`data/raw/pubmed/search_ledger.csv`, `data/raw/provenance_ledger.csv`).

## Query battery

The executable query set lives in `scripts/01_pubmed_search.py` (`QUERIES`). Layers:

- **1B** genotype → human sensory phenotype (TAS2R38/PROP-PTC; TAS2R variants; TAS1R sweet/umami; SCNN1/ENaC salt; OTOP1 sour)
- **1C** drug → chemosensory receptor/sensory response (receptor assays; human taste panels)
- **1D** genotype → drug sensory response (the critical layer)
- **1E** sensory phenotype → medication behavior (adherence, acceptance, formulation preference)
- **1F** environment/training → taste plasticity (salt reduction, sweet reduction, repeated exposure)
- **1G** extraoral TAS2R biology (competing mechanism)
- **1H** evolutionary framing
- **NEG** negative-control searches (failed replication, ancestry/linkage confounding, publication bias, adherence confounding)
- **REV** reviews for framing only (never a substitute for primary evidence)

Filters: `humans[MeSH Terms]` where the layer requires human evidence; no date restriction; English abstracts retrieved. `retmax=400` per query; any query hitting the cap is flagged in the ledger (none did at freeze — see ledger).

## Inclusion / exclusion

**Include:** human sensory measurements (intensity, detection/recognition threshold, pleasantness, preference, consumption); cell-based TAS2R/TAS1R functional assays with quantitative potency; randomized or controlled taste-plasticity interventions; medication acceptance/adherence studies that measured or manipulated sensory properties.

**Exclude:** docking-only ligand predictions without experimental validation; animal-only sensory claims used to support a *human* arrow (animals may support mechanism, flagged as such); non-oral routes for oral-sensory claims; studies where "taste" is only an unmeasured clinician impression.

## Snowballing

Cited references inside included papers and BitterDB per-receptor source lists were used to seed targeted follow-up esearch/efetch calls (recorded in the ledger as `seed_*` queries when run).

## Synthesis rules

- ≥3 reasonably comparable studies → quantitative synthesis (`meta_analysis/`).
- Otherwise structured effect-direction synthesis; phenotypes (intensity vs threshold vs pleasantness vs preference vs intake) are **never** pooled across constructs.
- Every extracted edge retains citation, design, human/non-human, N, effect, 95% CI, P, replication status, evidence grade.
