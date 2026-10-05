"""22 privacy-safe export: copies aggregate results with small-cell suppression; refuses identifier columns
or any cell equal to a participant/family ID. work/ (participant-level) is never exported."""
import json
import shutil

import pandas as pd

from chemotommo._common import sha256

COUNT_COLS = ("n", "events", "exposed_n", "risk_set_n", "n_rows", "n_nonmissing", "n_participants", "n_tested", "n_frozen",
              "n_untestable", "n_snps", "n_controls")
ID_COLS = {"pid", "participant_id", "family_id"}


def suppress(df, k):
    df = df.copy()
    for c in df.columns:
        if c in COUNT_COLS or (c.startswith("n_") and pd.api.types.is_numeric_dtype(df[c])):
            v = pd.to_numeric(df[c], errors="coerce")
            mask = v.notna() & (v > 0) & (v < k)
            df[c] = df[c].astype(object)
            df.loc[mask, c] = f"<{k}"
    return df


def run(ctx):
    k = ctx.cfg["analysis_config"]["testability"]["small_cell_suppression"]
    ids = set(map(str, ctx.t["answered"]["pid"]))
    if "cov" in ctx.t and "family_id" in ctx.t["cov"]:
        ids |= set(map(str, ctx.t["cov"]["family_id"].dropna()))
    exp = ctx.out_dir / "export"
    shutil.rmtree(exp, ignore_errors=True)
    exp.mkdir()
    man = []
    for f in sorted((ctx.out_dir / "results").glob("*")):
        if f.suffix == ".csv":
            df = pd.read_csv(f, dtype=str)
            if ID_COLS & set(df.columns):
                raise RuntimeError(f"identifier column in {f.name}")
            if any(df[c].isin(ids).any() for c in df.columns):
                raise RuntimeError(f"participant identifier value in {f.name}")
            num = pd.read_csv(f)
            suppress(num, k).to_csv(exp / f.name, index=False)
        elif f.suffix == ".json":
            txt = f.read_text()
            if f.name != "11_analysis_set_lock.json" and any(i in txt for i in ids if len(i) >= 4):
                raise RuntimeError(f"participant identifier value in {f.name}")
            shutil.copy(f, exp / f.name)
    for f in sorted((ctx.out_dir / "figures").glob("*.png")):
        shutil.copy(f, exp / f.name)
    for f in sorted(exp.glob("*")):
        man.append(dict(file=f.name, bytes=f.stat().st_size, sha256=sha256(f)))
    pd.DataFrame(man).to_csv(exp / "EXPORT_MANIFEST.csv", index=False)
    (exp / "EXPORT_NOTE.json").write_text(json.dumps(dict(mode=ctx.mode, small_cell_threshold=k,
                                                          participant_level_files_exported=0), indent=2))
