"""Offline pipeline validation on synthetic data only (17_SYNTHETIC_PIPELINE_VALIDATION)."""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE))
from chemotommo import _common as C  # noqa: E402


@pytest.fixture(scope="session")
def run(tmp_path_factory):
    d = tmp_path_factory.mktemp("syn")
    data, out = d / "data", d / "out"
    subprocess.run([sys.executable, str(PIPE / "synthetic" / "make_synthetic.py"), "--out", str(data)], check=True)
    subprocess.run([sys.executable, str(PIPE / "run_pipeline.py"), "--data", str(data), "--out", str(out), "--mode", "synthetic"],
                   check=True)
    return data, out


def ep(run):
    e = pd.read_csv(run[1] / "work" / "08_endpoints.csv").set_index("pid")
    return e


@pytest.mark.parametrize("pid,expect", [
    ("S00001", dict(ANY_MEDICATION_CHANGE=0, ACTIVE_INGREDIENT_CHANGE=0)),                      # brand change only
    ("S00002", dict(ANY_MEDICATION_CHANGE=1, STANDARDIZED_DOSE_INCREASE=1, STANDARDIZED_DOSE_DECREASE=0)),
    ("S00003", dict(ACTIVE_INGREDIENT_CHANGE=1, WITHIN_CLASS_SWITCH=1)),
    ("S00004", dict(MEDICATION_ADDITION=1, MEDICATION_REMOVAL=None, ACTIVE_INGREDIENT_CHANGE=None)),
    ("S00005", dict(MEDICATION_REMOVAL=1, MEDICATION_ADDITION=0)),
    ("S00006", dict(ANY_MEDICATION_CHANGE=0, STANDARDIZED_DOSE_INCREASE=0)),                     # duplicates summed
    ("S00007", dict(MEDICATION_REMOVAL=1, ACTIVE_INGREDIENT_CHANGE=0, STANDARDIZED_DOSE_INCREASE=0)),  # combination
    ("S00008", dict(STANDARDIZED_DOSE_INCREASE=None, STANDARDIZED_DOSE_DECREASE=None)),          # incompatible units
    ("S00010", dict(ANY_MEDICATION_CHANGE=0)),                                                   # unknown Drug ID -> text
    ("S00012", dict(ANY_MEDICATION_CHANGE=0)),                                                   # Drug ID vs KEDD ID
])
def test_fixed_cases(run, pid, expect):
    e = ep(run)
    for k, v in expect.items():
        got = e.at[pid, k]
        assert (pd.isna(got) if v is None else got == v), (pid, k, got)


def test_missing_phase_excluded(run):
    assert "S00009" not in ep(run).index


def test_unknown_ids_flagged(run):
    r = pd.read_csv(run[1] / "work" / "04_medication_rows.csv")
    s10 = r[r.pid == "S00010"].iloc[0]
    assert s10.drug_id_unknown and s10.id_source == "free_text"
    assert r[r.pid == "S00011"].unresolved.all() and r[r.pid == "S00011"].kedd_unknown.all()
    assert r[(r.pid == "S00012") & (r.wave == "ph2")].iloc[0].id_source == "kedd_id"


def test_structured_id_precedence():
    assert C.load_config(PIPE / "config")["drug_dictionary"]["id_priority"] == ["drug_id", "kedd_id", "free_text"]


@pytest.mark.parametrize("args,exp", [
    ((5, "mg", 1, "日"), (5.0, "mg")),
    ((1, "錠", 2, "日", 5), (10.0, "mg")),
    ((1, "錠", 2, "日", None, 1, "X"), (2.0, "count:X")),
    ((500, "µg", 1, "日"), (0.5, "mg")),
    ((1, "錠", 1, "週", 70), (10.0, "mg")),
    ((5, "mg", None, "日"), (math.nan, None)),
    ((5, "適量", 1, "日"), (math.nan, None)),
    ((5, "mg", 1, "日", None, 2), (math.nan, None)),            # combination mass not attributable
])
def test_dose_harmonization(args, exp):
    v, b = C.harmonize_dose(*args)
    assert b == exp[1] and (math.isnan(v) if math.isnan(exp[0]) else abs(v - exp[0]) < 1e-9)


