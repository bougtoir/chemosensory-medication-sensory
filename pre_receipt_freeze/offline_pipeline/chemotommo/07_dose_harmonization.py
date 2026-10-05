"""07 dose harmonization: daily amount per row (07_DOSE_HARMONIZATION_RULES) and duplicate collapse."""
import math

import numpy as np
import pandas as pd

from chemotommo._common import harmonize_dose


def collapse(rows):
    """participant-wave-ingredient table; duplicates summed only when all share one non-null basis."""
    out = []
    for (pid, wave, ing), g in rows.dropna(subset=["ingredient"]).groupby(["pid", "wave", "ingredient"]):
        bases = set(g["basis"])
        if len(bases) == 1 and None not in bases and not any(isinstance(b, float) for b in bases):
            daily, basis = float(g["daily"].sum()), next(iter(bases))
        else:
            daily, basis = math.nan, None
        out.append(dict(pid=pid, wave=wave, ingredient=ing, daily=daily, basis=basis, n_rows=len(g), duplicate=len(g) > 1,
                        combination=bool(g["combination"].any()), formulation=";".join(sorted(set(g["formulation"])))))
    return pd.DataFrame(out, columns=["pid", "wave", "ingredient", "daily", "basis", "n_rows", "duplicate", "combination", "formulation"])


def run(ctx):
    ing = ctx.t["ing_rows"]
    res = [harmonize_dose(r["dose_value"], r["dose_unit"], r["frequency_value"], r["frequency_unit"],
                          r["strength_ing_mg"], r["n_ingredients"], r["product_key"]) for r in ing.to_dict("records")]
    ing["daily"] = [x[0] for x in res]
    ing["basis"] = [x[1] for x in res]
    ctx.t["collapse"] = collapse
    ctx.work("07_ingredient_rows_dosed", ing)
    summ = ing.assign(basis_type=ing["basis"].map(lambda b: b.split(":")[0] if isinstance(b, str) else "not_harmonizable"))
    ctx.result("07_dose_harmonization_summary", summ.groupby(["wave", "basis_type"]).size().rename("n_rows").reset_index())
