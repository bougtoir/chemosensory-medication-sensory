"""17 Family G calibration: Spearman(frozen evidence score, signed Z_i), >=10,000 permutations, seed 42."""
import math

import numpy as np
import pandas as pd
from scipy import stats


def run(ctx):
    ac = ctx.cfg["analysis_config"]
    g = ac["families"]["G"]
    preds = pd.concat([ctx.t["result:12_family_A"], ctx.t["result:12_family_AS"]], ignore_index=True)
    preds["evidence_score"] = preds["test"].map(ac["evidence_score"])
    preds["Z_signed"] = preds["sign"] * preds["z"]
    ev = preds[(preds["status"] == "TESTED") & preds["Z_signed"].notna()]
    out = dict(n_frozen=12, n_in_scope=len(preds), n_evaluable=len(ev), min_evaluable=g["min_evaluable"])
    if len(ev) >= g["min_evaluable"]:
        rho = stats.spearmanr(ev["evidence_score"], ev["Z_signed"]).correlation
        rng = np.random.default_rng(ac["seed"])
        perm = np.array([stats.spearmanr(ev["evidence_score"], rng.permutation(ev["Z_signed"].values)).correlation
                         for _ in range(g["permutations"])])
        out.update(rho=rho, p_perm_one_sided=float((1 + (perm >= rho).sum()) / (1 + len(perm))), status="EVALUATED")
    else:
        out.update(rho=math.nan, p_perm_one_sided=math.nan, status="UNDEFINED (evaluable predictions below minimum)")
    ctx.result("17_calibration_points", preds[["test", "evidence_score", "status", "z", "sign", "Z_signed", "beta", "se"]])
    ctx.result("17_calibration", pd.DataFrame([out]))
