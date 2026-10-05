#!/usr/bin/env python3
"""Pre-analysis power assessment for the frozen prediction panel.

GENOTYPE-BLIND: uses only ASSUMED parameters (exposure prevalence, genotype
frequency, effect size). No ToMMo or any other individual-level data.
Deterministic seed. Outputs power_assessment.csv.
"""
import numpy as np, csv, os
from scipy.stats import norm

SEED = 42
rng = np.random.default_rng(SEED)

# assumed scenario grid (all assumptions, not observed values)
SCENARIOS = [
    # (label, N, exposure_prev, genotype_freq, OR)
    ("common drug, common variant, modest OR", 50000, 0.05, 0.40, 1.30),
    ("common drug, common variant, small OR", 50000, 0.05, 0.40, 1.15),
    ("uncommon drug, common variant, modest OR", 50000, 0.01, 0.40, 1.30),
    ("uncommon drug, common variant, large OR", 50000, 0.01, 0.40, 1.50),
    ("rare drug, common variant, large OR", 50000, 0.005, 0.40, 1.50),
    ("rare drug, rare variant, large OR", 50000, 0.005, 0.10, 1.50),
    ("common drug, rare variant, large OR", 50000, 0.05, 0.10, 1.50),
    ("EX3-class exposure (aggregate), common variant", 50000, 0.10, 0.40, 1.20),
    ("formulation contrast within-drug (discordant pairs)", 50000, 0.02, 0.40, 1.40),
]

def analytic_power(n, p_exp, p_gen, log_or, alpha=0.05):
    """Approx power for logistic exposure~genotype comparison (Wald).
    Exposure prevalence p_exp; we test exposure rate difference between
    genotype carriers (freq p_gen) vs non-carriers."""
    z = norm.ppf(1 - alpha / 2)
    p0 = p_exp
    p1 = p0 * np.exp(log_or) / (1 - p0 + p0 * np.exp(log_or))  # OR -> risk
    se = np.sqrt(p0*(1-p0)/(n*(1-p_gen)) + p1*(1-p1)/(n*p_gen))
    d = abs(p1 - p0) / se
    return float(norm.cdf(d - z) + norm.cdf(-d - z)), float(p1)

rows = []
for label, N, pe, pg, OR in SCENARIOS:
    power, p1 = analytic_power(N, pe, pg, np.log(OR))
    n_exp = N * pe
    rows.append([label, N, pe, pg, OR, round(n_exp), round(p1, 4), round(power, 3),
                 "ADEQUATE" if power >= 0.8 else ("MARGINAL" if power >= 0.5 else "UNDERPOWERED")])

os.makedirs("build", exist_ok=True)
with open("build/power_assessment.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["scenario", "N", "assumed_exposure_prevalence", "assumed_genotype_freq",
                "assumed_OR", "expected_exposed_n", "exposed_risk_carriers", "power_2sided_a0.05", "verdict"])
    w.writerows(rows)
for r in rows:
    print(f"{r[0]:55s} exp_n={r[5]:>6} power={r[7]:.3f} {r[8]}")
