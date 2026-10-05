"""06 drug class mapping: ingredient -> ATC level 5 / level 4 using master ATC codes first, then the frozen
KEGG br08303 snapshot by name. Defines supplement rows (not prescribed and no ATC code)."""
import pandas as pd

from chemotommo._common import atc_level, load_atc_index, sha256


def run(ctx):
    dd = ctx.cfg["drug_dictionary"]
    p = ctx.path(dd["atc_snapshot"]["path"])
    if sha256(p) != dd["atc_snapshot"]["sha256"]:
        raise RuntimeError("ATC snapshot hash differs from frozen value")
    by_name, _ = load_atc_index(p)
    ing = ctx.t["ing_rows"]
    syn = dd.get("atc_name_synonyms", {})
    atc5 = {}
    for rec in ing[["ingredient", "atc_master"]].dropna(subset=["ingredient"]).drop_duplicates().to_dict("records"):
        codes = set(x for x in str(rec["atc_master"]).split(";") if len(x) >= 5) if rec["atc_master"] else set()
        nm = rec["ingredient"]
        atc5.setdefault(nm, set()).update(codes or by_name.get(nm, set()) or by_name.get(syn.get(nm, ""), set()))
    atc4 = {k: atc_level(v, dd["atc_snapshot"]["class_level"]) for k, v in atc5.items()}
    ing["has_atc"] = ing["ingredient"].map(lambda i: bool(atc5.get(i)))
    ing["supplement"] = (~ing["rx"]) & (~ing["has_atc"])
    ctx.t["atc5_of"], ctx.t["atc4_of"] = atc5, atc4
    tab = pd.DataFrame([dict(ingredient=k, atc5=";".join(sorted(v)), atc4=";".join(sorted(atc4[k]))) for k, v in sorted(atc5.items())])
    ctx.result("06_ingredient_atc_map", tab)
    ctx.note(f"ATC: {sum(bool(v) for v in atc5.values())}/{len(atc5)} ingredients classified")
