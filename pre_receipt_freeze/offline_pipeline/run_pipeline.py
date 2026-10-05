#!/usr/bin/env python3
"""Offline pipeline runner. Stages: qc (01-07), lock (01-11), analysis (01-22), all (=analysis).
Real mode refuses 'analysis' unless receipt/RECEIPT_SIGNOFF.json exists, the parser real-string gate passed,
and the recomputed analysis-set lock equals the lock written at the 'lock' stage."""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from chemotommo._common import Ctx, PKG, load_module, sha256  # noqa: E402

MODULES = ["01_inventory", "02_variable_mapping", "03_snp_harmonization", "04_medication_id_mapping",
           "05_medication_long_format", "06_drug_class_mapping", "07_dose_harmonization", "08_cross_wave_medication_change",
           "09_ffq_phenotypes", "10_covariates", "11_analysis_dataset", "12_primary_variant_models",
           "13_gene_constrained_secondary", "14_medication_change_models", "15_formulation_module", "16_negative_controls",
           "17_calibration", "18_machine_learning_secondary", "19_sensitivity", "20_tables", "21_figures",
           "22_privacy_safe_export"]
STAGE_END = {"qc": 7, "lock": 11, "analysis": 22, "all": 22}


def check_signoff(ctx):
    so = ctx.out_dir / "receipt" / "RECEIPT_SIGNOFF.json"
    lock = ctx.out_dir / "results" / "11_analysis_set_lock.json"
    if not so.exists() or not lock.exists():
        sys.exit("real mode: analysis stage requires receipt/RECEIPT_SIGNOFF.json and a prior 'lock' stage")
    s = json.loads(so.read_text())
    if s.get("parser_realstring_gate") != "PASS":
        ctx.t["parser_gate"] = s.get("parser_realstring_gate", "NOT RUN")
    else:
        ctx.t["parser_gate"] = "PASS"
    if s.get("variable_map_sha256") != sha256(ctx.cfg_dir / "variable_map.yaml"):
        sys.exit("variable_map.yaml changed after sign-off: log a technical amendment first")
    if s.get("analysis_set_lock_sha256") != sha256(lock):
        sys.exit("analysis-set lock differs from signed-off lock")
    return json.loads(lock.read_text())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config"))
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["synthetic", "real"], required=True)
    ap.add_argument("--stage", choices=list(STAGE_END), default="all")
    a = ap.parse_args(argv)
    os.environ.setdefault("PYTHONHASHSEED", "0")
    ctx = Ctx(a.config, a.data, a.out, a.mode, a.stage)
    saved = None
    if a.mode == "real" and STAGE_END[a.stage] > 11:
        saved = check_signoff(ctx)
    for i, name in enumerate(MODULES[:STAGE_END[a.stage]], 1):
        load_module(PKG / f"{name}.py", f"m{name}").run(ctx)
        if i == 11 and saved is not None:
            new = ctx.t["lock"]
            for k in ("participant_set_sha256", "config_sha256", "parser_sha256", "atc_snapshot_sha256", "code_sha256"):
                if new[k] != saved[k]:
                    sys.exit(f"analysis-set lock mismatch on {k}; analysis refused")
    (ctx.out_dir / "results" / "RUN_LOG.json").write_text(json.dumps(dict(mode=a.mode, stage=a.stage, notes=ctx.log), indent=2,
                                                                       ensure_ascii=False))
    print("\n".join(ctx.log))
    print(f"completed {a.stage} ({a.mode}) -> {ctx.out_dir}")


if __name__ == "__main__":
    main()
