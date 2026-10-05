"""Shared core library. All column names come from config (variable_map.yaml); none are hard-coded."""
import glob
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

PKG = Path(__file__).resolve().parent
PIPE = PKG.parent
CONFIGS = ["variable_map", "snp_map", "drug_dictionary", "ffq_lock", "analysis_config"]
ENDPOINTS = ["ANY_MEDICATION_CHANGE", "ACTIVE_INGREDIENT_CHANGE", "WITHIN_CLASS_SWITCH", "MEDICATION_ADDITION",
             "MEDICATION_REMOVAL", "STANDARDIZED_DOSE_INCREASE", "STANDARDIZED_DOSE_DECREASE"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    return {k: yaml.safe_load((cfg_dir / f"{k}.yaml").read_text(encoding="utf-8")) for k in CONFIGS}


class Ctx:
    """Run context. work/ holds participant-level intermediates (restricted; never exported);
    results/ holds aggregate outputs; export/ holds the privacy-checked release."""

    def __init__(self, cfg_dir, data_dir, out_dir, mode="synthetic", stage="all"):
        self.cfg_dir, self.data_dir, self.out_dir = Path(cfg_dir).resolve(), Path(data_dir).resolve(), Path(out_dir).resolve()
        self.cfg = load_config(self.cfg_dir)
        self.mode, self.stage = mode, stage
        self.t = {}
        self.log = []
        for sub in ("work", "results", "figures", "export"):
            (self.out_dir / sub).mkdir(parents=True, exist_ok=True)

    def path(self, rel):
        return (self.cfg_dir / rel).resolve()

    def note(self, msg):
        self.log.append(msg)

    def work(self, name, df):
        df.to_csv(self.out_dir / "work" / f"{name}.csv", index=False)

    def result(self, name, df):
        df.to_csv(self.out_dir / "results" / f"{name}.csv", index=False)
        self.t[f"result:{name}"] = df


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_files(ctx, key):
    pat = ctx.cfg["variable_map"]["files"].get(key)
    return sorted(glob.glob(str(ctx.data_dir / pat))) if pat else []


def read_table(ctx, key):
    files = find_files(ctx, key)
    if not files:
        return None
    frames = []
    for f in files:
        for enc in ctx.cfg["variable_map"]["encoding_candidates"]:
            try:
                frames.append(pd.read_csv(f, dtype=str, encoding=enc, keep_default_na=True))
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"cannot decode {f}")
    df = pd.concat(frames, ignore_index=True)
    return df


def num(s):
    return pd.to_numeric(s, errors="coerce")


def is_true(v, true_values):
    t = str(v).strip()
    if t in {str(x) for x in true_values}:
        return True
    try:
        return float(t) == 1.0 and any(str(x) == "1" for x in true_values)
    except ValueError:
        return False


def canon_ingredient(name, aliases):
    if name is None or (isinstance(name, float) and math.isnan(name)):
        return None
    n = re.sub(r"\s+", " ", str(name).strip().lower())
    return aliases.get(n, n) if n else None


# ---------------------------------------------------------------- ATC snapshot
def load_atc_index(path):
    """Return (name->set(ATC5), dnum->set(ATC5)) from KEGG br08303 JSON."""
    j = json.loads(Path(path).read_text())
    by_name, by_d = {}, {}

    def strip(nm):
        nm = re.sub(r"\s*\[DG:[^\]]*\]", "", nm)
        nm = re.sub(r"&lt;.*?&gt;", "", nm)
        nm = re.sub(r"\(.*?\)", "", nm)
        return re.sub(r"\s+", " ", nm).strip().lower()

    def walk(node, atc5=None):
        nm = node["name"]
        m = re.match(r"^([A-Z]\d\d[A-Z][A-Z]\d\d) (.*)", nm)
        if m:
            atc5 = m.group(1)
            by_name.setdefault(strip(m.group(2)), set()).add(atc5)
        md = re.match(r"^(D\d{5})\s+(.*)", nm)
        if md and atc5:
            by_d.setdefault(md.group(1), set()).add(atc5)
            by_name.setdefault(strip(md.group(2)), set()).add(atc5)
        for c in node.get("children", []):
            walk(c, atc5)

    walk(j)
    return by_name, by_d


