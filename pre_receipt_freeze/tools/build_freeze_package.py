#!/usr/bin/env python3
"""Build the final pre-receipt freeze package: generated documents (03, 05, 09, 17 tables, 18, 19, 22,
AMENDMENT_LOG, INSTRUCTION_REGISTER, ENVIRONMENT), the completeness audit, and the deterministic timestamp ZIP.
Fails (exit 1) if any completeness check fails. Uses no participant-level data and no network."""
import csv
import hashlib
import io
import json
import platform
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]           # pre_receipt_freeze/
PROJ = ROOT.parent                                   # chemosensory_medication_sensory/
DOCS = ROOT / "docs"
SI = ROOT / "session_instructions"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import instruction_register as IR  # noqa: E402

FREEZE_DATE = "20261004"
ZIP_NAME = f"CHEMOSENSORY_TOMMO_PRE_RECEIPT_FREEZE_{FREEZE_DATE}.zip"
ATT = Path("/home/ubuntu/attachments")
RESTRICTED = [
    ("tommo研究計画.docx", "265e0355-7dae-4476-8f38-f983e02753a2", "research plan (study 2025-0057); text identical to the 2026-03-13 submission",
     "objective, design, cohort, gene universe, methods"),
    ("tommo申請書.docx", "b5f04712-795f-4c9e-b1ea-16fac7c7601e", "distribution application (study 2025-0057); text identical to the 2026-03-13 submission",
     "requested data items, purpose, handling"),
    ("tommoデータセット.xlsx", "6b8d6819-701f-4aaf-b60f-3cb5754e7489", "distribution specification / data dictionary, release 3.1.1",
     "selected file families and items; no participant-level values"),
    ("CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip", "61778961-e727-4c8f-a173-202860c59691", "legacy handoff package",
     "legacy frozen files (also present unpacked in the project)"),
]
KNOWN_RESTRICTED_SHA = {
    "tommo研究計画.docx": "c81cdef22d61a732f8053b83dcddb439e8824207a2692e5bc4280275ae1988cd",
    "tommo申請書.docx": "9cd2b24324c905d28024f68bdc40df4570e74bcb2c414033fefefed010f2b9f6",
    "tommoデータセット.xlsx": "f77fb87cb76f631b01f7c04b6a66e1667074a11b6f56d38e17cf442a2f34d465",
    "CHEMOSENSORY_TOMMO_LEGACY_SESSION_HANDOFF.zip": "f7b9fbc30791a5d332c15c71ebdd9805a187d9679fe5cc5e069be505b1a272eb",
}
# third-party record-level material kept out of the archive (hash-only)
THIRD_PARTY = ["data", "evidence/bitterdb_compounds.csv", "evidence/bitterdb_human_receptors.csv",
               "evidence/bitterdb_receptor_ligands.csv", "evidence/search_pool.csv"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(PROJ))


# ---------------------------------------------------------------- generated documents
def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def doc03():
    rows = [
        ("T01", "Chemosensory phenotype has a genetic component (S = f(G, E), G part)", "taste-bud-related gene polymorphisms (approved 20 genes)", "05", "direct (genotype only)"),
        ("T02", "Acquired plasticity of chemosensory phenotype (E part)", "not measured in the distribution", "27", "not tested"),
        ("T03", "Drug-related behaviour depends on chemosensory engagement (M = g(S, D))", "prescription change ph1→ph2 by receptor-ligand prediction (P01–P12)", "06, 14", "direct (population association)"),
        ("T04", "Effect scales with oral sensory exposure", "formulation/route information in the medication section", "11", "conditional direct"),
        ("T05", "Specificity: no effect without oral exposure or receptor match", "negative controls N01–N12", "10", "direct"),
        ("T06", "Same variants shape dietary chemosensory phenotype", "FFQ ph1/ph2 items", "09", "secondary triangulation"),
        ("T07", "Evidence strength predicts effect size", "frozen evidence scores", "12", "direct (calibration)"),
        ("T08", "Taste receptors as extra-oral chemical sensors (chemical surveillance)", "protocol background (gut, airway, innate immunity, metabolism)", "25", "indirect: compatible only"),
        ("T09", "Immune mediation", "none", "25", "not tested"),
        ("T10", "Modifiable sensory component enables intervention", "none", "27", "not tested"),
        ("T11", "Health-economic / global-health benefit", "none", "28", "not tested"),
    ]
    write_csv(DOCS / "03_THEORY_TO_PROTOCOL_MAP.csv",
              [dict(theory_id=a, theory_element=b, protocol_element=c, frozen_in=d, testability=e) for a, b, c, d, e in rows],
              ["theory_id", "theory_element", "protocol_element", "frozen_in", "testability"])


