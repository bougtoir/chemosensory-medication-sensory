#!/usr/bin/env python3
"""Build 07_EVIDENCE_GRAPH.csv / .json from curated evidence + BitterDB edges.

Node classes: Gene, Variant, Receptor, Ligand, Drug, FoodCompound,
SensoryPhenotype, BehavioralPhenotype, DietaryExposure, TrainingIntervention.
Every edge carries provenance (pmid/source, design, species, n, grade).
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
edges = []

def add(src, src_type, edge, dst, dst_type, pmid="", design="", species="human",
        n="", effect="", pval="", grade="", note=""):
    edges.append(dict(src=src, src_type=src_type, relation=edge, dst=dst, dst_type=dst_type,
                      citation_pmid=pmid, study_design=design, species=species, n=n,
                      effect=effect, p_value=pval, evidence_grade=grade, note=note))

# Variant -> receptor function and -> sensory phenotype (from 04)
v = pd.read_csv(ROOT / "04_VARIANT_EVIDENCE.csv")
for _, r in v.iterrows():
    if str(r.pmid) == "?": continue
    vn = f"{r.gene}:{r.variant}"
    add(vn, "Variant", "variant->sensory_phenotype", f"S1:{r.stimulus} perception",
        "SensoryPhenotype", pmid=r.pmid, design=r.design, species="human", n=r.n,
        effect=r.effect, pval=r.pval,
        grade="A" if "replicat" in str(r.replication).lower() or "GWAS" in str(r.design) else "B",
        note=r.note)
    if pd.notna(r.get("functional")) and str(r.get("functional")).strip():
        add(vn, "Variant", "variant->receptor_function", f"{r.gene} receptor",
            "Receptor", pmid=r.pmid, design=r.design, species="human", effect=r.functional,
            grade="B")

# BitterDB drug->receptor edges (only drugs in our drug list)
d = pd.read_csv(ROOT / "prediction" / "drug_chemical_space.csv")
b = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
import re
norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
b["n"] = b.compound_name.map(norm); d["n"] = d.generic_name.map(norm)
m = d.merge(b, on="n", suffixes=("", "_b"))
for _, r in m.iterrows():
    add(r.generic_name, "Drug", "drug->receptor_activation", r.receptor, "Receptor",
        pmid=39535052, design="curated heterologous assays (BitterDB)", species="human",
        effect="agonist/activator", grade="B", note="BitterDB 2024 update")

# sensory -> behavior (1E)
beh = pd.read_csv(ROOT / "evidence" / "sensory_behavior_evidence.csv")
for _, r in beh.iterrows():
    add(f"S1:{r.sensory}", "SensoryPhenotype", "sensory_phenotype->medication_behavior",
        f"S2:{r.behavior}", "BehavioralPhenotype", pmid=r.pmid, design=r.design,
        species="human", n=r.n, effect=r.effect, pval=r.pval,
        grade="B" if "cohort" in str(r.design).lower() else "C", note=r.note)

# diet/training -> sensory phenotype (1F)
pl = pd.read_csv(ROOT / "06_PLASTICITY_EVIDENCE.csv")
for _, r in pl.iterrows():
    add(r.intervention, "TrainingIntervention", "diet/training->sensory_phenotype",
        f"S1:{r.outcome[:60]}", "SensoryPhenotype", pmid=r.pmid, design=r.design,
        species="human", n=r.n, effect=r.effect, pval=r.pval,
        grade="A" if "RCT" in str(r.design) else "B", note=r.note)

# drug -> sensory phenotype (human-panel rows of 05)
dr = pd.read_csv(ROOT / "05_DRUG_SENSORY_EVIDENCE.csv")
for _, r in dr.iterrows():
    if r.evidence_grade in ("A",):
        add(r.drug, "Drug", "drug->sensory_phenotype", f"S1:{r.finding[:60]}",
            "SensoryPhenotype", pmid=r.pmid, design=r.system, species=r.species,
            effect=r.finding, grade="A", note=r.note)

# variant -> medication behavior (Lipchock/Mennella)
add("TAS2R38:bitter-sensitive haplotype", "Variant", "variant->medication_behavior",
    "solid formulation usage (children)", "BehavioralPhenotype", pmid=22440514,
    design="retrospective", species="human", n="448", effect="more solid-form use", pval="<0.05", grade="B")
add("TAS2R38:A49P P allele", "Variant", "variant->medication_behavior",
    "liquid medication rejection reports (children)", "BehavioralPhenotype", pmid=26391354,
    design="retrospective interview", species="human", n="172", effect="more rejection", pval="0.02", grade="B")

g = pd.DataFrame(edges)
g.to_csv(ROOT / "07_EVIDENCE_GRAPH.csv", index=False)
nodes = sorted(set(g.src) | set(g.dst))
js = {"nodes": [{"id": x, "type": (g[g.src == x].src_type.iloc[0] if (g.src == x).any()
                                   else g[g.dst == x].dst_type.iloc[0])} for x in nodes],
      "edges": g.to_dict("records")}
(ROOT / "08_EVIDENCE_GRAPH.json").write_text(json.dumps(js, indent=1))
print("nodes:", len(nodes), "edges:", len(g))
print(g.src_type.value_counts().to_string())
