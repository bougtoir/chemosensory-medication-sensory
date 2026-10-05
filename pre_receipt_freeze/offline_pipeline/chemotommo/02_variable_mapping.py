"""02 variable mapping: resolve every logical variable in config to a delivered column; report availability."""
import pandas as pd

from chemotommo._common import read_table


def run(ctx):
    vm, ffq = ctx.cfg["variable_map"], ctx.cfg["ffq_lock"]
    cache, rows = {}, []

    def cols(key):
        if key not in cache:
            df = read_table(ctx, key)
            cache[key] = set(df.columns) if df is not None else set()
        return cache[key]

    med = vm["medication"]
    for wave, key in med["waves"].items():
        rows.append(dict(domain="medication", logical="any_use", wave=wave, file=key, column=med["any_use_column"],
                         available=med["any_use_column"] in cols(key)))
        for logical, tmpl in med["slot_columns"].items():
            n = sum(tmpl.format(k=k) in cols(key) for k in range(1, med["n_slots"] + 1))
            rows.append(dict(domain="medication", logical=logical, wave=wave, file=key, column=tmpl,
                             available=n == med["n_slots"], n_slots_found=n))
    for logical, spec in vm["covariates"].items():
        rows.append(dict(domain="covariate", logical=logical, wave="ph1", file=spec["file"], column=spec["column"],
                         available=spec["column"] in cols(spec["file"])))
    for item, spec in ffq["items"].items():
        for wave in ("ph1", "ph2"):
            rows.append(dict(domain="ffq", logical=item, wave=wave, file=f"ffq_{wave}", column=spec[wave],
                             available=spec[wave] in cols(f"ffq_{wave}"), optional=bool(spec.get("optional"))))
    for wave, spec in vm["questionnaire_date"].items():
        rows.append(dict(domain="date", logical="questionnaire_date", wave=wave, file=spec["file"], column=spec["column"],
                         available=spec["column"] in cols(spec["file"])))
    av = pd.DataFrame(rows)
    ctx.result("02_variable_availability", av)
    ctx.t["availability"] = av
    missing = av[(~av["available"]) & (av.get("optional", False) != True)]  # noqa: E712
    ctx.note(f"variable mapping: {len(av) - len(missing)} available, {len(missing)} missing (see 02_variable_availability)")
