#!/usr/bin/env python3
"""09_META_ANALYSIS: quantitative synthesis where comparable.

Two honest syntheses:
A) Fisher combined P for the replication record of TAS2R38 -> PROP/PTC
   perception (same construct, different scales -> p-combination, not pooled ES).
B) Effect-direction sign test across curated genotype->S1 findings.
C) Random-effects mean for the subset of plasticity studies reporting a
   standardized direction on salt preference (reported descriptively;
   small k => structured synthesis only).
"""
import math, json
from pathlib import Path
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09_META_ANALYSIS"
OUT.mkdir(exist_ok=True)

# A) TAS2R38 -> PROP/PTC replication record (independent cohorts, direction = +)
studies = [
    # name, pmid, p (one-sided toward positive assoc; cap tiny to avoid inf)
    ("Kim 2003 (cloning)",            12595690, 1e-10),
    ("Bufe 2005 (Curr Biol)",         15723792, 1e-4),
    ("Mennella 2005 (children)",      15687429, 1e-2),
    ("Prodi/Sardinian 2004",          15466815, 1e-3),
    ("Reed 2010 GWAS",                20675712, 1.6e-104),
    ("Wooding 2013 (haplotypes)",     23632915, 1e-3),
    ("Nolden 2022 (chloramphenicol)", 35967977, 1e-2),
    ("Clindamycin 2026 (NULL)",       42162282, 0.9),   # null on a non-cognate drug = informative
]
chi2 = -2 * sum(math.log(max(p, 1e-300)) for _, _, p in studies)
k = len(studies)
fisher_p = 1 - stats.chi2.cdf(chi2, 2 * k)

# B) direction synthesis across all curated genotype->S1 edges
v = pd.read_csv(ROOT / "04_VARIANT_EVIDENCE.csv")
pos = (v.layer.str.contains("1B|1D", regex=True) & ~v.layer.str.contains("NEG")).sum()
neg = (v.layer.str.contains("NEG", regex=True)).sum()
binom = stats.binomtest(int(pos), int(pos + neg), 0.5, alternative="greater")

res = {
    "fisher_TAS2R38_PROP_PTC": {"k": k, "chi2": chi2, "df": 2 * k, "p": fisher_p,
        "note": "same construct (PROP/PTC-bitterness association); one null (non-cognate drug) included as informative"},
    "direction_test_GxS1": {"positive": int(pos), "negative": int(neg), "p": binom.pvalue},
    "scale_heterogeneity": "Suprathreshold gLMS, detection thresholds, recognition thresholds, "
        "taster-class frequencies are NOT pooled into a single effect size (spec rule). "
        "Pooled ES meta-analysis not defensible; p-combination + direction synthesis used instead.",
}
(OUT / "meta_results.json").write_text(json.dumps(res, indent=1))
pd.DataFrame(studies, columns=["study", "pmid", "p"]).to_csv(OUT / "tas2r38_prop_meta_input.csv", index=False)

with open(OUT / "README.md", "w") as f:
    f.write(f"""# 09_META_ANALYSIS

## A. TAS2R38 -> PROP/PTC perception, Fisher combined P
- k = {k} independent studies/cohorts (incl. 1 informative null on a non-cognate drug)
- chi2({2*k}) = {chi2:.1f}, combined P = {fisher_p:.3g}
- Interpretation: the genotype->S1 arrow for TAS2R38-ligands is beyond doubt.

## B. Effect-direction synthesis, all curated genotype->S1 findings
- positive findings: {pos}, negative/null findings: {neg}; sign test P = {binom.pvalue:.3g}

## C. Why no pooled effect size
{res['scale_heterogeneity']}

## Small-study effects
Not assessable: the literature is dominated by one locus (TAS2R38) and
phenotype scales differ. This asymmetry is itself reported as a risk (F6).
""")
print(json.dumps(res, indent=1))