def doc05(cfg):
    sm = cfg["snp_map"]
    ea = {r["rsid"]: r for r in csv.DictReader(open(ROOT / "offline_pipeline/config/derived/effect_alleles.csv"))}
    fam = {"P01": "A", "P02": "A", "P05": "A", "P03": "AS", "P04": "AS", "P07": "AS", "P08": "AS", "P12": "AS"}
    rows = []
    for vid, v in sm["level_a"].items():
        snps = v.get("snps") or [v["rsid"]]
        fb = (f"if haplotype SNPs unavailable/fail QC: {v['fallback']['rsid']} ({v['fallback']['label']}) -> {v['fallback']['status']}"
              if "fallback" in v else f"if absent/fail QC: within-sample proxy r2>={v['proxy_r2']} within ±{sm.get('proxy_window_bp', 250000)} bp -> TESTABLE WITH PRE-SPECIFIED PROXY; else other QC-passing SNPs in {v['gene']} -> GENE-LEVEL SECONDARY ONLY; else UNTESTABLE")
        rows.append(dict(variant_id=vid, level="A", gene=v["gene"], rsids=";".join(snps),
                         effect_allele=";".join(ea[s]["effect_allele"] for s in snps), coding=f"additive {v['type']}",
                         predictions=";".join(v["predictions"]), families="C;C2;" + ";".join(sorted({fam[p] for p in v["predictions"]})),
                         if_directly_available="DIRECTLY TESTABLE", fallback_rule=fb, status_at_freeze="determined at receipt (deterministic)"))
    for g in sm["approved_genes"]:
        rows.append(dict(variant_id=f"{g}_levelB", level="B", gene=g, rsids="all delivered QC-passing SNPs in gene region (approved_gene_regions.csv)",
                         effect_allele="minor allele", coding="additive", predictions="", families="B",
                         if_directly_available="GENE-LEVEL SECONDARY ONLY", fallback_rule="none delivered -> not analysed",
                         status_at_freeze="secondary; never promoted to confirmatory"))
    for vid, v in sm["amendment_only"].items():
        rows.append(dict(variant_id=vid, level="amendment-only", gene=v["gene"], rsids=v["rsid"] or "", effect_allele="",
                         coding="", predictions=";".join(v["predictions"]), families="",
                         if_directly_available="REQUIRES PROTOCOL AMENDMENT", fallback_rule="outside approved 20-gene universe: retained, not analysed, not deleted",
                         status_at_freeze="REQUIRES PROTOCOL AMENDMENT"))
    cols = ["variant_id", "level", "gene", "rsids", "effect_allele", "coding", "predictions", "families",
            "if_directly_available", "fallback_rule", "status_at_freeze"]
    write_csv(DOCS / "05_SNP_ANALYSIS_HIERARCHY.csv", rows, cols)


FFQ_RATIONALE = {
    "F01": "PAV (taster) carriers perceive thiourea-like and other bitter compounds more intensely; lower intake of bitter beverages expected",
    "F02": "coffee bitterness is mostly caffeine/other TAS2Rs; TAS2R38 relation inconsistent in literature -> two-sided",
    "F03": "green-tea catechin bitterness is TAS2R39/14-mediated; TAS2R38 relation uncertain -> two-sided",
    "F04": "glucosinolate-derived compounds in brassica activate TAS2R38; PAV carriers report lower liking/intake",
    "F05": "PAV carriers mask bitterness by adding sugar to coffee/tea",
    "F06": "TAS1R2 rs12033832 G allele associated with lower sucrose sensitivity and higher sugar intake (Eny et al. 2010)",
    "F07": "lower sweet sensitivity -> more sugar added to beverages",
    "F08": "TAS2R9 V187A changes receptor response; dietary bitter-beverage relation unknown -> two-sided",
}


