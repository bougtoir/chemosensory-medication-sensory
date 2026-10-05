"""20 tables: combined results, family denominators (frozen/testable/untestable), and 85 pattern assignment."""
import json

import pandas as pd

FAMILIES = [("A", "12_family_A"), ("AS", "12_family_AS"), ("B", "13_family_B"), ("C", "14_family_C"), ("C2", "14_family_C2"),
            ("D", "14_family_D"), ("E", "15_family_E"), ("F", "16_family_F")]

PATTERN_TEXT = {
    "A": "genotype predicts formulation/exposure pattern consistent with a taste-mediated channel",
    "B": "support concentrated in pre-specified high-evidence predictions",
    "C": "associations observed but mechanistic interpretation not supported",
    "D": "no detectable population signature (informative null only for adequately powered tests)",
    "E": "report as unexecuted, with reasons",
}


def assign_pattern(t):
    a, c, e = t.get("A"), t.get("C"), t.get("E")
    tested = lambda df: df is not None and (df["status"] == "TESTED").any()  # noqa: E731
    if not tested(a) and not tested(c):
        return "E", "no Family A or C test met testability floors"
    sup = lambda df: df is not None and bool((df["reject"] & df["direction_as_predicted"].fillna(False)).any())  # noqa: E731
    support = sup(a) or sup(c)
    behave = bool(t.get("controls_behave", False))
    grad = e is not None and bool(((e["test"] == "GR1") & (e["status"] == "TESTED") & e["reject"] & (e["beta"] > 0)).any())
    if support and behave and grad:
        return "A", "directional support, controls null, G x EX gradient significant in frozen direction"
    if support and behave:
        return "B", "directional support with controls behaving; gradient not significant or not testable"
    if support or not behave:
        return "C", "positives with control failure" if support else "control failure without primary support"
    return "D", "no directional support; controls null"


def run(ctx):
    allr, den, t = [], [], {}
    for fam, name in FAMILIES:
        df = ctx.t.get(f"result:{name}")
        if df is None or not len(df):
            continue
        t[fam] = df
        allr.append(df.assign(family=fam))
        den.append(dict(family=fam, n_frozen=len(df), n_tested=int((df["status"] == "TESTED").sum()),
                        n_untestable=int((df["status"] != "TESTED").sum()),
                        n_reject=int(df["reject"].sum()) if "reject" in df else 0))
    t["controls_behave"] = ctx.t.get("controls_behave", False)
    cols = ["family", "test", "variant", "outcome", "status", "n", "events", "exposed_n", "beta", "se", "z", "p", "p_adj",
            "reject", "correction", "direction_as_predicted"]
    comb = pd.concat(allr, ignore_index=True)
    ctx.result("20_all_results", comb[[c for c in cols if c in comb]])
    ctx.result("20_family_denominators", pd.DataFrame(den))
    pat, why = assign_pattern(t)
    cal = ctx.t.get("result:17_calibration")
    interp = dict(pattern=pat, reason=why, claim_level=PATTERN_TEXT[pat], level5_claims="prohibited in all patterns (85 rule 4)",
                  calibration=cal.iloc[0].to_dict() if cal is not None else None,
                  note="isolated SNP-drug association without gradient support is never proof of the general framework (85 rule 1b)")
    (ctx.out_dir / "results" / "20_interpretation.json").write_text(json.dumps(interp, indent=2, default=str))
    ctx.t["interpretation"] = interp
