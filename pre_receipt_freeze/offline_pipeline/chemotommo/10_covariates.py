"""10 covariates: frozen covariate set from variable_map; follow-up years; ph1 prescription count; family id."""
import pandas as pd

from chemotommo._common import read_table


def run(ctx):
    vm, idc = ctx.cfg["variable_map"], ctx.cfg["variable_map"]["id_column"]
    cache = {}

    def tab(key):
        if key not in cache:
            cache[key] = read_table(ctx, key)
        return cache[key]

    cov = pd.DataFrame({"pid": ctx.t["answered"]["pid"]})
    for name, spec in vm["covariates"].items():
        t = tab(spec["file"])
        if t is None or spec["column"] not in t:
            ctx.note(f"covariate {name} not delivered")
            continue
        s = t[[idc, spec["column"]]].drop_duplicates(idc).rename(columns={idc: "pid", spec["column"]: name})
        if spec["type"] in ("numeric", "binary"):
            s[name] = pd.to_numeric(s[name], errors="coerce")
        cov = cov.merge(s, on="pid", how="left")
    d = {}
    for wave, spec in vm["questionnaire_date"].items():
        t = tab(spec["file"])
        if t is not None and spec["column"] in t:
            d[wave] = t[[idc, spec["column"]]].rename(columns={idc: "pid", spec["column"]: f"date_{wave}"})
    if len(d) == 2:
        dd = d["ph1"].merge(d["ph2"], on="pid")
        dd["followup_years"] = (pd.to_datetime(dd["date_ph2"], errors="coerce") - pd.to_datetime(dd["date_ph1"], errors="coerce")).dt.days / 365.25
        cov = cov.merge(dd[["pid", "followup_years"]], on="pid", how="left")
    fam = vm.get("family_column")
    if fam:
        for key in ("cohort_profile", "demographics"):
            t = tab(key)
            if t is not None and fam in t:
                cov = cov.merge(t[[idc, fam]].drop_duplicates(idc).rename(columns={idc: "pid", fam: "family_id"}), on="pid", how="left")
                break
    rows = ctx.t["rows_scope"]
    n1 = rows[rows["wave"] == "ph1"].groupby("pid")["ingredient"].nunique()
    cov["n_rx_ph1"] = cov["pid"].map(n1).fillna(0)
    ctx.t["cov"] = cov
    ctx.work("10_covariates", cov)
    ctx.result("10_covariate_missingness", pd.DataFrame([dict(covariate=c, missing_share=float(cov[c].isna().mean()))
                                                         for c in cov.columns if c != "pid"]))
