"""11 analysis dataset + analysis-set lock (hash of participant set, configs, parser, ATC snapshot, code)."""
import datetime as dt
import os
import hashlib
import json

import pandas as pd

from chemotommo._common import PKG, sha256


def _now():
    """SOURCE_DATE_EPOCH (reproducible-build convention) fixes the lock time in synthetic validation."""
    e = os.environ.get("SOURCE_DATE_EPOCH")
    t = dt.datetime.fromtimestamp(int(e), dt.timezone.utc) if e else dt.datetime.now(dt.timezone.utc)
    return t.isoformat(timespec="seconds")


def code_hash():
    h = hashlib.sha256()
    for p in sorted(PKG.glob("*.py")):
        h.update(p.name.encode()); h.update(p.read_bytes())
    return h.hexdigest()


def run(ctx):
    ac, sm = ctx.cfg["analysis_config"], ctx.cfg["snp_map"]
    ans, geno, ep, cov, ffq = ctx.t["answered"], ctx.t["geno"], ctx.t["endpoints"], ctx.t["cov"], ctx.t["ffq"]
    flow = [dict(step="medication section present in >=1 wave", n=len(ans))]
    both = ans[ans["ph1_answered"] & ans["ph2_answered"]]
    flow.append(dict(step="both waves answered", n=len(both)))
    df = both[["pid"]].merge(cov, on="pid", how="left")
    if "age" in df:
        df = df[df["age"] >= ac["population"]["min_age_ph1"]]
    flow.append(dict(step=f"age >= {ac['population']['min_age_ph1']} at ph1", n=len(df)))
    la = [v for v in sm["level_a"] if v in geno.columns]
    if ac["population"]["require_genotype_qc_pass"]:
        ok = geno.loc[geno[la].notna().any(axis=1), "pid"] if la else pd.Series(dtype=object)
        df = df[df["pid"].isin(set(ok))]
    flow.append(dict(step="genotype available (>=1 Level-A variant after QC)", n=len(df)))
    df = df.merge(geno, on="pid", how="left").merge(ep, on="pid", how="left").merge(ffq, on="pid", how="left")
    ctx.t["ads"] = df
    ctx.work("11_analysis_dataset", df)
    ctx.result("11_flow", pd.DataFrame(flow))
    pid_hash = hashlib.sha256("\n".join(sorted(map(str, df["pid"]))).encode()).hexdigest()
    lock = dict(created_utc=_now(), mode=ctx.mode,
                n_participants=len(df), participant_set_sha256=pid_hash, columns=list(df.columns),
                config_sha256={p.name: sha256(p) for p in sorted(ctx.cfg_dir.glob("*.yaml"))},
                parser_sha256=sha256(ctx.path(ctx.cfg["drug_dictionary"]["free_text"]["parser"])),
                atc_snapshot_sha256=sha256(ctx.path(ctx.cfg["drug_dictionary"]["atc_snapshot"]["path"])),
                code_sha256=code_hash())
    (ctx.out_dir / "results" / "11_analysis_set_lock.json").write_text(json.dumps(lock, indent=2))
    ctx.t["lock"] = lock
