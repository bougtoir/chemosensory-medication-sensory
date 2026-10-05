"""14 Family C (Level-A variants x E1-E7; Holm), Family C2 (revised-plan drug categories x ANY change; BH),
secondary log dose-ratio models and cross-sectional exposure presence (secondary only)."""
import math

import pandas as pd

from chemotommo._common import (ENDPOINTS, adjust, compute_endpoints, covariate_types, cluster_col, exposure_presence,
                                fit_linear, fit_logit, model_covariates, suite_endpoints)


def run(ctx):
    family_d(ctx)
    ac, dd = ctx.cfg["analysis_config"], ctx.cfg["drug_dictionary"]
    ads, rows, daily = ctx.t["ads"], ctx.t["rows_scope"], ctx.t["daily_scope"]
    fc = ac["families"]["C"]
    res = adjust(suite_endpoints(ctx, ads, fc["variants"], ENDPOINTS), fc["method"], fc["alpha"])
    res["family"], res["sign"] = "C", ac["family_c_sign"]
    res["direction_as_predicted"] = res["beta"] * res["sign"] > 0
    ctx.result("14_family_C", res)
    # C2: category-restricted ANY change
    f2, out = ac["families"]["C2"], []
    types, cl = covariate_types(ctx), cluster_col(ctx, ads)
    atc5 = ctx.t["atc5_of"]
    for cat, prefixes in dd["drug_categories"].items():
        mask = daily["ingredient"].map(lambda i: any(c.startswith(tuple(prefixes)) for c in atc5.get(i, set()))).astype(bool)
        sub = daily.loc[mask]
        ep = compute_endpoints(sub, ctx.t["atc4_of"], ads["pid"].tolist(), ac["endpoints"]["dose_ratio_increase"],
                               ac["endpoints"]["dose_ratio_decrease"])
        d = ads.assign(_y=ep["ANY_MEDICATION_CHANGE"].values)
        for v in f2["variants"]:
            if v not in d:
                continue
            r = fit_logit(d, "_y", v, model_covariates(ctx, d, "primary", True), types, cl, ac["testability"]["min_events"],
                          ac["testability"]["min_exposed"], exposed_n=int(d["_y"].notna().sum()))
            out.append(dict(test=f"{v}|{cat}", variant=v, outcome=f"ANY_CHANGE[{cat}]", **r))
    c2 = adjust(pd.DataFrame(out), f2["method"], f2["q"]) if out else pd.DataFrame()
    if len(c2):
        c2["family"] = "C2"
    ctx.result("14_family_C2", c2)
    # secondary: continuous dose ratio and cross-sectional exposure presence
    sec = []
    for v in fc["variants"]:
        if v in ads:
            r = fit_linear(ads, "mean_log_dose_ratio", v, model_covariates(ctx, ads, "primary", True), types, cl)
            sec.append(dict(test=f"{v}|mean_log_dose_ratio", variant=v, outcome="mean_log_dose_ratio", analysis="secondary-continuous", **r))
    for pid_, spec in dd["prediction_drugs"].items():
        v = ac["prediction_variant"][pid_]
        if v not in ads:
            continue
        x = exposure_presence(rows, spec, atc5, ads["pid"].tolist(), "ph1")
        d = ads.assign(_x=x.values)
        r = fit_logit(d, "_x", v, model_covariates(ctx, d, "primary"), types, cl, ac["testability"]["min_events"])
        sec.append(dict(test=f"{pid_}|exposure_presence_ph1", variant=v, outcome="EXPOSURE_PRESENCE_PH1",
                        analysis="secondary-cross-sectional", **r))
    s = adjust(pd.DataFrame(sec), "fdr_bh", 0.10) if sec else pd.DataFrame()
    if len(s):
        s["family"] = "SECONDARY"
    ctx.result("14_secondary_models", s)


def family_d(ctx):
    """Family D FFQ triangulation (09 lock): ph1 primary, ph2 replication; linear (log1p) or logistic (binary); BH q=0.05."""
    from chemotommo._common import fit_linear
    fl, ac = ctx.cfg["ffq_lock"], ctx.cfg["analysis_config"]
    ads, types, cl = ctx.t["ads"], covariate_types(ctx), cluster_col(ctx, ctx.t["ads"])
    covs = model_covariates(ctx, ads, "primary")
    out = []
    for fid, ph in fl["phenotypes"].items():
        for wave in (fl["primary_wave"], fl["replication_wave"]):
            col, v = f"{fid}_{wave}", ph["variant"]
            base = dict(test=f"{fid}|{wave}", variant=v, outcome=ph["name"], wave=wave, direction=ph["direction"])
            if col not in ads or v not in ads:
                out.append(dict(base, status="UNTESTABLE (FFQ item or variant unavailable)"))
                continue
            r = fit_logit(ads, col, v, covs, types, cl, ac["testability"]["min_events"]) if ph["transform"] in ("binary", "binary_any") else \
                fit_linear(ads, col, v, covs, types, cl)
            out.append(dict(base, **r))
    df = pd.DataFrame(out)
    prim = adjust(df[df["wave"] == fl["primary_wave"]], ac["families"]["D"]["method"], ac["families"]["D"]["q"])
    rep = df[df["wave"] == fl["replication_wave"]].assign(correction="replication (unadjusted, direction check)")
    res = pd.concat([prim, rep], ignore_index=True)
    sgn = res["direction"].map({"+": 1, "-": -1})
    res["direction_as_predicted"] = (res["beta"] * sgn > 0).where(sgn.notna())
    res["family"] = "D"
    ctx.result("14_family_D", res)
