"""Persist the KEGG BRITE ATC hierarchy (br08303) as a frozen drug-class database.

Never overwrites an existing snapshot. Writes LEDGER.csv with URL, UTC time,
size, SHA-256 and usage conditions. KEGG content stays under data/ (excluded
from public sync); only its hash enters the public freeze package.
"""
import csv, datetime as dt, hashlib, json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URLS = {
    "br08303.json": "https://rest.kegg.jp/get/br:br08303/json",
    "kegg_info.txt": "https://rest.kegg.jp/info/kegg",
}
USAGE = ("KEGG: academic use of the website/REST API is free; bulk redistribution is not "
         "permitted (https://www.kegg.jp/kegg/legal.html). Stored locally only.")


def main(stamp):
    dest = ROOT / "data" / f"raw_atc_{stamp}"
    if dest.exists():
        sys.exit(f"{dest} exists; snapshots are never overwritten")
    dest.mkdir(parents=True)
    rows = []
    for name, url in URLS.items():
        t = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        body = urllib.request.urlopen(url, timeout=120).read()
        (dest / name).write_bytes(body)
        rows.append(dict(file=name, url=url, query="GET", retrieved_utc=t, bytes=len(body),
                         sha256=hashlib.sha256(body).hexdigest(), conditions="unauthenticated REST GET",
                         storage=str((dest / name).relative_to(ROOT)), usage_conditions=USAGE))
    json.loads((dest / "br08303.json").read_text())
    with open(dest / "LEDGER.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        p = ROOT / r["storage"]
        assert p.stat().st_size == r["bytes"] and hashlib.sha256(p.read_bytes()).hexdigest() == r["sha256"]
    print(f"{len(rows)} files -> {dest}; verified")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else dt.date.today().strftime("%Y%m%d"))
