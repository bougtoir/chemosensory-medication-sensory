"""03 SNP harmonization: allele alignment to frozen effect alleles, QC, TAS2R38 EM diplotypes,
deterministic fallback status (direct / pre-specified proxy / gene-level only / untestable), Level-B set."""
import itertools
import math

import numpy as np
import pandas as pd
from scipy import stats

from chemotommo._common import read_table

COMP = str.maketrans("ACGT", "TGCA")


def effect_dosage(series, ref, alt, effect):
    """Return effect-allele dosage (0/1/2, NaN). Accepts dosage of alt or allele strings like 'A/G', 'AG'."""
    s = series.astype(str).str.strip()
    numeric = pd.to_numeric(s, errors="coerce")
    if numeric.notna().mean() > 0.5:
        if effect == alt:
            return numeric
        if effect == ref:
            return 2 - numeric
        if effect.translate(COMP) == alt:
            return numeric
        if effect.translate(COMP) == ref:
            return 2 - numeric
        return pd.Series(np.nan, index=s.index)
    alleles = s.str.replace(r"[^ACGT]", "", regex=True)
    eff = effect
    observed = set("".join(alleles.dropna().tolist()))
    if eff not in observed and eff.translate(COMP) in observed and {ref, alt} != {"A", "T"} and {ref, alt} != {"C", "G"}:
        eff = eff.translate(COMP)
    return alleles.map(lambda a: a.count(eff) if len(a) == 2 else np.nan).astype(float)


def snp_qc(d, q):
    call = d.notna().mean()
    p = d.mean() / 2 if d.notna().any() else math.nan
    maf = min(p, 1 - p) if not math.isnan(p) else math.nan
    n0, n1, n2 = [(d == k).sum() for k in (0, 1, 2)]
    n = n0 + n1 + n2
    if n and 0 < p < 1:
        exp = np.array([(1 - p) ** 2, 2 * p * (1 - p), p ** 2]) * n
        hwe = float(stats.chi2.sf(((np.array([n0, n1, n2]) - exp) ** 2 / exp).sum(), 1))
    else:
        hwe = math.nan
    ok = call >= q["min_call_rate"] and (maf >= q["min_maf"] if not math.isnan(maf) else False) and \
        (hwe >= q["hwe_p"] if not math.isnan(hwe) else False)
    return dict(call_rate=call, maf=maf, hwe_p=hwe, qc_pass=bool(ok))


def em_pav_dosage(G, min_post=0.9, iters=200):
    """G: n x 3 effect(PAV)-allele dosages. EM over 8 haplotypes; returns PAV-haplotype count (0/1/2)
    when the posterior of that count >= min_post and both haplotypes are PAV/AVI, else NaN; plus 'other' flag."""
    haps = list(itertools.product([0, 1], repeat=3))
    PAV, AVI = haps.index((1, 1, 1)), haps.index((0, 0, 0))
    pairs = [(i, j) for i in range(8) for j in range(i, 8)]
    geno_of = {pr: tuple(a + b for a, b in zip(haps[pr[0]], haps[pr[1]])) for pr in pairs}
    freq = np.full(8, 1 / 8)
    obs = [tuple(int(v) for v in row) if not np.isnan(row).any() else None for row in G]
    compat = {}
    for g in set(o for o in obs if o):
        compat[g] = [pr for pr in pairs if geno_of[pr] == g]
    for _ in range(iters):
        cnt = np.zeros(8)
        for g in obs:
            if not g:
                continue
            w = np.array([freq[i] * freq[j] * (2 if i != j else 1) for i, j in compat[g]])
            w = w / w.sum() if w.sum() > 0 else np.full(len(w), 1 / len(w))
            for (i, j), wk in zip(compat[g], w):
                cnt[i] += wk
                cnt[j] += wk
        new = cnt / cnt.sum()
        if np.abs(new - freq).max() < 1e-8:
            freq = new
            break
        freq = new
    out, other = [], []
    for g in obs:
        if not g:
            out.append(np.nan); other.append(np.nan); continue
        w = np.array([freq[i] * freq[j] * (2 if i != j else 1) for i, j in compat[g]])
        w = w / w.sum()
        post = {}
        oth = 0.0
        for (i, j), wk in zip(compat[g], w):
            if {i, j} <= {PAV, AVI}:
                k = (i == PAV) + (j == PAV)
                post[k] = post.get(k, 0) + wk
            else:
                oth += wk
        best = max(post, key=post.get) if post else None
        out.append(float(best) if best is not None and post[best] >= min_post else np.nan)
        other.append(float(oth >= min_post))
    return np.array(out), np.array(other), dict(zip(["".join(map(str, h)) for h in haps], freq))


