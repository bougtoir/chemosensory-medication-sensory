#!/usr/bin/env python3
"""Scrape BitterDB receptor->ligand map (human receptors only).

Saves raw HTML under data/raw/bitterdb/ and writes
evidence/bitterdb_receptor_ligands.csv (receptor, uniprot, compound_id,
compound_name) and evidence/bitterdb_compounds.csv.
"""
import re, time, urllib.request, hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "bitterdb"
RAW.mkdir(parents=True, exist_ok=True)
BASE = "https://bitterdb.agri.huji.ac.il"

def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    for a in range(3):
        try:
            return urllib.request.urlopen(r, timeout=40).read()
        except Exception:
            if a == 2: raise
            time.sleep(3)

home = get(f"{BASE}/dbbitter.php").decode("utf-8", "replace")
(RAW / "dbbitter_home.html").write_text(home)
rec_ids = sorted(set(int(m) for m in re.findall(r'Receptor\.php\?id=(\d+)', home)))
print("receptor ids found:", len(rec_ids))

rows, ledger = [], []
for rid in rec_ids:
    html = get(f"{BASE}/Receptor.php?id={rid}").decode("utf-8", "replace")
    (RAW / f"receptor_{rid}.html").write_text(html)
    # receptor name/species from title block
    m = re.search(r'<h[23][^>]*>\s*(TAS\w+|T2R\w+|[A-Za-z0-9 ]*TAS2R\d+)\s*', html)
    gene = ""
    g = re.search(r'>\s*(TAS2R\d+|TAS1R\d+)\s*<', html)
    if g: gene = g.group(1)
    else:
        g2 = re.search(r'(TAS2R\d+|TAS1R\d+)', html)
        gene = g2.group(1) if g2 else f"id{rid}"
    human = bool(re.search(r'Homo\s*sapiens|human', html, re.I))
    n_lig = 0
    if human:
        for cid, name in re.findall(r'compound\.php\?id=(\d+)"[^>]*>([^<]+)</a>', html):
            rows.append({"receptor_id": rid, "receptor": gene,
                         "compound_id": int(cid), "compound_name": name.strip()})
            n_lig += 1
    ledger.append({"receptor_id": rid, "receptor": gene, "human_page": human,
                   "n_ligands": n_lig, "sha256_16": hashlib.sha256(html.encode()).hexdigest()[:16]})
    time.sleep(0.3)

df = pd.DataFrame(rows).drop_duplicates()
df.to_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv", index=False)
pd.DataFrame(ledger).to_csv(RAW / "bitterdb_ledger.csv", index=False)
comp = df[["compound_id", "compound_name"]].drop_duplicates().sort_values("compound_id")
comp.to_csv(ROOT / "evidence" / "bitterdb_compounds.csv", index=False)
print("edges:", len(df), "| receptors with ligands:", df.receptor.nunique(), "| compounds:", len(comp))
print(df.receptor.value_counts().to_string())