def atc_level(codes, level=4):
    n = {1: 1, 2: 3, 3: 4, 4: 5, 5: 7}[level]
    return {c[:n] for c in codes if isinstance(c, str) and len(c) >= n}


# ---------------------------------------------------------------- dose harmonization (07)
MASS = {"mg": 1.0, "g": 1000.0, "µg": 0.001, "μg": 0.001, "mcg": 0.001, "ug": 0.001, "ｍｇ": 1.0}
COUNT = {"錠", "t", "tab", "tablet", "カプセル", "cap", "capsule", "c", "包", "本", "個", "枚", "滴", "吸入", "単位", "iu", "u"}
VOLUME = {"ml": 1.0, "ｍｌ": 1.0, "cc": 1.0}
FREQ = {"日": 1.0, "1日": 1.0, "/日": 1.0, "day": 1.0, "回/日": 1.0, "週": 1 / 7, "1週": 1 / 7, "/週": 1 / 7, "week": 1 / 7,
        "月": 1 / 30, "1月": 1 / 30, "ヶ月": 1 / 30, "/月": 1 / 30, "month": 1 / 30}


def harmonize_dose(dose_value, dose_unit, freq_value, freq_unit, strength_mg=None, n_ingredients=1, product_key=None):
    """Return (daily_amount, basis). basis = 'mg' or 'count:<product>' or 'ml:<product>' or None.
    No value is imputed: missing frequency, unknown unit or ambiguous combination strength -> (nan, None)."""
    dv, fv = num(pd.Series([dose_value])).iloc[0], num(pd.Series([freq_value])).iloc[0]
    du = str(dose_unit).strip().lower() if dose_unit is not None and str(dose_unit) != "nan" else ""
    fu = str(freq_unit).strip().lower() if freq_unit is not None and str(freq_unit) != "nan" else ""
    if pd.isna(dv) or pd.isna(fv) or fu not in FREQ or dv <= 0 or fv <= 0:
        return math.nan, None
    per_day = fv * FREQ[fu]
    if du in MASS:
        if n_ingredients > 1:
            return math.nan, None            # mass of a combination product is not attributable per ingredient
        return dv * MASS[du] * per_day, "mg"
    if du in COUNT:
        if strength_mg is not None and not pd.isna(strength_mg):
            return dv * float(strength_mg) * per_day, "mg"
        return (dv * per_day, f"count:{product_key}") if product_key else (math.nan, None)
    if du in VOLUME:
        return (dv * VOLUME[du] * per_day, f"ml:{product_key}") if product_key else (math.nan, None)
    return math.nan, None


# ---------------------------------------------------------------- endpoints (08)
def wave_sets(ing):
    """ing: participant-wave-ingredient table (collapsed) restricted to analysis scope."""
    out = {}
    for (pid, wave), g in ing.groupby(["pid", "wave"]):
        out.setdefault(pid, {})[wave] = g.set_index("ingredient")
    return out


