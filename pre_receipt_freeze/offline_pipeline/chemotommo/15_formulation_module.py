"""15 Family E (conditional): testability gate, GR1 formal gradient (G x EX ordinal, GEE logit, 1 df),
C1-C4 within-drug contrasts (Holm with GR1), C5 parenteral route-null check."""
import json
import math

import numpy as np
import pandas as pd

from chemotommo._common import adjust, covariate_types, design, fit_logit, model_covariates, row_matches


def bitter_set(ctx):
    dd = ctx.cfg["drug_dictionary"]
    b = pd.read_csv(ctx.path(dd["bitter_ligands"]["path"]))
    b = b[b["receptor"].astype(str).str.startswith(dd["bitter_ligands"]["human_receptor_prefix"])]
    names = set()
    for n in b["compound_name"].dropna():
        for x in str(n).split(","):
            names.add(x.strip().lower())
    al = dd["ingredient_aliases"]
    return names | {al[n] for n in names if n in al}


def row_outcome(rows, daily, dec):
    d = daily.set_index(["pid", "wave", "ingredient"])
    p2 = rows[rows["wave"] == "ph2"].groupby("pid")["ingredient"].apply(set).to_dict()
    ys = []
    for r in rows[rows["wave"] == "ph1"].itertuples():
        y = float(r.ingredient not in p2.get(r.pid, set()))
        if not y:
            try:
                a, b = d.loc[(r.pid, "ph1", r.ingredient)], d.loc[(r.pid, "ph2", r.ingredient)]
                if a["basis"] and a["basis"] == b["basis"] and a["daily"] > 0 and b["daily"] > 0 and b["daily"] / a["daily"] <= dec:
                    y = 1.0
            except KeyError:
                pass
        ys.append(y)
    return pd.Series(ys, index=rows[rows["wave"] == "ph1"].index)


def gate(ctx, rows):
    fm = ctx.cfg["analysis_config"]["formulation_module"]
    r1 = rows[rows["wave"] == "ph1"]
    cov = float(r1["ex_class"].notna().mean()) if len(r1) else 0.0
    pg = ctx.t.get("parser_gate", "SYNTHETIC-NOT-EVALUATED" if ctx.mode == "synthetic" else "NOT RUN")
    ok = cov >= fm["min_ex_coverage"] and pg in ("PASS", "SYNTHETIC-NOT-EVALUATED")
    return ok, dict(ex_coverage=cov, min_ex_coverage=fm["min_ex_coverage"], parser_gate=pg,
                    status="TESTABLE" if ok else "MECHANISTIC GRADIENT NOT TESTABLE")


def run(ctx):
    import statsmodels.api as sm
    import warnings
    ac = ctx.cfg["analysis_config"]
    ads, rows, daily = ctx.t["ads"], ctx.t["rows_scope"], ctx.t["daily_scope"]
    rows = rows[rows["pid"].isin(set(ads["pid"]))]
    ok, g = gate(ctx, rows)
    (ctx.out_dir / "results" / "15_formulation_gate.json").write_text(json.dumps(g, indent=2))
    v = ac["formulation_module"]["gradient_variant"]
    types = covariate_types(ctx)
    out = []
    nan = dict(n=0, events=0, beta=math.nan, se=math.nan, z=math.nan, p=math.nan, odds_ratio=math.nan)
    if not ok or v not in ads:
        for t in ["GR1", "C1", "C2", "C3", "C4", "C5"]:
            out.append(dict(test=t, variant=v, status=g["status"], **nan))
        ctx.result("15_family_E", pd.DataFrame(out))
        return
    dec = ac["endpoints"]["dose_ratio_decrease"]
    bset = bitter_set(ctx)
    r1 = rows[(rows["wave"] == "ph1") & rows["ingredient"].isin(bset) & rows["ex_class"].notna() & (rows["route"] != "inhaled")].copy()
    r1["_y"] = row_outcome(rows[rows["ingredient"].isin(bset)], daily, dec).reindex(r1.index)
    d = r1.merge(ads, on="pid", how="inner")
    d["E"] = pd.to_numeric(d["ex_class"], errors="coerce")
    covs = model_covariates(ctx, ads, "primary", True)
    d = d.dropna(subset=["_y", v, "E"] + covs)
    if len(d) >= ac["testability"]["min_exposed"] and d["_y"].sum() >= ac["testability"]["min_events"] and d["E"].nunique() > 1:
        d["GxE"] = d[v] * d["E"]
        X = sm.add_constant(design(d, [v, "E", "GxE"] + covs, types), has_constant="add")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = sm.GEE(d["_y"], X, groups=pd.factorize(d["pid"])[0], family=sm.families.Binomial(),
                             cov_struct=sm.cov_struct.Exchangeable()).fit()
            b, se = float(res.params["GxE"]), float(res.bse["GxE"])
            out.append(dict(test="GR1", variant=v, status="TESTED", n=len(d), events=int(d["_y"].sum()), beta=b, se=se, z=b / se,
                            p=float(res.pvalues["GxE"]), odds_ratio=math.exp(b), n_participants=d["pid"].nunique()))
        except Exception as e:  # noqa: BLE001
            out.append(dict(test="GR1", variant=v, status=f"FIT_FAILED ({type(e).__name__})", **nan))
    else:
        out.append(dict(test="GR1", variant=v, status="UNTESTABLE (rows/events below floor)", n=len(d), **{k: nan[k] for k in nan if k != "n"}))
    for cid, spec in ac["contrasts"].items():
        if cid == "C5":
            continue
        m = rows["ingredient"].isin(spec["ingredients"]) & (rows["wave"] == "ph1") & rows["formulation"].isin(spec["high"] + spec["low"])
        rr = rows[m].copy()
        rr["_y"] = row_outcome(rows[rows["ingredient"].isin(spec["ingredients"])], daily, dec).reindex(rr.index)
        rr["high"] = rr["formulation"].isin(spec["high"]).astype(float)
        dd_ = rr.merge(ads, on="pid", how="inner")
        dd_["GxH"] = dd_[v] * dd_["high"]
        r = fit_logit(dd_, "_y", "GxH", [v, "high"] + covs, types, None, ac["testability"]["min_events"],
                      ac["testability"]["min_exposed"], exposed_n=len(dd_))
        out.append(dict(test=cid, variant=v, **r))
    res = adjust(pd.DataFrame(out), ac["families"]["E"]["method"], ac["families"]["E"]["alpha"])
    c5 = ac["contrasts"]["C5"]
    from chemotommo._common import drug_change_away
    y = drug_change_away(rows, daily, c5, ctx.t["atc5_of"], ads["pid"].tolist(), dec)
    r = fit_logit(ads.assign(_y=y.values), "_y", v, covs, types, None, ac["testability"]["min_events"],
                  ac["testability"]["min_exposed"], exposed_n=int(y.notna().sum()))
    res = pd.concat([res, pd.DataFrame([dict(test="C5", variant=v, correction="route-null check (not in Holm set)", **r)])], ignore_index=True)
    res["family"] = "E"
    ctx.result("15_family_E", res)
