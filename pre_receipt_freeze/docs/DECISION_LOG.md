# Decision log (final pre-receipt)

Each decision was made before receipt or inspection of any participant-level ToMMo data. Origin: L = carried from legacy freeze; R = required by approved protocol/distribution (reconciliation); P = new pre-receipt decision taken in this session (agent-drafted; requires PI endorsement at signature, `29`). Instruction IDs refer to `INSTRUCTION_REGISTER.csv`.

| ID | Decision | Origin | Instructions | Frozen in | Status |
|---|---|---|---|---|---|
| D01 | Attached plan/application govern; frozen plan valid under the 2026-06-13 revision; C2 promoted to confirmatory (Holm) only if PI records before the independent timestamp that the revision is the approved version | R+P | I003, I026, I062 | 01, 13 | FROZEN (conditional switch, administrative fact) |
| D02 | Primary = longitudinal medication change (Family A drug-specific change-away; Family C general endpoints); current exposure secondary | R | I013, I051, I052 | 06, 14 | FROZEN |
| D03 | P01/P02/P05 outcome = DRUG_SPECIFIC_CHANGE_AWAY among ph1 users (absent at ph2 or dose ratio ≤0.80), covariates + n_rx_ph1 | P | I013, I052, I053 | 06, 14 | FROZEN |
| D04 | Family A = P01, P02, P05 (62 governs over 82/README/LOCK_STATUS); P10 separate and amendment-required | L+R | I007, I008 | 13, AMENDMENT_LOG AM04 | FROZEN |
| D05 | C1–C5 = legacy 25 definitions (bound by 67 and parser vocabulary); 72 labels not executed | P | I042, I008 | 11, AM05 | FROZEN |
| D06 | GR1: G = TAS2R38 PAV dosage; E = EX0–EX3 ordinal; Y = row-level change-away; rows = ph1 Rx bitter-ligand ingredients (BitterDB extract), inhaled excluded; GEE logit by participant; estimand β3 > 0 | L+P | I042 | 11 | FROZEN |
| D07 | Calibration requires ≥5 tested in-scope predictions; else UNDEFINED | P | I011, I055 | 12, AM06 | FROZEN |
| D08 | Covariates (primary/minimal lists); no ancestry PCs (not derivable); family-clustered SE else HC1 | R+P | I045, I046, I053 | 14, AM07 | FROZEN |
| D09 | FFQ lock F01–F08 (items verified in distribution specification; ph1 primary, ph2 replication; no change scores) | P | I014, I043, I044 | 09 | FROZEN |
| D10 | Identification hierarchy Drug ID > KEDD ID > free text; KEGG ATC br08303 snapshot (hash-guarded); same class = ATC level 4 | R+P | I015, I033, I034, I041 | 08 | FROZEN |
| D11 | Dose: mg for mass, same-unit only for count/volume, no imputation; thresholds ≥1.25 / ≤0.80 | P | I038, I040 | 07 | FROZEN |
| D12 | Testability floors: ≥200 exposed, ≥20 events and non-events (legacy 73) | L | I030 | 14 | FROZEN |
| D13 | Control failure = p<0.05 in paired-prediction sign; zero failures required; failure → pattern C | P | I050 | 10 | FROZEN |
| D14 | Formulation module requires real-string parser gate (≥95%, 300–500 strings, blind) and ≥70% EX coverage | L+P | I042 | 11 | FROZEN |
| D15 | Not in plan: GWAS, claims, external validation, survival, metabolomics, tolerance models; ML secondary only | R | I016, I032, I047, I056, I057 | 14, 15, 24 | FROZEN |
| D16 | Population: both waves, age ≥20, genotype QC pass; missing phase excluded, never imputed | R | I013, I035 | 06, 14 | FROZEN |
| D17 | Medication scope: prescription rows with resolved ingredient; OTC/supplements only S11/N12 | P | I033 | 06 | FROZEN |
| D18 | Effect alleles on GRCh38 forward strand from frozen Ensembl VEP snapshot (rs713598 G, rs1726866 G, rs10246939 C → PAV; rs3741845 G → 187A; rs12033832 G) | P | I029, I031 | 05 | FROZEN (independent check recommended, `29`) |
| D19 | Proxy: only within-sample r² ≥ 0.80 within ±250 kb, genotype-only, deterministic tie-break; target absent with no proxy → gene-level secondary only or untestable | P | I030, I031 | 05 | FROZEN |
| D20 | All prediction signs +1 (effect allele increases change-away) from 13 predicted_direction | L | I050 | 12 | FROZEN |
| D21 | Seeds and resampling: seed 42; 10,000 permutations; 2,000 bootstraps; 20 imputations; 5×3 nested CV | L+P | I058, R03 | analysis_config.yaml | FROZEN |
| D22 | Interpretation by legacy 85 pattern rule A–E | L | I066, I067 | 14, 25 | FROZEN |
| D23 | Real-mode staging: qc → lock → sign-off → analysis, hash-checked | P | I012, I065, I071 | 16, 23 | FROZEN |
| D24 | Public/restricted separation; restricted sources only as hashes; third-party raw downloads excluded from public mirror | R | I063, R02 | 20, 22 | FROZEN |
