import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_inventory_covers_all_evidence_pmids():
    inv = set(pd.read_csv(ROOT / "03_STUDY_INVENTORY.csv").pmid.astype(int))
    for f in ["04_VARIANT_EVIDENCE.csv", "05_DRUG_SENSORY_EVIDENCE.csv",
              "06_PLASTICITY_EVIDENCE.csv"]:
        df = pd.read_csv(ROOT / f)
        missing = set(df.pmid.astype(int)) - inv
        assert not missing, f"{f}: PMIDs missing from inventory: {missing}"


def test_locked_predictions_have_required_columns_and_neg_controls():
    p = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS.csv")
    for c in ["variant", "drug", "tier", "predicted_direction", "magnitude",
              "mechanism", "expected_behavior", "alternative",
              "negative_control", "falsifier"]:
        assert c in p.columns
    assert (p.tier == "4 (negative control)").any(), "need explicit negative controls"
    tier1 = p[p.tier == "1"]
    assert not tier1.expected_behavior.str.contains("null", case=False).any()


def test_no_tommo_data():
    """Only publicly documented ToMMo materials (questionnaire PDFs and
    text extracts) are allowed — no participant-level data."""
    allowed = {"tommo_public"}
    for p in (ROOT / "data").rglob("*tommo*"):
        assert any(a in p.parts for a in allowed), f"unexpected ToMMo file: {p}"
    pub = ROOT / "data" / "raw" / "tommo_public"
    if pub.exists():
        for p in pub.iterdir():
            assert p.suffix in {".pdf", ".txt", ".csv"}, p


def test_references_have_no_orphans():
    bib = (ROOT / "18_REFERENCES.bib").read_text()
    entries = re.findall(r"@article\{(\w+),", bib)
    inv = pd.read_csv(ROOT / "03_STUDY_INVENTORY.csv")
    assert len(entries) == len(inv)


def test_graph_nodes_edges_consistent():
    edges = pd.read_csv(ROOT / "07_EVIDENCE_GRAPH.csv")
    import json
    g = json.loads((ROOT / "08_EVIDENCE_GRAPH.json").read_text())
    ids = {n["id"] for n in g["nodes"]}
    for _, r in edges.iterrows():
        assert r.src in ids and r.dst in ids


def test_v2_freeze_files():
    v2 = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv")
    pre = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv")
    assert len(pre) == len(v2)
    assert (v2.primary_or_secondary == "control").sum() >= 8
    pos = v2[v2.primary_or_secondary != "control"]
    assert len(pos) >= 10
    for c in ["evidence_score", "falsifying_result", "negative_control"]:
        assert c in v2.columns
    tmm = pd.read_csv(ROOT / "31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv")
    assert set(v2.prediction_id) == set(tmm.prediction_id)
    assert tmm.testability_status.isin(
        ["FULLY TESTABLE","TESTABLE WITH PROXY","PARTIALLY TESTABLE","NOT TESTABLE"]).all()


