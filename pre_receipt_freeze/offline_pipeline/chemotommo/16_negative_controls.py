"""16 Family F negative controls (N01-N10, N12; N11 requires amendment). Failure = p<0.05 in paired positive direction."""
import pandas as pd

from chemotommo._common import suite_predictions


def run(ctx):
    ac, dd = ctx.cfg["analysis_config"], ctx.cfg["drug_dictionary"]
    ads = ctx.t["ads"]
    all_rows = ctx.t["ing_rows"].dropna(subset=["ingredient"])
    all_rows = all_rows[all_rows["pid"].isin(set(ads["pid"]))]
    rx_rows = all_rows[all_rows["rx"]]
    collapse = ctx.t["collapse"]
    res = []
    for nid, (var, paired) in ac["negative_controls"].items():
        spec = dd["negative_control_drugs"][nid]
        rows = all_rows if spec.get("supplement") else rx_rows
        r = suite_predictions(ctx, ads, rows, collapse(rows), [nid], {nid: spec}, variant_override={nid: var})
        r["paired_prediction"], r["paired_sign"] = paired, ac["prediction_sign"][paired]
        res.append(r)
    df = pd.concat(res, ignore_index=True)
    df["failure"] = (df["status"] == "TESTED") & (df["p"] < 0.05) & (df["beta"] * df["paired_sign"] > 0)
    df = pd.concat([df, pd.DataFrame([dict(test="N11", status="REQUIRES PROTOCOL AMENDMENT (TRPA1 outside approved genes)")])],
                   ignore_index=True)
    df["family"] = "F"
    ctx.result("16_family_F", df)
    tested = int((df["status"] == "TESTED").sum())
    fails = int(df["failure"].eq(True).sum())
    ctx.t["controls_behave"] = fails <= ac["controls_behave_max_failures"]
    ctx.result("16_control_summary", pd.DataFrame([dict(n_controls=len(df), n_tested=tested, n_failures=fails,
                                                        max_failures=ac["controls_behave_max_failures"],
                                                        controls_behave=ctx.t["controls_behave"])]))
