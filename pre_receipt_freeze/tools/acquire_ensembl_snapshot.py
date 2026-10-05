"""Persist Ensembl REST annotations used to freeze effect alleles and approved-gene regions.

- VEP for frozen Level-A variants (amino-acid allele assignment, GRCh38).
- Gene coordinates of the 20 approved genes on GRCh38 and GRCh37.
Never overwrites an existing snapshot; writes LEDGER.csv (URL, UTC, bytes, SHA-256, usage).
"""
import csv, datetime as dt, hashlib, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RSIDS = ["rs713598", "rs1726866", "rs10246939", "rs3741845", "rs12033832", "rs10772420", "rs11988795"]
GENES = ["TAS1R1", "TAS1R2", "TAS1R3", "TAS2R8", "TAS2R9", "TAS2R10", "TAS2R14", "TAS2R16", "TAS2R38",
         "TAS2R46", "SCNN1A", "SCNN1B", "SCNN1G", "SCNN1D", "OTOP1", "GNAT3", "GNG13", "PLCB2", "ITPR3", "TRPM5"]
USAGE = "Ensembl data: no restrictions on use (https://www.ensembl.org/info/about/legal/disclaimer.html)."


def get(url):
    for attempt in range(10):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception:
            time.sleep(2 + 3 * attempt)
    raise RuntimeError(url)


def main(stamp):
    dest = ROOT / "data" / f"raw_ensembl_{stamp}"
    if dest.exists():
        sys.exit(f"{dest} exists; snapshots are never overwritten")
    (dest / "vep").mkdir(parents=True); (dest / "genes").mkdir()
    jobs = [(f"vep/{r}.json", f"https://rest.ensembl.org/vep/human/id/{r}?content-type=application/json") for r in RSIDS]
    for g in GENES:
        jobs.append((f"genes/{g}_GRCh38.json", f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{g}?content-type=application/json"))
        jobs.append((f"genes/{g}_GRCh37.json", f"https://grch37.rest.ensembl.org/lookup/symbol/homo_sapiens/{g}?content-type=application/json"))
    rows = []
    for name, url in jobs:
        t = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        body = get(url); json.loads(body)
        (dest / name).write_bytes(body)
        rows.append(dict(file=name, url=url, query="GET", retrieved_utc=t, bytes=len(body),
                         sha256=hashlib.sha256(body).hexdigest(), conditions="unauthenticated REST GET",
                         storage=str((dest / name).relative_to(ROOT)), usage_conditions=USAGE))
        time.sleep(0.2)
    with open(dest / "LEDGER.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        p = ROOT / r["storage"]
        assert p.stat().st_size == r["bytes"] and hashlib.sha256(p.read_bytes()).hexdigest() == r["sha256"]
    print(f"{len(rows)} files -> {dest}; verified")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else dt.date.today().strftime("%Y%m%d"))
