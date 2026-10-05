"""18 Family H ML secondary: nested CV; clinical vs clinical+genetic; delta AUC with bootstrap CI; calibration; Brier.
Does not replace any prespecified genetic test."""
import math
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from chemotommo._common import covariate_types, design, model_covariates


def models(seed):
    enet = (make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                          LogisticRegression(penalty="elasticnet", solver="saga", max_iter=5000, random_state=seed)),
            {"logisticregression__C": [0.01, 0.1, 1.0], "logisticregression__l1_ratio": [0.2, 0.8]})
    gb = (HistGradientBoostingClassifier(random_state=seed), {"learning_rate": [0.05, 0.1], "max_depth": [3]})
    return {"elastic_net_logistic": enet, "gradient_boosting": gb}


def nested_pred(X, y, est, grid, ac):
    seed = ac["seed"]
    outer = StratifiedKFold(ac["ml"]["outer_folds"], shuffle=True, random_state=seed)
    pred = np.zeros(len(y))
    for tr, te in outer.split(X, y):
        gs = GridSearchCV(est, grid, cv=StratifiedKFold(ac["ml"]["inner_folds"], shuffle=True, random_state=seed), scoring="roc_auc")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gs.fit(X.iloc[tr], y[tr])
        pred[te] = gs.predict_proba(X.iloc[te])[:, 1]
    return pred


def cal_slope(y, p):
    import statsmodels.api as sm
    lp = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
    r = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit()
    return float(r.params[1]), float(r.params[0])


def run(ctx):
    ac = ctx.cfg["analysis_config"]
    ads, e = ctx.t["ads"], ac["ml"]["endpoint"]
    d = ads[ads[e].notna()].reset_index(drop=True)
    y = d[e].astype(int).values
    if len(d) < 200 or y.sum() < 20 or (len(y) - y.sum()) < 20:
        ctx.result("18_ml", pd.DataFrame([dict(status="UNTESTABLE (n/events below floor)")]))
        return
    clin = design(d, model_covariates(ctx, d, "primary"), covariate_types(ctx))
    gen_cols = [c for c in d.columns if c in ctx.cfg["snp_map"]["level_a"] or c.startswith("B__")]
    full = pd.concat([clin, d[gen_cols].astype(float)], axis=1)
    rng = np.random.default_rng(ac["seed"])
    rows = []
    for name, (est, grid) in models(ac["seed"]).items():
        p0, p1 = nested_pred(clin, y, est, grid, ac), nested_pred(full, y, est, grid, ac)
        a0, a1 = roc_auc_score(y, p0), roc_auc_score(y, p1)
        boots = []
        for _ in range(ac["ml"]["bootstrap"]):
            i = rng.integers(0, len(y), len(y))
            if y[i].min() == y[i].max():
                continue
            boots.append(roc_auc_score(y[i], p1[i]) - roc_auc_score(y[i], p0[i]))
        s1, i1 = cal_slope(y, p1)
        rows.append(dict(model=name, endpoint=e, n=len(y), events=int(y.sum()), auc_clinical=a0, auc_clinical_genetic=a1,
                         delta_auc=a1 - a0, delta_auc_ci_low=float(np.percentile(boots, 2.5)),
                         delta_auc_ci_high=float(np.percentile(boots, 97.5)), brier_clinical=brier_score_loss(y, p0),
                         brier_clinical_genetic=brier_score_loss(y, p1), calibration_slope=s1, calibration_intercept=i1,
                         n_genetic_features=len(gen_cols), status="EVALUATED"))
    ctx.result("18_ml", pd.DataFrame(rows))