def test_dose_thresholds_boundary():
    ing = pd.DataFrame([dict(pid="a", wave="ph1", ingredient="x", daily=4.0, basis="mg"),
                        dict(pid="a", wave="ph2", ingredient="x", daily=5.0, basis="mg"),
                        dict(pid="b", wave="ph1", ingredient="x", daily=5.0, basis="mg"),
                        dict(pid="b", wave="ph2", ingredient="x", daily=4.0, basis="mg"),
                        dict(pid="c", wave="ph1", ingredient="x", daily=5.0, basis="mg"),
                        dict(pid="c", wave="ph2", ingredient="x", daily=6.0, basis="mg")])
    e = C.compute_endpoints(ing, {}, ["a", "b", "c"], 1.25, 0.80).set_index("pid")
    assert e.at["a", "STANDARDIZED_DOSE_INCREASE"] == 1      # ratio exactly 1.25
    assert e.at["b", "STANDARDIZED_DOSE_DECREASE"] == 1      # ratio exactly 0.80
    assert e.at["c", "ANY_MEDICATION_CHANGE"] == 0            # 1.20 below threshold


def test_snp_status_and_proxy(run):
    s = pd.read_csv(run[1] / "results" / "03_snp_status.csv").set_index("variant")
    assert s.at["TAS2R38_PAV", "status"] == "DIRECTLY TESTABLE"
    assert s.at["TAS2R9_V187A", "status"] == "TESTABLE WITH PRE-SPECIFIED PROXY"
    assert s.at["TAS1R2_rs12033832", "status"] == "DIRECTLY TESTABLE"
    for v in ("TAS2R19_rs10772420", "TRPA1_rs11988795", "TAS2R4_unresolved", "TAS2R43_46"):
        assert s.at[v, "status"].startswith("REQUIRES PROTOCOL AMENDMENT")
    lb = pd.read_csv(run[1] / "results" / "03_level_b_snps.csv")
    assert set(lb.gene) == {"TAS1R3", "SCNN1A", "GNAT3"}     # TRPA1 excluded, PLCB2 fails HWE


def test_effect_allele_strand():
    e = pd.read_csv(PIPE / "config" / "derived" / "effect_alleles.csv").set_index("rsid")
    # PAV = Pro49/Ala262/Val296 on the minus-strand coding sequence = forward G/G/C
    assert (e.at["rs713598", "effect_allele"], e.at["rs1726866", "effect_allele"], e.at["rs10246939", "effect_allele"]) == ("G", "G", "C")
    assert e.at["rs3741845", "effect_allele"] == "G"


def test_em_haplotype():
    from importlib import util
    spec = util.spec_from_file_location("m03", PIPE / "chemotommo" / "03_snp_harmonization.py")
    m = util.module_from_spec(spec); spec.loader.exec_module(m)
    G = np.array([[2, 2, 2], [0, 0, 0], [1, 1, 1]] * 50, dtype=float)
    pav, other, _ = m.em_pav_dosage(G)
    assert list(pav[:3]) == [2, 0, 1]


def test_privacy_export(run):
    exp = run[1] / "export"
    ids = set(pd.read_csv(run[0] / "demographics.csv").participant_id)
    for f in exp.glob("*.csv"):
        df = pd.read_csv(f, dtype=str)
        assert not ({"pid", "participant_id", "family_id"} & set(df.columns)), f
        assert not any(df[c].isin(ids).any() for c in df.columns), f
    assert not list(exp.glob("0[3-9]_*rows*")) and not (exp / "11_analysis_dataset.csv").exists()
    assert json.loads((exp / "EXPORT_NOTE.json").read_text())["participant_level_files_exported"] == 0


