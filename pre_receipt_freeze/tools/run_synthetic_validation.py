#!/usr/bin/env python3
"""Generate synthetic PH1/PH2 data, run the full offline pipeline twice in fresh processes, and persist
the privacy-safe export, fixed edge-case endpoints and a determinism ledger to synthetic_validation/."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "offline_pipeline"
DEST = ROOT / "synthetic_validation"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd, env):
    subprocess.run([sys.executable, *cmd], check=True, env=env, stdout=subprocess.DEVNULL)


def main():
    env = {"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0", "MPLBACKEND": "Agg", "SOURCE_DATE_EPOCH": "1791072000",
           "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9"}
    tmp = Path(tempfile.mkdtemp(prefix="chemotommo_syn_"))
    data, outs = tmp / "data", [tmp / "run1", tmp / "run2"]
    run([str(PIPE / "synthetic" / "make_synthetic.py"), "--out", str(data)], env)
    for o in outs:
        run([str(PIPE / "run_pipeline.py"), "--data", str(data), "--out", str(o), "--mode", "synthetic"], env)
    exp = [sorted(p for p in (o / "export").iterdir() if p.suffix in (".csv", ".json")) for o in outs]
    hashes = [{p.name: sha(p) for p in e} for e in exp]
    if DEST.exists():
        shutil.rmtree(DEST)
    (DEST / "export").mkdir(parents=True)
    for p in (outs[0] / "export").iterdir():
        shutil.copy2(p, DEST / "export" / p.name)
    ep = pd.read_csv(outs[0] / "work" / "08_endpoints.csv")
    ep[ep["pid"].str.startswith("S")].sort_values("pid").to_csv(DEST / "fixed_case_endpoints.csv", index=False)
    ledger = dict(
        generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        participant_level_tommo_data_used=False,
        synthetic_inputs={p.name: sha(p) for p in sorted(data.iterdir()) if p.is_file()},
        run1_export=hashes[0], run2_export=hashes[1],
        deterministic=hashes[0] == hashes[1],
    )
    (DEST / "RUN_LEDGER.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    shutil.rmtree(tmp)
    print("deterministic:", ledger["deterministic"], "->", DEST)
    sys.exit(0 if ledger["deterministic"] else 1)


if __name__ == "__main__":
    main()
