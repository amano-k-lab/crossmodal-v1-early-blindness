"""Group statistics for the cross-modal RSA (Figure 3, Table S4).

Fisher z values are tested against zero with two-tailed one-sample t-tests across
the six blind participants (V1 = a priori primary ROI; FEF, A1/2 and S1 =
secondary/exploratory). Group means and 95% CIs are computed on z and transformed
back to r for reporting. An exact two-sided sign test is also reported.

Usage: python rsa/rsa_stats.py [--input OUTPUT_DIR/rsa/rsa_participant_values.csv]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=config.OUTPUT_DIR / "rsa" / "rsa_participant_values.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.input)

    rows = []
    for roi in config.RSA_ROIS:
        z = df.loc[df.ROI == roi, "fisher_z"].dropna().to_numpy()
        n = len(z)
        t, p = stats.ttest_1samp(z, 0.0)
        half = stats.t.ppf(0.975, n - 1) * stats.sem(z)
        n_pos = int((z > 0).sum())
        rows.append({"ROI": roi, "n": n, "mean_r": np.tanh(z.mean()),
                     "CI_low_r": np.tanh(z.mean() - half), "CI_high_r": np.tanh(z.mean() + half),
                     "mean_z": z.mean(), "t": t, "p": p, "n_positive": n_pos,
                     "sign_test_p": stats.binomtest(n_pos, n, 0.5).pvalue})
    table = pd.DataFrame(rows)
    wide = df.pivot(index="participant", columns="ROI", values="r")[config.RSA_ROIS]

    table.to_csv(config.out("rsa", "table_S4_rsa_stats.csv"), index=False)
    wide.to_csv(config.out("rsa", "table_S4_participant_r.csv"))
    print(wide.round(3).to_string())
    print()
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