def doc09(cfg):
    fl = cfg["ffq_lock"]
    gene = {k: v["gene"] for k, v in cfg["snp_map"]["level_a"].items()}
    rows = []
    for pid, ph in fl["phenotypes"].items():
        it = [fl["items"][i] for i in ph["items"]]
        rows.append(dict(phenotype_id=pid, name=ph["name"], items="; ".join(f"{x['label']} [{x['item_code']}]" for x in it),
                         derivation=ph["transform"] + (" of frequency (times/day, category midpoints)" if ph["transform"] == "log1p_sum" else " (yes if any item yes)"),
                         gene=gene[ph["variant"]], variant=ph["variant"], predicted_direction=ph["direction"],
                         biological_rationale=FFQ_RATIONALE[pid], primary_wave=fl["primary_wave"], replication_wave=fl["replication_wave"],
                         testing_family="D", correction="BH q=0.05", status="secondary-triangulation (frozen)"))
    cols = ["phenotype_id", "name", "items", "derivation", "gene", "variant", "predicted_direction", "biological_rationale",
            "primary_wave", "replication_wave", "testing_family", "correction", "status"]
    write_csv(DOCS / "09_CHEMOSENSORY_FFQ_LOCK.csv", rows, cols)


AMENDMENTS = [
    ("AM01", "analytic (pre-receipt)", "34_PRIMARY_VALIDATION_FREEZE.md; 83_PRIMARY_SAP_FINAL.md", "docs/06_MEDICATION_LONGITUDINAL_ENDPOINT_FREEZE.md",
     "primary = current exposure; cross-wave transition secondary (O3)", "primary = longitudinal ph1→ph2 medication change; current exposure secondary",
     "approved plan objective (I013, I052)", "SUPERSEDED BY APPROVED-PROTOCOL REQUIREMENT"),
    ("AM02", "clerical", "approved plan gene list (restricted)", "offline_pipeline/config/snp_map.yaml", "AS2R8", "TAS2R8", "typographical (I028)", "applied"),
    ("AM03", "analytic (scope)", "13_LOCKED_PREDICTIONS_v2_FINAL.csv; 79_NEGATIVE_CONTROL_FINAL.csv", "docs/05_SNP_ANALYSIS_HIERARCHY.csv",
     "P06 TAS2R19, P09/N11 TRPA1, P10 TAS2R4, P11 TAS2R43 in plan", "retained, not analysed, not deleted: REQUIRES PROTOCOL AMENDMENT",
     "outside approved 20-gene universe (I008)", "open: requires ethics/protocol amendment"),
    ("AM04", "clerical (conflict record)", "82_MULTIPLE_TESTING_FINAL.md; README_HANDOFF.md; LOCK_STATUS.md", "docs/13_MULTIPLE_TESTING_FINAL.md",
     "F-PRIMARY = P01, P02, P05, P10", "Family A = P01, P02, P05 (62 governs; 91 separates P10)", "internal conflict; 62 + 91 authoritative (I007)", "applied; legacy files unchanged"),
    ("AM05", "analytic (pre-receipt)", "25_FORMULATION_ROUTE_CONTRASTS.csv; 72_PREDICTION_OBSERVABILITY_FINAL.csv", "docs/11_FORMULATION_MODULE_FREEZE.md",
     "two conflicting C1–C5 definitions", "25 definitions executed; 72 labels retained, not executed", "67 binds contrasts to 25 (D05)", "applied"),
    ("AM06", "analytic (pre-receipt, new)", "81_CALIBRATION_FINAL_LOCK.md; 96_CONTINUOUS_CALIBRATION_AMENDMENT.md", "docs/12_CALIBRATION_FINAL.md",
     "no minimum evaluable count", "≥5 tested in-scope predictions, else UNDEFINED", "avoid uninterpretable ρ (D07)", "applied"),
    ("AM07", "data-availability", "83_PRIMARY_SAP_FINAL.md", "docs/14_CONFIRMATORY_SAP_PRE_RECEIPT.md",
     "ancestry PCs among covariates", "no ancestry PCs (not derivable from candidate-region SNPs)", "distribution scope (D08)", "applied"),
    ("AM08", "data-availability", "75_CLAIMS_SUBCOHORT_FINAL_AUDIT.md", "docs/02_ACTUAL_DISTRIBUTION_SCOPE.md",
     "claims sub-cohort analyses", "not assumed; future data-availability amendment only", "no claims in distribution (I016, I047)", "applied"),
    ("AM09", "clerical", "79_NEGATIVE_CONTROL_FINAL.csv", "docs/10_NEGATIVE_CONTROL_FINAL.md",
     "type labels adherence / mismatch / published_null", "behavioral / receptor-mismatch", "wording drift found in dry reproduction", "applied"),
    ("AM10", "clerical (mapping)", "82_MULTIPLE_TESTING_FINAL.md", "docs/13_MULTIPLE_TESTING_FINAL.md",
     "F-PRIMARY, F-SECONDARY, F-CONTROL, F-CONTRAST, F-GRADIENT, F-CALIBRATION, F-EXPLORATORY", "A, AS, F, E, E, G, X (+ C, C2, B, D, H new)", "longitudinal endpoint families added (I055)", "applied"),
    ("AM11", "analytic (pre-receipt)", "36_GATE_DECISION.md; 69_MEDICATION_PARSER_VALIDATION.md", "docs/08_DRUG_CLASS_MAPPING_RULES.md",
     "drug identification via free-text product names", "Drug ID > KEDD ID > free text", "structured IDs in distribution (I015, I034)", "applied"),
    ("AM12", "procedural", "92_TOMMO_REALSTRING_PARSER_VALIDATION.md", "docs/23_DATA_RECEIPT_EVENT_LOG_TEMPLATE.md",
     "real-string parser QC as pre-opening condition", "genotype-blind post-receipt QC step before sign-off", "real strings exist only after receipt", "applied"),
    ("AM13", "clerical", "HANDOFF_MANIFEST.csv", "../DRY_REPRODUCTION_AUDIT.md",
     "13_LOCKED_PREDICTIONS_v2_FINAL.csv = 23 rows", "24 rows (hash matches)", "manifest row-count error", "recorded"),
    ("AM14", "analytic (pre-receipt, new)", "29_TOMMO_DIETARY_VARIABLE_MATRIX.csv", "docs/09_CHEMOSENSORY_FFQ_LOCK.csv",
     "dietary variable matrix (no phenotype lock)", "F01–F08 lock with items, direction, gene, family", "I014, I043, I044", "applied"),
    ("AM15", "analytic (pre-receipt, conditional)", "approved plan (restricted)", "docs/13_MULTIPLE_TESTING_FINAL.md",
     "no category family", "Family C2 (five revised-plan categories) secondary; confirmatory if D01 switch exercised", "2026-06-13 revision (D01)", "applied"),
]


