#!/usr/bin/env python3
"""Stage 1 literature search — reproducible PubMed query battery.

Runs the frozen query set (docs/02_SEARCH_STRATEGY.md), stores RAW JSON/XML
responses in data/raw/pubmed/, and writes evidence/search_pool.csv
(dedup'd PMIDs with query-layer tags).

NCBI eutils polite use: 3 req/s without API key; we sleep 0.4s between calls.
"""
import json, time, urllib.parse, urllib.request, hashlib, sys
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "pubmed"
RAW.mkdir(parents=True, exist_ok=True)
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# (layer, query_label, pubmed_query)
QUERIES = [
    ("1B", "tas2r38_prop_ptc", '(TAS2R38[Title/Abstract] OR "taste receptor 2 member 38"[Title/Abstract]) AND (PROP OR PTC OR phenylthiocarbamide OR propylthiouracil OR bitterness) AND humans[MeSH Terms]'),
    ("1B", "tas2r_genotype_perception", '(TAS2R*[Title/Abstract]) AND (polymorphism OR variant OR genotype OR haplotype OR SNP) AND (bitterness OR "taste perception" OR threshold OR intensity) AND humans[MeSH Terms]'),
    ("1B", "sweet_umami_genotype", '(TAS1R1 OR TAS1R2 OR TAS1R3) AND (polymorphism OR variant OR genotype OR SNP) AND (sweet OR umami OR "taste perception")'),
    ("1B", "scnn1_salt_genotype", '(SCNN1A OR SCNN1B OR SCNN1G OR SCNN1D OR "ENaC") AND (salt taste OR sodium taste) AND (polymorphism OR variant OR SNP OR genotype)'),
    ("1B", "otop1_sour", '(OTOP1) AND (sour OR acid taste)'),
    ("1C", "drug_bitterness_receptor_assay", '(TAS2R OR "bitter taste receptor" OR "T2R") AND (drug OR pharmaceutical OR medication OR "active pharmaceutical ingredient") AND (activation OR agonist OR antagonist OR EC50 OR "cell-based assay" OR heterologous)'),
    ("1C", "drug_bitter_panel", '(bitterness OR bitter taste) AND (drug OR medicine OR pharmaceutical) AND (panel OR "sensory evaluation" OR palatability) AND humans[MeSH Terms]'),
    ("1D", "genotype_drug_sensory", '(taste receptor OR TAS2R OR TAS1R) AND (polymorphism OR genotype OR variant) AND (drug OR medicine OR medication OR pharmaceutical OR antibiotic OR formulation) AND (taste OR bitterness OR palatability OR acceptance)'),
    ("1D", "tas2r38_medication", 'TAS2R38 AND (medication OR drug OR medicine OR treatment OR adherence OR formulation)'),
    ("1E", "taste_adherence", '(taste OR palatability OR bitterness OR flavor) AND (adherence OR compliance OR acceptance OR refusal OR persistence) AND (medication OR drug OR medicine OR antibiotic OR formulation) AND humans[MeSH Terms]'),
    ("1E", "formulation_behavior", '(formulation OR "oral liquid" OR tablet OR "orodispersible") AND (preference OR acceptance OR "pill swallowing") AND humans[MeSH Terms]'),
    ("1F", "salt_reduction_plasticity", '("salt reduction" OR "sodium reduction" OR "low sodium diet" OR "salt intake") AND (taste OR preference OR threshold OR perception) AND (trial OR intervention OR randomized)'),
    ("1F", "sweet_reduction_plasticity", '("sweet taste" OR sweetness OR "sugar reduction" OR "sweetness reduction") AND (intervention OR trial OR exposure OR training) AND humans[MeSH Terms]'),
    ("1F", "repeated_exposure_bitter", '("repeated exposure" OR "taste exposure" OR "sensory training" OR "flavor learning" OR "taste learning") AND (bitter OR taste OR vegetable OR food) AND humans[MeSH Terms]'),
    ("1G", "extraoral_tas2r", '(TAS2R OR "bitter taste receptor" OR "taste receptor") AND (airway OR "smooth muscle" OR gut OR intestinal OR enteroendocrine OR pancreas OR immune OR respiratory OR nasal OR "solitary chemosensory")'),
    ("1H", "evolution_chemosensation", '(taste receptor OR bitter taste OR chemosensation OR gustation) AND (evolution OR evolutionary OR phylogenetic OR "natural selection")'),
    ("NEG", "tas2r_failed_replication", '(TAS2R OR "taste receptor" OR PROP OR "taster status") AND (replication OR "failed to replicate" OR "no association" OR "not associated" OR null)'),
    ("NEG", "tas2r_publication_bias", '(candidate gene OR "candidate-gene") AND (taste OR TAS2R OR PROP) AND (bias OR replication OR GWAS OR "genome-wide")'),
    ("NEG", "adherence_confounding", '(medication adherence OR persistence) AND (taste OR palatability) AND (confounding OR "health behavior" OR indication)'),
    ("REV", "reviews_framework", '(taste receptor OR chemosensory OR bitter) AND (drug OR pharmacogenomic OR pharmacogenetic) AND review[Publication Type]'),
]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "chemosensory-med-sensory/1.0 (research)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))

