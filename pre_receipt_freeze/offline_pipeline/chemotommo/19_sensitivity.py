"""19 sensitivity analyses (84 + endpoint-specific). Re-run Family A and Family C under each frozen variation."""
import math

import numpy as np
import pandas as pd

from chemotommo._common import (ENDPOINTS, covariate_types, cluster_col, design, model_covariates, suite_endpoints,
                                suite_predictions)


def evalue(or_, prev):
    if or_ is None or not np.isfinite(or_):
        return math.nan
    rr = math.sqrt(or_) if prev > 0.15 else or_
    rr = 1 / rr if rr < 1 else rr
    return rr + math.sqrt(rr * (rr - 1))


def mi_endpoints(ctx, ads, variants, m):
    import statsmodels.api as sm
    import warnings
    from sklearn.experimental import enable_iterative_imputer  # noqa: F401
    from sklearn.impute import IterativeImputer
    ac = ctx.cfg["analysis_config"]
    types = covariate_types(ctx)
    covs = model_covariates(ctx, ads, "primary")
    num = [c for c in covs if types.get(c) != "categorical"]
    cat = [c for c in covs if types.get(c) == "categorical"]
    out = []
    for v in variants:
        if v not in ads:
            continue
        for e in ENDPOINTS:
            d = ads[ads[e].notna() & ads[v].notna()].copy()
            if d[e].sum() < ac["testability"]["min_events"]:
                out.append(dict(test=f"{v}|{e}", variant=v, outcome=e, status="UNTESTABLE (events below floor)"))
                continue
            for c in cat:
                d[c] = d[c].fillna("missing")
            betas, ses = [], []
            for k in range(m):
                imp = IterativeImputer(sample_posterior=True, random_state=ac["seed"] + k, max_iter=10)
                dk = d.copy()
                if num:
                    dk[num] = imp.fit_transform(dk[num + [v, e]])[:, :len(num)]
                X = sm.add_constant(design(dk, [v] + covs, types), has_constant="add")
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    r = sm.GLM(dk[e].astype(float), X, family=sm.families.Binomial()).fit(cov_type="HC1")
                betas.append(r.params[v]); ses.append(r.bse[v])
            qbar, ubar, b = np.mean(betas), np.mean(np.square(ses)), np.var(betas, ddof=1)
            t = ubar + (1 + 1 / m) * b
            se = math.sqrt(t)
            from scipy import stats
            out.append(dict(test=f"{v}|{e}", variant=v, outcome=e, status="TESTED", n=len(d), events=int(d[e].sum()), beta=qbar,
                            se=se, z=qbar / se, p=float(2 * stats.norm.sf(abs(qbar / se))), odds_ratio=math.exp(qbar)))
    return pd.DataFrame(out)


def run(ctx):
    ac, dd = ctx.cfg["analysis_config"], ctx.cfg["drug_dictionary"]
    ads, rows, daily = ctx.t["ads"], ctx.t["rows_scope"], ctx.t["daily_scope"]
    build = ctx.t["build_endpoints"]
    A = ac["families"]["A"]["tests"] + ac["families"]["AS"]["tests"]
    V = ac["families"]["C"]["variants"]
    specs = dd["prediction_drugs"]
    res = []

    def add(name, a=None, c=None):
        for df, fam in ((a, "A+AS"), (c, "C")):
            if df is not None and len(df):
                res.append(df.assign(sensitivity=name, family=fam))

    def swap(new_ep):
        base = ads.drop(columns=[c for c in ENDPOINTS + ["mean_log_dose_ratio"] if c in ads])
        return base.merge(new_ep[["pid"] + ENDPOINTS], on="pid", how="left")

    pids = ads["pid"].tolist()
    if "TAS2R38_PAV__A49P" in ads:
        ov = {p: "TAS2R38_PAV__A49P" for p in A if ac["prediction_variant"][p] == "TAS2R38_PAV"}
        add("S03_A49P_only", suite_predictions(ctx, ads, rows, daily, A, specs, variant_override=ov),
            suite_endpoints(ctx, ads, ["TAS2R38_PAV__A49P"]))
    else:
        res.append(pd.DataFrame([dict(sensitivity="S03_A49P_only", status="UNTESTABLE (rs713598 unavailable)")]))
    a40 = ads[ads["age"] >= 40] if "age" in ads else ads
    add("S04_age40", suite_predictions(ctx, a40, rows, daily, A, specs), suite_endpoints(ctx, a40, V))
    car = ads.copy()
    for v in V:
        if v in car:
            car[v] = (car[v] > 0).astype(float).where(car[v].notna())
    add("S07_carrier", suite_predictions(ctx, car, rows, daily, A, specs), suite_endpoints(ctx, car, V))
    add("S08_minimal_adjustment", suite_predictions(ctx, ads, rows, daily, A, specs, covkind="minimal"),
        suite_endpoints(ctx, ads, V, covkind="minimal"))
    res.append(mi_endpoints(ctx, ads, V, ac["ml"]["mi_imputations"]).assign(sensitivity="S10_multiple_imputation", family="C"))
    ep, r2, d2 = build(ctx, pids, scope="all")
    add("S11_all_medications", suite_predictions(ctx, ads, r2, d2, A, specs), suite_endpoints(ctx, swap(ep), V))
    for name, inc, dec in (("S12_dose_threshold_any", 1.000001, 0.999999), ("S12b_dose_threshold_50", 1.5, 1 / 1.5)):
        ep, _, _ = build(ctx, pids, inc=inc, dec=dec)
        add(name, None, suite_endpoints(ctx, swap(ep), V, ["ANY_MEDICATION_CHANGE", "STANDARDIZED_DOSE_INCREASE", "STANDARDIZED_DOSE_DECREASE"]))
    mr = ctx.t["med_rows"]
    bad = set(mr.loc[mr["unresolved"] | mr["drug_id_unknown"] | mr["kedd_unknown"] | mr["id_conflict"], "pid"])
    clean = ads[~ads["pid"].isin(bad)]
    add("S13_exclude_unknown_id", suite_predictions(ctx, clean, rows, daily, A, specs), suite_endpoints(ctx, clean, V))
    ep, r3, d3 = build(ctx, pids, exclude_combination=True)
    add("S14_exclude_combination", suite_predictions(ctx, ads, r3, d3, A, specs), suite_endpoints(ctx, swap(ep), V))
    users = ads[ads["n_ph1"] > 0] if "n_ph1" in ads else ads
    add("S15_ph1_users_only_addition", None, suite_endpoints(ctx, users, V, ["MEDICATION_ADDITION"]))
    out = pd.concat(res, ignore_index=True)
    # S09 E-values for primary Family A and C results
    ev = []
    for name in ("12_family_A", "14_family_C"):
        df = ctx.t.get(f"result:{name}")
        if df is None:
            continue
        for r in df[df["status"] == "TESTED"].itertuples():
            prev = r.events / r.n if r.n else 0
            ev.append(dict(sensitivity="S09_evalue", source=name, test=r.test, odds_ratio=r.odds_ratio, outcome_prevalence=prev,
                           e_value=evalue(r.odds_ratio, prev)))
    ctx.result("19_sensitivity", out)
    ctx.result("19_evalues", pd.DataFrame(ev))