def test_small_cell_suppression():
    m = C.load_module(PIPE / "chemotommo" / "22_privacy_safe_export.py", "m22")
    df = m.suppress(pd.DataFrame(dict(n=[3, 0, 50], events=[9, 10, 1])), 10)
    assert list(df.n) == ["<10", 0, 50] and list(df.events) == ["<10", 10, "<10"]


def test_interpretation_and_families(run):
    j = json.loads((run[1] / "results" / "20_interpretation.json").read_text())
    assert j["pattern"] in "ABCDE"
    den = pd.read_csv(run[1] / "results" / "20_family_denominators.csv").set_index("family")
    assert den.at["A", "n_frozen"] == 3 and den.at["AS", "n_frozen"] == 5 and den.at["C", "n_frozen"] == 21
    f = pd.read_csv(run[1] / "results" / "16_family_F.csv")
    assert f[f.test == "N11"].status.iloc[0].startswith("REQUIRES PROTOCOL AMENDMENT")


def test_real_mode_refuses_analysis_without_signoff(run, tmp_path):
    r = subprocess.run([sys.executable, str(PIPE / "run_pipeline.py"), "--data", str(run[0]), "--out", str(tmp_path / "o"),
                        "--mode", "real", "--stage", "analysis"], capture_output=True, text=True)
    assert r.returncode != 0 and "RECEIPT_SIGNOFF" in (r.stderr + r.stdout)


def test_no_hardcoded_delivered_columns():
    vm = C.load_config(PIPE / "config")["variable_map"]
    names = [t.split("{")[0] for t in vm["medication"]["slot_columns"].values()] + [v["column"] for v in vm["covariates"].values()]
    for p in (PIPE / "chemotommo").glob("*.py"):
        src = p.read_text()
        for n in names:
            assert not re.search(r"[\"']" + re.escape(n), src), (p.name, n)


def test_frozen_hashes_guarded():
    cfg = C.load_config(PIPE / "config")
    assert C.sha256((PIPE / "config" / cfg["drug_dictionary"]["free_text"]["parser"]).resolve()) == cfg["drug_dictionary"]["free_text"]["parser_sha256"]
    assert C.sha256((PIPE / "config" / cfg["drug_dictionary"]["atc_snapshot"]["path"]).resolve()) == cfg["drug_dictionary"]["atc_snapshot"]["sha256"]


def test_deterministic_rerun(run, tmp_path):
    out2 = tmp_path / "o2"
    subprocess.run([sys.executable, str(PIPE / "run_pipeline.py"), "--data", str(run[0]), "--out", str(out2), "--mode", "synthetic",
                    "--stage", "lock"], check=True)
    a = json.loads((run[1] / "results" / "11_analysis_set_lock.json").read_text())
    b = json.loads((out2 / "results" / "11_analysis_set_lock.json").read_text())
    assert a["participant_set_sha256"] == b["participant_set_sha256"] and a["code_sha256"] == b["code_sha256"]
    for f in ("08_endpoint_counts.csv", "03_snp_status.csv", "06_ingredient_atc_map.csv"):
        assert (run[1] / "results" / f).read_bytes() == (out2 / "results" / f).read_bytes()


def test_parser_vocabulary():
    src = (PIPE / "config" / C.load_config(PIPE / "config")["drug_dictionary"]["free_text"]["parser"]).resolve().read_text()
    vocab = set(re.findall(r'"([^"]+)": (?:\d|"oral"|"parenteral"|"inhaled"|"topical"|"transdermal"|"rectal"|"sublingual"|"unknown")', src))
    cfg = C.load_config(PIPE / "config")
    used = set()
    for d in list(cfg["drug_dictionary"]["prediction_drugs"].values()) + list(cfg["drug_dictionary"]["negative_control_drugs"].values()):
        used |= set(d.get("formulation_any", []))
    for c in cfg["analysis_config"]["contrasts"].values():
        used |= set(c.get("high", [])) | set(c.get("low", []))
    assert used <= vocab, used - vocab
