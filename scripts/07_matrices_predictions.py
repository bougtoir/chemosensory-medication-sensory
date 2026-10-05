#!/usr/bin/env python3
"""Stage 2 outputs:
11_RECEPTOR_DRUG_MATRIX.csv   (R x D, known/predicted/unknown, never merged)
12_VARIANT_FUNCTION_MATRIX.csv (G x R functional annotation)
13_LOCKED_PREDICTIONS.csv     (frozen predictions for future validation)
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "prediction" / "drug_chemical_space.csv")
b = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
b["n"] = b.compound_name.map(norm); d["n"] = d.generic_name.map(norm)
m = d.merge(b, on="n")

# ---- 11: receptor x drug matrix (long form) ----
receptors = sorted(b.receptor.unique())
rows = []
for _, dr in d.iterrows():
    known = m[m.n == dr["n"]].receptor.tolist()
    for r in receptors:
        status = "known_agonism" if r in known else "unknown"
        rows.append({"receptor": r, "drug": dr.generic_name, "status": status,
                     "evidence": "BitterDB" if r in known else "",
                     "oral_exposure": dr.oral_exposure})
mat = pd.DataFrame(rows)
mat.to_csv(ROOT / "11_RECEPTOR_DRUG_MATRIX.csv", index=False)

# literature drug->sensory (human) flag column appended separately
lit = pd.read_csv(ROOT / "05_DRUG_SENSORY_EVIDENCE.csv")
human_panel = lit[lit.evidence_grade == "A"].drug.tolist()

# ---- 12: variant function matrix ----
vf = [
 dict(gene="TAS2R38", variant="PAV", rsid="rs713598;rs1726866;rs10246939",
      effect_class="gain vs AVI", detail="responds to PTC/PROP/goitrin/methimazole; PROP EC50 2.1uM, PTC 1.1uM",
      delta_ec50="reference", delta_emax="high", pmid=15723792),
 dict(gene="TAS2R38", variant="AVI", rsid="same", effect_class="loss of function",
      detail="no detectable response to PTC/PROP; dominant non-taster allele",
      delta_ec50="undefined (no response)", delta_emax="~0", pmid=15723792),
 dict(gene="TAS2R38", variant="AAI, PVI, AVV, etc.", rsid="", effect_class="altered potency",
      detail="continuous range of in vitro responses across 6 haplotypes; rare haplotypes lack phenotypic association",
      delta_ec50="intermediate", delta_emax="variable", pmid=23632915),
 dict(gene="TAS2R38", variant="A49P (sub-haplotype marker)", rsid="rs713598",
      effect_class="proxy marker", detail="P allele tracks PAV-taster function in pediatric studies",
      delta_ec50="", delta_emax="", pmid=15687429),
 dict(gene="TAS2R19", variant="R299C", rsid="rs10772420", effect_class="altered potency (quinine)",
      detail="GWAS lead for quinine intensity (5.8% variance); salivary-gene confound possible",
      delta_ec50="", delta_emax="", pmid=20675712),
 dict(gene="TAS2R31", variant="allelic variants", rsid="", effect_class="altered sensitivity (quinine)",
      detail="associates with quinine bitterness + grapefruit liking", delta_ec50="", delta_emax="",
      pmid=26024668),
 dict(gene="TAS2R9", variant="V187A", rsid="", effect_class="altered sensitivity (ofloxacin)",
      detail="associates with ofloxacin bitterness in humans; BitterDB: ofloxacin->TAS2R9",
      delta_ec50="", delta_emax="", pmid=35967977),
 dict(gene="TAS2R31/43", variant="multiple", rsid="", effect_class="altered potency (acesulfame-K)",
      detail="Ace-K bitterness varies with receptor polymorphisms", delta_ec50="", delta_emax="",
      pmid=23599216),
 dict(gene="TAS2R4", variant="differential-activation variant", rsid="",
      effect_class="compensatory potency (PROP)", detail="may restore PROP tasting in AVI carriers",
      delta_ec50="", delta_emax="", pmid=38732607),
 dict(gene="TAS1R1/TAS1R3", variant="TAS1R1-372T; TAS1R3-757C", rsid="",
      effect_class="altered potency (umami)", detail="TAS1R1-372T more sensitive; TAS1R3-757C less sensitive",
      delta_ec50="shift", delta_emax="", pmid=19696921),
 dict(gene="TAS1R2", variant="rs12033832", rsid="rs12033832", effect_class="altered sensitivity (sucrose, BMI-dependent)",
      detail="G allele -> lower sensitivity + higher sugar intake in BMI>=25", delta_ec50="", delta_emax="",
      pmid=26279452),
 dict(gene="SCNN1B", variant="rs239345; rs3785368", rsid="rs239345;rs3785368",
      effect_class="altered sensitivity (salt)", detail="AA/TT homozygotes perceive salt less intensely",
      delta_ec50="", delta_emax="", pmid=23118204),
 dict(gene="TRPA1", variant="rs11988795", rsid="rs11988795", effect_class="altered chemesthesis",
      detail="tingling response to ibuprofen formulation, ancestry-independent", delta_ec50="",
      delta_emax="", pmid=37685855),
]
pd.DataFrame(vf).to_csv(ROOT / "12_VARIANT_FUNCTION_MATRIX.csv", index=False)

# ---- 13: locked predictions (frozen before any validation) ----
pred = [
 dict(variant="TAS2R38 PAV/AVI diplotype (rs713598 etc.)", drug="propylthiouracil-class thiourea drugs / PROP probe",
      predicted_direction="PAV -> stronger bitterness", magnitude="large",
      mechanism="TAS2R38 agonism", expected_behavior="higher avoidance of bitter liquid forms",
      alternative="none credible (validated chain)", negative_control="non-oral drug, same genotype -> null",
      falsifier="no sensory difference despite power+exposure", tier="1"),
 dict(variant="TAS2R38 diplotype", drug="chloramphenicol (and structurally related bitter antibiotics)",
      predicted_direction="PAV -> stronger bitterness", magnitude="moderate",
      mechanism="TAS2R38-dependent perception", expected_behavior="liquid rejection reports",
      alternative="ancestry, indication", negative_control="ofloxacin (different receptor)",
      falsifier="null in powered sample", tier="1"),
 dict(variant="TAS2R9 V187A", drug="ofloxacin (fluoroquinolones)",
      predicted_direction="187A -> altered bitterness", magnitude="moderate",
      mechanism="TAS2R9 agonism (BitterDB)", expected_behavior="formulation preference",
      alternative="single-cohort finding may not replicate", negative_control="non-TAS2R9 bitter drug",
      falsifier="no assoc in powered replication", tier="2"),
 dict(variant="TAS2R38 diplotype", drug="liquid oral medications generally",
      predicted_direction="PAV -> more rejection / solid-form preference", magnitude="small-moderate",
      mechanism="bitter intensity -> acceptance", expected_behavior="formulation choice",
      alternative="confounded by age/indication/adherence traits",
      negative_control="enteric-coated masked formulation -> null", falsifier="no assoc",
      tier="2"),
 dict(variant="TAS2R38 diplotype", drug="clindamycin liquid",
      predicted_direction="NULL predicted (2026 prospective null already published)", magnitude="unknown/null",
      mechanism="non-TAS2R38 ligand", expected_behavior="no genotype effect",
      alternative="", negative_control="", falsifier="spurious positive in validation",
      tier="4 (negative control)"),
 dict(variant="TAS1R2 rs12033832", drug="sweetened formulations",
      predicted_direction="G allele -> lower sweet perception -> different masking benefit",
      magnitude="small", mechanism="sweet receptor sensitivity",
      expected_behavior="formulation preference", alternative="BMI interaction",
      negative_control="unflavored formulation", falsifier="no genotype x sweetness interaction",
      tier="3"),
 dict(variant="TRPA1 rs11988795", drug="chemesthetic oral liquids (ibuprofen-like)",
      predicted_direction="variant -> more tingling/irritation", magnitude="moderate",
      mechanism="chemesthesis, not taste", expected_behavior="palatability differences",
      alternative="single cohort, unvalidated", negative_control="non-irritating formulation",
      falsifier="no replication", tier="3"),
 dict(variant="TAS2R38 diplotype", drug="insulin (parenteral)", predicted_direction="NULL",
      magnitude="null", mechanism="no oral chemosensory exposure", expected_behavior="no association",
      alternative="", negative_control="—", falsifier="any positive assoc = pipeline artifact/confounding",
      tier="4 (negative control)"),
 dict(variant="TAS2R38 diplotype", drug="omeprazole (enteric-coated, masked)",
      predicted_direction="NULL or attenuated vs unmasked", magnitude="null-small",
      mechanism="formulation removes oral exposure", expected_behavior="no genotype effect",
      alternative="residual taste on chewing", negative_control="—",
      falsifier="strong positive assoc", tier="4 (negative control)"),
]
pd.DataFrame(pred).to_csv(ROOT / "13_LOCKED_PREDICTIONS.csv", index=False)

print("matrix rows:", len(mat), "| known edges:", (mat.status=='known_agonism').sum())
print("variant matrix:", len(vf), "| locked predictions:", len(pred))
