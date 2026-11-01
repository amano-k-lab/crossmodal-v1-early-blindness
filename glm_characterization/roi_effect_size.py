"""GLM-based characterisation of the DCM nodes (Figure S2, Table S6).

For each participant and modality, a voxel-wise Cohen's d for OBT > PS is computed
from the GLMsingle block betas of all runs:

    d = (mean_OBT - mean_PS) / sqrt(((n_OBT - 1) s2_OBT + (n_PS - 1) s2_PS) / (n_OBT + n_PS - 2))

d is averaged within each DCM node (same masks as the DCM: V1, IOG, SOG, IPS, FEF
and S1 or A1/2), using voxels inside the fMRIPrep coverage masks. Group means are
tested against zero with exploratory one-sample t-tests; p values are
Benjamini-Hochberg corrected across ROIs within each modality x group.

Outputs (OUTPUT_DIR/glm/): participant_roi_cohens_d.csv, table_S6_roi_effect_size.csv
"""
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
import roi_utils  # noqa: E402

ROI_ORDER = ["V1", "IOG", "SOG", "IPS", "FEF", "sensory"]


def block_betas(subject, task):
    imgs = [nib.load(config.OUTPUT_DIR / "betas" / subject / task / f"beta_run-{i:02d}.nii.gz")
            for i in range(1, len(config.bold_runs(subject, task)) + 1)]
    return np.concatenate([im.get_fdata() for im in imgs], axis=3), imgs[0]


def cohens_d(subject, modality):
    obt, ref = block_betas(subject, config.TASK_LABEL[modality, "OBT"])
    ps, _ = block_betas(subject, config.TASK_LABEL[modality, "PS"])
    n1, n2 = obt.shape[3], ps.shape[3]
    pooled = ((n1 - 1) * obt.var(axis=3, ddof=1) + (n2 - 1) * ps.var(axis=3, ddof=1)) / (n1 + n2 - 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        d = (obt.mean(axis=3) - ps.mean(axis=3)) / np.sqrt(pooled)
    nib.save(nib.Nifti1Image(d.astype(np.float32), ref.affine),
             config.out("glm", "cohens_d", f"{subject}_{modality}_OBT_vs_PS_cohens_d.nii.gz"))
    return d, ref


def summarise(values):
    x = values.dropna().to_numpy()
    n, mean, sem = len(x), x.mean(), stats.sem(x)
    t, p = stats.ttest_1samp(x, 0.0)
    half = stats.t.ppf(0.975, n - 1) * sem
    return pd.Series({"n": n, "mean_d": mean, "SEM": sem, "CI_low": mean - half,
                      "CI_high": mean + half, "t": t, "p": p})


def main():
    rows = []
    for group, subjects in config.GROUPS.items():
        for subject in subjects:
            for modality in config.MODALITIES:
                d, ref = cohens_d(subject, modality)
                for roi in ROI_ORDER:
                    name = config.SENSORY_ROI[modality] if roi == "sensory" else roi
                    vals = d[roi_utils.roi_mask(name, ref)]
                    vals = vals[np.isfinite(vals)]   # voxels inside the coverage masks
                    rows.append({"modality": modality, "group": group,
                                 "participant": config.LABELS[subject], "ROI": name,
                                 "cohens_d": vals.mean() if vals.size else np.nan})
    indiv = pd.DataFrame(rows)
    indiv.to_csv(config.out("glm", "participant_roi_cohens_d.csv"), index=False)

    table = (indiv.groupby(["modality", "group", "ROI"], sort=False)["cohens_d"]
             .apply(summarise).unstack().reset_index())
    table["p_FDR"] = table.groupby(["modality", "group"])["p"].transform(
        lambda p: multipletests(p, method="fdr_bh")[1])
    table.to_csv(config.out("glm", "table_S6_roi_effect_size.csv"), index=False)
    print(table.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
