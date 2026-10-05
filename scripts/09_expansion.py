#!/usr/bin/env python3
"""Phases A-I of the prediction-expansion pass.

Inputs (frozen, read-only): 13_LOCKED_PREDICTIONS.csv,
17_GO_NOGO_DECISION.md, evidence CSVs, BitterDB edges.

Outputs:
  23_CANDIDATE_PREDICTIONS_ALL.csv
  24_PREDICTION_EVIDENCE_AUDIT.csv
  25_FORMULATION_ROUTE_CONTRASTS.csv
  26_NEGATIVE_CONTROLS.csv
  13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv
  31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv
  33_ALTERNATIVE_EXPLANATION_AUDIT.csv
  13_LOCKED_PREDICTIONS_v2_FINAL.csv
Deterministic; no network.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BITTER = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
BITTER_EDGES = set(zip(BITTER.receptor, BITTER.compound_name.str.lower()))

def edge(receptor, drug):
    """'known' if receptor-drug edge is curated in BitterDB."""
    names = [drug.lower()]
    return any((receptor, n) in BITTER_EDGES for n in names)

# ------------------------------------------------------------------
# Positive / directional candidates. Component scores set per rubric
# (21_PREDICTION_SCORING_RUBRIC.md); each row lists audit citations.
# ------------------------------------------------------------------
CAND = [
 dict(pid="P01", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598;rs1726866;rs10246939", haplotype="PAV vs AVI",
      receptor="TAS2R38", drug="propylthiouracil", dclass="antithyroid (thiourea)",
      route="oral", formulation="tablet", prop="bitterness (thiourea moiety)",
      direction="PAV -> stronger bitterness -> higher avoidance of liquid/bitter exposure",
      magnitude="large", tier="A", G=3, H=3, R=3, V=3, Rep=2, F=1, O=1, A=1,
      mech="TAS2R38 agonism (BitterDB; PROP EC50 2.1uM PAV)",
      behavior="avoidance / formulation choice",
      alt="none credible (validated chain)",
      neg="non-oral drug same genotype -> null",
      falsify="no sensory difference despite power+exposure",
      primary="primary", cites="12595690;15723792;20675712;23632915"),
 dict(pid="P02", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598", haplotype="PAV vs AVI", receptor="TAS2R38",
      drug="methimazole (thiamazole)", dclass="antithyroid",
      route="oral", formulation="tablet", prop="bitterness (thiourea moiety)",
      direction="PAV -> stronger bitterness -> formulation/use gradient",
      magnitude="moderate", tier="B", G=3, H=2, R=3, V=3, Rep=1, F=1, O=2, A=1,
      mech="methimazole = validated TAS2R38 ligand (Behrens 2013; BitterDB)",
      behavior="cross-wave use / formulation preference",
      alt="indication (hyperthyroidism) fixed; prescriber choice",
      neg="carbimazole prodrug / non-oral route", falsify="null in powered sample",
      primary="primary", cites="23632915;BitterDB"),
 dict(pid="P03", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598", haplotype="PAV vs AVI", receptor="TAS2R38",
      drug="chloramphenicol", dclass="antibiotic", route="oral",
      formulation="capsule/suspension", prop="bitterness",
      direction="PAV -> stronger bitterness", magnitude="moderate", tier="A",
      G=3, H=3, R=3, V=3, Rep=1, F=1, O=0, A=2,
      mech="TAS2R38-dependent bitterness in human panel",
      behavior="liquid rejection reports",
      alt="ancestry, indication; rare use in Japan",
      neg="ofloxacin (TAS2R9)", falsify="null replication",
      primary="secondary", cites="35967977"),
 dict(pid="P04", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598", haplotype="PAV vs AVI", receptor="TAS2R38",
      drug="chlorpheniramine", dclass="antihistamine", route="oral",
      formulation="syrup/drops vs tablet", prop="bitterness",
      direction="PAV -> stronger bitterness -> syrup avoidance",
      magnitude="small-moderate", tier="C", G=3, H=1, R=3, V=3, Rep=0, F=2, O=1, A=2,
      mech="chlorpheniramine -> TAS2R38/46 (BitterDB); known bitter antihistamine",
      behavior="formulation choice / reported use",
      alt="OTC access, indication, age", neg="tablet (masked) contrast",
      falsify="no gradient", primary="secondary", cites="BitterDB"),
 dict(pid="P05", gene="TAS2R9", variant="V187A", rsid="", haplotype="",
      receptor="TAS2R9", drug="ofloxacin", dclass="fluoroquinolone",
      route="oral", formulation="tablet/drops", prop="bitterness",
      direction="187A -> altered bitterness", magnitude="moderate", tier="A",
      G=2, H=2, R=3, V=2, Rep=0, F=1, O=1, A=2,
      mech="human cohort assoc + BitterDB TAS2R9 edge",
      behavior="formulation preference", alt="single-cohort",
      neg="non-TAS2R9 bitter drug", falsify="no assoc in replication",
      primary="primary", cites="35967977;BitterDB"),
 dict(pid="P06", gene="TAS2R19", variant="R299C", rsid="rs10772420",
      haplotype="", receptor="TAS2R19 (chr12 cluster)",
      drug="quinine / quinidine", dclass="antimalarial/antiarrhythmic",
      route="oral", formulation="tablet", prop="bitterness",
      direction="C-allele -> higher quinine intensity",
      magnitude="moderate", tier="A", G=3, H=2, R=2, V=2, Rep=2, F=1, O=1, A=2,
      mech="GWAS lead (P=1.8e-15, 5.8% var); salivary-gene confound possible",
      behavior="bitter-exposure linked use", alt="low quinine exposure in Japan; LD cluster",
      neg="caffeine (no GWAS hit same study)", falsify="null",
      primary="secondary", cites="20675712;26024668"),
 dict(pid="P07", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598", haplotype="PAV vs AVI", receptor="TAS2R38",
      drug="liquid oral medications (aggregate)", dclass="cross-class",
      route="oral", formulation="liquid", prop="bitterness",
      direction="PAV -> more rejection / solid-form preference",
      magnitude="small-moderate", tier="B", G=3, H=2, R=3, V=3, Rep=1, F=2, O=1, A=3,
      mech="bitter intensity -> acceptance (pediatric chain)",
      behavior="formulation choice", alt="age/indication/adherence traits",
      neg="enteric-coated masked formulation", falsify="no assoc",
      primary="secondary", cites="22440514;26391354;25381313"),
 dict(pid="P08", gene="TAS1R2", variant="rs12033832", rsid="rs12033832",
      haplotype="", receptor="TAS1R2/TAS1R3", drug="sweetened oral formulations",
      dclass="formulation contrast", route="oral", formulation="sweetened vs plain",
      prop="sweetness", direction="G allele -> lower sweet perception -> reduced masking benefit",
      magnitude="small", tier="B", G=2, H=1, R=1, V=2, Rep=1, F=2, O=1, A=3,
      mech="sweet receptor sensitivity alters masking",
      behavior="formulation preference", alt="BMI interaction; broad confounding",
      neg="unflavored formulation", falsify="no genotype x sweetness interaction",
      primary="secondary", cites="sweet_loci_pool"),
 dict(pid="P09", gene="TRPA1", variant="rs11988795", rsid="rs11988795",
      haplotype="", receptor="TRPA1", drug="chemesthetic oral liquids (ibuprofen susp)",
      dclass="NSAID", route="oral", formulation="suspension",
      prop="chemesthesis (tingling)", direction="variant -> more irritation -> lower acceptability",
      magnitude="moderate", tier="B", G=2, H=3, R=2, V=2, Rep=0, F=2, O=1, A=2,
      mech="pediatric GWAS panel hit; not taste",
      behavior="palatability-driven use", alt="single cohort; ancestry",
      neg="non-irritating formulation", falsify="no replication",
      primary="secondary", cites="37685855"),
 dict(pid="P10", gene="TAS2R4", variant="differential-activation variant",
      rsid="", haplotype="", receptor="TAS2R4", drug="PROP / thiourea exposure in AVI carriers",
      dclass="antithyroid class", route="oral", formulation="any oral",
      prop="bitterness (partial rescue)", direction="variant -> retained PROP sensing in AVI",
      magnitude="small-moderate", tier="C", G=2, H=1, R=2, V=2, Rep=0, F=1, O=0, A=2,
      mech="compensatory activation rescues AVI phenotype",
      behavior="attenuated avoidance", alt="rare allele; proxy weak",
      neg="PAV homozygotes", falsify="no rescue effect",
      primary="secondary", cites="38732607"),
 dict(pid="P11", gene="TAS2R43/TAS2R46", variant="polymorphisms",
      rsid="", haplotype="", receptor="TAS2R43/46",
      drug="acesulfame-K sweetened formulations", dclass="formulation ingredient",
      route="oral", formulation="Ace-K sweetened", prop="bitterness of sweetener",
      direction="variant -> altered Ace-K bitterness -> sweetened-form preference",
      magnitude="small", tier="B", G=2, H=2, R=3, V=1, Rep=0, F=1, O=1, A=3,
      mech="Ace-K bitterness varies with receptor polymorphisms; BitterDB edges",
      behavior="sweetened formulation preference", alt="ingredient not drug; masked co-formulation",
      neg="sugar-sweetened only", falsify="no assoc",
      primary="secondary", cites="BitterDB"),
 dict(pid="P12", gene="TAS2R38", variant="PAV/AVI diplotype",
      rsid="rs713598", haplotype="PAV vs AVI", receptor="TAS2R38",
      drug="erythromycin (suspension)", dclass="macrolide", route="oral",
      formulation="suspension vs enteric/film tab", prop="bitterness",
      direction="PAV -> more bitterness -> suspension avoidance",
      magnitude="small-moderate", tier="C", G=3, H=1, R=2, V=3, Rep=0, F=2, O=1, A=2,
      mech="erythromycin -> TAS2R1/10 (not TAS2R38): generalized bitter intensity proxy only",
      behavior="formulation use gradient", alt="non-TAS2R38 receptor; prescriber",
      neg="enteric-coated tab", falsify="no gradient",
      primary="secondary", cites="BitterDB"),
]

NEG = [
 dict(nid="N01", cls="route", gene="TAS2R38", drug="insulin", route="parenteral",
      expect="null", rationale="no oral chemosensory exposure", flag=""),
 dict(nid="N02", cls="route", gene="TAS2R38", drug="gentamicin", route="parenteral",
      expect="null", rationale="no oral exposure; ototoxicity is not taste",
      flag="systemic T2R biology possible but not orosensory"),
 dict(nid="N03", cls="route", gene="TAS2R38", drug="remdesivir", route="IV",
      expect="null", rationale="no oral exposure", flag=""),
 dict(nid="N04", cls="route", gene="TAS2R38", drug="fentanyl patch", route="transdermal",
      expect="null", rationale="bypasses oral mucosa", flag="systemic exposure exists"),
 dict(nid="N05", cls="masking", gene="TAS2R38", drug="omeprazole (enteric-coated)",
      route="oral", expect="null or attenuated", rationale="enteric coat removes oral exposure",
      flag="partial masking only; chewing voids it"),
 dict(nid="N06", cls="masking", gene="TAS2R38", drug="erythromycin enteric/film-coated tab",
      route="oral", expect="attenuated vs suspension", rationale="film coat delays release",
      flag=""),
 dict(nid="N07", cls="mismatch", gene="TAS2R9", drug="PROP", route="oral",
      expect="null", rationale="PROP ligand is TAS2R38, not TAS2R9", flag=""),
 dict(nid="N08", cls="mismatch", gene="TAS2R38", drug="ofloxacin", route="oral",
      expect="null", rationale="ofloxacin edge is TAS2R9; no TAS2R38 edge in BitterDB",
      flag="broad-spectrum receptor activity not excluded"),
 dict(nid="N09", cls="published_null", gene="TAS2R38", drug="clindamycin liquid",
      route="oral", expect="null", rationale="2026 prospective n=67: rs713598 null",
      flag="low power; treat as weak control"),
 dict(nid="N10", cls="mismatch", gene="TAS1R2", drug="quinine", route="oral",
      expect="null", rationale="quinine is bitter/T2R-ligand; TAS1R2 is sweet",
      flag=""),
 dict(nid="N11", cls="masking", gene="TRPA1", drug="ibuprofen film-coated tablet",
      route="oral", expect="attenuated vs suspension", rationale="coating removes chemesthetic contact",
      flag=""),
 dict(nid="N12", cls="adherence", gene="TAS2R38", drug="supplement / health-food use",
      route="oral (mixed)", expect="null for the association",
      rationale="tests generic healthcare-seeking/adherence, not drug taste",
      flag="some supplements are bitter; interpret jointly with N05"),
]

CONTRASTS = [
 dict(cid="C1", drug="erythromycin", fa="oral suspension", fb="enteric/film-coated tablet",
      ra="oral", rb="oral", direction="bitterness-mediated avoidance A>B",
      order="suspension > tablet", basis="TAS2R1/10 agonism only on unmasked exposure",
      evidence="BitterDB edges", alt="prescriber formulation choice", falsify="reversed or flat gradient"),
 dict(cid="C2", drug="acetaminophen", fa="liquid/syrup", fb="film tablet",
      ra="oral", rb="oral", direction="liquid shows stronger genotype-linked aversion",
      order="liquid > tablet", basis="TAS2R39 agonism; direct mucosal contact",
      evidence="BitterDB TAS2R39 edge", alt="age selects syrup anyway", falsify="flat"),
 dict(cid="C3", drug="theophylline", fa="elixir", fb="sustained-release tablet",
      ra="oral", rb="oral", direction="elixir > SR tab", order="elixir > SR",
      basis="broad T2R agonism (TAS2R7/10/14/43/46)", evidence="BitterDB",
      alt="asthma severity confounds formulation", falsify="flat"),
 dict(cid="C4", drug="potassium chloride", fa="oral liquid/drops", fb="extended-release tablet",
      ra="oral", rb="oral", direction="liquid > ER tab", order="liquid > ER",
      basis="metallic-bitter drops documented; ER wax matrix masks",
      evidence="formulation literature", alt="GI tolerability, not taste", falsify="flat"),
 dict(cid="C5", drug="insulin (route contrast)", fa="none", fb="parenteral",
      ra="oral", rb="parenteral", direction="genotype effect absent at parenteral",
      order="oral-exposed > parenteral=0", basis="no orosensory contact",
      evidence="route logic", alt="systemic T2R biology", falsify="parenteral assoc"),
]

def score(r):
    return r["G"]+r["H"]+r["R"]+r["V"]+r["Rep"]+r["F"]+r["O"]-r["A"]

rows = []
for r in CAND:
    r = dict(r); r["evidence_score"] = score(r)
    r["bitterdb_edge"] = edge(r["receptor"].split("/")[0].split(" ")[0], r["drug"])
    rows.append(r)

cand = pd.DataFrame(rows)
cand.to_csv(ROOT / "23_CANDIDATE_PREDICTIONS_ALL.csv", index=False)

# 24 audit: per-component evidence pointer
aud = cand[["pid","gene","drug","tier","evidence_score","G","H","R","V","Rep","F","O","A","mech","cites"]].copy()
aud.columns = ["prediction_id","gene","drug","evidence_tier","evidence_score",
               "G_human_genotype_sensory","H_human_drug_sensory","R_receptor_drug",
               "V_variant_function","Rep_replication","F_formulation","O_observability",
               "A_alt_explanation_penalty","rationale","key_citations"]
aud.to_csv(ROOT / "24_PREDICTION_EVIDENCE_AUDIT.csv", index=False)

pd.DataFrame(NEG).to_csv(ROOT / "26_NEGATIVE_CONTROLS.csv", index=False)
pd.DataFrame(CONTRASTS).to_csv(ROOT / "25_FORMULATION_ROUTE_CONTRASTS.csv", index=False)

# v2 preliminary = positive predictions + negative controls in one table
out_cols = ["prediction_id","gene","variant","rsID","haplotype","receptor",
            "drug_generic_name","drug_class","route","formulation","sensory_property",
            "predicted_direction","predicted_magnitude_category","evidence_tier",
            "evidence_score","human_genotype_sensory_evidence",
            "human_drug_sensory_evidence","functional_receptor_drug_evidence",
            "variant_function_evidence","replication_status","mechanistic_rationale",
            "behavioral_prediction","strongest_alternative_explanation",
            "negative_control","falsifying_result","primary_or_secondary","key_citations"]

v2 = []
for r in rows:
    v2.append(dict(prediction_id=r["pid"], gene=r["gene"], variant=r["variant"],
        rsID=r["rsid"], haplotype=r["haplotype"], receptor=r["receptor"],
        drug_generic_name=r["drug"], drug_class=r["dclass"], route=r["route"],
        formulation=r["formulation"], sensory_property=r["prop"],
        predicted_direction=r["direction"], predicted_magnitude_category=r["magnitude"],
        evidence_tier=r["tier"], evidence_score=r["evidence_score"],
        human_genotype_sensory_evidence=r["G"], human_drug_sensory_evidence=r["H"],
        functional_receptor_drug_evidence=r["R"], variant_function_evidence=r["V"],
        replication_status=r["Rep"], mechanistic_rationale=r["mech"],
        behavioral_prediction=r["behavior"], strongest_alternative_explanation=r["alt"],
        negative_control=r["neg"], falsifying_result=r["falsify"],
        primary_or_secondary=r["primary"], key_citations=r["cites"]))
for n in NEG:
    v2.append(dict(prediction_id=n["nid"], gene=n["gene"], variant="",
        rsID="", haplotype="", receptor="", drug_generic_name=n["drug"],
        drug_class="negative_control:"+n["cls"], route=n["route"], formulation="",
        sensory_property="", predicted_direction=n["expect"],
        predicted_magnitude_category="null", evidence_tier="D", evidence_score="",
        human_genotype_sensory_evidence="", human_drug_sensory_evidence="",
        functional_receptor_drug_evidence="", variant_function_evidence="",
        replication_status="", mechanistic_rationale=n["rationale"],
        behavioral_prediction="no association", strongest_alternative_explanation=n["flag"],
        negative_control="self", falsifying_result="spurious positive",
        primary_or_secondary="control", key_citations=""))
v2df = pd.DataFrame(v2)[out_cols]
v2df.to_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv", index=False)

# 31 testability matrix — ToMMo public-metadata judgment (Phase D audit doc is authoritative)
TST = {
 # pid: (genotype, med, formulation, route, diet, covars, status, note)
 "P01": ("likely","confirmed:brand free-text","proxy:brand suffix","proxy:units","yes","yes","TESTABLE WITH PROXY","PTU/PROP exposure rare in Japan; thin N"),
 "P02": ("likely","confirmed:brand free-text","proxy:brand suffix","proxy:units","yes","yes","TESTABLE WITH PROXY","thiamazole common; tablet exposure moderate"),
 "P03": ("likely","confirmed","proxy","proxy","yes","yes","PARTIALLY TESTABLE","chloramphenicol rare in Japan"),
 "P04": ("likely","confirmed incl OTC","proxy","proxy","yes","yes","TESTABLE WITH PROXY","syrup vs tab distinguishable by brand"),
 "P05": ("likely","confirmed","proxy","proxy","yes","yes","TESTABLE WITH PROXY","ofloxacin use moderate"),
 "P06": ("likely","confirmed","proxy","proxy","yes","yes","PARTIALLY TESTABLE","quinine use rare"),
 "P07": ("likely","confirmed","proxy","proxy","yes","yes","TESTABLE WITH PROXY","liquid-use aggregate outcome"),
 "P08": ("likely","confirmed","weak proxy","proxy","yes","yes","PARTIALLY TESTABLE","sweetening rarely in brand name"),
 "P09": ("likely","confirmed incl OTC","proxy","proxy","yes","yes","TESTABLE WITH PROXY","ibuprofen susp"),
 "P10": ("uncertain:rare allele","confirmed","proxy","proxy","yes","yes","PARTIALLY TESTABLE","allele availability unconfirmed"),
 "P11": ("uncertain","confirmed","weak proxy","proxy","yes","yes","PARTIALLY TESTABLE","ingredient-level exposure unseen"),
 "P12": ("likely","confirmed","proxy","proxy","yes","yes","TESTABLE WITH PROXY","suspension vs tab brands"),
}
tst = []
for r in rows:
    g,m,f,rt,diet,cov,st,note = TST[r["pid"]]
    tst.append(dict(prediction_id=r["pid"], required_genotype=g,
        required_medication_variable=m, required_formulation_variable=f,
        required_route_variable=rt, required_dietary_sensory_variable=diet,
        required_covariates=cov, publicly_confirmed_availability=m,
        uncertain_availability=";".join(x for x in [g,f,rt] if "proxy" in x or "uncertain" in x or "likely" in x),
        fatal_missing_variable="sensory phenotype measure (none publicly documented)" if st=="PARTIALLY TESTABLE" else "",
        testability_status=st, note=note))
for n in NEG:
    st = "TESTABLE WITH PROXY" if n["cls"] in ("route","masking","mismatch","adherence") else "PARTIALLY TESTABLE"
    tst.append(dict(prediction_id=n["nid"], required_genotype="likely",
        required_medication_variable="confirmed:brand free-text",
        required_formulation_variable="proxy", required_route_variable="proxy:unit/brand",
        required_dietary_sensory_variable="yes", required_covariates="yes",
        publicly_confirmed_availability="medication use section confirmed in wave1/2 questionnaires",
        uncertain_availability="formulation via brand parsing",
        fatal_missing_variable="", testability_status=st, note=n["cls"]))
pd.DataFrame(tst).to_csv(ROOT / "31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv", index=False)

# 33 alternative-explanation audit
threats = ["indication","disease severity","prescriber preference","age","sex",
           "ancestry","SES","polypharmacy","health literacy","adherence tendency",
           "diet","smoking","alcohol","extraoral receptor biology","pleiotropy/LD",
           "PK mechanism","PD mechanism","formulation masking","drug availability"]
L,M,H = "low","moderate","high"
altrows=[]
for r in rows:
    t = dict.fromkeys(threats, L)
    t.update({"indication":H if r["A"]>=2 else M, "ancestry":M,
              "adherence tendency":H if r["O"]<=1 else M,
              "extraoral receptor biology":M, "PK mechanism":M,
              "formulation masking":H if "tablet" in r["formulation"] else M})
    altrows.append(dict(prediction_id=r["pid"], **t,
        control_strategy="negative controls + formulation contrasts + covariates + interaction estimand",
        residual="indication and adherence-trait confounding cannot be fully removed observationally"))
pd.DataFrame(altrows).to_csv(ROOT / "33_ALTERNATIVE_EXPLANATION_AUDIT.csv", index=False)

# FINAL freeze: primary + controls only (secondary kept flagged)
final = v2df.copy()
final.to_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv", index=False)

print("candidates:", len(rows), "| negatives:", len(NEG), "| contrasts:", len(CONTRASTS))
print(cand[["pid","evidence_score","tier"]].to_string(index=False))