def run(ctx):
    sm = ctx.cfg["snp_map"]
    vm = ctx.cfg["variable_map"]
    idc = vm["id_column"]
    eff = pd.read_csv(ctx.path(sm["effect_alleles"])).set_index("rsid")
    regions = pd.read_csv(ctx.path(sm["gene_regions"]))
    geno_raw = read_table(ctx, "snp_genotypes")
    man = read_table(ctx, "snp_manifest")
    status_rows, qc_rows = [], []
    if geno_raw is None or man is None:
        ctx.note("SNP files absent: all variants UNTESTABLE")
        ctx.t["geno"] = pd.DataFrame(columns=["pid"])
        for vid, spec in sm["level_a"].items():
            status_rows.append(dict(variant=vid, gene=spec["gene"], status="UNTESTABLE", detail="no genotype file"))
        ctx.result("03_snp_status", pd.DataFrame(status_rows))
        return
    mc = vm["snp_manifest_columns"]
    man = man.rename(columns={v: k for k, v in mc.items()})
    man["pos"] = pd.to_numeric(man["pos"], errors="coerce")
    man = man.set_index("rsid")
    geno_raw = geno_raw.set_index(idc)
    q = sm["qc"]
    dos, qc = {}, {}
    for rs in man.index:
        if rs not in geno_raw.columns:
            continue
        ref, alt = man.at[rs, "ref"], man.at[rs, "alt"]
        effect = eff.at[rs, "effect_allele"] if rs in eff.index and isinstance(eff.at[rs, "effect_allele"], str) else alt
        d = effect_dosage(geno_raw[rs], ref, alt, effect)
        dos[rs] = d
        qc[rs] = snp_qc(d, q)
        qc_rows.append(dict(rsid=rs, gene=man.at[rs, "gene"], coded_allele=effect, **qc[rs]))
    ok = {rs for rs, v in qc.items() if v["qc_pass"]}
    out = pd.DataFrame(index=geno_raw.index)
    used = set()
    for vid, spec in sm["level_a"].items():
        if spec["type"] == "haplotype":
            snps = spec["snps"]
            if all(s in ok for s in snps):
                G = np.column_stack([dos[s].values for s in snps])
                pav, other, freqs = em_pav_dosage(G, spec["min_posterior"])
                out[vid] = pav
                out[vid + "_other_haplotype"] = other
                status_rows.append(dict(variant=vid, gene=spec["gene"], status="DIRECTLY TESTABLE", detail=
                                        "EM diplotype; missing(non-PAV/AVI or low posterior)=%.4f; hap freq PAV=%.3f AVI=%.3f" %
                                        (np.isnan(pav).mean(), freqs["111"], freqs["000"]), snps=";".join(snps)))
                used |= set(snps)
                if spec["fallback"]["rsid"] in ok:
                    out[vid + "__A49P"] = dos[spec["fallback"]["rsid"]].values
            elif spec["fallback"]["rsid"] in ok:
                fb = spec["fallback"]["rsid"]
                out[vid] = dos[fb].values
                status_rows.append(dict(variant=vid, gene=spec["gene"], status=spec["fallback"]["status"],
                                        detail=spec["fallback"]["label"] + " (PAV/AVI label not claimed)", snps=fb))
                used.add(fb)
            else:
                status_rows.append(gene_level_or_untestable(vid, spec["gene"], man, ok))
        else:
            rs = spec["rsid"]
            if rs in ok:
                out[vid] = dos[rs].values
                status_rows.append(dict(variant=vid, gene=spec["gene"], status="DIRECTLY TESTABLE", detail="", snps=rs))
                used.add(rs)
                continue
            prox = choose_proxy(rs, spec, man, dos, ok, sm["proxy"]["window_bp"], eff)
            if prox:
                prs, r2, r = prox
                d = dos[prs] if r > 0 else 2 - dos[prs]
                out[vid] = d.values
                status_rows.append(dict(variant=vid, gene=spec["gene"], status="TESTABLE WITH PRE-SPECIFIED PROXY",
                                        detail=f"proxy {prs} r2={r2:.3f} (within-sample, genotype-only)", snps=prs))
                used.add(prs)
            else:
                status_rows.append(gene_level_or_untestable(vid, spec["gene"], man, ok))
    for vid, spec in sm["amendment_only"].items():
        status_rows.append(dict(variant=vid, gene=spec["gene"], status="REQUIRES PROTOCOL AMENDMENT (not analysed)",
                                detail="outside approved 20-gene universe", snps=spec.get("rsid") or ""))
    approved = set(sm["approved_genes"])
    lb = []
    for rs in sorted(ok - used):
        g = annotate_gene(rs, man, regions, approved)
        if g:
            out["B__" + g + "__" + rs] = dos[rs].values
            lb.append(dict(rsid=rs, gene=g))
    out.index.name = "pid"
    geno = out.reset_index()
    ctx.t["geno"] = geno
    ctx.t["level_b"] = pd.DataFrame(lb, columns=["rsid", "gene"])
    ctx.work("03_genotypes", geno)
    ctx.result("03_snp_status", pd.DataFrame(status_rows))
    ctx.result("03_snp_qc", pd.DataFrame(qc_rows))
    ctx.result("03_level_b_snps", ctx.t["level_b"])


