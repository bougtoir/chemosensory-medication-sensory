"""12 Family A (P01, P02, P05; Holm) and Family AS (P03, P04, P07, P08, P12; BH q=0.10):
frozen variant x drug-specific change-away outcome among ph1 users (06 section 4)."""
from chemotommo._common import adjust, suite_predictions


def run(ctx):
    ac, dd = ctx.cfg["analysis_config"], ctx.cfg["drug_dictionary"]
    ads, rows, daily = ctx.t["ads"], ctx.t["rows_scope"], ctx.t["daily_scope"]
    for fam in ("A", "AS"):
        f = ac["families"][fam]
        res = suite_predictions(ctx, ads, rows, daily, f["tests"], dd["prediction_drugs"])
        res = adjust(res, f["method"], f.get("alpha", f.get("q")))
        res["family"], res["sign"] = fam, res["test"].map(ac["prediction_sign"])
        res["direction_as_predicted"] = (res["beta"] * res["sign"]) > 0
        ctx.result(f"12_family_{fam}", res)
