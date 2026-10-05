#!/usr/bin/env python3
"""Provisional Nature-style figures 1-7 (draft quality, dry phase)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

def box(ax, x, y, w, h, text, fc="#eef4ff", ec="#335"):
    ax.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                 fc=fc, ec=ec, lw=1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8)

def arrow(ax, x1, y1, x2, y2, style="->", ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, lw=1.4, color="#335", linestyle=ls))

# ---------- Figure 1: conceptual framework ----------
fig, ax = plt.subplots(figsize=(7.2, 4.2)); ax.axis("off")
box(ax, .03, .55, .27, .3, "Ancient chemical sensing\n(chemosensory receptors:\nTAS1R / TAS2R / ENaC / OTOP1)")
box(ax, .03, .1, .27, .3, "Inherited variation\n(151 coding haplotypes;\nbalancing selection at TAS2R38)", "#fdf3e7")
box(ax, .4, .55, .27, .3, "Evolutionarily novel\nexposures: modern\noral medicines")
box(ax, .72, .55, .26, .3, "Sensory phenotype (S1):\nbitterness, irritation,\npalatability")
box(ax, .72, .1, .26, .3, "Behavior (S2):\nacceptance, refusal,\nformulation choice", "#eef9ee")
box(ax, .4, .1, .27, .3, "Environment / training\n(diet, repeated exposure)\n-> ΔS1", "#f9eef7")
arrow(ax, .30, .7, .40, .7); arrow(ax, .67, .7, .72, .7)
arrow(ax, .85, .55, .85, .40); arrow(ax, .30, .25, .40, .25)
arrow(ax, .67, .25, .72, .25); arrow(ax, .16, .4, .16, .55)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("Figure 1. Conceptual framework: ancient chemical sensing meets modern medicines")
fig.savefig(FIG / "fig1_conceptual.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 2: genotype->S1 architecture summary ----------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
v = pd.read_csv(ROOT / "04_VARIANT_EVIDENCE.csv")
v["strong"] = ~v.layer.str.contains("NEG")
counts = v.groupby(["gene", "strong"]).size().unstack(fill_value=0)
counts["total"] = counts.sum(1)
counts = counts.sort_values("total", ascending=True)
y = np.arange(len(counts))
ax.barh(y, counts.get(True, 0), color="#3b6ea5", label="supporting association")
ax.barh(y, -counts.get(False, 0), color="#c0504d", label="null/caution")
ax.set_yticks(y, counts.index)
ax.axvline(0, color="k", lw=.8)
ax.set_xlabel("curated evidence records (n)")
ax.set_title("Figure 2. Human genotype->S1 architecture: curated records by gene")
ax.legend(loc="lower right", fontsize=8)
fig.savefig(FIG / "fig2_genotype_s1.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 3: drug space + receptor matrix ----------
fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.4))
d = pd.read_csv(ROOT / "prediction" / "drug_chemical_space.csv")
b = pd.read_csv(ROOT / "evidence" / "bitterdb_receptor_ligands.csv")
import re
norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
b["n"] = b.compound_name.map(norm); d["n"] = d.generic_name.map(norm)
m = d.merge(b, on="n")
ax = axes[0]
ax.scatter(d.xlogp, d.tpsa, s=18, c="#bbb", alpha=.5, label="all oral drugs")
ax.scatter(m.drop_duplicates("generic_name").xlogp, m.drop_duplicates("generic_name").tpsa,
           s=30, c="#c0504d", label="BitterDB TAS2R agonist")
ax.set_xlabel("XLogP"); ax.set_ylabel("TPSA"); ax.legend(fontsize=8)
ax.set_title("Drug chemical space")
ax = axes[1]
counts = m.groupby("receptor").generic_name.nunique().sort_values(ascending=True)
ax.barh(np.arange(len(counts)), counts.values, color="#3b6ea5")
ax.set_yticks(np.arange(len(counts)), counts.index, fontsize=7)
ax.set_xlabel("drugs in our list hitting receptor")
ax.set_title("Known drug->receptor edges")
fig.suptitle("Figure 3. Drug chemosensory chemical space and receptor-drug matrix")
fig.savefig(FIG / "fig3_drug_space_matrix.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 4: locked predictions ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
p = pd.read_csv(ROOT / "13_LOCKED_PREDICTIONS.csv")
mag = {"large": 3, "moderate": 2, "small": 1, "small-moderate": 1.5, "unknown/null": 0.3,
       "null": 0, "null-small": 0.3}
col = {"1": "#2a7a2a", "2": "#3b6ea5", "3": "#b08a00", "4 (negative control)": "#888"}
y = np.arange(len(p))
ax.scatter(p.magnitude.map(mag), y, s=90,
           c=[col[t] for t in p["tier"]], zorder=3)
ax.set_yticks(y, [f"{r.variant[:28]} -> {r.drug[:28]}" for r in p.itertuples()], fontsize=7)
ax.set_xlabel("predicted magnitude category")
ax.set_title("Figure 4. Locked variant-specific drug-response predictions (frozen)")
for t, c in col.items():
    ax.scatter([], [], c=c, label=f"Tier {t}")
ax.legend(fontsize=7, loc="lower right")
fig.savefig(FIG / "fig4_locked_predictions.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 5: plasticity evidence ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
pl = pd.read_csv(ROOT / "06_PLASTICITY_EVIDENCE.csv")
direction = []
for _, r in pl.iterrows():
    txt = (str(r.effect) + str(r.outcome)).lower()
    if "null" in txt or "no change" in txt or "unchanged" in txt:
        direction.append(-1)
    else:
        direction.append(1)
pl["dir"] = direction
y = np.arange(len(pl))
ax.scatter(pl["dir"], y, s=80, c=["#c0504d" if x < 0 else "#3b6ea5" for x in pl["dir"]])
ax.set_yticks(y, [f"{r.intervention[:44]} ({r.population})" for r in pl.itertuples()], fontsize=6.5)
ax.set_xlim(-1.6, 1.6); ax.axvline(0, color="k", lw=.8)
ax.set_xticks([-1, 1], ["no S1 shift / null", "plasticity signal"])
ax.set_title("Figure 5. Adult sensory plasticity: direction of evidence")
fig.savefig(FIG / "fig5_plasticity.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 6: future validation model ----------
fig, ax = plt.subplots(figsize=(7.2, 4.0)); ax.axis("off")
box(ax, .02, .6, .2, .25, "Genotype\n(TAS2R haplotypes)")
box(ax, .40, .6, .22, .25, "Drug chemical property\n(receptor agonism,\noral exposure)")
box(ax, .76, .6, .22, .25, "Outcome\n(formulation use,\nrejection, choice)")
box(ax, .40, .12, .22, .25, "G x drug interaction\n(beta_3: key test)", "#fdf3e7")
box(ax, .02, .12, .2, .25, "Covariates:\nage, sex, ancestry PCs,\nindication, smoking,\nalcohol, diet", "#eee")
arrow(ax, .22, .72, .40, .72); arrow(ax, .62, .72, .76, .72)
arrow(ax, .51, .37, .60, .60); arrow(ax, .12, .37, .40, .60)
ax.text(.5, .04, "Pre-specified predictions only; no indiscriminate gene-drug scans. ToMMo data NOT accessed.",
        ha="center", fontsize=8, color="#800")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("Figure 6. Locked predictions -> future population validation (FUTURE, not executed)")
fig.savefig(FIG / "fig6_future_validation.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure 7: intervention model (future) ----------
fig, ax = plt.subplots(figsize=(7.2, 4.0)); ax.axis("off")
box(ax, .02, .55, .24, .3, "Genotype-stratified\nrandomization\n(bitter-sensitive vs not)")
box(ax, .38, .55, .26, .3, "Sensory conditioning\n(repeated exposure /\ndietary training)", "#eef9ee")
box(ax, .76, .55, .22, .3, "Delta S1 ->\nDelta S2\n(acceptability of\nvalidated surrogate)", "#f9eef7")
box(ax, .38, .1, .26, .25, "Mediation test:\nintervention -> DeltaS1 ->\nDeltaS2; genotype as\nmodifier", "#fdf3e7")
arrow(ax, .26, .7, .38, .7); arrow(ax, .64, .7, .76, .7)
arrow(ax, .51, .35, .51, .55)
ax.text(.5, .03, "FUTURE trial only - never performed in this phase; surrogate endpoints, no therapeutic-drug exposure in healthy volunteers.",
        ha="center", fontsize=7.5, color="#800")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("Figure 7. Future genotype x sensory-training intervention model (FUTURE, not executed)")
fig.savefig(FIG / "fig7_future_trial.png", dpi=200, bbox_inches="tight"); plt.close(fig)

print("figures written:", sorted(x.name for x in FIG.glob("*.png")))
