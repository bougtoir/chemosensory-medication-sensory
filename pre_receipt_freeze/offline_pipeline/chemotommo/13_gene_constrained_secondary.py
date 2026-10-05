"""13 Family B: Level-B SNPs in approved genes x ANY_MEDICATION_CHANGE (BH q=0.05); gene summaries. Never confirmatory."""
import pandas as pd

from chemotommo._common import adjust, suite_endpoints


def run(ctx):
    f = ctx.cfg["analysis_config"]["families"]["B"]
    ads = ctx.t["ads"]
    cols = [c for c in ads.columns if c.startswith("B__")]
    res = suite_endpoints(ctx, ads, cols, [f["endpoint"]]) if cols else pd.DataFrame(
        columns=["test", "variant", "outcome", "status", "n", "events", "beta", "se", "z", "p", "odds_ratio"])
    res = adjust(res, f["method"], f["q"])
    res["gene"] = res["variant"].str.split("__").str[1]
    res["family"] = "B"
    ctx.result("13_family_B", res)
    if len(res):
        g = res.groupby("gene").agg(n_snps=("variant", "size"), n_tested=("status", lambda s: int((s == "TESTED").sum())),
                                    min_p=("p", "min"), n_reject=("reject", "sum")).reset_index()
        ctx.result("13_gene_summary", g)