def test_preopening_lock_files_exist_and_consistent():
    """Files 60-90 present; frozen IDs consistent across locks."""
    for f in ["60_PREOPENING_INPUT_MANIFEST.md", "61_PREOPENING_ERRATA.md",
              "62_PREDICTION_HIERARCHY_FREEZE.csv", "63_GENOTYPE_IMPLEMENTATION_FINAL.csv",
              "64_GENOTYPE_PROXY_FREEZE.md", "65_TAS2R38_HAPLOTYPE_FREEZE.md",
              "66_FORMULATION_DICTIONARY_FINAL.csv", "67_ORAL_SENSORY_EXPOSURE_FREEZE.md",
              "68_TASTE_MASKING_FREEZE.csv", "69_MEDICATION_PARSER_VALIDATION.md",
              "70_MEDICATION_PARSER_VERSION.txt", "72_PREDICTION_OBSERVABILITY_FINAL.csv",
              "73_PREANALYSIS_POWER_ASSESSMENT.md", "74_REPEATED_WAVE_FREEZE.md",
              "75_CLAIMS_SUBCOHORT_FINAL_AUDIT.md", "76_INDICATION_CONFOUNDING_FINAL.csv",
              "78_OUTCOME_TERMINOLOGY_FREEZE.md", "79_NEGATIVE_CONTROL_FINAL.csv",
              "80_MECHANISTIC_GRADIENT_FINAL.md", "81_CALIBRATION_FINAL_LOCK.md",
              "82_MULTIPLE_TESTING_FINAL.md", "83_PRIMARY_SAP_FINAL.md",
              "84_SENSITIVITY_FREEZE_FINAL.md", "85_INTERPRETATION_MATRIX_FINAL.md",
              "86_JOURNAL_DECISION_TREE_FINAL.md", "87_ANALYSIS_AUTHORIZATION_MATRIX.csv",
              "88_AMENDMENT_POLICY_FINAL.md", "89_FINAL_OPENING_DECISION.md",
              "90_PRIMARY_VALIDATION_HANDOFF.md",
              "71_MEDICATION_PARSER/medication_parser.py",
              "71_MEDICATION_PARSER/gold_corpus.csv",
              "77_PRIMARY_DAGS/README.md"]:
        assert (ROOT / f).exists(), f"missing {f}"
    hier = set(pd.read_csv(ROOT / "62_PREDICTION_HIERARCHY_FREEZE.csv").prediction_id)
    obs = set(pd.read_csv(ROOT / "72_PREDICTION_OBSERVABILITY_FINAL.csv").prediction_id)
    v2 = set(pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv").prediction_id)
    assert v2 <= hier, f"hierarchy missing {v2 - hier}"
    assert v2 <= obs | {"C1","C2","C3","C4","C5"}, obs


def test_parser_hash_and_validation_thresholds():
    import hashlib, subprocess, sys, csv
    ver = dict(l.strip().split("=", 1) for l in
               (ROOT / "70_MEDICATION_PARSER_VERSION.txt").read_text().splitlines()
               if "=" in l)
    p = ROOT / "71_MEDICATION_PARSER" / "medication_parser.py"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == ver["sha256"], "parser drifted"
    sys.path.insert(0, str(ROOT / "71_MEDICATION_PARSER"))
    import importlib
    mp = importlib.import_module("medication_parser")
    gold = list(csv.DictReader(open(ROOT / "71_MEDICATION_PARSER" / "gold_corpus.csv")))
    n = len(gold)
    assert n >= 100
    ing = sum(mp.parse(r["raw_text"])["generic_name"] == r["gold_generic"] for r in gold) / n
    route = sum(mp.parse(r["raw_text"])["route"] == r["gold_route"] for r in gold) / n
    form = sum(mp.parse(r["raw_text"])["formulation"] == r["gold_formulation"] for r in gold) / n
    exp = sum(str(mp.parse(r["raw_text"])["oral_sensory_exposure"]) == r["gold_exposure"] for r in gold) / n
    assert ing >= 0.95 and route >= 0.95 and form >= 0.90 and exp >= 0.90


def test_banned_terminology_not_in_freezes():
    txt = (ROOT / "78_OUTCOME_TERMINOLOGY_FREEZE.md").read_text()
    for banned in ["adherence", "persistence", "discontinuation"]:
        assert banned in txt  # listed as banned
    out = pd.read_csv(ROOT / "72_PREDICTION_OBSERVABILITY_FINAL.csv")
    assert not out.observability_status.str.contains("adherence|persistence", case=False).any()


def test_amendment_files_and_p01_separation():
    for f in ["91_P01_P10_SEPARATION_AMENDMENT.md","92_TOMMO_REALSTRING_PARSER_VALIDATION.md",
              "93_TOMMO_REALSTRING_QC_SAMPLE.csv","94_MEDICATION_PARSER_FINAL_VERSION.txt",
              "95_FORMAL_GRADIENT_AMENDMENT.md","96_CONTINUOUS_CALIBRATION_AMENDMENT.md",
              "97_PREOPENING_AMENDMENT_MANIFEST.md","98_FINAL_OPENING_DECISION_V2.md",
              "99_PRIMARY_VALIDATION_HANDOFF_V2.md"]:
        assert (ROOT/f).exists(), f"missing {f}"
    t = (ROOT/"74_REPEATED_WAVE_FREEZE.md").read_text()
    assert "collapses into the P10" not in t
    assert "never merged" in t
    obs = (ROOT/"72_PREDICTION_OBSERVABILITY_FINAL.csv").read_text()
    assert "merge with P02" not in obs and "rescue logic" not in obs
    import hashlib
    ver = dict(l.split("=",1) for l in (ROOT/"94_MEDICATION_PARSER_FINAL_VERSION.txt").read_text().splitlines() if "=" in l)
    assert hashlib.sha256((ROOT/"71_MEDICATION_PARSER/medication_parser.py").read_bytes()).hexdigest()==ver["sha256"]
    g = (ROOT/"82_MULTIPLE_TESTING_FINAL.md").read_text()
    assert "F-GRADIENT" in g and "F-CALIBRATION" in g
    sap = (ROOT/"83_PRIMARY_SAP_FINAL.md").read_text()
    assert "β3" in sap or "G×E" in sap
