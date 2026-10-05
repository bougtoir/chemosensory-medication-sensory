"""01 inventory: file-level hashes and shapes only (no content is read into outputs)."""
from pathlib import Path

import pandas as pd

from chemotommo._common import find_files, read_table, sha256


def run(ctx):
    rows = []
    for key in ctx.cfg["variable_map"]["files"]:
        files = find_files(ctx, key)
        if not files:
            rows.append(dict(key=key, file="", bytes=0, sha256="", n_rows=0, n_cols=0, present=False))
            continue
        df = read_table(ctx, key)
        for f in files:
            rows.append(dict(key=key, file=Path(f).name, bytes=Path(f).stat().st_size, sha256=sha256(f),
                             n_rows=len(df), n_cols=df.shape[1], present=True))
    inv = pd.DataFrame(rows)
    ctx.result("01_inventory", inv)
    ctx.note(f"inventory: {inv['present'].sum()} of {len(inv)} file keys present")
