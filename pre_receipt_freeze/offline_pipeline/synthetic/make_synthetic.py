#!/usr/bin/env python3
"""Synthetic ToMMo-shaped data (NO real participant data). Columns follow config/variable_map.yaml.
Twelve fixed cases (S00001-S00012) exercise every endpoint/ID/unit edge case; the remainder are random."""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
CFG = HERE.parent / "config"

# drug_id, kedd_id, product text, ingredients, atc (master), strength_mg
CATALOG = [
    ("D001", "K001", "ノルバスク錠5mg", "amlodipine", "", "5"),
    ("D002", "K002", "アムロジン錠5mg", "amlodipine", "", "5"),
    ("D003", "K003", "リピトール錠10mg", "atorvastatin", "C10AA05", "10"),
    ("D004", "K004", "クレストール錠2.5mg", "rosuvastatin", "", "2.5"),
    ("D005", "K005", "メトグルコ錠250mg", "metformin", "", "250"),
    ("D006", "K006", "ガスター錠20mg", "famotidine", "", "20"),
    ("D007", "K007", "カデュエット配合錠", "amlodipine;atorvastatin", "", "5;10"),
    ("D008", "K008", "メルカゾール錠5mg", "thiamazole", "", "5"),
    ("D009", "K009", "プロパジール錠50mg", "propylthiouracil", "", "50"),
    ("D010", "K010", "タリビット錠100mg", "ofloxacin", "", "100"),
    ("D011", "K011", "エリスロシンドライシロップ", "erythromycin", "", ""),
    ("D012", "K012", "エリスロマイシン腸溶錠200mg", "erythromycin", "", "200"),
    ("D013", "K013", "ポララミン錠2mg", "dexchlorphenamine", "", "2"),
    ("D014", "K014", "カロナールシロップ", "paracetamol", "", ""),
    ("D015", "K015", "オメプラール腸溶錠20mg", "omeprazole", "", "20"),
    ("D016", "K016", "ヒューマリンR注", "insulin (human)", "A10AB01", ""),
    ("D017", "K017", "ロキソニン錠60mg", "loxoprofen", "", "60"),
    ("D018", "K018", "テオドールSR錠100mg", "theophylline", "", "100"),
    ("D019", "K019", "テオドールシロップ", "theophylline", "", ""),
    ("D020", "K020", "青汁健康食品", "green juice extract", "", ""),
    ("D021", "K021", "バルサルタン錠80mg", "valsartan", "", "80"),
]
POOL = {  # drug_id: ph1 prevalence among random participants
    "D001": .12, "D002": .05, "D003": .08, "D004": .05, "D005": .06, "D006": .06, "D008": .09, "D009": .01,
    "D010": .07, "D011": .04, "D012": .04, "D013": .07, "D014": .03, "D015": .06, "D016": .03, "D017": .06,
    "D018": .03, "D019": .02, "D020": .08, "D021": .06,
}
SWITCH = {"D003": "D004", "D004": "D003", "D001": "D021", "D021": "D001", "D011": "D012", "D012": "D011"}


def slot(drug=None, kedd=None, text=None, rx=1, dose=1, unit="錠", freq=1, funit="日"):
    return dict(drug_id=drug, kedd_id=kedd, text=text, rx=rx, other=1 - rx, dose_value=dose, dose_unit=unit,
                frequency_value=freq, frequency_unit=funit, duration_value=1, duration_unit="年")


def prod(d, **kw):
    c = next(x for x in CATALOG if x[0] == d)
    rx = 0 if d == "D020" else 1
    return slot(drug=c[0], kedd=c[1], text=c[2], rx=rx, **kw)


FIXED = {  # pid: (ph1 slots or None=section missing, ph2 slots)
    "S00001": ([prod("D001")], [prod("D002")]),                                      # same ingredient, other brand
    "S00002": ([prod("D001", dose=1)], [prod("D001", dose=2)]),                      # dose increase (count x strength)
    "S00003": ([prod("D003")], [prod("D004")]),                                      # within-class switch
    "S00004": ([], [prod("D005")]),                                                  # addition (no ph1 meds)
    "S00005": ([prod("D006")], []),                                                  # removal
    "S00006": ([prod("D001", dose=5, unit="mg"), prod("D001", dose=5, unit="mg")],
               [prod("D001", dose=10, unit="mg")]),                                  # duplicate rows summed
    "S00007": ([prod("D007")], [prod("D001")]),                                      # combination -> mono: atorvastatin removed
    "S00008": ([prod("D010", dose=100, unit="mg", freq=2)], [prod("D010", dose=1, unit="適量", freq=2)]),  # incompatible units
    "S00009": ([prod("D001")], None),                                                # missing phase 2
    "S00010": ([slot(drug="D999", text="メルカゾール錠5mg")], [prod("D008")]),         # unknown Drug ID -> free text
    "S00011": ([slot(kedd="K999")], [slot(kedd="K999")]),                             # unknown KEDD, no text -> unresolved
    "S00012": ([prod("D008")], [dict(prod("D008"), drug_id=None)]),                  # Drug ID at ph1, KEDD only at ph2
}


