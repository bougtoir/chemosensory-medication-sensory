"""21 figures from aggregate results only: forest plots (A/AS/C) and calibration scatter."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def forest(df, title, path):
    d = df[df["status"] == "TESTED"]
    fig, ax = plt.subplots(figsize=(7, 0.4 * max(len(d), 3) + 1))
    if len(d):
        y = np.arange(len(d))[::-1]
        ax.errorbar(d["beta"], y, xerr=1.96 * d["se"], fmt="o", color="k", capsize=3)
        ax.set_yticks(y)
        ax.set_yticklabels(d["test"])
        ax.axvline(0, color="grey", lw=0.8)
    else:
        ax.text(0.5, 0.5, "no test met testability floors", ha="center", transform=ax.transAxes)
    ax.set_xlabel("log odds ratio per effect allele (95% CI)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run(ctx):
    fd = ctx.out_dir / "figures"
    for name, title in (("12_family_A", "Family A"), ("12_family_AS", "Family AS"), ("14_family_C", "Family C")):
        df = ctx.t.get(f"result:{name}")
        if df is not None:
            forest(df, title, fd / f"21_{name}.png")
    cp = ctx.t.get("result:17_calibration_points")
    if cp is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        d = cp[cp["Z_signed"].notna()]
        ax.scatter(d["evidence_score"], d["Z_signed"], color="k")
        for r in d.itertuples():
            ax.annotate(r.test, (r.evidence_score, r.Z_signed), fontsize=8, xytext=(3, 3), textcoords="offset points")
        ax.axhline(0, color="grey", lw=0.8)
        ax.set_xlabel("frozen evidence score")
        ax.set_ylabel("signed standardized effect Z_i")
        fig.tight_layout()
        fig.savefig(fd / "21_calibration.png", dpi=150)
        plt.close(fig)
