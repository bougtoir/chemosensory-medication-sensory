"""08 cross-wave medication change: E1-E7 (06_MEDICATION_LONGITUDINAL_ENDPOINT_FREEZE) on the frozen scope."""
import pandas as pd

from chemotommo._common import ENDPOINTS, compute_endpoints


def scope_rows(ctx, scope="prescription", exclude_combination=False, exclude_unknown_pids=None):
    ing = ctx.t["ing_rows"]
    r = ing.dropna(subset=["ingredient"])
    if scope == "prescription":
        r = r[r["rx"]]
    if exclude_combination:
        r = r[~r["combination"]]
    if exclude_unknown_pids is not None:
        r = r[~r["pid"].isin(exclude_unknown_pids)]
    return r


def build(ctx, pids, scope="prescription", inc=None, dec=None, exclude_combination=False):
    e = ctx.cfg["analysis_config"]["endpoints"]
    rows = scope_rows(ctx, scope, exclude_combination)
    daily = ctx.t["collapse"](rows)
    return compute_endpoints(daily, ctx.t["atc4_of"], pids, inc or e["dose_ratio_increase"], dec or e["dose_ratio_decrease"]), rows, daily


def run(ctx):
    ans = ctx.t["answered"]
    pids = ans.loc[ans["ph1_answered"] & ans["ph2_answered"], "pid"].tolist()
    ep, rows, daily = build(ctx, pids)
    ctx.t["endpoints"], ctx.t["rows_scope"], ctx.t["daily_scope"] = ep, rows, daily
    ctx.t["build_endpoints"] = build
    ctx.work("08_endpoints", ep)
    cnt = [dict(endpoint=k, risk_set_n=int(ep[k].notna().sum()), events=int(ep[k].sum(skipna=True))) for k in ENDPOINTS]
    ctx.result("08_endpoint_counts", pd.DataFrame(cnt))
