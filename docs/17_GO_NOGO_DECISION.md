# 17 — GO / NO-GO Decision

## Verdict: **CONDITIONAL GO**

The central biology is credible; one critical link — genotype-dependent
sensory response translating to medication *behavior* in adults — remains
weak. A pre-specified population validation is justified **only** under the
constraints listed below.

## Falsification criteria scorecard

| ID | Trigger | Status | Reason |
|----|---------|--------|--------|
| F1 | No reproducible genotype→S1 | **Not supported** | TAS2R38→PROP/PTC replicated worldwide incl. GWAS (rs713598 P=1.6e-104, 45.9% variance); multiple other loci with functional confirmation |
| F2 | Effects limited to canonical lab tastants | **Partially supported** | Direct drug evidence exists (PROP itself is a drug; chloramphenicol TAS2R38, ofloxacin TAS2R9) but is thin: 1 cohort, plus 1 published null (clindamycin). Cross-domain generalization is the unresolved question, not a resolved failure |
| F3 | Adult S1 fixed; no plasticity | **Partially supported** | Salt preference/thresholds and sweet intensity shift in adults (Bertino 1982/86; Wise 2016); but bitter hedonic plasticity is weak/null (Mattes 1994; low-Na cereal no preference shift 2019; oral rinsing null 2023) |
| F4 | No credible S1→S2 for drugs | **Partially supported** | Pediatric link established (TAS2R38→liquid rejection reports, solid-form usage; antibiotic palatability reviews). Adult medication S1→S2 evidence is sparse — formulation studies concern form/size more than taste |
| F5 | Associations better explained by PK/ancestry/linkage | **Partially supported** | Ancestry effects on ibuprofen perception observed; extraoral T2R pathway is a live competing mechanism; indication confounding unavoidable for medication outcomes — mitigated by embedded negative controls |
| F6 | Isolated candidate-gene reports, no architecture | **Not supported (with flag)** | Mechanistic architecture is coherent (receptor→perception→function), BUT the field is lopsided toward TAS2R38 and older candidate-gene methods — publication bias unquantifiable |
| F7 | Docking-only receptor–drug links | **Not supported** | BitterDB edges are curated experimental assays; computational-only evidence excluded by design |
| F8 | ToMMo outcomes can't separate sensory from adherence/behavior | **Partially supported** | Genuine risk: questionnaire outcomes lack claims data; the β3 genotype×drug-property design + embedded negative controls is the only feasible discriminator |

## Final decision table (0–4; L inverted)

| Domain | Score | Note |
|--------|-------|------|
| A. Human genetic evidence | 4 | locus-level certainty for TAS2R38; broader loci moderate |
| B. Functional receptor evidence | 4 | 23 receptors with curated ligands, 76 drug edges |
| C. Pharmaceutical sensory evidence | 3 | human panels + sensor data; formulation dominates API |
| D. Genotype × pharmaceutical evidence | 2 | 3 direct studies, 1 is null; thin |
| E. Sensory→behavior evidence | 2 | pediatric credible; adult sparse |
| F. Adult sensory plasticity | 2 | real for salt/sweet intensity; weak for bitter hedonic |
| G. Cross-domain generalization | 2 | receptor-level yes; perceptual outcome-level thin |
| H. Evolutionary coherence | 3 | strong substrate; framing stays supportive |
| I. Falsifiability | 4 | frozen predictions + negative controls defined |
| J. Future ToMMo testability | 2 | feasible only via β3 interaction design; no claims data |
| K. Nature-level conceptual breadth | 1 | Levels 1–2 supported; Levels 3–5 aspirational |
| L. Alternative-explanation risk | 3 | ancestry, indication, adherence traits, extraoral T2R pathways are material |

**Critical bottleneck:** domain D/E — whether genotype-dependent drug
perception changes real medication behavior in adults. If ToMMo
questionnaires cannot isolate formulation/taste-linked outcomes, even a
large-N validation cannot resolve the bottleneck.

## Conditions attached to GO

1. Validation restricted to the locked prediction table (file 13); no
   hypothesis updates after seeing population data.
2. Embedded negative controls (non-oral, masked formulations) required;
   positive signals there invalidate the pipeline.
3. β3 genotype×drug-property interaction is the primary estimand, not
   main effects.
4. Claims capped at Levels 1–2 until interventional or replicated
   drug-level evidence exists.
5. If pediatric-style rejection endpoints are unavailable in ToMMo, the
   validation should pivot to formulation-exposure proxies with
   explicit, pre-specified limits on inference.

## What would flip to NO-GO

- ToMMo instruments lack any formulation/taste-linked outcome and
  category-C claims data (→ F8 becomes fully supported).
- Locked-prediction pre-test shows available outcomes cannot distinguish
  sensory from generic adherence behavior.