def compute_endpoints(ing, atc4, pids, inc=1.25, dec=0.80):
    """Participant-level E1-E7 with endpoint-specific risk sets (NaN = not in risk set).
    ing columns: pid, wave, ingredient, daily, basis. atc4: ingredient -> set(ATC4)."""
    sets = wave_sets(ing)
    rows = []
    empty = pd.DataFrame(columns=["daily", "basis"])
    for pid in pids:
        w = sets.get(pid, {})
        a, b = w.get("ph1", empty), w.get("ph2", empty)
        i1, i2 = set(a.index), set(b.index)
        removed, added, shared = i1 - i2, i2 - i1, i1 & i2
        ratios = []
        for s in shared:
            ra, rb = a.loc[s], b.loc[s]
            if ra["basis"] and ra["basis"] == rb["basis"] and ra["daily"] > 0 and rb["daily"] > 0:
                ratios.append(rb["daily"] / ra["daily"])
        inc_y = any(r >= inc for r in ratios)
        dec_y = any(r <= dec for r in ratios)
        switch = any(atc4.get(r, set()) & atc4.get(x, set()) for r in removed for x in added)
        both = len(i1) > 0 and len(i2) > 0
        rows.append(dict(
            pid=pid, n_ph1=len(i1), n_ph2=len(i2), n_added=len(added), n_removed=len(removed), n_shared=len(shared),
            n_dose_comparable=len(ratios),
            mean_log_dose_ratio=float(np.mean(np.log(ratios))) if ratios else math.nan,
            ANY_MEDICATION_CHANGE=float(bool(added or removed or inc_y or dec_y)) if (i1 or i2) else math.nan,
            ACTIVE_INGREDIENT_CHANGE=float(bool(added and removed)) if both else math.nan,
            WITHIN_CLASS_SWITCH=float(switch) if both else math.nan,
            MEDICATION_ADDITION=float(bool(added)),
            MEDICATION_REMOVAL=float(bool(removed)) if i1 else math.nan,
            STANDARDIZED_DOSE_INCREASE=float(inc_y) if ratios else math.nan,
            STANDARDIZED_DOSE_DECREASE=float(dec_y) if ratios else math.nan,
        ))
    return pd.DataFrame(rows)


def row_matches(rows, spec, atc5_of):
    """Boolean mask: medication rows (ingredient-level) matching a drug-set spec from drug_dictionary.yaml."""
    m = pd.Series(True, index=rows.index)
    if "ingredients" in spec:
        m &= rows["ingredient"].isin(spec["ingredients"])
    if "atc_prefix" in spec:
        m &= rows["ingredient"].map(lambda i: any(c.startswith(tuple(spec["atc_prefix"])) for c in atc5_of.get(i, set()))).astype(bool)
    if "route" in spec:
        m &= rows["route"].isin(spec["route"])
    if "ex_class" in spec:
        m &= rows["ex_class"].isin(spec["ex_class"])
    if "formulation_any" in spec:
        m &= rows["formulation"].isin(spec["formulation_any"])
    if spec.get("supplement"):
        m &= rows["supplement"].astype(bool)
    return m


def drug_change_away(rows_scope, daily, spec, atc5_of, pids, dec=0.80, include_increase=False):
    """Drug-set-specific outcome (Families A, AS, F). Risk set: participants with >=1 matching ph1 row.
    Y=1 if a matching ph1 ingredient has no matching row at ph2 (removal / switch-out / formulation-out),
    or its standardized daily dose ratio <= dec (or >= 1/dec when include_increase)."""
    m = row_matches(rows_scope, spec, atc5_of)
    r1 = rows_scope[m & (rows_scope["wave"] == "ph1")]
    r2 = rows_scope[m & (rows_scope["wave"] == "ph2")]
    p2 = r2.groupby("pid")["ingredient"].apply(set).to_dict()
    d = daily.set_index(["pid", "wave", "ingredient"])
    out = []
    for pid, g in r1.groupby("pid"):
        y = 0
        for ing in set(g["ingredient"]):
            if ing not in p2.get(pid, set()):
                y = 1
                break
            try:
                a, b = d.loc[(pid, "ph1", ing)], d.loc[(pid, "ph2", ing)]
            except KeyError:
                continue
            if a["basis"] and a["basis"] == b["basis"] and a["daily"] > 0 and b["daily"] > 0:
                ratio = b["daily"] / a["daily"]
                if ratio <= dec or (include_increase and ratio >= 1 / dec):
                    y = 1
                    break
        out.append((pid, y))
    s = pd.Series({p: v for p, v in out}, dtype=float)
    return s.reindex(pids)


