# 64 — Genotype Proxy Freeze

Rules (frozen):

1. A proxy may replace a frozen variant ONLY if the need is identified
   before any genotype–outcome inspection.
2. LD established on an **East Asian / Japanese reference panel**
   (1000 Genomes JPT phase-3, or ToMMo-internal reference if supplied
   as metadata).
3. Minimum r² threshold: **r² ≥ 0.8** (preferred ≥ 0.9). Below → the
   prediction is UNTESTABLE, not weakened.
4. Allele direction harmonized to the literature effect allele before
   use; strand flips logged.
5. The original prediction_id remains identifiable — no silent
   substitution, no opportunistic alternative SNP "that hits".

| target | proxy status | reference | r² floor | note |
|--------|--------------|-----------|----------|------|
| TAS2R38 PAV/AVI haplotype | all 3 component SNPs required; no single-SNP proxy acceptable | JPT | n/a (haplotype) | rs713598 alone is an accepted *biological* shorthand only when documented as A49P proxy |
| TAS2R9 rs3741845 (V187A) | allowed | JPT | 0.8 | candidate proxies frozen only from EAS LD catalog at implementation |
| TAS2R19 rs10772420 | allowed | JPT | 0.9 | chr12 TAS2R cluster; prefer direct |
| TRPA1 rs11988795 | allowed | JPT | 0.9 | prefer direct |
| TAS1R2 rs12033832 | allowed | JPT | 0.9 | prefer direct |
| TAS2R4 compensatory variant | **UNRESOLVED** — no proxy permitted until the rsID itself is anchored | — | — | prediction P10 stays secondary |