def legacy_hash(spec):
    out = []
    for f in [s.strip() for s in spec.split(";")]:
        p = PROJ / f
        out.append(f"{f}:{sha(p)[:16]}" if p.exists() else f"{f}:restricted/hash in 22")
    return "; ".join(out)


def amendment_log():
    L = ["# Amendment log (pre-receipt)", "",
         "All entries precede receipt of participant-level data. Legacy files are never edited; old/new SHA-256 (first 16 hex) identify the exact versions. Class per `24_AMENDMENT_POLICY.md`. Owner: PI (endorsement at `29`).", "",
         "| ID | Class | Old (file: sha256-16) | New (file: sha256-16) | Old content | New content | Reason | Status | Date (UTC) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for a in AMENDMENTS:
        newp = (ROOT / a[3]) if not a[3].startswith("../") else (ROOT / a[3]).resolve()
        newh = f"{a[3]}:{sha(newp)[:16]}" if newp.exists() and newp.suffix != ".md" or (newp.exists() and newp.name != "AMENDMENT_LOG.md") else a[3]
        L.append(f"| {a[0]} | {a[1]} | {legacy_hash(a[2])} | {newh} | {a[4]} | {a[5]} | {a[6]} | {a[7]} | 2026-10-04 |")
    L += ["", "Note: new-file hashes refer to the version in this archive; `19_SHA256_CHECKSUMS.txt` gives full hashes."]
    (DOCS / "AMENDMENT_LOG.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def doc22():
    L = ["# 22 — Restricted source hash index", "",
         "Restricted documents are NOT included in the archive or any public mirror. Identity is fixed by SHA-256 of the files as received in this session.", "",
         "| File | Bytes | SHA-256 | Document | Scope summary |", "|---|---|---|---|---|"]
    for name, uid, docd, scope in RESTRICTED:
        p = ATT / uid / name
        h, b = (sha(p), p.stat().st_size) if p.exists() else (KNOWN_RESTRICTED_SHA[name], "n/a (not on this machine)")
        assert h == KNOWN_RESTRICTED_SHA[name], name
        L.append(f"| {name} | {b} | {h} | {docd} | {scope} |")
    L += ["", "## Third-party material excluded from the archive (hash-only, reacquirable)", "",
          "| Path | Bytes | SHA-256 | Note |", "|---|---|---|---|"]
    for t in THIRD_PARTY:
        p = PROJ / t
        files = sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [p]
        for f in files:
            if "__pycache__" in f.parts:
                continue
            L.append(f"| {rel(f)} | {f.stat().st_size} | {sha(f)} | third-party download/derivative; see ledger in same directory |")
    (DOCS / "22_RESTRICTED_SOURCE_HASH_INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def environment():
    pk = ["numpy", "pandas", "scipy", "statsmodels", "scikit-learn", "matplotlib", "PyYAML", "pytest", "openpyxl"]
    vers = {}
    for p in pk:
        r = subprocess.run([sys.executable, "-m", "pip", "show", p], capture_output=True, text=True)
        m = re.search(r"^Version: (.+)$", r.stdout, re.M)
        vers[p] = m.group(1) if m else "not installed"
    (ROOT / "offline_pipeline" / "requirements.txt").write_text("".join(f"{k}=={v}\n" for k, v in vers.items() if v != "not installed"))
    L = ["# Environment specification", "", f"- Python {platform.python_version()} ({platform.python_implementation()})",
         f"- OS: {platform.system()} {platform.release()} {platform.machine()}", "- Network: not required (pipeline is fully offline; snapshots hash-guarded)",
         "- PYTHONHASHSEED=0, MPLBACKEND=Agg", "", "| Package | Version |", "|---|---|"] + [f"| {k} | {v} |" for k, v in vers.items()]
    L += ["", "Install: `pip install -r offline_pipeline/requirements.txt`."]
    (DOCS / "ENVIRONMENT.md").write_text("\n".join(L) + "\n")


def doc17():
    sv = ROOT / "synthetic_validation"
    led = json.loads((sv / "RUN_LEDGER.json").read_text())
    den = list(csv.DictReader(open(sv / "export" / "20_family_denominators.csv")))
    t = ["| Family | Frozen | Tested | Untestable | Rejected |", "|---|---|---|---|---|"] + \
        [f"| {r['family']} | {r['n_frozen']} | {r['n_tested']} | {r['n_untestable']} | {r['n_reject']} |" for r in den]
    t += ["", f"Two fresh-process runs produced identical export hashes: {led['deterministic']}. participant_level_tommo_data_used = {led['participant_level_tommo_data_used']}."]
    fc = list(csv.DictReader(open(sv / "fixed_case_endpoints.csv")))
    eps = ["ANY_MEDICATION_CHANGE", "ACTIVE_INGREDIENT_CHANGE", "WITHIN_CLASS_SWITCH", "MEDICATION_ADDITION", "MEDICATION_REMOVAL",
           "STANDARDIZED_DOSE_INCREASE", "STANDARDIZED_DOSE_DECREASE"]
    t += ["", "Fixed-case endpoints (blank = not in risk set / undefined; S00009 absent = excluded):", "",
          "| Case | " + " | ".join(e.replace("STANDARDIZED_", "STD_").replace("MEDICATION_", "MED_") for e in eps) + " |",
          "|---" * (len(eps) + 1) + "|"]
    for r in fc:
        t.append(f"| {r['pid']} | " + " | ".join(("" if r.get(e, "") in ("", "nan") else str(int(float(r[e])))) for e in eps) + " |")
    pt = (sv / "PYTEST_SUMMARY.txt").read_text().strip()
    s = (DOCS / "17_SYNTHETIC_PIPELINE_VALIDATION.md").read_text()
    s = re.sub(r"## Results\n.*?\n## Test suite", "## Results\n" + "\n".join(t) + "\n\n## Test suite", s, flags=re.S)
    s = s.replace("SYNTHETIC_RESULTS_TABLE", "\n".join(t))
    s = re.sub(r"`tests/test_pipeline.py`: [^.]*?\. Covers", f"`tests/test_pipeline.py`: {pt}. Covers", s)
    s = s.replace("TEST_SUMMARY", pt)
    (DOCS / "17_SYNTHETIC_PIPELINE_VALIDATION.md").write_text(s)


def register(dlog):
    dref = {}
    for m in re.finditer(r"^\| (D\d\d) \|.*?\| [^|]* \| ([^|]*) \| [^|]* \| [^|]* \|$", dlog, re.M):
        for i in re.findall(r"[IR]\d\d\d|R\d\d", m.group(2)):
            dref.setdefault(i, []).append(m.group(1))
    rows = []
    for k, (iid, src, loc, cat, extra, sci, summ, dels, ev) in enumerate(sorted(IR.REGISTER, key=lambda r: (IR.ORDER[r[1]], r[0])), 1):
        rows.append(dict(instruction_id=iid, chronology_seq=k, source_message=src, source_location=loc, introduced=IR.INTRODUCED[src],
                         primary_category=cat, additional_categories=";".join(extra), scientifically_consequential=sci,
                         instruction_summary=summ, frozen_deliverables=";".join(dels), evidence_phrase=ev,
                         decision_ids=";".join(dref.get(iid, [])), status="incorporated"))
    for e in IR.EVENTS:
        rows.append(dict(instruction_id=e[0], chronology_seq="", source_message=e[1], source_location="0", introduced=IR.INTRODUCED[e[1]],
                         primary_category="scientific", additional_categories="", scientifically_consequential="Y",
                         instruction_summary=e[2], frozen_deliverables=";".join(e[3]), evidence_phrase=e[4], decision_ids="D01",
                         status="clarification pending; resolved by conditional rule D01"))
    cols = list(rows[0])
    write_csv(DOCS / "INSTRUCTION_REGISTER.csv", rows, cols)
    return rows, dref


# ---------------------------------------------------------------- completeness audit
def paras(f):
    return [p for p in re.split(r"\n\s*\n", (SI / f).read_text()) if p.strip()]


def expand(loc):
    out = set()
    for part in loc.split(","):
        a, _, b = part.partition("-")
        out |= set(range(int(a), int(b or a) + 1))
    return out


def audit(rows, dref, dlog):
    checks, fails = [], []

    def ck(name, ok, detail=""):
        checks.append((name, ok, detail))
        if not ok:
            fails.append(name)

    for f, src in [("U1_initial_instruction.txt", "U1"), ("U2_dry_reproduction.txt", "U2"), ("U3_consolidation.txt", "U3")]:
        n = len(paras(f))
        cov = set().union(*[expand(r["source_location"]) for r in rows if r["source_message"] == src])
        miss = sorted(set(range(n)) - cov)
        ck(f"{src}: every paragraph ({n}) mapped to an instruction", not miss, f"unmapped {miss}" if miss else "")
    mp = (SI / "MP_main_prompt.txt").read_text().splitlines()
    heads = [h for h in IR.MP_SECTIONS if h not in [x.strip() for x in mp]]
    ck("MP: every listed section heading exists verbatim in the captured main prompt", not heads, str(heads))
    allcaps = [x.strip() for i, x in enumerate(mp) if i > 0 and set(mp[i - 1].strip()) == {"="} and x.strip() and set(x.strip()) != {"="}]
    unlisted = sorted(set(allcaps) - set(IR.MP_SECTIONS))
    ck("MP: every '====' delimited section of the main prompt is in the section list", not unlisted, str(unlisted))
    covered = set(s for r in rows if r["source_message"] == "MP" for s in r["source_location"].split(";"))
    miss = [h for h in IR.MP_SECTIONS if h not in covered and h not in ("STOP",)] + (["STOP"] if "STOP" not in covered else [])
    ck(f"MP: every section ({len(IR.MP_SECTIONS)}) mapped to an instruction", not miss, str(miss))
    a1 = (SI / "A1_assistant_clarification.txt").read_text()
    ck("A1 clarification recorded as event E01", "2026-06-13" in a1 and any(r["instruction_id"] == "E01" for r in rows))
    ck("every instruction has a primary category from the five required", all(r["primary_category"] in IR.CATEGORIES for r in rows))
    ck("every additional category is valid", all(c in IR.CATEGORIES for r in rows for c in r["additional_categories"].split(";") if c))
    bad, noev = [], []
    for r in rows:
        dels = r["frozen_deliverables"].split(";")
        for p in dels:
            if not (ROOT / p).resolve().exists():
                bad.append(f"{r['instruction_id']}:{p}")
        first = (ROOT / dels[0]).resolve()
        if first.exists() and r["evidence_phrase"] not in first.read_text(encoding="utf-8", errors="ignore"):
            noev.append(f"{r['instruction_id']}:{dels[0]}")
    ck("every deliverable named in the register exists", not bad, str(bad))
    ck("every instruction's evidence phrase is present in its first frozen deliverable (not only in chat)", not noev, str(noev))
    sci = [r for r in rows if r["scientifically_consequential"] == "Y"]
    ck(f"every scientifically consequential instruction ({len(sci)}) maps to >=1 frozen file outside chat history",
       all(r["frozen_deliverables"] for r in sci))
    ids = {r["instruction_id"] for r in rows}
    dangling = sorted({i for i in dref if i not in ids})
    ck("every instruction referenced by DECISION_LOG exists in the register", not dangling, str(dangling))
    st = re.findall(r"^\| D\d\d \|.*\| ([^|]+) \|$", dlog, re.M)
    ck(f"every decision ({len(st)}) has status FROZEN", st and all(s.strip().startswith("FROZEN") for s in st))
    for n in range(1, 30):
        hit = list(DOCS.glob(f"{n:02d}_*"))
        ck(f"document {n:02d} exists", len(hit) == 1 or n in (18, 19), "" if hit else "missing")
    led = json.loads((ROOT / "synthetic_validation" / "RUN_LEDGER.json").read_text())
    ck("synthetic pipeline ran end to end twice with identical outputs", led["deterministic"] is True)
    ck("synthetic validation used no participant-level data", led["participant_level_tommo_data_used"] is False)
    ck("pytest suite passed", "passed" in (ROOT / "synthetic_validation" / "PYTEST_SUMMARY.txt").read_text() and
       "failed" not in (ROOT / "synthetic_validation" / "PYTEST_SUMMARY.txt").read_text())
    rec = [p for p in PROJ.rglob("RECEIPT_SIGNOFF.json")] + [p for p in PROJ.rglob("receipt") if p.is_dir()]
    ck("no receipt sign-off or receipt directory exists (no participant-level data received)", not rec, str(rec))
    return checks, fails


def write_audit(checks, fails, rows):
    by = {}
    for r in rows:
        if r["chronology_seq"]:
            by.setdefault(r["primary_category"], 0)
            by[r["primary_category"]] += 1
    L = ["# Completeness audit (pre-receipt instructions vs frozen deliverables)", "",
         f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} by `tools/build_freeze_package.py` against the verbatim session captures in `session_instructions/` (initial message U1 with the main prompt MP, U2, assistant clarification A1, U3) and the standing rules (R).", "",
         f"Instructions registered: {sum(1 for r in rows if r['chronology_seq'])} (+1 clarification event). Scientifically consequential: {sum(1 for r in rows if r['scientifically_consequential'] == 'Y' and r['chronology_seq'])}.", "",
         "| Primary category | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(by.items())] + ["",
         "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, (n, ok, dt) in enumerate(checks, 1):
        L.append(f"| {i} | {n} | {'PASS' if ok else 'FAIL'} | {dt} |")
    L += ["", f"Result: {'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)} checks). "
          + ("All pre-receipt instructions are incorporated into frozen deliverables; no scientifically consequential instruction exists only in chat history."
             if not fails else "Failures: " + "; ".join(fails)),
          "", "Limitation: the chat transport does not expose exact message timestamps; chronology is the order of arrival, and captures were written 2026-10-04T18:42Z."]
    (DOCS / "COMPLETENESS_AUDIT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- archive
def archive_members():
    out = []
    ex_dirs = {"__pycache__", ".pytest_cache", "timestamp"}
    for p in sorted(PROJ.rglob("*")):
        if not p.is_file():
            continue
        r = rel(p)
        if any(part in ex_dirs for part in p.parts) or any(r == t or r.startswith(t + "/") for t in THIRD_PARTY):
            continue
        out.append(p)
    return out


def write_manifest():
    restricted = set(KNOWN_RESTRICTED_SHA.values())
    mem = [p for p in archive_members() if p.name not in ("18_PRE_RECEIPT_MANIFEST.csv", "19_SHA256_CHECKSUMS.txt")]
    leak = [rel(p) for p in mem if sha(p) in restricted]
    if leak:
        sys.exit(f"restricted source inside archive: {leak}")
    top = lambda p: rel(p).split("/")[0]
    man = [dict(path=rel(p), bytes=p.stat().st_size, sha256=sha(p),
                layer="pre-receipt freeze" if top(p) == "pre_receipt_freeze" else
                ("reconciliation/dry-reproduction" if top(p) in ("reconciliation", "dry_reproduction", "PROTOCOL_DISTRIBUTION_FREEZE_RECONCILIATION.md", "DRY_REPRODUCTION_AUDIT.md")
                 else "legacy frozen package"))
           for p in mem]
    write_csv(DOCS / "18_PRE_RECEIPT_MANIFEST.csv", man, ["path", "bytes", "sha256", "layer"])
    mem.append(DOCS / "18_PRE_RECEIPT_MANIFEST.csv")
    (DOCS / "19_SHA256_CHECKSUMS.txt").write_text("".join(f"{sha(p)}  {rel(p)}\n" for p in mem))
    mem.append(DOCS / "19_SHA256_CHECKSUMS.txt")
    return mem


def main():
    cfg = {k: yaml.safe_load(open(ROOT / "offline_pipeline/config" / f"{k}.yaml")) for k in ("snp_map", "ffq_lock")}
    r = subprocess.run([sys.executable, "-m", "pytest", str(ROOT / "offline_pipeline/tests"), "-q", "-p", "no:cacheprovider"],
                       capture_output=True, text=True)
    (ROOT / "synthetic_validation" / "PYTEST_SUMMARY.txt").write_text(r.stdout.strip().splitlines()[-1].strip("= ") + "\n")
    doc03(); doc05(cfg); doc09(cfg); environment(); doc17()
    dlog = (DOCS / "DECISION_LOG.md").read_text()
    rows, dref = register(dlog)
    doc22()
    checks, fails = audit(rows, dref, dlog)
    write_audit(checks, fails, rows)
    amendment_log()
    mem = write_manifest()
    checks, fails = audit(rows, dref, dlog)
    write_audit(checks, fails, rows)
    mem = write_manifest()
    tdir = ROOT / "timestamp"
    tdir.mkdir(exist_ok=True)
    zp = tdir / ZIP_NAME
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(mem, key=rel):
            zi = zipfile.ZipInfo("CHEMOSENSORY_TOMMO_PRE_RECEIPT_FREEZE/" + rel(p), date_time=(2026, 10, 4, 0, 0, 0))
            zi.compress_type, zi.external_attr = zipfile.ZIP_DEFLATED, 0o644 << 16
            z.writestr(zi, p.read_bytes())
    h = sha(zp)
    (tdir / "ARCHIVE_SHA256.txt").write_text(f"{h}  {ZIP_NAME}\n")
    print(f"audit: {'PASS' if not fails else 'FAIL'} {len(checks) - len(fails)}/{len(checks)}; files={len(mem)}; {ZIP_NAME} sha256={h}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