def exposure_presence(rows_scope, spec, atc5_of, pids, wave="ph1"):
    m = row_matches(rows_scope, spec, atc5_of) & (rows_scope["wave"] == wave)
    users = set(rows_scope.loc[m, "pid"])
    return pd.Series([float(p in users) for p in pids], index=pids)


# ---------------------------------------------------------------- models
def design(df, cols, types):
    parts = []
    for c in cols:
        if c not in df:
            continue
        t = types.get(c, "numeric")
        if t == "categorical":
            parts.append(pd.get_dummies(df[c].astype(str), prefix=c, drop_first=True, dtype=float))
        else:
            parts.append(pd.to_numeric(df[c], errors="coerce").rename(c))
    X = pd.concat(parts, axis=1) if parts else pd.DataFrame(index=df.index)
    return X.loc[:, X.nunique(dropna=True) > 1]


def fit_logit(df, y, x, covars, types, cluster=None, min_events=20, min_exposed=0, exposed_n=None):
    import statsmodels.api as sm
    import warnings
    cols = [y, x] + [c for c in covars if c in df] + ([cluster] if cluster and cluster in df else [])
    d = df[cols].dropna(subset=[y, x] + [c for c in covars if c in df])
    n, ev = len(d), int(d[y].sum()) if len(d) else 0
    base = dict(n=n, events=ev, beta=math.nan, se=math.nan, z=math.nan, p=math.nan, odds_ratio=math.nan)
    if exposed_n is not None and exposed_n < min_exposed:
        return dict(base, status="PRE-SPECIFIED BUT UNTESTABLE (exposed n < floor)")
    if n == 0 or ev < min_events or n - ev < min_events or d[x].nunique() < 2:
        return dict(base, status="UNTESTABLE (events/variation below floor)")
    X = design(d, [x] + [c for c in covars if c in d], types)
    if x not in X:
        return dict(base, status="UNTESTABLE (no genotype variation)")
    X = sm.add_constant(X, has_constant="add")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = sm.GLM(d[y].astype(float), X, family=sm.families.Binomial())
            if cluster and cluster in d and d[cluster].notna().all():
                res = model.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
            else:
                res = model.fit(cov_type="HC1")
        b, se = float(res.params[x]), float(res.bse[x])
        return dict(base, beta=b, se=se, z=b / se, p=float(res.pvalues[x]), odds_ratio=math.exp(b), status="TESTED")
    except Exception as e:  # noqa: BLE001
        return dict(base, status=f"FIT_FAILED ({type(e).__name__})")


