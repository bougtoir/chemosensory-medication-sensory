#!/usr/bin/env python3
"""Participant-data-free dry reproduction audit of the legacy chemosensory freeze.

Re-derives the dry evidence package from its stored raw sources and frozen
search outputs, without network access for the offline stages and without any
ToMMo participant-level data, and compares every regenerated artefact with the
frozen file. Results are written to dry_reproduction/results/ and injected into
DRY_REPRODUCTION_AUDIT.md via --render (unknown placeholders abort the build).

Usage:
  python3 dry_reproduction/run_dry_reproduction_audit.py \
      [--live-dir DIR] [--handoff-zip ZIP] [--render]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "dry_reproduction"
OUT = HERE / "results"
TEMPLATE = HERE / "DRY_REPRODUCTION_AUDIT.template.md"
REPORT = ROOT / "DRY_REPRODUCTION_AUDIT.md"

OFFLINE_SCRIPTS = ["04_curate_evidence", "05_evidence_graph", "06_meta_analysis",
                   "07_matrices_predictions", "08_figures", "09_expansion",
                   "10_power_assessment"]
NETWORK_SCRIPTS = ["01_pubmed_search", "02_bitterdb_scrape", "03_pubchem_drug_space"]
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "results", "build")
EXCLUDE_TOP = {"dry_reproduction", "DRY_REPRODUCTION_AUDIT.md",
               "PROTOCOL_DISTRIBUTION_FREEZE_RECONCILIATION.md", "reconciliation"}
PARTICIPANT_EXT = {".vcf", ".bcf", ".bed", ".bim", ".fam", ".bgen", ".pgen", ".pvar",
                   ".psam", ".sav", ".dta", ".sas7bdat", ".parquet", ".feather", ".rds"}
RUBRIC_RANGE = {"G": (0, 3), "H": (0, 3), "R": (0, 3), "V": (0, 3),
                "Rep": (0, 2), "F": (0, 2), "O": (0, 2), "A": (0, 3)}

ROWS, FILECMP, S = [], [], {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def add(cid, component, check, status, observed="", expected="", note=""):
    ROWS.append(dict(check_id=cid, component=component, check=check, status=status,
                     observed=str(observed), expected=str(expected), note=note))


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def offline_env():
    env = dict(os.environ)
    dead = "http://127.0.0.1:9"
    env.update(HTTP_PROXY=dead, HTTPS_PROXY=dead, http_proxy=dead, https_proxy=dead,
               NO_PROXY="", no_proxy="", MPLBACKEND="Agg", PYTHONHASHSEED="0")
    return env


def norm_cell(x):
    x = "" if x is None else str(x).strip()
    if x.lower() in {"nan", "none"}:
        return ""
    try:
        f = float(x)
    except ValueError:
        return x
    if f != f:
        return ""
    return str(int(f)) if f.is_integer() else repr(round(f, 10))


def read_norm(p):
    df = pd.read_csv(p, dtype=str, keep_default_na=False)
    return df.apply(lambda c: c.map(norm_cell)) if len(df) else df


def compare_csv(frozen, regen):
    a, b = read_norm(frozen), read_norm(regen)
    if list(a.columns) != list(b.columns):
        return "DIFFERENT_COLUMNS", f"cols {list(a.columns)} vs {list(b.columns)}"
    if a.equals(b):
        return "SEMANTIC_MATCH_ORDERED", "values equal after numeric normalisation"
    ra = sorted(map(tuple, a.values.tolist()))
    rb = sorted(map(tuple, b.values.tolist()))
    if ra == rb:
        return "SEMANTIC_MATCH_UNORDERED", "same rows, different row order"
    key = a.columns[0]
    ka, kb = set(a[key]), set(b[key])
    only_a, only_b = sorted(ka - kb), sorted(kb - ka)
    ncell = ""
    if a.shape == b.shape:
        ncell = f"; differing cells={int((a.values != b.values).sum())}"
    return "DIFFERENT", (f"shape {a.shape} vs {b.shape}; {key} only-frozen={only_a[:5]} "
                         f"only-regenerated={only_b[:5]}{ncell}")


def package_files(base):
    out = {}
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(base)
        if rel.parts[0] in EXCLUDE_TOP or rel.parts[0] in {"build", ".pytest_cache"}:
            continue
        if "__pycache__" in rel.parts:
            continue
        out[str(rel)] = p
    return out


def run_scripts(base, scripts):
    (base / "build").mkdir(exist_ok=True)
    res = {}
    for s in scripts:
        r = subprocess.run([sys.executable, f"scripts/{s}.py"], cwd=base, env=offline_env(),
                           capture_output=True, text=True)
        res[s] = r.returncode
    return res


def diff_trees(frozen_base, regen_base, label):
    fa, fb = package_files(frozen_base), package_files(regen_base)
    counts = {}
    for rel in sorted(set(fa) | set(fb)):
        if rel not in fb:
            st, note = "MISSING_IN_REGENERATED", ""
        elif rel not in fa:
            st, note = "NEW_IN_REGENERATED", ""
        elif sha(fa[rel]) == sha(fb[rel]):
            continue
        elif rel.endswith(".csv"):
            st, note = compare_csv(fa[rel], fb[rel])
        elif rel.endswith(".png"):
            st, note = "REGENERATED_BYTES_DIFFER", "raster re-render"
        else:
            st, note = "BYTES_DIFFER", ""
        counts[st] = counts.get(st, 0) + 1
        FILECMP.append(dict(run=label, file=rel, status=st, note=note))
    return fa, fb, counts


def pytest_counts(base):
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                       cwd=base, capture_output=True, text=True, env=offline_env())
    txt = r.stdout + r.stderr
    p = re.search(r"(\d+) passed", txt)
    f = re.search(r"(\d+) failed", txt)
    fails = re.findall(r"FAILED (\S+)", txt)
    return int(p.group(1)) if p else 0, int(f.group(1)) if f else 0, fails


def ledger_xml(r):
    """seed_ledger.csv mixes two schemas: query rows and one appended anchor row
    written as (file stem, pmid, bytes, sha256, retrieved_utc)."""
    if re.fullmatch(r"[0-9a-f]{64}", str(r.n_parsed)):
        return f"{r.layer}.xml", str(r.n_parsed), int(r.n_ids)
    return f"{r.layer}_{r.label}.xml", str(r.sha256_16), None


def parse_xml_records(path, parse_article):
    recs = []
    for art in ET.parse(path).getroot().iter("PubmedArticle"):
        try:
            recs.append(parse_article(art))
        except Exception:
            continue
    return recs


# ---------------------------------------------------------------- sections
def sec_manifests():
    m = pd.read_csv(ROOT / "HANDOFF_MANIFEST.csv")
    ok = missing = bad = 0
    miss = []
    for _, r in m.iterrows():
        p = ROOT / r.relative_path
        if not p.exists():
            missing += 1
            miss.append(r.relative_path)
        elif sha(p) == r.sha256:
            ok += 1
        else:
            bad += 1
    S.update(manifest_rows=len(m), manifest_ok=ok, manifest_missing=missing,
             manifest_bad=bad, manifest_missing_files=", ".join(miss) or "none")
    add("M1", "manifest", "HANDOFF_MANIFEST.csv SHA-256 vs files",
        "PASS" if bad == 0 and missing == 0 else "DISCREPANCY",
        f"{ok} match, {bad} mismatch, {missing} missing ({S['manifest_missing_files']})",
        f"{len(m)} match")
    t60 = (ROOT / "60_PREOPENING_INPUT_MANIFEST.md").read_text()
    t97 = (ROOT / "97_PREOPENING_AMENDMENT_MANIFEST.md").read_text()
    pat = re.compile(r"^\|\s*([\w./-]+)\s*\|\s*([0-9a-f]{16,64})\s*\|", re.M)
    h60, h97 = dict(pat.findall(t60)), dict(pat.findall(t97))
    cur97 = sum(sha(ROOT / f).startswith(h) for f, h in h97.items())
    S.update(m97_rows=len(h97), m97_match=cur97)
    add("M2", "manifest", "97 amendment manifest prefixes vs current files",
        "PASS" if cur97 == len(h97) else "DISCREPANCY", f"{cur97}/{len(h97)} match", len(h97))
    same = superseded = unexplained = 0
    une = []
    for f, h in h60.items():
        cur = sha(ROOT / f)
        if cur.startswith(h):
            same += 1
        elif f in h97:
            superseded += 1
        else:
            unexplained += 1
            une.append(f)
    S.update(m60_rows=len(h60), m60_match=same, m60_superseded=superseded,
             m60_unexplained=unexplained, m60_unexplained_files=", ".join(une) or "none")
    add("M3", "manifest", "60 pre-opening manifest hashes vs current files",
        "PASS" if unexplained == 0 else "DISCREPANCY",
        f"{same} unchanged, {superseded} changed and re-hashed in 97, {unexplained} changed without manifest entry ({S['m60_unexplained_files']})",
        "unchanged or superseded via 97")
    rows60 = re.search(r"13_LOCKED_PREDICTIONS_v2_FINAL\.csv \|[^|]+\|[^|]*\((\d+) rows\)", t60)
    nrows = len(pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv"))
    S.update(m60_stated_rows=rows60.group(1) if rows60 else "n/a", v2_rows=nrows)
    add("M4", "manifest", "60 stated row count of 13_LOCKED_PREDICTIONS_v2_FINAL.csv",
        "PASS" if rows60 and int(rows60.group(1)) == nrows else "DISCREPANCY",
        f"stated {S['m60_stated_rows']}", f"actual {nrows}", "clerical; hash matches the 24-row file")


def sec_raw():
    raw = ROOT / "data" / "raw"
    for led, cid in [("search_ledger.csv", "R1"), ("seed_ledger.csv", "R2")]:
        L = pd.read_csv(raw / "pubmed" / led, dtype=str)
        ok, odd = 0, []
        for _, r in L.iterrows():
            f, h, nbytes = ledger_xml(r)
            p = raw / "pubmed" / f
            if nbytes is not None:
                odd.append(f)
            if p.exists() and sha(p).startswith(h) and (nbytes is None or p.stat().st_size == nbytes):
                ok += 1
        S[f"pubmed_{cid}_rows"], S[f"pubmed_{cid}_ok"] = len(L), ok
        S[f"pubmed_{cid}_schema_rows"] = ", ".join(odd) or "none"
        add(cid, "raw/pubmed", f"{led} hashes vs stored XML",
            "PASS" if ok == len(L) else "DISCREPANCY", f"{ok}/{len(L)}", len(L),
            f"rows in a different column schema: {S[f'pubmed_{cid}_schema_rows']}")
    listed = set()
    for led in ["search_ledger.csv", "seed_ledger.csv"]:
        L = pd.read_csv(raw / "pubmed" / led, dtype=str)
        listed |= {ledger_xml(r)[0] for _, r in L.iterrows()}
    unl = sorted(p.name for p in (raw / "pubmed").glob("*.xml") if p.name not in listed)
    S["pubmed_unledgered"] = ", ".join(unl) or "none"
    add("R3", "raw/pubmed", "XML files without ledger entry",
        "PASS" if not unl else "DISCREPANCY", S["pubmed_unledgered"], "none")
    L = pd.read_csv(raw / "bitterdb" / "bitterdb_ledger.csv")
    ok = sum(sha(raw / "bitterdb" / f"receptor_{r.receptor_id}.html").startswith(r.sha256_16)
             for _, r in L.iterrows())
    S.update(bitterdb_ledger_rows=len(L), bitterdb_ledger_ok=ok)
    add("R4", "raw/bitterdb", "bitterdb_ledger sha256_16 vs stored HTML",
        "PASS" if ok == len(L) else "DISCREPANCY", f"{ok}/{len(L)}", len(L))
    L = pd.read_csv(raw / "pubchem" / "pubchem_ledger.csv")
    okrows = L[L.status == "ok"]
    have = sum((raw / "pubchem" / f"{n.replace(' ', '_')}.json").exists() for n in okrows.generic_name)
    fails = L[L.status != "ok"].generic_name.tolist()
    S.update(pubchem_ok=len(okrows), pubchem_json=have, pubchem_fail=", ".join(fails) or "none")
    add("R5", "raw/pubchem", "ledger ok rows with stored JSON",
        "PASS" if have == len(okrows) else "DISCREPANCY", f"{have}/{len(okrows)}", len(okrows),
        f"ledger failures retained: {S['pubchem_fail']}")
    L = pd.read_csv(raw / "tommo_public" / "ledger.csv")
    ok = sum((ROOT / r.file).exists() and sha(ROOT / r.file) == r.sha256
             and (ROOT / r.file).stat().st_size == r.bytes for _, r in L.iterrows())
    S.update(tommo_public_rows=len(L), tommo_public_ok=ok)
    add("R6", "raw/tommo_public", "public questionnaire ledger (bytes+SHA-256)",
        "PASS" if ok == len(L) else "DISCREPANCY", f"{ok}/{len(L)}", len(L),
        "public blank questionnaires only")


def sec_pool(parse_article):
    raw = ROOT / "data" / "raw" / "pubmed"
    frozen = pd.read_csv(ROOT / "evidence" / "search_pool.csv")
    fset = set(frozen.pmid.astype(int))
    stage1, seeds, other = set(), set(), {}
    for _, r in pd.read_csv(raw / "search_ledger.csv").iterrows():
        stage1 |= {int(x["pmid"]) for x in parse_xml_records(raw / f"{r.layer}_{r.label}.xml", parse_article)}
    for _, r in pd.read_csv(raw / "seed_ledger.csv", dtype=str).iterrows():
        seeds |= {int(x["pmid"]) for x in parse_xml_records(raw / ledger_xml(r)[0], parse_article)}
    for name in S["pubmed_unledgered"].split(", "):
        if name.endswith(".xml"):
            other[name] = {int(x["pmid"]) for x in parse_xml_records(raw / name, parse_article)}
    led = stage1 | seeds
    allx = led.union(*other.values()) if other else led
    S.update(pool_all_xml=len(allx), pool_all_only_frozen=", ".join(map(str, sorted(fset - allx))) or "none",
             pool_all_only_xml=", ".join(map(str, sorted(allx - fset))) or "none",
             pool_ledgered_only=", ".join(map(str, sorted(led - fset))) or "none")
    S.update(pool_frozen=len(fset), pool_stage1=len(stage1), pool_ledgered=len(led),
             pool_only_frozen=len(fset - led), pool_only_ledgered=len(led - fset),
             pool_anchor_in_frozen=27569025 in fset,
             pool_unledgered_pmids="; ".join(f"{k}: {sorted(v)}" for k, v in other.items()))
    add("P1", "search_pool", "Stage-1 query XML (20 files) -> unique PMIDs", "AUDIT_ONLY",
        len(stage1), "", "subset of frozen pool")
    add("P2", "search_pool", "Stage-1 + ledgered seed XML vs frozen evidence/search_pool.csv",
        "PASS" if led == fset else "DISCREPANCY",
        f"ledgered={len(led)}, frozen={len(fset)}, only-frozen={len(fset - led)}, only-ledgered={len(led - fset)}",
        "identical PMID sets")
    add("P2b", "search_pool", "all stored XML (incl. unledgered SEED_extra_anchors.xml) vs frozen pool",
        "PASS" if allx == fset else "DISCREPANCY",
        f"all={len(allx)}, only-frozen=[{S['pool_all_only_frozen']}], only-XML=[{S['pool_all_only_xml']}]",
        "identical PMID sets", "set-level only; frozen row order and per-row metadata assembly are not encoded in any script")
    add("P3", "search_pool", "anchor PMID 27569025 present in frozen pool",
        "PASS" if 27569025 in fset else "DISCREPANCY", 27569025 in fset, True,
        f"unledgered XML content: {S['pool_unledgered_pmids']}")
    return parse_article


def sec_bitterdb():
    raw = ROOT / "data" / "raw" / "bitterdb"
    led = pd.read_csv(raw / "bitterdb_ledger.csv")
    hum = pd.read_csv(ROOT / "evidence" / "bitterdb_human_receptors.csv")
    frozen = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
    rows, script_led = [], []
    for rid in sorted(int(m) for m in led.receptor_id):
        html = (raw / f"receptor_{rid}.html").read_text()
        g = re.search(r'>\s*(TAS2R\d+|TAS1R\d+)\s*<', html)
        if g:
            gene = g.group(1)
        else:
            g2 = re.search(r'(TAS2R\d+|TAS1R\d+)', html)
            gene = g2.group(1) if g2 else f"id{rid}"
        human = bool(re.search(r'Homo\s*sapiens|human', html, re.I))
        n = 0
        if human:
            for cid, name in re.findall(r'compound\.php\?id=(\d+)"[^>]*>([^<]+)</a>', html):
                rows.append((rid, gene, int(cid), name.strip()))
                n += 1
        script_led.append((rid, gene, human, n))
    naive = pd.DataFrame(rows, columns=frozen.columns).drop_duplicates()
    sl = pd.DataFrame(script_led, columns=["receptor_id", "receptor", "human_page", "n_ligands"])
    m = led.merge(sl, on="receptor_id", suffixes=("_ledger", "_script"))
    led_match = int(((m.receptor_ledger == m.receptor_script) & (m.human_page_ledger == m.human_page_script)
                     & (m.n_ligands_ledger == m.n_ligands_script)).sum())
    lab = dict(zip(hum.receptor_id, hum.receptor))
    filt = naive[naive.receptor_id.isin(lab)].copy()
    filt["receptor"] = filt.receptor_id.map(lab)
    key = ["receptor_id", "receptor", "compound_id", "compound_name"]
    fe = set(map(tuple, frozen[key].values.tolist()))
    re_ = set(map(tuple, filt[key].values.tolist()))
    comp = pd.read_csv(ROOT / "evidence" / "bitterdb_compounds.csv")
    rc = naive[["compound_id", "compound_name"]].drop_duplicates()
    rc_h = filt[["compound_id", "compound_name"]].drop_duplicates()
    S.update(bitterdb_naive_edges=len(naive), bitterdb_ledger_script_match=led_match,
             bitterdb_human_ids=len(lab), bitterdb_filtered_edges=len(filt),
             bitterdb_frozen_edges=len(frozen), bitterdb_edge_sets_equal=fe == re_,
             bitterdb_compounds_regen=len(rc), bitterdb_compounds_frozen=len(comp),
             bitterdb_compounds_human_only=len(rc_h),
             bitterdb_receptors_with_ligands=frozen.receptor.nunique())
    add("B1", "bitterdb", "02_bitterdb_scrape.py parse logic applied to stored HTML vs stored ledger",
        "PASS" if led_match == len(led) else "DISCREPANCY", f"{led_match}/{len(led)} ledger rows reproduced",
        len(led), f"script logic yields {len(naive)} edges (non-human pages pass the 'human' regex)")
    add("B2", "bitterdb", "edges after frozen human-receptor mapping vs frozen ligand table",
        "PASS" if fe == re_ else "DISCREPANCY",
        f"{len(filt)} edges / {len(lab)} receptor ids", f"{len(frozen)} edges",
        "requires evidence/bitterdb_human_receptors.csv (curation step not encoded in 02)")
    add("B3", "bitterdb", "compound table re-derived with 02 logic (unfiltered pages)",
        "PASS" if set(map(tuple, rc.values.tolist())) == set(map(tuple, comp.values.tolist())) else "DISCREPANCY",
        len(rc), len(comp), f"frozen compound table was NOT human-filtered; human-only compounds = {len(rc_h)}")


def sec_pubchem():
    raw = ROOT / "data" / "raw" / "pubchem"
    frozen = pd.read_csv(ROOT / "prediction" / "drug_chemical_space.csv")
    cols = {"cid": "CID", "mw": "MolecularWeight", "xlogp": "XLogP", "tpsa": "TPSA",
            "hbd": "HBondDonorCount", "hba": "HBondAcceptorCount", "rotb": "RotatableBondCount",
            "charge": "Charge", "inchikey": "InChIKey", "smiles": "CanonicalSMILES"}
    ok = shaok = 0
    for _, r in frozen.iterrows():
        txt = (raw / f"{r.generic_name.replace(' ', '_')}.json").read_text()
        p = json.loads(txt)["PropertyTable"]["Properties"][0]
        if all(norm_cell(p.get(v)) == norm_cell(r[k]) for k, v in cols.items()):
            ok += 1
        shaok += hashlib.sha256(txt.encode()).hexdigest()[:16] == r.sha256_16
    S.update(pubchem_rows=len(frozen), pubchem_props_ok=ok, pubchem_sha_ok=shaok)
    add("C1", "pubchem", "drug_chemical_space.csv properties re-derived from stored JSON",
        "PASS" if ok == len(frozen) and shaok == len(frozen) else "DISCREPANCY",
        f"props {ok}/{len(frozen)}, sha {shaok}/{len(frozen)}", len(frozen))


def sec_offline(tmp):
    regen = tmp / "regen"
    shutil.copytree(ROOT, regen, ignore=IGNORE)
    rc = run_scripts(regen, OFFLINE_SCRIPTS)
    S["offline_returncodes"] = ", ".join(f"{k}={v}" for k, v in rc.items())
    add("O0", "offline rerun", "scripts 04-10 exit codes (network blocked)",
        "PASS" if not any(rc.values()) else "FAIL", S["offline_returncodes"], "all 0")
    fa, fb, counts = diff_trees(ROOT, regen, "offline")
    produced = ["03_STUDY_INVENTORY.csv", "04_VARIANT_EVIDENCE.csv", "05_DRUG_SENSORY_EVIDENCE.csv",
                "06_PLASTICITY_EVIDENCE.csv", "evidence/sensory_behavior_evidence.csv",
                "evidence/extraoral_evidence.csv", "evidence/evolution_evidence.csv",
                "07_EVIDENCE_GRAPH.csv", "08_EVIDENCE_GRAPH.json", "09_META_ANALYSIS/meta_results.json",
                "09_META_ANALYSIS/tas2r38_prop_meta_input.csv", "09_META_ANALYSIS/README.md",
                "11_RECEPTOR_DRUG_MATRIX.csv", "12_VARIANT_FUNCTION_MATRIX.csv", "13_LOCKED_PREDICTIONS.csv",
                "23_CANDIDATE_PREDICTIONS_ALL.csv", "24_PREDICTION_EVIDENCE_AUDIT.csv",
                "25_FORMULATION_ROUTE_CONTRASTS.csv", "26_NEGATIVE_CONTROLS.csv",
                "13_LOCKED_PREDICTIONS_v2_PRELIMINARY.csv", "31_TOMMO_PREDICTION_TESTABILITY_MATRIX.csv",
                "33_ALTERNATIVE_EXPLANATION_AUDIT.csv", "13_LOCKED_PREDICTIONS_v2_FINAL.csv"]
    exact = [f for f in produced if f in fa and f in fb and sha(fa[f]) == sha(fb[f])]
    S.update(offline_targets=len(produced), offline_exact=len(exact),
             offline_nonexact=", ".join(f for f in produced if f not in exact) or "none")
    for f in produced:
        st = "EXACT" if f in exact else next((c["status"] for c in FILECMP if c["run"] == "offline" and c["file"] == f), "MISSING")
        note = next((c["note"] for c in FILECMP if c["run"] == "offline" and c["file"] == f), "")
        add(f"O-{f}", "offline rerun", f"regenerate {f}", st, "", "byte-identical", note)
    figs = sorted(f for f in fa if f.startswith("figures/") and f.endswith(".png"))
    figexact = sum(sha(fa[f]) == sha(fb[f]) for f in figs if f in fb)
    S.update(fig_total=len(figs), fig_exact=figexact)
    add("O-figures", "offline rerun", "figures/*.png (08_figures.py)", "AUDIT_ONLY",
        f"{figexact}/{len(figs)} byte-identical", "", "rasters are not scientific inputs to locks")
    pw = pd.read_csv(regen / "build" / "power_assessment.csv")
    t73 = (ROOT / "73_PREANALYSIS_POWER_ASSESSMENT.md").read_text()
    pcol = [c for c in pw.columns if "power" in c.lower()][0]
    found = sum(f"{float(v):.3f}" in t73 for v in pw[pcol])
    S.update(power_rows=len(pw), power_in_73=found)
    add("O-power", "offline rerun", "10_power_assessment.py power values vs 73 table",
        "PASS" if found == len(pw) else "DISCREPANCY", f"{found}/{len(pw)} values found in 73", len(pw))
    return regen


def sec_augmented(tmp, parse_article):
    aug = tmp / "aug"
    shutil.copytree(ROOT, aug, ignore=IGNORE)
    pool = pd.read_csv(aug / "evidence" / "search_pool.csv")
    recs = parse_xml_records(ROOT / "data" / "raw" / "pubmed" / "SEED_27569025.xml", parse_article)
    add_df = pd.DataFrame(recs).assign(layer="SEED", query_label="anchor_27569025")[pool.columns]
    pd.concat([pool, add_df], ignore_index=True).to_csv(aug / "evidence" / "search_pool.csv", index=False)
    rc = run_scripts(aug, ["04_curate_evidence"])
    res = {}
    for f in ["03_STUDY_INVENTORY.csv", "05_DRUG_SENSORY_EVIDENCE.csv"]:
        if sha(ROOT / f) == sha(aug / f):
            st, note = "EXACT", ""
        else:
            st, note = compare_csv(ROOT / f, aug / f)
        res[f] = st
        add(f"A-{f}", "anchor-augmented rerun", f"04 with SEED_27569025 appended to pool: {f}",
            st, "", "byte-identical", note + f"; exit={rc['04_curate_evidence']}")
    S.update(aug_inventory=res["03_STUDY_INVENTORY.csv"], aug_drug=res["05_DRUG_SENSORY_EVIDENCE.csv"])


def sec_scores():
    c = pd.read_csv(ROOT / "23_CANDIDATE_PREDICTIONS_ALL.csv")
    v = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv")
    comp = sum(c[k] for k in ["G", "H", "R", "V", "Rep", "F", "O"]) - c["A"]
    mism = c.pid[comp != c.evidence_score].tolist()
    rng = [f"{p}:{k}" for k, (lo, hi) in RUBRIC_RANGE.items() for p in c.pid[(c[k] < lo) | (c[k] > hi)]]
    pv = v[v.prediction_id.str.startswith("P")].set_index("prediction_id")
    cs = c.set_index("pid")
    fin_mism = [p for p in cs.index if float(pv.loc[p, "evidence_score"]) != float(cs.loc[p, "evidence_score"])]
    tier_mism = [p for p in cs.index if pv.loc[p, "evidence_tier"] != cs.loc[p, "tier"]]
    S.update(score_n=len(c), score_recomputed_mismatch=", ".join(mism) or "none",
             score_range_violations=", ".join(rng) or "none",
             score_final_mismatch=", ".join(fin_mism) or "none", tier_mismatch=", ".join(tier_mism) or "none",
             score_table="; ".join(f"{p}={int(s)}" for p, s in zip(c.pid, comp)))
    add("S1", "evidence score", "G+H+R+V+Rep+F+O-A recomputed from components (23)",
        "PASS" if not mism else "DISCREPANCY", S["score_table"], "equal to evidence_score column")
    add("S2", "evidence score", "component ranges per rubric 21",
        "PASS" if not rng else "DISCREPANCY", S["score_range_violations"], "none")
    add("S3", "evidence score", "13_v2_FINAL evidence_score equals 23", "PASS" if not fin_mism else "DISCREPANCY",
        S["score_final_mismatch"], "none")
    add("S4", "evidence score", "13_v2_FINAL evidence_tier equals 23 tier", "PASS" if not tier_mism else "DISCREPANCY",
        S["tier_mismatch"], "none")
    hi = sorted(c.pid[comp >= 9])
    t36 = (ROOT / "36_GATE_DECISION.md").read_text()
    t61 = (ROOT / "61_PREOPENING_ERRATA.md").read_text()
    n36 = re.search(r"(\d+) with evidence_score ≥ ?9 \(([^)]+)\)", t36)
    n61 = re.search(r'read "(\d+) with evidence_score', t61)
    S.update(gate_hi_n=len(hi), gate_hi_ids=", ".join(hi), gate_36_stated=n36.group(1),
             gate_36_list=n36.group(2), gate_61_corrected=n61.group(1))
    add("G1", "gate", "count of directional predictions with score>=9 vs 36",
        "PASS" if int(n36.group(1)) == len(hi) else "DISCREPANCY (errata 61)",
        f"recomputed {len(hi)} ({S['gate_hi_ids']})", f"36 states {n36.group(1)} ({n36.group(2)})",
        f"61 corrects to {n61.group(1)}: " + ("consistent" if int(n61.group(1)) == len(hi) else "inconsistent"))
    ndir = int((~c.pid.str.startswith("N")).sum())
    m12 = re.search(r"(\d+) directional", t36)
    add("G2", "gate", "number of directional predictions vs 36",
        "PASS" if m12 and int(m12.group(1)) == ndir else "DISCREPANCY", ndir, m12.group(1) if m12 else "n/a")


def sec_hierarchy():
    c = pd.read_csv(ROOT / "23_CANDIDATE_PREDICTIONS_ALL.csv")
    v = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv")
    h = pd.read_csv(ROOT / "62_PREDICTION_HIERARCHY_FREEZE.csv")

    def ids(txt):
        return sorted(set(re.findall(r"P\d\d", txt)))
    src = {
        "23.primary": sorted(c.pid[c.primary == "primary"]),
        "13_v2_FINAL.primary_or_secondary": sorted(v.prediction_id[v.primary_or_secondary == "primary"]),
        "62.confirmatory_status": sorted(h.prediction_id[h.confirmatory_status == "primary"]),
        "82.F-PRIMARY": ids(re.search(r"\| F-PRIMARY \|([^|]+)\|", (ROOT / "82_MULTIPLE_TESTING_FINAL.md").read_text()).group(1).split("(")[0]),
        "README_HANDOFF.F-PRIMARY": ids(re.search(r"F-PRIMARY:([^（\n]+)", (ROOT / "README_HANDOFF.md").read_text()).group(1)),
        "LOCK_STATUS.F-PRIMARY": ids(re.search(r"F-PRIMARY = ([P0-9, ]+)", (ROOT / "LOCK_STATUS.md").read_text()).group(1)),
    }
    t91 = (ROOT / "91_P01_P10_SEPARATION_AMENDMENT.md").read_text()
    src["91.P10_status"] = ["P10=secondary"] if re.search(r"P10 remains an independently frozen secondary", t91) else ["P10=?"]
    for k, val in src.items():
        S[f"hier_{k}"] = ", ".join(val)
    base = src["62.confirmatory_status"]
    diffs = [k for k in ["23.primary", "13_v2_FINAL.primary_or_secondary", "82.F-PRIMARY",
                         "README_HANDOFF.F-PRIMARY", "LOCK_STATUS.F-PRIMARY"] if src[k] != base]
    S["hier_inconsistent_sources"] = ", ".join(diffs) or "none"
    for k, val in src.items():
        add(f"H-{k}", "hierarchy", f"primary set according to {k}",
            "PASS" if (val == base or k.startswith("91")) else "DISCREPANCY", ", ".join(val), ", ".join(base),
            "62 is the declared source of truth (82 rule 1)")


def sec_controls():
    n26 = pd.read_csv(ROOT / "26_NEGATIVE_CONTROLS.csv")
    n79 = pd.read_csv(ROOT / "79_NEGATIVE_CONTROL_FINAL.csv")
    v = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS_v2_FINAL.csv")
    vn = v[v.prediction_id.str.startswith("N")].set_index("prediction_id")
    a, b = n26.set_index("nid"), n79.set_index("control_id")
    idok = set(a.index) == set(b.index) == set(vn.index)
    gene = [i for i in a.index if not (a.loc[i, "gene"] == b.loc[i, "genotype"] == vn.loc[i, "gene"])]
    def tok(s):
        return re.split(r"[\s(/]", str(s).lower())[0]
    drug = [i for i in a.index if not (tok(a.loc[i, "drug"]) == tok(b.loc[i, "exposure"]) == tok(vn.loc[i, "drug_generic_name"]))]
    cls = sorted({(a.loc[i, "cls"], b.loc[i, "control_type"]) for i in a.index if a.loc[i, "cls"] != b.loc[i, "control_type"]})
    t36 = (ROOT / "36_GATE_DECISION.md").read_text()
    m = re.search(r"(\d+) controls across (\d+) classes \(([^)]+)\)", t36)
    S.update(nc_n=len(b), nc_ids_equal=idok, nc_gene_mismatch=", ".join(gene) or "none",
             nc_drug_mismatch=", ".join(drug) or "none",
             nc_class_relabels="; ".join(f"{x}->{y}" for x, y in cls) or "none",
             nc_classes_26=", ".join(sorted(n26.cls.unique())), nc_classes_79=", ".join(sorted(n79.control_type.unique())),
             nc_36_text=m.group(0) if m else "n/a")
    add("N1", "negative controls", "control IDs identical across 26, 79, 13_v2_FINAL",
        "PASS" if idok else "DISCREPANCY", len(b), 12)
    add("N2", "negative controls", "genotype per control identical across 26/79/13_v2_FINAL",
        "PASS" if not gene else "DISCREPANCY", S["nc_gene_mismatch"], "none")
    add("N3", "negative controls", "exposure (first token) identical across 26/79/13_v2_FINAL",
        "PASS" if not drug else "DISCREPANCY", S["nc_drug_mismatch"], "none")
    add("N4", "negative controls", "class labels 26 (regenerated by 09) vs 79 (final)",
        "PASS" if not cls else "DISCREPANCY (label only)", S["nc_class_relabels"], "identical",
        f"26 classes: {S['nc_classes_26']} | 79 classes: {S['nc_classes_79']} | 36 text: {S['nc_36_text']}")
    k = pd.read_csv(ROOT / "25_FORMULATION_ROUTE_CONTRASTS.csv")
    S["contrast_n"] = len(k)
    o = pd.read_csv(ROOT / "72_PREDICTION_OBSERVABILITY_FINAL.csv").set_index("prediction_id")
    cdiff = []
    for _, r in k.iterrows():
        d72 = str(o.loc[r.cid, "exposure_constructible_from_freetext"]) if r.cid in o.index else ""
        tok = re.split(r"[\s(]", str(r.drug).lower())[0]
        if tok not in d72.lower():
            cdiff.append(f"{r.cid}: 25='{r.drug} {r.fa} vs {r.fb}' / 72='{d72}'")
    S["contrast_def_mismatch"] = " ; ".join(cdiff) or "none"
    S["contrast_def_mismatch_n"] = len(cdiff)
    add("N6", "contrasts", "C1-C5 definitions in 25 (script 09) vs 72 (observability)",
        "PASS" if not cdiff else "DISCREPANCY", f"{len(cdiff)}/5 differ", "same contrast per ID", S["contrast_def_mismatch"])
    add("N5", "contrasts", "C1-C5 present", "PASS" if list(k.cid) == [f"C{i}" for i in range(1, 6)] else "DISCREPANCY",
        ", ".join(k.cid), "C1..C5")


def sec_gates():
    pat = re.compile(r"##\s*(?:Verdict|Decision):\s*\*\*([^*]+)\*\*")
    chain = []
    for f in ["docs/17_GO_NOGO_DECISION.md", "36_GATE_DECISION.md", "89_FINAL_OPENING_DECISION.md",
              "98_FINAL_OPENING_DECISION_V2.md"]:
        m = pat.search((ROOT / f).read_text())
        chain.append(f"{f.split('/')[-1][:2]}: {m.group(1) if m else '?'}")
    S["gate_chain"] = " -> ".join(chain)
    ls = (ROOT / "LOCK_STATUS.md").read_text()
    for f, label in [("docs/17", "CONDITIONAL GO"), ("36", "CONDITIONAL GO TO PRIMARY VALIDATION"),
                     ("89", "OPEN WITH RESTRICTIONS"), ("98", "OPEN PRIMARY DATA WITH RESTRICTIONS")]:
        ok = label in ls
        add(f"V-{f}", "gate", f"verdict of {f} recorded in LOCK_STATUS chain", "PASS" if ok else "DISCREPANCY",
            label, "present", "verdicts are judgments; inputs re-derived in G1/G2/N*/S*")
    add("V-chain", "gate", "historical gate chain (judgment, not computable)", "AUDIT_ONLY", S["gate_chain"], "")
    t17 = (ROOT / "docs/17_GO_NOGO_DECISION.md").read_text()
    m = re.search(r"(\d+) receptors with curated ligands, (\d+) drug edges", t17)
    S.update(g17_receptors=m.group(1), g17_edges=m.group(2))
    add("V-17B", "gate", "docs/17 domain B receptor count vs frozen BitterDB ligand table",
        "PASS" if int(m.group(1)) == S["bitterdb_receptors_with_ligands"] else "DISCREPANCY",
        S["bitterdb_receptors_with_ligands"], m.group(1),
        f"'{m.group(2)} drug edges' not re-derivable: definition not encoded in any script")


def sec_parser():
    pdir = ROOT / "71_MEDICATION_PARSER"
    t94 = (ROOT / "94_MEDICATION_PARSER_FINAL_VERSION.txt").read_text()
    frozen_hash = re.search(r"sha256=([0-9a-f]{64})", t94).group(1)
    cur = sha(pdir / "medication_parser.py")
    add("X1", "parser", "medication_parser.py SHA-256 vs 94", "PASS" if cur == frozen_hash else "FAIL", cur, frozen_hash)
    mod = load_module(pdir / "medication_parser.py", "medication_parser_audit")
    gold = pd.read_csv(pdir / "gold_corpus.csv", dtype=str, keep_default_na=False)
    val = read_norm(pdir / "validation_output.csv")
    out = pd.DataFrame([mod.parse(t) for t in gold.raw_text])
    fields = {"generic_name": "gold_generic", "formulation": "gold_formulation", "route": "gold_route",
              "oral_sensory_exposure": "gold_exposure", "taste_masking": "gold_masking"}
    same = all((out[k].map(norm_cell).values == val[k].values).all() for k in fields)
    acc = {k: int((out[k].map(norm_cell).values == gold[g].map(norm_cell).values).sum()) for k, g in fields.items()}
    S.update(parser_version=getattr(mod, "VERSION", "n/a"),
             parser_n=len(gold), parser_acc="; ".join(f"{k}={v}/{len(gold)}" for k, v in acc.items()),
             parser_semantic_equal=same)
    add("X2", "parser", "rerun on gold corpus vs frozen validation_output.csv",
        "SEMANTIC_MATCH" if same else "DISCREPANCY", same, True, "integer vs float exposure codes normalised")
    t69 = (ROOT / "69_MEDICATION_PARSER_VALIDATION.md").read_text()
    stated = re.findall(r"(\d+)/146", t69)
    exp = {"generic_name": stated[0], "route": stated[1], "formulation": stated[2],
           "oral_sensory_exposure": stated[3], "taste_masking": stated[4]}
    okacc = all(str(acc[k]) == exp[k] for k in exp)
    add("X3", "parser", "accuracy vs gold labels vs 69 table", "PASS" if okacc else "DISCREPANCY",
        S["parser_acc"], "; ".join(f"{k}={v}/146" for k, v in exp.items()))
    fails = gold.raw_text[out.generic_name.map(norm_cell).values != gold.gold_generic.map(norm_cell).values].tolist()
    S["parser_fail_strings"] = ", ".join(fails) or "none"
    add("X4", "parser", "real ToMMo-string validation (92)", "NOT_RUN",
        "requires delivered ToMMo strings", "", "mandatory gate before any association run; out of scope here")


def sec_tests(regen):
    p, f, fl = pytest_counts(ROOT)
    S.update(pytest_frozen=f"{p} passed, {f} failed")
    add("T1", "tests", "pytest on frozen package", "PASS" if f == 0 else "FAIL", S["pytest_frozen"], "0 failed", "; ".join(fl))
    p, f, fl = pytest_counts(regen)
    S.update(pytest_regen=f"{p} passed, {f} failed", pytest_regen_failed="; ".join(fl) or "none")
    add("T2", "tests", "pytest on offline-regenerated package", "PASS" if f == 0 else "FAIL",
        S["pytest_regen"], "0 failed", S["pytest_regen_failed"])


def sec_exclusion():
    tracked = subprocess.run(["git", "ls-files", "data"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    roots = sorted({"/".join(Path(t).parts[:3]) for t in tracked})
    bad_ext = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.suffix.lower() in PARTICIPANT_EXT and ".git" not in p.parts)
    hits = []
    for s in OFFLINE_SCRIPTS:
        t = (ROOT / "scripts" / f"{s}.py").read_text()
        if re.search(r"urllib|requests|http[s]?://", t):
            hits.append(s)
    S.update(excl_data_roots=", ".join(roots), excl_bad_ext=", ".join(bad_ext) or "none",
             excl_network_in_offline=", ".join(hits) or "none")
    add("E1", "exclusion", "tracked data/ roots", "PASS" if all(r.split("/")[-1] in
        {"pubmed", "bitterdb", "pubchem", "tommo_public"} for r in roots) else "DISCREPANCY",
        S["excl_data_roots"], "public sources only")
    add("E2", "exclusion", "genotype/participant-type files in package", "PASS" if not bad_ext else "FAIL",
        S["excl_bad_ext"], "none")
    add("E3", "exclusion", "network calls in offline scripts 04-10", "PASS" if not hits else "DISCREPANCY",
        S["excl_network_in_offline"], "none", "offline stages also run with a dead proxy")


def sec_zip(zpath):
    if not zpath:
        S.update(zip_files="n/a", zip_common="n/a", zip_mismatch="n/a", zip_only_repo_dirs="n/a")
        add("Z1", "handoff zip", "handoff ZIP vs package", "NOT_RUN", "", "")
        return
    z = zipfile.ZipFile(zpath)
    names = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    def strip(n):
        parts = n.split("/")
        return "/".join(parts[1:]) if len(parts) > 1 and not (ROOT / n).exists() and (ROOT / "/".join(parts[1:])).exists() else n
    files = package_files(ROOT)
    common = mism = 0
    mm = []
    for n, data in names.items():
        rel = strip(n)
        if rel in files:
            common += 1
            if hashlib.sha256(data).hexdigest() != sha(files[rel]):
                mism += 1
                mm.append(rel)
    zrel = {strip(n) for n in names}
    absent_dirs = sorted({r.split("/")[0] for r in files if r not in zrel and "/" in r})
    absent_top = sorted(r for r in files if r not in zrel and "/" not in r)
    S.update(zip_files=len(names), zip_common=common, zip_mismatch=", ".join(mm) or "none",
             zip_only_repo_dirs=", ".join(absent_dirs) or "none", zip_only_repo_top=", ".join(absent_top) or "none")
    add("Z1", "handoff zip", "files in ZIP identical to package", "PASS" if mism == 0 else "DISCREPANCY",
        f"{common} common, {mism} differ", "0 differ")
    add("Z2", "handoff zip", "package directories absent from ZIP", "INCOMPLETE_HANDOFF" if absent_dirs else "PASS",
        S["zip_only_repo_dirs"], "none", "ZIP is a document-level handoff; scripts/tests/raw sources exist only in the git branch, so ZIP-only reproduction is impossible")


def sec_live(live, tmp, parse_article):
    if not live:
        add("L0", "live re-acquisition", "live sources", "NOT_RUN", "", "")
        for k in ["live_pool", "live_pool_vs_stage1_added", "live_pool_vs_stage1_removed", "live_edges",
                  "live_edges_added", "live_edges_removed", "live_pubchem_ok", "live_pubchem_changed",
                  "live_pred_status"]:
            S[k] = "n/a"
        return
    live = Path(live)
    raw = ROOT / "data" / "raw" / "pubmed"
    stage1 = set()
    for _, r in pd.read_csv(raw / "search_ledger.csv").iterrows():
        stage1 |= {int(x["pmid"]) for x in parse_xml_records(raw / f"{r.layer}_{r.label}.xml", parse_article)}
    lp = set(pd.read_csv(live / "evidence" / "search_pool.csv").pmid.astype(int))
    S.update(live_pool=len(lp), live_pool_vs_stage1_added=len(lp - stage1), live_pool_vs_stage1_removed=len(stage1 - lp))
    add("L1", "live re-acquisition", "live Stage-1 PubMed pool vs frozen Stage-1 XML", "SOURCE_DRIFT" if lp != stage1 else "PASS",
        f"{len(lp)} PMIDs (+{len(lp - stage1)} / -{len(stage1 - lp)})", f"{len(stage1)} PMIDs",
        "PubMed index growth since freeze; frozen seed/anchor layer not re-queried by 01")
    fe = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
    le = pd.read_csv(live / "evidence" / "bitterdb_receptor_ligands.csv")
    hum = set(pd.read_csv(ROOT / "evidence" / "bitterdb_human_receptors.csv").receptor_id)
    le_h = le[le.receptor_id.isin(hum)]
    k = ["receptor_id", "compound_id"]
    a, b = set(map(tuple, fe[k].values.tolist())), set(map(tuple, le_h[k].values.tolist()))
    S.update(live_edges=len(le), live_edges_human=len(b), live_edges_added=len(b - a), live_edges_removed=len(a - b))
    add("L2", "live re-acquisition", "live BitterDB human edges (frozen receptor mapping) vs frozen",
        "PASS" if a == b else "SOURCE_DRIFT", f"{len(b)} (+{len(b - a)} / -{len(a - b)}); raw script output {len(le)}", len(a))
    fp = pd.read_csv(ROOT / "prediction" / "drug_chemical_space.csv").set_index("generic_name")
    lpc = pd.read_csv(live / "prediction" / "drug_chemical_space.csv").set_index("generic_name")
    cols = ["cid", "mw", "xlogp", "tpsa", "hbd", "hba", "rotb", "charge", "inchikey"]
    common = fp.index.intersection(lpc.index)
    changed = [n for n in common if any(norm_cell(fp.loc[n, c]) != norm_cell(lpc.loc[n, c]) for c in cols)]
    S.update(live_pubchem_ok=len(lpc), live_pubchem_changed=", ".join(changed) or "none",
             live_pubchem_new=", ".join(sorted(set(lpc.index) - set(fp.index))) or "none")
    add("L3", "live re-acquisition", "live PubChem properties vs frozen", "PASS" if not changed and len(lpc) == len(fp) else "SOURCE_DRIFT",
        f"{len(lpc)} resolved; changed: {S['live_pubchem_changed']}; new: {S['live_pubchem_new']}", f"{len(fp)} resolved")
    lcopy = tmp / "live"
    shutil.copytree(ROOT, lcopy, ignore=IGNORE)
    lab = dict(pd.read_csv(ROOT / "evidence" / "bitterdb_human_receptors.csv")[["receptor_id", "receptor"]].values)
    lh = le[le.receptor_id.isin(lab)].copy()
    lh["receptor"] = lh.receptor_id.map(lab)
    lh.to_csv(lcopy / "evidence" / "bitterdb_receptor_ligands.csv", index=False)
    for rel in ["evidence/bitterdb_compounds.csv", "prediction/drug_chemical_space.csv"]:
        shutil.copy(live / rel, lcopy / rel)
    rc = run_scripts(lcopy, ["04_curate_evidence", "05_evidence_graph", "06_meta_analysis",
                             "07_matrices_predictions", "09_expansion"])
    st = {}
    for f in ["11_RECEPTOR_DRUG_MATRIX.csv", "23_CANDIDATE_PREDICTIONS_ALL.csv", "26_NEGATIVE_CONTROLS.csv",
              "13_LOCKED_PREDICTIONS_v2_FINAL.csv"]:
        s_, note = ("EXACT", "") if sha(ROOT / f) == sha(lcopy / f) else compare_csv(ROOT / f, lcopy / f)
        st[f] = s_
        add(f"L-{f}", "live re-acquisition", f"pipeline on live BitterDB/PubChem + frozen pool: {f}", s_,
            "", "frozen", note + f"; exits={sorted(set(rc.values()))}")
    S["live_pred_status"] = "; ".join(f"{k}={v}" for k, v in st.items())


def render():
    summary = json.loads((OUT / "summary.json").read_text())
    summary.update({re.sub(r"\W", "_", k): v for k, v in list(summary.items())})
    checks = pd.read_csv(OUT / "dry_reproduction_checks.csv", dtype=str, keep_default_na=False)
    tbl = ["| ID | component | check | status | observed | expected/note |", "|---|---|---|---|---|---|"]
    for _, r in checks.iterrows():
        esc = lambda s: str(s).replace("|", "/").replace("\n", " ")
        tbl.append(f"| {esc(r.check_id)} | {esc(r.component)} | {esc(r.check)} | **{esc(r.status)}** | "
                   f"{esc(r.observed)} | {esc(r.expected)}{(' — ' + esc(r.note)) if r.note else ''} |")
    summary["RESULTS_TABLE"] = "\n".join(tbl)
    fc = pd.read_csv(OUT / "file_comparison.csv", dtype=str, keep_default_na=False)
    ft = ["| run | file | status | note |", "|---|---|---|---|"]
    for _, r in fc.iterrows():
        ft.append(f"| {r.run} | `{r.file}` | {r.status} | {str(r.note).replace('|', '/')} |")
    summary["FILE_TABLE"] = "\n".join(ft)
    tpl = TEMPLATE.read_text()
    keys = set(re.findall(r"\{\{(\w+)\}\}", tpl))
    missing = sorted(keys - set(summary))
    if missing:
        sys.exit(f"render: unknown placeholders {missing}")
    for k in keys:
        tpl = tpl.replace("{{" + k + "}}", str(summary[k]))
    REPORT.write_text(tpl)
    print("wrote", REPORT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-dir")
    ap.add_argument("--handoff-zip")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--render-only", action="store_true")
    a = ap.parse_args()
    if a.render_only:
        render()
        return
    OUT.mkdir(parents=True, exist_ok=True)
    parse_article = load_module(ROOT / "scripts" / "01_pubmed_search.py", "pubmed_audit").parse_article
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        sec_manifests()
        sec_raw()
        sec_pool(parse_article)
        sec_bitterdb()
        sec_pubchem()
        regen = sec_offline(tmp)
        sec_augmented(tmp, parse_article)
        sec_scores()
        sec_hierarchy()
        sec_controls()
        sec_gates()
        sec_parser()
        sec_tests(regen)
        sec_exclusion()
        sec_zip(a.handoff_zip)
        sec_live(a.live_dir, tmp, parse_article)
    pd.DataFrame(ROWS).to_csv(OUT / "dry_reproduction_checks.csv", index=False)
    pd.DataFrame(FILECMP, columns=["run", "file", "status", "note"]).to_csv(OUT / "file_comparison.csv", index=False)
    S["n_checks"] = len(ROWS)
    S["status_counts"] = "; ".join(f"{k}={v}" for k, v in pd.Series([r["status"] for r in ROWS]).value_counts().sort_index().items())
    (OUT / "summary.json").write_text(json.dumps({k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in S.items()},
                                                 indent=1, ensure_ascii=False, sort_keys=True))
    print(S["status_counts"])
    if a.render:
        render()


if __name__ == "__main__":
    main()