def annotate_gene(rs, man, regions, approved):
    g = str(man.at[rs, "gene"]) if "gene" in man.columns else ""
    if g in approved:
        return g
    build = str(man.at[rs, "build"]) if "build" in man.columns else "GRCh38"
    build = "GRCh37" if "37" in build or "19" in build else "GRCh38"
    r = regions[(regions["build"] == build) & (regions["chrom"].astype(str) == str(man.at[rs, "chrom"]).replace("chr", ""))]
    pos = man.at[rs, "pos"]
    hit = r[(r["region_start"] <= pos) & (r["region_end"] >= pos)]
    hit = hit[hit["gene"].isin(approved)]
    return hit["gene"].iloc[0] if len(hit) else None


def choose_proxy(rs, spec, man, dos, ok, window, eff):
    if rs not in eff.index:
        return None
    chrom, pos = str(eff.at[rs, "chrom"]), eff.at[rs, "pos_grch38"]
    target = dos.get(rs)
    if target is None or target.notna().sum() < 100:
        return None  # r2 cannot be estimated without the target genotype; untested proxy is not allowed
    cands = []
    for c in ok:
        if str(man.at[c, "chrom"]).replace("chr", "") != chrom or abs(man.at[c, "pos"] - pos) > window:
            continue
        m = target.notna() & dos[c].notna()
        r = np.corrcoef(target[m], dos[c][m])[0, 1]
        cands.append((r * r, -abs(man.at[c, "pos"] - pos), c, r))
    cands = [x for x in cands if x[0] >= spec["proxy_r2"]]
    if not cands:
        return None
    best = sorted(cands, key=lambda x: (-x[0], -x[1], x[2]))[0]
    return best[2], best[0], best[3]


def gene_level_or_untestable(vid, gene, man, ok):
    has = any(str(man.at[rs, "gene"]) == gene for rs in ok) if "gene" in man.columns else False
    return dict(variant=vid, gene=gene, status="GENE-LEVEL SECONDARY ONLY" if has else "UNTESTABLE",
                detail="frozen variant and proxy unavailable", snps="")
