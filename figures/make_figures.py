"""Plot Figures 2, 3, 4C-F and S2 from the analysis outputs.

Figure 1 / S1 (surface coherence maps and time courses) were produced in mrVista
and are not regenerated here; Figure 4A-B are schematics.

Usage: python figures/make_figures.py --coherence DataS1_phase_specified_coherence.csv
Figures whose inputs are missing are skipped.
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from coherence.coherence_stats import load as load_coherence  # noqa: E402

COHERENCE_ROIS = {"tactile": ["S1", "V1", "V2", "V3", "hV4", "TO-1", "FEF"],
                  "auditory": ["A1/2", "V1", "V2", "V3", "hV4", "TO-1", "FEF"]}


def ci95(x):
    x = np.asarray(x, float)
    return stats.t.ppf(0.975, len(x) - 1) * stats.sem(x)


def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.out("figures", f"{name}.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {name}")


def figure2(path):
    df = load_coherence(path)
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharey=True)
    for col, modality in enumerate(["tactile", "auditory"]):
        rois = COHERENCE_ROIS[modality]
        for row, group in enumerate(["Blind", "Control"]):
            ax = axes[row, col]
            sub = df[(df.modality == modality) & (df.group == group)]
            for i, roi in enumerate(rois):
                r = sub[sub.ROI == roi]
                for dx, cond, face in [(-0.15, "PS", "white"), (0.15, "OBT", "black")]:
                    ax.scatter(np.full(len(r), i + dx), r[cond], s=8, color="0.6", zorder=1)
                    ax.errorbar(i + dx, r[cond].mean(), yerr=ci95(r[cond]), fmt="o", color="black",
                                mfc=face, ms=6, capsize=2, zorder=2)
                p = stats.ttest_rel(r["OBT"], r["PS"]).pvalue
                ax.text(i, 0.85, stars(p), ha="center")
            ax.axhline(0, color="0.5", lw=0.8, ls="--")
            ax.set_xticks(range(len(rois)), rois)
            ax.set_ylim(-0.4, 0.95)
            if col == 0:
                ax.set_ylabel(f"{group}\nPhase-specified coherence")
            if row == 0:
                ax.set_title(f"{'AB'[col]}  {modality.capitalize()}", loc="left")
    save(fig, "Figure2_coherence")


def figure3(path):
    df = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(4, 3.5))
    for i, roi in enumerate(config.RSA_ROIS):
        z = df.loc[df.ROI == roi, "fisher_z"].dropna().to_numpy()
        ax.scatter(np.full(len(z), i) + np.linspace(-0.15, 0.15, len(z)), np.tanh(z), s=12, color="0.6")
        half = ci95(z)
        m = np.tanh(z.mean())
        ax.errorbar(i + 0.3, m, yerr=[[m - np.tanh(z.mean() - half)], [np.tanh(z.mean() + half) - m]],
                    fmt="o", color="black", capsize=3)
        if roi == "V1":
            ax.text(i + 0.3, 1.0, stars(stats.ttest_1samp(z, 0).pvalue), ha="center")
    ax.axhline(0, color="0.5", ls="--", lw=0.8)
    ax.set_xticks(range(len(config.RSA_ROIS)), config.RSA_ROIS)
    ax.set_ylabel("Cross-modal similarity (Pearson r)")
    ax.set_ylim(-0.4, 1.05)
    save(fig, "Figure3_crossmodal_rsa")


def figure4(path):
    df = pd.read_csv(path)
    panels = [("C", "auditory", "OBT"), ("D", "auditory", "PS"), ("E", "tactile", "OBT"), ("F", "tactile", "PS")]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3), sharey=True)
    for ax, (letter, modality, condition) in zip(axes, panels):
        for gi, group in enumerate(["Blind", "Control"]):
            for fi, (family, shade) in enumerate([("Sensory-input", "0.8"), ("FEF-input", "0.35")]):
                g = df[(df.modality == modality) & (df.condition == condition) &
                       (df.group == group) & (df.family == family)]["g_nk"]
                x = gi + (fi - 0.5) * 0.35
                ax.bar(x, g.mean(), 0.35, yerr=stats.sem(g), color=shade, edgecolor="black", capsize=2)
                ax.scatter(np.full(len(g), x), g, s=8, color="red", zorder=3)
        ax.set_xticks([0, 1], ["Blind", "Control"])
        ax.set_title(f"{letter}  {modality.capitalize()} {condition}", loc="left")
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("Participant-level posterior probability")
    save(fig, "Figure4CF_family_bms")


def figure_s2(path):
    df = pd.read_csv(path)
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharey=True)
    for col, modality in enumerate(["tactile", "auditory"]):
        for row, group in enumerate(["Blind", "Control"]):
            ax = axes[row, col]
            sub = df[(df.modality == modality) & (df.group == group)]
            rois = list(dict.fromkeys(sub.ROI))
            for i, roi in enumerate(rois):
                d = sub.loc[sub.ROI == roi, "cohens_d"].dropna()
                ax.bar(i, d.mean(), 0.6, yerr=stats.sem(d), color="0.7", edgecolor="black", capsize=2)
                ax.scatter(np.full(len(d), i), d, s=8, color="black", zorder=3)
            ax.axhline(0, color="0.5", lw=0.8)
            ax.set_xticks(range(len(rois)), rois)
            ax.set_title(f"{modality.capitalize()} - {group}", loc="left")
            if col == 0:
                ax.set_ylabel("Cohen's d (OBT - PS)")
    save(fig, "FigureS2_glm_effect_size")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coherence", help="Data S1 phase-specified coherence (CSV)")
    args = parser.parse_args()
    out = config.OUTPUT_DIR
    if args.coherence:
        figure2(args.coherence)
    for fn, path in [(figure3, out / "rsa" / "rsa_participant_values.csv"),
                     (figure4, out / "dcm" / "participant_family_gnk.csv"),
                     (figure_s2, out / "glm" / "participant_roi_cohens_d.csv")]:
        if path.exists():
            fn(path)
        else:
            print(f"skipped {fn.__name__}: {path} not found")


if __name__ == "__main__":
    main()
