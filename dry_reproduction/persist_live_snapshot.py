#!/usr/bin/env python3
"""Persist a live re-acquisition (scripts 01-03 run in a separate checkout) as a
new, dated raw snapshot next to the frozen data/raw/ tree, without touching it.

PubMed XML is stored gzip-compressed (mtime=0, deterministic); the ledger
records SHA-256/size of both the original bytes and the stored file.

Usage: python3 dry_reproduction/persist_live_snapshot.py LIVE_CHECKOUT SNAPSHOT_NAME
"""
import csv
import datetime as dt
import gzip
import hashlib
import shutil
import sys
import urllib.parse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
USAGE = {
    "pubmed": "NCBI E-utilities; PubMed records (NLM terms; citation metadata/abstracts may be copyrighted) — local use only, not for public mirrors",
    "bitterdb": "BitterDB (https://bitterdb.agri.huji.ac.il) page snapshots; academic use, cite Dagan-Wiener et al. 2019 — local use only",
    "pubchem": "PubChem PUG-REST (public domain data, NCBI usage policy)",
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(live, name):
    live = Path(live)
    dest = ROOT / "data" / name
    if dest.exists():
        sys.exit(f"{dest} exists; snapshots are never overwritten")
    rows = []
    pm = pd.read_csv(live / "data/raw/pubmed/search_ledger.csv")
    qmap = {f"{r.layer}_{r.label}.xml": r.query for _, r in pm.iterrows()}
    for src_dir in ["pubmed", "bitterdb", "pubchem"]:
        sd = live / "data" / "raw" / src_dir
        dd = dest / src_dir
        dd.mkdir(parents=True)
        for p in sorted(sd.iterdir()):
            b = p.read_bytes()
            mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if src_dir == "pubmed" and p.suffix == ".xml":
                if p.name not in qmap:
                    continue  # seed/anchor XML copied from the frozen tree, not re-acquired
                out = dd / (p.name + ".gz")
                with open(out, "wb") as fh, gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as gz:
                    gz.write(b)
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=400 + efetch.fcgi?retmode=xml"
                cond = f"query={qmap[p.name]}"
            else:
                out = dd / p.name
                shutil.copy2(p, out)
                if src_dir == "bitterdb" and p.name.startswith("receptor_"):
                    url = f"https://bitterdb.agri.huji.ac.il/Receptor.php?id={p.stem.split('_')[1]}"
                elif src_dir == "bitterdb" and p.name == "dbbitter_home.html":
                    url = "https://bitterdb.agri.huji.ac.il/dbbitter.php"
                elif src_dir == "pubchem" and p.suffix == ".json":
                    url = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                           f"{urllib.parse.quote(p.stem.replace('_', ' '))}/property/.../JSON")
                else:
                    url = "derived ledger written by acquisition script"
                cond = "scripts/0[1-3] unmodified, User-Agent per script"
            ob = out.read_bytes()
            rows.append(dict(source=src_dir, original_file=p.name, stored_path=str(out.relative_to(ROOT)),
                             source_url=url, acquisition_conditions=cond, retrieved_utc=mtime,
                             original_bytes=len(b), original_sha256=sha(b),
                             stored_bytes=len(ob), stored_sha256=sha(ob), usage_conditions=USAGE[src_dir]))
    led = dest / "LEDGER.csv"
    with open(led, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # verify
    bad = 0
    for r in rows:
        ob = (ROOT / r["stored_path"]).read_bytes()
        orig = gzip.decompress(ob) if r["stored_path"].endswith(".gz") else ob
        bad += sha(ob) != r["stored_sha256"] or sha(orig) != r["original_sha256"]
    print(f"{len(rows)} files -> {dest}; verification failures: {bad}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