def main(out, n=3000, seed=20261004):
    rng = np.random.default_rng(seed)
    vm = yaml.safe_load((CFG / "variable_map.yaml").read_text())
    ffq = yaml.safe_load((CFG / "ffq_lock.yaml").read_text())
    eff = pd.read_csv(CFG / "derived" / "effect_alleles.csv").set_index("rsid")
    reg = pd.read_csv(CFG / "derived" / "approved_gene_regions.csv")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    pids = list(FIXED) + [f"T{i:05d}" for i in range(n - len(FIXED))]
    N = len(pids)
    # genotypes: TAS2R38 haplotypes (PAV=111 in effect-allele coding, AVI=000, AAI=100)
    haps = rng.choice(3, size=(N, 2), p=[.45, .50, .05])
    code = {0: (1, 1, 1), 1: (0, 0, 0), 2: (0, 1, 0)}
    t38 = np.array([[sum(code[h][j] for h in row) for j in range(3)] for row in haps])
    pav = (haps == 0).sum(axis=1)
    v187 = rng.binomial(2, .35, N)
    s1r2 = rng.binomial(2, .25, N)
    proxy = np.where(rng.random(N) < .95, v187, rng.binomial(2, .35, N))
    lb = {s: rng.binomial(2, .3, N) for s in ("rsSYN1", "rsSYN2", "rsSYN3", "rsSYN4")}
    hwe_bad = np.where(rng.random(N) < .5, 0, 2)                    # no heterozygotes -> HWE failure

    def alleles(d, rs, ref, alt):
        e = eff.at[rs, "effect_allele"] if rs in eff.index else alt
        o = ref if e != ref else alt.split("/")[0]
        return [e * k + o * (2 - k) for k in d]

    man = []

    def add(rs, gene, chrom, pos, ref, alt):
        man.append(dict(rsid=rs, gene=gene, chrom=chrom, pos=pos, build="GRCh38", ref=ref, alt=alt))

    g = pd.DataFrame({vm["id_column"]: pids})
    for j, rs in enumerate(["rs713598", "rs1726866", "rs10246939"]):
        r = eff.loc[rs]
        alt = r["effect_allele"] if r["effect_allele"] != r["ref"] else r["alts"].split("/")[0]
        add(rs, "TAS2R38", 7, r["pos_grch38"], r["ref"], alt)
        g[rs] = alleles(t38[:, j], rs, r["ref"], alt)
    r = eff.loc["rs3741845"]
    add("rs3741845", "TAS2R9", 12, r["pos_grch38"], r["ref"], "G")
    v = alleles(v187, "rs3741845", r["ref"], "G")
    g["rs3741845"] = [x if rng.random() > .25 else "" for x in v]  # call rate ~75% -> fails QC -> proxy path
    add("rsSYNPROXY", "TAS2R9", 12, int(r["pos_grch38"]) + 4000, "C", "T")
    g["rsSYNPROXY"] = (2 - proxy).astype(float) * 0 + proxy                                         # dosage of alt
    r = eff.loc["rs12033832"]
    add("rs12033832", "TAS1R2", 1, r["pos_grch38"], "G", "A")
    g["rs12033832"] = alleles(s1r2, "rs12033832", "G", "A")
    pos = lambda gene: int(reg[(reg.gene == gene) & (reg.build == "GRCh38")].iloc[0]["start"]) + 500  # noqa: E731
    add("rsSYN1", "TAS1R3", 1, pos("TAS1R3"), "A", "G"); g["rsSYN1"] = lb["rsSYN1"]
    add("rsSYN2", "SCNN1A", 12, pos("SCNN1A"), "A", "G"); g["rsSYN2"] = lb["rsSYN2"]
    add("rsSYN3", "", 7, pos("GNAT3"), "A", "G"); g["rsSYN3"] = lb["rsSYN3"]                # gene by region
    add("rsSYN4", "TRPA1", 8, 72037000, "A", "G"); g["rsSYN4"] = lb["rsSYN4"]               # outside universe
    add("rsSYN5", "PLCB2", 15, pos("PLCB2"), "A", "G"); g["rsSYN5"] = hwe_bad
    # numeric dosage columns must be dosage-of-alt; mixing formats per column is not allowed
    for c in ("rsSYNPROXY", "rsSYN1", "rsSYN2", "rsSYN3", "rsSYN4", "rsSYN5"):
        g[c] = g[c].astype(int)
    g.to_csv(out / "snp_genotypes.csv", index=False)
    pd.DataFrame(man).to_csv(out / "snp_manifest.csv", index=False)
    # masters
    pd.DataFrame([dict(drug_id=c[0], product=c[2], ingredients=c[3], atc=c[4], formulation_text=c[2], strength_mg=c[5])
                  for c in CATALOG]).to_csv(out / "drug_id_master.csv", index=False)
    pd.DataFrame([dict(kedd_id=c[1], product=c[2], ingredients=c[3], atc=c[4], formulation_text=c[2], strength_mg=c[5])
                  for c in CATALOG]).to_csv(out / "kedd_master.csv", index=False)
    # medications
    meds = {"ph1": {}, "ph2": {}}
    for i, p in enumerate(pids):
        if p in FIXED:
            meds["ph1"][p], meds["ph2"][p] = FIXED[p]
            continue
        s1, s2 = [], []
        for d, pr in POOL.items():
            if rng.random() < pr:
                dose = int(rng.choice([1, 2]))
                s1.append(prod(d, dose=dose))
                u = rng.random()
                lp = -2.2 + (0.6 * pav[i] if d == "D008" else 0) + (0.4 * v187[i] if d == "D010" else 0)
                if d == "D008" and rng.random() < 1 / (1 + np.exp(-lp)):
                    continue                                               # change-away (removal)
                if d == "D010" and rng.random() < 1 / (1 + np.exp(-lp)):
                    continue
                if u < .08:
                    continue
                if u < .16 and d in SWITCH:
                    s2.append(prod(SWITCH[d], dose=dose)); continue
                if u < .24:
                    s2.append(prod(d, dose=dose + 1)); continue
                s2.append(prod(d, dose=dose))
        for d, pr in POOL.items():
            if rng.random() < pr / 4 and not any(x["drug_id"] == d for x in s1):
                s2.append(prod(d))
        for s in s1 + s2:                                                    # 10% text-only rows
            if rng.random() < .10:
                s["drug_id"] = s["kedd_id"] = None
        meds["ph1"][p], meds["ph2"][p] = s1, s2
    sc, K = vm["medication"]["slot_columns"], vm["medication"]["n_slots"]
    age = np.where(np.arange(N) < len(FIXED), 55, rng.integers(20, 90, N))
    sex = rng.choice(["1", "2"], N)
    fam = [f"F{i // 3:05d}" for i in range(N)]
    pd.DataFrame({vm["id_column"]: pids, "age_ph1": age, "sex": sex}).to_csv(out / "demographics.csv", index=False)
    pd.DataFrame({vm["id_column"]: pids, "cohort_type": rng.choice(["CommCohort", "BirThree"], N), vm["family_column"]: fam}
                 ).to_csv(out / "cohort_profile.csv", index=False)
    for w, date in (("ph1", "2013-06-01"), ("ph2", "2018-06-01")):
        rows = []
        for i, p in enumerate(pids):
            ss = meds[w][p]
            r = {vm["id_column"]: p, "answer_date": date}
            r["med_any"] = None if ss is None else (1 if ss else 0)
            for k, s in enumerate(ss or [], 1):
                for lg, tmpl in sc.items():
                    r[tmpl.format(k=k)] = s.get(lg)
            if w == "ph1":
                r.update(smoking_status=str(rng.choice(["never", "former", "current"])), alcohol_freq=int(rng.integers(0, 7)),
                         education=str(rng.choice(["hs", "college", "univ"])) if rng.random() > .05 else None,
                         hx_hypertension=int(rng.random() < .3), hx_diabetes=int(rng.random() < .1),
                         hx_dyslipidemia=int(rng.random() < .2), alcohol_flush=int(rng.random() < .4))
            rows.append(r)
        allcols = [tmpl.format(k=k) for k in range(1, K + 1) for tmpl in sc.values()]
        df = pd.DataFrame(rows)
        df = pd.concat([df, pd.DataFrame(None, index=df.index, columns=[c for c in allcols if c not in df])], axis=1)
        df.to_csv(out / f"qa_lifestyle.{w}.csv", index=False)
        pd.DataFrame({vm["id_column"]: pids, "bmi": rng.normal(23, 3, N).round(1), "sbp": rng.normal(128, 15, N).round()}
                     ).to_csv(out / f"physiological_test.{w}.csv", index=False)
        pd.DataFrame({vm["id_column"]: pids, "hba1c": rng.normal(5.6, .5, N).round(1), "ldl": rng.normal(120, 30, N).round()}
                     ).to_csv(out / f"laboratory_test.{w}.csv", index=False)
        f = {vm["id_column"]: pids}
        for item, spec in ffq["items"].items():
            if spec.get("type") == "binary":
                f[spec[w]] = rng.binomial(1, .4, N)
            else:
                base = 4 - (0.4 * pav if item in ("coffee", "green_tea") else 0)
                f[spec[w]] = np.clip(np.round(rng.normal(base, 1.8, N)), 1, 9).astype(int)
        pd.DataFrame(f).to_csv(out / f"qa_ffq.{w}.csv", index=False)
    print(f"synthetic data: {N} participants -> {out}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--out", required=True)
    a.add_argument("--n", type=int, default=3000)
    ns = a.parse_args()
    main(ns.out, ns.n)
