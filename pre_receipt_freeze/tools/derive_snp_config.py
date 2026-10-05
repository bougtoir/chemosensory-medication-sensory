"""Derive frozen effect alleles and approved-gene regions from the ledgered Ensembl snapshot.

Effect alleles are assigned from VEP amino-acid annotation on the forward (GRCh38) strand,
so no allele choice is left for after data receipt. Writes:
  offline_pipeline/config/derived/effect_alleles.csv
  offline_pipeline/config/derived/approved_gene_regions.csv
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / "data" / "raw_ensembl_20261004b"
OUT = ROOT / "pre_receipt_freeze" / "offline_pipeline" / "config" / "derived"
COMP = str.maketrans("ACGT", "TGCA")
# variant -> (gene, protein position, effect amino acid) from 63/65 (literature effect allele)
TARGETS = {
    "rs713598": ("TAS2R38", 49, "P"),     # A49P: Pro = PAV (taster) allele
    "rs1726866": ("TAS2R38", 262, "A"),   # V262A: Ala = PAV
    "rs10246939": ("TAS2R38", 296, "V"),  # I296V: Val = PAV
    "rs3741845": ("TAS2R9", 187, "A"),    # V187A: 187A = effect allele (P05)
    "rs10772420": ("TAS2R19", None, None),
    "rs11988795": ("TRPA1", None, None),
}
NONCODING = {"rs12033832": ("TAS1R2", "G")}   # synonymous; Eny et al. 2010 G allele, forward strand


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for rs, (gene, pos, aa) in TARGETS.items():
        d = json.loads((SNAP / "vep" / f"{rs}.json").read_text())[0]
        ref, *alts = d["allele_string"].split("/")
        eff, note = "", "amendment-only variant; no effect allele frozen" if aa is None else ""
        if aa:
            for t in d.get("transcript_consequences", []):
                if t.get("gene_symbol") != gene or not t.get("amino_acids") or t.get("protein_start") != pos:
                    continue
                ref_aa, alt_aa = t["amino_acids"].split("/")
                tx_allele = t["variant_allele"]
                fwd = tx_allele if t.get("strand", 1) == 1 else tx_allele  # VEP variant_allele is forward-strand
                if alt_aa == aa:
                    eff = fwd
                elif ref_aa == aa:
                    eff = ref
                if eff:
                    note = f"{gene} p.{ref_aa}{pos}{alt_aa} transcript {t['transcript_id']} strand {t.get('strand')}"
                    break
        rows.append(dict(rsid=rs, gene=gene, chrom=d["seq_region_name"], pos_grch38=d["start"], ref=ref,
                         alts="/".join(alts), effect_allele=eff, effect_allele_complement=eff.translate(COMP) if eff else "",
                         basis=note))
    for rs, (gene, eff) in NONCODING.items():
        d = json.loads((SNAP / "vep" / f"{rs}.json").read_text())[0]
        ref, *alts = d["allele_string"].split("/")
        rows.append(dict(rsid=rs, gene=gene, chrom=d["seq_region_name"], pos_grch38=d["start"], ref=ref,
                         alts="/".join(alts), effect_allele=eff, effect_allele_complement=eff.translate(COMP),
                         basis="synonymous (VEP); literature effect allele G (Eny et al. 2010), forward strand"))
    with open(OUT / "effect_alleles.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    regs = []
    for p in sorted((SNAP / "genes").glob("*.json")):
        g = json.loads(p.read_text()); build = p.stem.split("_")[-1]
        regs.append(dict(gene=g["display_name"], build=build, chrom=g["seq_region_name"], start=g["start"], end=g["end"],
                         flank_bp=10000, region_start=max(1, g["start"] - 10000), region_end=g["end"] + 10000, ensembl_id=g["id"]))
    with open(OUT / "approved_gene_regions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(regs[0])); w.writeheader(); w.writerows(regs)
    for r in rows:
        print(r["rsid"], r["gene"], r["ref"], r["alts"], "effect=", r["effect_allele"], "|", r["basis"])
    print(len(regs), "gene-build regions")


if __name__ == "__main__":
    main()
