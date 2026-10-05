# 77 — Primary causal DAGs (frozen)

Text DAGs for the primary tests. Arrow = directed causal assumption.
All downstream nodes in the chemosensory chain are latent in the data
(no sensory phenotype is collected).

## DAG-1 — Directional prediction (e.g. P02: TAS2R38 → methimazole exposure/formulation)

```
genotype (TAS2R38 PAV dosage)
   │
   ├─► [S1: bitterness perception]  (LATENT — unmeasured)
   │        │
   │        ▼
   │   [sensory-driven medication behavior]  (LATENT)
   │        │
   │        ▼
   │   medication exposure / formulation class  ◄── observed outcome
   │
   ▼ (potential non-sensory pleiotropic paths — assumed absent,
      checked by negative controls N01–N12)
   other outcomes

age ─► indication ─► exposure        (indication confounding)
sex ─► exposure
health behavior (smoking, alcohol, FFQ) ─► exposure
wave ─► exposure
```

Tested path: genotype → exposure/formulation class, through the latent
sensory node. The sensory node being unmeasured is exactly why this study
can only test the population-level signature of the chain, not the chain
itself.

## DAG-2 — Negative-control logic

```
genotype ──?──► non-oral exposure (EX0)   expected: NULL
genotype ──?──► masked oral exposure (EX1) expected: NULL/attenuated
genotype X (mismatched receptor) ──?──► ligand of receptor Y  expected: NULL
```

A positive result on any EX0/route control breaks the sensory-channel
interpretation → interpretation matrix pattern C/D (`85`).

## DAG-3 — Indication-confounding control via formulation contrast

```
indication ─► drug prescribed ─► formulation options {EX3 | EX1}
                                        ▲
genotype ─► [latent sensory] ───────────┘
```

Within a drug and indication, the formulation contrast (C1–C5) holds
indication constant: any residual association isolates the
taste-relevant channel from indication selection. Residual confounders:
age, sex, swallowing difficulty (unmeasured — acknowledged limitation).

## DAG-4 — Behavioral confounding (N12 guard)

```
health-consciousness (LATENT) ─► supplement use
health-consciousness (LATENT) ─► medication behavior
genotype ──?──► supplement use   expected: NULL
```

A positive genotype → supplement-use association would indicate general
behavioral drift rather than a sensory channel → pattern D.
