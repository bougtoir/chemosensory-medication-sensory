# 65 — TAS2R38 Haplotype Freeze

## Coding unit

The analytical unit is the **PAV/AVI diplotype** built from
rs713598 (A49P), rs1726866 (V262A), rs10246939 (I296V).

## Inference

- Method: unphased three-SNP haplotype calling via standard EM phasing
  (e.g., SHAPEIT/beagle-equivalent); direct trio-free phase acceptable
  because the three SNPs are ~1 kb apart and common.
- Minimum posterior probability: **0.9** per individual; below →
  missing.
- Rare haplotypes (AAI, PVI, AVV, AAI etc.): pooled into
  "other" and reported; NEVER re-merged into PAV/AVI after outcome
  inspection.
- Strand: harmonized to coding-strand bases before haplotyping.

## Primary coding scheme

| code | diplotype |
|------|-----------|
| 2 | PAV/PAV |
| 1 | PAV/AVI |
| 0 | AVI/AVI |

Primary genetic model: **ordinal (0/1/2 PAV dosage)** — frozen.
Secondary descriptive: 3-group categorical. No best-model selection
after outcome inspection.

## Proxy fallback

If phasing is impossible (e.g., one SNP fails), **rs713598 alone** is
the prespecified A49P proxy with coding PAV-copy dosage — flagged as
`READY_WITH_PRESPECIFIED_PROXY` in 63, and the PAV/AVI label must not
be claimed (report as "A49P proxy").
