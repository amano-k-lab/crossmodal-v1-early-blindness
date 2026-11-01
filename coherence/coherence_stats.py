"""Statistics on phase-specified coherence (Figure 2, Table S3, main-text values).

Phase-specified coherence values were computed in mrVista (see README); this script
starts from the ROI-level values provided in Data S1 (one row per participant x
modality x condition x ROI). For each modality and ROI it reports:

  * group means (SEM) for PS and OBT;
  * in the blind group, the OBT - PS paired t-test with its 95% CI, Cohen's dz and
    the number of participants with a positive shift; Benjamini-Hochberg FDR across
    ROIs within modality;
  * the Group x Condition interaction of a 2 x 2 mixed ANOVA (Group between,
    Condition within), with partial eta squared and FDR across ROIs. With two
    levels per factor the interaction F equals the squared independent-samples t
    statistic on the OBT - PS differences.

It also prints the V1 one-sample tests against zero quoted in the main text.

Usage: python coherence/coherence_stats.py --input DataS1_phase_specified_coherence.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

COLUMN_ALIASES = {"subject_id": "participant", "phase_specified_coherence": "coherence"}
CONDITION_ALIASES = {"PV": "PS", "passive": "PS"}


def load(path):
    df = pd.read_csv(path).rename(columns=COLUMN_ALIASES)
    df["condition"] = df["condition"].replace(CONDITION_ALIASES)
    return df.pivot_table(index=["group", "modality", "ROI", "participant"],
                          columns="condition", values="coherence").dropna().reset_index()


def mean_ci(x):
    half = stats.t.ppf(0.975, len(x) - 1) * stats.sem(x)
    return x.mean(), x.mean() - half, x.mean() + half


def roi_row(blind, control):
    delta_b = blind["OBT"] - blind["PS"]
    delta_c = control["OBT"] - control["PS"]
    t, p = stats.ttest_rel(blind["OBT"], blind["PS"])
    mean, lo, hi = mean_ci(delta_b)
    t_int, p_int = stats.ttest_ind(delta_b, delta_c)
    df_err = len(delta_b) + len(delta_c) - 2
    F = t_int ** 2
    return {
        "Ctrl_PS": f"{control['PS'].mean():.4f} ({stats.sem(control['PS']):.4f})",
        "Ctrl_OBT": f"{control['OBT'].mean():.4f} ({stats.sem(control['OBT']):.4f})",
        "Blind_PS": f"{blind['PS'].mean():.4f} ({stats.sem(blind['PS']):.4f})",
        "Blind_OBT": f"{blind['OBT'].mean():.4f} ({stats.sem(blind['OBT']):.4f})",
        "delta": mean, "CI_low": lo, "CI_high": hi, "df": len(delta_b) - 1, "t": t, "p": p,
        "dz": delta_b.mean() / delta_b.std(ddof=1),
        "n_positive": f"{int((delta_b > 0).sum())}/{len(delta_b)}",
        "F_int": F, "df_int_err": df_err, "p_int": p_int, "partial_eta2": F / (F + df_err),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Data S1 phase-specified coherence (CSV)")
    args = parser.parse_args()
    df = load(args.input)

    rows = []
    for (modality, roi), sub in df.groupby(["modality", "ROI"]):
        row = roi_row(sub[sub.group == "Blind"], sub[sub.group == "Control"])
        rows.append({"modality": modality, "ROI": roi, **row})
    table = pd.DataFrame(rows)
    for p, q in [("p", "q_FDR"), ("p_int", "q_int_FDR")]:
        table[q] = table.groupby("modality")[p].transform(lambda x: multipletests(x, method="fdr_bh")[1])
    table.to_csv(config.out("coherence", "table_S3_coherence_stats.csv"), index=False)
    print(table.round(4).to_string(index=False))

    print("\nV1 one-sample tests against zero (main text)")
    v1 = df[df.ROI == "V1"]
    for (modality, group), sub in v1.groupby(["modality", "group"]):
        for cond in ["PS", "OBT"]:
            x = sub[cond]
            t, p = stats.ttest_1samp(x, 0.0)
            m, lo, hi = mean_ci(x)
            print(f"  {modality:8s} {group:7s} {cond:3s}: mean = {m:.3f} [{lo:.3f}, {hi:.3f}], "
                  f"t({len(x) - 1}) = {t:.3f}, p = {p:.3f}")
        d = sub["OBT"] - sub["PS"]
        t, p = stats.ttest_rel(sub["OBT"], sub["PS"])
        m, lo, hi = mean_ci(d)
        print(f"  {modality:8s} {group:7s} OBT-PS: mean = {m:.3f} [{lo:.3f}, {hi:.3f}], "
              f"t({len(d) - 1}) = {t:.3f}, p = {p:.3f}, dz = {d.mean() / d.std(ddof=1):.3f}")


if __name__ == "__main__":
    main()
