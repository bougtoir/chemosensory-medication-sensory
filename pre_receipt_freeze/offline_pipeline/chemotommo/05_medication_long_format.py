"""05 long format: one row per (participant, wave, slot, ingredient); combination products expanded."""
import pandas as pd


def run(ctx):
    mr = ctx.t["med_rows"].copy()
    mr["ingredient_list"] = mr["ingredients"].fillna("").map(lambda s: [x for x in s.split(";") if x] or [None])
    mr["strength_list"] = mr["strength_mg"].fillna("").astype(str).map(lambda s: s.split(";") if s else [])
    rows = []
    for rec in mr.to_dict("records"):
        n = len([x for x in rec["ingredient_list"] if x])
        for i, ing in enumerate(rec["ingredient_list"]):
            r = {k: v for k, v in rec.items() if k not in ("ingredient_list", "strength_list")}
            r["ingredient"] = ing
            r["combination"] = n > 1
            sl = rec["strength_list"]
            r["strength_ing_mg"] = pd.to_numeric(sl[i], errors="coerce") if len(sl) == n and n > 0 else (
                pd.to_numeric(sl[0], errors="coerce") if len(sl) == 1 and n == 1 else float("nan"))
            rows.append(r)
    ing = pd.DataFrame(rows)
    ctx.t["ing_rows"] = ing
    ctx.work("05_ingredient_rows", ing)
    ctx.result("05_long_format_summary", pd.DataFrame([dict(
        n_rows=len(mr), n_ingredient_rows=len(ing), n_combination_rows=int(mr["n_ingredients"].gt(1).sum()) if len(mr) else 0,
        n_unresolved_rows=int(mr["unresolved"].sum()) if len(mr) else 0)]))
