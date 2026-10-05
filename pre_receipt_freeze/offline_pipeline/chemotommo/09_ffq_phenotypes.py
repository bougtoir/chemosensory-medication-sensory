"""09 FFQ phenotypes: locked chemosensory phenotypes F01-F08 per wave (09_CHEMOSENSORY_FFQ_LOCK)."""
import numpy as np
import pandas as pd

from chemotommo._common import read_table


def run(ctx):
    fl, idc = ctx.cfg["ffq_lock"], ctx.cfg["variable_map"]["id_column"]
    fmap = {int(k): v for k, v in fl["frequency_to_per_day"].items()}
    out = None
    for wave in ("ph1", "ph2"):
        df = read_table(ctx, f"ffq_{wave}")
        if df is None:
            continue
        w = pd.DataFrame({"pid": df[idc]})
        items = {}
        for name, spec in fl["items"].items():
            col = spec[wave]
            if col not in df:
                continue
            v = pd.to_numeric(df[col], errors="coerce")
            if spec.get("type") == "binary":
                yes, no = set(fl["binary_yes_values"]), set(fl["binary_no_values"])
                items[name] = v.map(lambda x: 1.0 if x in yes else (0.0 if x in no else np.nan))
                continue
            items[name] = v.map(lambda x: fmap.get(int(x)) if pd.notna(x) and int(x) in fmap else np.nan)
        for pid_, ph in fl["phenotypes"].items():
            avail = [items[i] for i in ph["items"] if i in items]
            if len(avail) != len(ph["items"]):
                continue
            if ph["transform"] in ("binary", "binary_any"):
                w[f"{pid_}_{wave}"] = pd.concat(avail, axis=1).max(axis=1, skipna=True)
            else:
                w[f"{pid_}_{wave}"] = np.log1p(pd.concat(avail, axis=1).sum(axis=1, min_count=len(avail)))
        out = w if out is None else out.merge(w, on="pid", how="outer")
    ctx.t["ffq"] = out if out is not None else pd.DataFrame(columns=["pid"])
    ctx.work("09_ffq_phenotypes", ctx.t["ffq"])
    ctx.result("09_ffq_availability", pd.DataFrame([dict(phenotype=c, n_nonmissing=int(ctx.t["ffq"][c].notna().sum()))
                                                    for c in ctx.t["ffq"].columns if c != "pid"]))