def fit_linear(df, y, x, covars, types, cluster=None, min_n=20):
    import statsmodels.api as sm
    d = df[[y, x] + [c for c in covars if c in df] + ([cluster] if cluster and cluster in df else [])].dropna(
        subset=[y, x] + [c for c in covars if c in df])
    base = dict(n=len(d), events=math.nan, beta=math.nan, se=math.nan, z=math.nan, p=math.nan, odds_ratio=math.nan)
    if len(d) < min_n or d[x].nunique() < 2:
        return dict(base, status="UNTESTABLE (n below floor)")
    X = sm.add_constant(design(d, [x] + [c for c in covars if c in d], types), has_constant="add")
    if cluster and cluster in d and d[cluster].notna().all():
        res = sm.OLS(d[y].astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
    else:
        res = sm.OLS(d[y].astype(float), X).fit(cov_type="HC1")
    b, se = float(res.params[x]), float(res.bse[x])
    return dict(base, beta=b, se=se, z=b / se, p=float(res.pvalues[x]), status="TESTED")


def adjust(df, method, level):
    from statsmodels.stats.multitest import multipletests
    df = df.copy()
    df["p_adj"], df["reject"] = math.nan, False
    m = df["status"].eq("TESTED") & df["p"].notna()
    if m.sum():
        rej, padj, _, _ = multipletests(df.loc[m, "p"], alpha=level, method=method)
        df.loc[m, "p_adj"], df.loc[m, "reject"] = padj, rej
    df["correction"] = f"{method}@{level}"
    return df


def covariate_types(ctx):
    t = {k: v.get("type", "numeric") for k, v in ctx.cfg["variable_map"]["covariates"].items()}
    t.update(followup_years="numeric", n_rx_ph1="numeric")
    return {k: ("categorical" if v == "categorical" else "numeric") for k, v in t.items()}


def model_covariates(ctx, df, kind="primary", within_user=False):
    a = ctx.cfg["analysis_config"]["covariates"]
    cov = list(a[kind]) + (list(a["within_user_extra"]) if within_user else [])
    present = [c for c in cov if c in df.columns and df[c].notna().any()]
    return present


def cluster_col(ctx, df):
    return "family_id" if "family_id" in df.columns and df["family_id"].notna().all() else None


# ---------------------------------------------------------------- family suites (shared by 12/14/16/19)
def suite_predictions(ctx, ads, rows, daily, ids, specs, covkind="primary", variant_override=None, include_increase=False):
    ac = ctx.cfg["analysis_config"]
    types, cl = covariate_types(ctx), cluster_col(ctx, ads)
    covs = model_covariates(ctx, ads, covkind, within_user=True)
    out = []
    for pid_ in ids:
        spec = specs[pid_]
        var = (variant_override or {}).get(pid_, ac["prediction_variant"].get(pid_))
        y = drug_change_away(rows, daily, spec, ctx.t["atc5_of"], ads["pid"].tolist(),
                             ac["endpoints"]["dose_ratio_decrease"], include_increase)
        d = ads.assign(_y=y.values)
        if var not in d.columns:
            out.append(dict(test=pid_, variant=var, outcome="DRUG_SPECIFIC_CHANGE_AWAY", status="UNTESTABLE (variant unavailable)",
                            n=0, events=0, exposed_n=int(y.notna().sum()), beta=math.nan, se=math.nan, z=math.nan, p=math.nan, odds_ratio=math.nan))
            continue
        r = fit_logit(d, "_y", var, covs, types, cl, ac["testability"]["min_events"], ac["testability"]["min_exposed"],
                      exposed_n=int(y.notna().sum()))
        out.append(dict(test=pid_, variant=var, outcome="DRUG_SPECIFIC_CHANGE_AWAY", exposed_n=int(y.notna().sum()), **r))
    return pd.DataFrame(out)


USER_ENDPOINTS = {"ACTIVE_INGREDIENT_CHANGE", "WITHIN_CLASS_SWITCH", "MEDICATION_REMOVAL",
                  "STANDARDIZED_DOSE_INCREASE", "STANDARDIZED_DOSE_DECREASE"}


def suite_endpoints(ctx, ads, variants, endpoints=ENDPOINTS, covkind="primary"):
    ac = ctx.cfg["analysis_config"]
    types, cl = covariate_types(ctx), cluster_col(ctx, ads)
    out = []
    for v in variants:
        for e in endpoints:
            if v not in ads.columns or e not in ads.columns:
                out.append(dict(test=f"{v}|{e}", variant=v, outcome=e, status="UNTESTABLE (variant or endpoint unavailable)",
                                n=0, events=0, beta=math.nan, se=math.nan, z=math.nan, p=math.nan, odds_ratio=math.nan))
                continue
            covs = model_covariates(ctx, ads, covkind, within_user=e in USER_ENDPOINTS)
            r = fit_logit(ads, e, v, covs, types, cl, ac["testability"]["min_events"])
            out.append(dict(test=f"{v}|{e}", variant=v, outcome=e, **r))
    return pd.DataFrame(out)