def esearch(query, retmax=400):
    u = f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}&term=" + urllib.parse.quote(query)
    return json.loads(get(u))

def efetch_xml(pmids):
    u = f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(pmids)
    return get(u)

def parse_article(art):
    med = art.find(".//MedlineCitation")
    pmid = med.findtext("PMID")
    article = med.find("Article")
    title = "".join(article.find("ArticleTitle").itertext()) if article.find("ArticleTitle") is not None else ""
    journal = article.findtext(".//Journal/Title") or ""
    year = (article.findtext(".//JournalIssue/PubDate/Year")
            or article.findtext(".//ArticleDate/Year") or "")
    authors = []
    for a in article.findall(".//AuthorList/Author")[:6]:
        last, init = a.findtext("LastName"), a.findtext("Initials")
        coll = a.findtext("CollectiveName")
        authors.append(coll or (f"{last} {init}" if last else ""))
    doi = ""
    for aid in art.findall(".//ArticleIdList/ArticleId"):
        if aid.get("IdType") == "doi":
            doi = aid.text or ""
    abst = " ".join("".join(x.itertext()) for x in article.findall(".//Abstract/AbstractText"))
    ptypes = [pt.text for pt in article.findall(".//PublicationTypeList/PublicationType")]
    mesh = [m.findtext("DescriptorName") for m in med.findall(".//MeshHeadingList/MeshHeading")]
    return dict(pmid=pmid, title=title, journal=journal, year=year,
                authors="; ".join(a for a in authors if a), doi=doi,
                abstract=abst, pub_types=";".join(ptypes), mesh=";".join(m for m in mesh if m))

def main():
    rows, ledger = [], []
    for layer, label, q in QUERIES:
        res = esearch(q)
        ids = res["esearchresult"]["idlist"]
        xml = efetch_xml(ids) if ids else b"<PubmedArticleSet/>"
        h = hashlib.sha256(xml).hexdigest()[:16]
        (RAW / f"{layer}_{label}.xml").write_bytes(xml)
        tree = ET.fromstring(xml)
        n = 0
        for art in tree.findall("PubmedArticle"):
            try:
                rec = parse_article(art)
            except Exception:
                continue
            rec["layer"] = layer
            rec["query_label"] = label
            rows.append(rec)
            n += 1
        ledger.append({"layer": layer, "label": label, "n_ids": len(ids),
                       "n_parsed": n, "sha256_16": h, "query": q})
        print(f"{layer}/{label}: {len(ids)} ids, {n} parsed, sha {h}")
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    if not df.empty:
        # one row per PMID; concatenate layer tags
        agg = (df.groupby("pmid", as_index=False)
                 .agg({"layer": lambda s: ";".join(sorted(set(s))),
                       "query_label": lambda s: ";".join(sorted(set(s))),
                       "title": "first", "journal": "first", "year": "first",
                       "authors": "first", "doi": "first", "abstract": "first",
                       "pub_types": "first", "mesh": "first"}))
        agg.to_csv(ROOT / "evidence" / "search_pool.csv", index=False)
        print("pool:", len(agg), "unique PMIDs ->", ROOT / "evidence/search_pool.csv")
    pd.DataFrame(ledger).to_csv(RAW / "search_ledger.csv", index=False)

if __name__ == "__main__":
    main()
