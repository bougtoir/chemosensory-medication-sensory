#!/usr/bin/env python3
"""Stage 2A: drug chemical space via PubChem PUG-REST.

Drug list = commonly used oral medicines (WHO essential medicines + common
Japanese/US outpatient orals). Frozen in drugs_oral_list.csv — edit there, not
here. Saves raw JSON to data/raw/pubchem/ and prediction/drug_chemical_space.csv.
"""
import json, time, urllib.parse, urllib.request, hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "pubchem"
RAW.mkdir(parents=True, exist_ok=True)
PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PROPS = ("MolecularWeight,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,"
         "RotatableBondCount,Charge,ExactMass,CanonicalSMILES,IsomericSMILES,InChIKey")

def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "chemed/1.0"})
    for a in range(4):
        try:
            return urllib.request.urlopen(r, timeout=40).read()
        except Exception:
            if a == 3: raise
            time.sleep(2 * a + 1)

drugs = pd.read_csv(ROOT / "prediction" / "drugs_oral_list.csv")
rows, ledger = [], []
for _, d in drugs.iterrows():
    name = d["generic_name"]
    u = f"{PUG}/compound/name/{urllib.parse.quote(name)}/property/{PROPS}/JSON"
    try:
        data = json.loads(get(u))
    except Exception as e:
        ledger.append({"generic_name": name, "status": f"FAIL {e}", "cid": ""})
        continue
    p = data["PropertyTable"]["Properties"][0]
    raw = json.dumps(data)
    (RAW / f"{name.replace(' ','_')}.json").write_text(raw)
    rows.append({"generic_name": name, "drug_class": d.get("drug_class", ""),
                 "route": d.get("route", "oral"),
                 "oral_exposure": d.get("oral_exposure", "high"),
                 "formulation_note": d.get("formulation_note", ""),
                 "cid": p.get("CID"), "mw": p.get("MolecularWeight"),
                 "xlogp": p.get("XLogP"), "tpsa": p.get("TPSA"),
                 "hbd": p.get("HBondDonorCount"), "hba": p.get("HBondAcceptorCount"),
                 "rotb": p.get("RotatableBondCount"), "charge": p.get("Charge"),
                 "inchikey": p.get("InChIKey"), "smiles": p.get("CanonicalSMILES"),
                 "sha256_16": hashlib.sha256(raw.encode()).hexdigest()[:16]})
    ledger.append({"generic_name": name, "status": "ok", "cid": p.get("CID")})
    time.sleep(0.25)

pd.DataFrame(rows).to_csv(ROOT / "prediction" / "drug_chemical_space.csv", index=False)
pd.DataFrame(ledger).to_csv(RAW / "pubchem_ledger.csv", index=False)
ok = pd.DataFrame(rows)
print(f"{len(ok)} drugs resolved", "| fails:", sum(1 for l in ledger if l['status']!='ok'))
