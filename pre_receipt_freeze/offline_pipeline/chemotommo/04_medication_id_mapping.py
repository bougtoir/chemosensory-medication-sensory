"""04 medication ID mapping: Drug ID -> KEDD ID -> free-text parser (fallback); free text always parsed for
formulation/route/EX class and QC. Writes the genotype-blind real-string QC sample (92 gate) in real mode."""
import glob

import numpy as np
import pandas as pd

from chemotommo._common import canon_ingredient, is_true, load_module, read_table, sha256


def load_master(ctx, spec):
    p = spec.get("path")
    if not p:
        return None
    files = sorted(glob.glob(str(ctx.data_dir / p[5:]))) if p.startswith("DATA:") else [str(ctx.path(p))]
    if not files:
        return None
    m = pd.concat([pd.read_csv(f, dtype=str) for f in files], ignore_index=True)
    return m.drop_duplicates(spec["id_column"]).set_index(spec["id_column"])


def run(ctx):
    vm, dd = ctx.cfg["variable_map"], ctx.cfg["drug_dictionary"]
    med, idc = vm["medication"], vm["id_column"]
    ppath = ctx.path(dd["free_text"]["parser"])
    if sha256(ppath) != dd["free_text"]["parser_sha256"]:
        raise RuntimeError("medication parser hash differs from frozen v1.0.0")
    parser = load_module(ppath, "medication_parser")
    masters = {k: load_master(ctx, dd["masters"][k]) for k in ("drug_id", "kedd_id")}
    aliases = dd["ingredient_aliases"]
    tv = med["flag_true_values"]
    rows, answered = [], {}
    for wave, key in med["waves"].items():
        df = read_table(ctx, key)
        if df is None:
            continue
        au = df[med["any_use_column"]] if med["any_use_column"] in df else pd.Series(np.nan, index=df.index)
        for pid, a in zip(df[idc], au):
            answered.setdefault(pid, {})[wave] = pd.notna(a) and str(a).strip() != ""
        sc = med["slot_columns"]
        for k in range(1, med["n_slots"] + 1):
            cols = {lg: tmpl.format(k=k) for lg, tmpl in sc.items()}
            present = {lg: c for lg, c in cols.items() if c in df.columns}
            if not present:
                continue
            sub = pd.DataFrame({lg: df[c] for lg, c in present.items()})
            sub["pid"], sub["wave"], sub["slot"] = df[idc].values, wave, k
            keep = sub[[c for c in ("text", "kedd_id", "drug_id") if c in sub]].notna().any(axis=1)
            rows.append(sub[keep])
    r = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["pid", "wave", "slot"])
    for c in ("text", "kedd_id", "drug_id", "rx", "other", "duration_value", "duration_unit", "frequency_value",
              "frequency_unit", "dose_value", "dose_unit"):
        if c not in r:
            r[c] = np.nan
    out = []
    parse_cache = {}
    for rec in r.to_dict("records"):
        res = dict(rec)
        res["rx"] = is_true(rec["rx"], tv)
        res["other"] = is_true(rec["other"], tv)
        ing, atc, form_text, strength, source = None, "", None, None, "unresolved"
        flags = dict(drug_id_unknown=False, kedd_unknown=False, id_conflict=False)
        hits = {}
        for kind in dd["id_priority"]:
            if kind == "free_text":
                continue
            val = rec.get(kind)
            if pd.isna(val) or str(val).strip() == "":
                continue
            m = masters.get(kind)
            spec = dd["masters"][kind]
            if m is not None and str(val) in m.index:
                hits[kind] = m.loc[str(val)]
            else:
                flags["drug_id_unknown" if kind == "drug_id" else "kedd_unknown"] = True
        for kind in dd["id_priority"]:
            if kind in hits:
                h, spec = hits[kind], dd["masters"][kind]
                ing = h.get(spec["ingredient_column"])
                atc = h.get(spec.get("atc_column"), "") if spec.get("atc_column") else ""
                form_text = h.get(spec.get("formulation_column")) if spec.get("formulation_column") else None
                strength = h.get(spec.get("strength_mg_column")) if spec.get("strength_mg_column") else None
                source = kind
                break
        if len(hits) == 2:
            a = {canon_ingredient(x, aliases) for x in str(hits["drug_id"].get(dd["masters"]["drug_id"]["ingredient_column"])).split(";")}
            b = {canon_ingredient(x, aliases) for x in str(hits["kedd_id"].get(dd["masters"]["kedd_id"]["ingredient_column"])).split(";")}
            flags["id_conflict"] = a != b
        text = rec.get("text")
        ptxt = form_text if isinstance(form_text, str) and form_text else (text if isinstance(text, str) else "")
        if ptxt not in parse_cache:
            parse_cache[ptxt] = parser.parse(ptxt) if ptxt else {}
        p = parse_cache[ptxt]
        if ing is None and isinstance(text, str) and text:
            pt = parse_cache.setdefault(text, parser.parse(text))
            if pt.get("generic_name"):
                ing, source = pt["generic_name"], "free_text"
        ings = [canon_ingredient(x, aliases) for x in str(ing).split(";")] if ing is not None and str(ing) != "nan" else []
        ings = [x for x in ings if x]
        res.update(flags)
        res.update(id_source=source, ingredients=";".join(ings), n_ingredients=len(ings), atc_master=atc if isinstance(atc, str) else "",
                   strength_mg=strength if strength is not None and str(strength) != "nan" else "",
                   formulation=p.get("formulation", "unknown") or "unknown", route=p.get("route", "unknown") or "unknown",
                   ex_class=p.get("oral_sensory_exposure"), parser_review=p.get("manual_review_flag", ""),
                   unresolved=len(ings) == 0,
                   product_key=str(rec["drug_id"]) if pd.notna(rec.get("drug_id")) else (
                       str(rec["kedd_id"]) if pd.notna(rec.get("kedd_id")) else (str(text).strip() if isinstance(text, str) else None)))
        out.append(res)
    mr = pd.DataFrame(out)
    ans = pd.DataFrame([dict(pid=p, ph1_answered=v.get("ph1", False), ph2_answered=v.get("ph2", False)) for p, v in answered.items()])
    ctx.t["med_rows"], ctx.t["answered"] = mr, ans
    ctx.work("04_medication_rows", mr)
    qc = mr.groupby(["wave", "id_source"]).size().rename("n_rows").reset_index() if len(mr) else pd.DataFrame()
    extra = pd.DataFrame([dict(wave="all", id_source=f"flag:{f}", n_rows=int(mr[f].sum())) for f in
                          ("drug_id_unknown", "kedd_unknown", "id_conflict", "unresolved")]) if len(mr) else pd.DataFrame()
    ctx.result("04_id_resolution_qc", pd.concat([qc, extra], ignore_index=True))
    if ctx.mode == "real" and len(mr):
        uniq = pd.Series(mr["text"].dropna().astype(str).unique())
        n = min(len(uniq), 500) if len(uniq) >= 300 else len(uniq)
        sample = uniq.sample(n=n, random_state=ctx.cfg["analysis_config"]["seed"]) if n else uniq
        pd.DataFrame({"raw_text": sample.values}).to_csv(ctx.out_dir / "work" / "04_realstring_qc_sample.csv", index=False)
        ctx.note(f"92 gate: genotype-blind real-string QC sample of {n} unique strings written (work/)")
