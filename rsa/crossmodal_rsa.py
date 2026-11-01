"""Cross-modal similarity of task-evoked spatial patterns (Figure 3, Table S4).

For each blind participant:
  1. GLMsingle block betas are averaged across blocks within each run, then across
     runs, giving one mean beta map per modality x condition.
  2. Task-related maps: OBT - PS, separately for tactile and auditory.
  3. Maps and masks are brought to a common 2-mm MNI152 grid (betas: linear,
     masks: nearest neighbour).
  4. Within each ROI (V1, FEF, A1/2, S1) the voxels that are inside the fMRIPrep
     coverage masks of every tactile and auditory run are vectorised, and the
     tactile and auditory OBT - PS patterns are correlated (Pearson r; no
     effect-size thresholding). r is Fisher z-transformed for group statistics.
     A participant whose ROI is not covered in both modalities is missing for it.

Output: OUTPUT_DIR/rsa/rsa_participant_values.csv
"""
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn.image import resample_img

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
import roi_utils  # noqa: E402

GRID = (config.COMMON_GRID_SHAPE, config.COMMON_GRID_AFFINE)


def to_grid(data, affine, interpolation):
    img = resample_img(nib.Nifti1Image(data, affine), target_affine=config.COMMON_GRID_AFFINE,
                       target_shape=config.COMMON_GRID_SHAPE, interpolation=interpolation)
    return img.get_fdata()


def mean_beta_and_coverage(subject, task):
    """Mean beta map (blocks, then runs) and the intersection of the run coverage masks."""
    run_means, coverage = [], np.ones(config.COMMON_GRID_SHAPE, bool)
    for i, bold in enumerate(config.bold_runs(subject, task), start=1):
        img = nib.load(config.OUTPUT_DIR / "betas" / subject / task / f"beta_run-{i:02d}.nii.gz")
        run_mean = np.nanmean(img.get_fdata(), axis=3)
        run_means.append(to_grid(np.nan_to_num(run_mean), img.affine, "continuous"))
        coverage &= roi_utils.coverage_mask(bold, GRID)
    return np.mean(run_means, axis=0), coverage


def task_map(subject, modality):
    obt, cov_obt = mean_beta_and_coverage(subject, config.TASK_LABEL[modality, "OBT"])
    ps, cov_ps = mean_beta_and_coverage(subject, config.TASK_LABEL[modality, "PS"])
    contrast = obt - ps
    contrast[~(cov_obt & cov_ps)] = np.nan
    return contrast


def main():
    rows = []
    for subject in config.BLIND:
        tactile, auditory = task_map(subject, "tactile"), task_map(subject, "auditory")
        for roi in config.RSA_ROIS:
            mask = roi_utils.roi_mask(roi, GRID)
            x, y = tactile[mask], auditory[mask]
            valid = np.isfinite(x) & np.isfinite(y)
            # An ROI outside the acquired slab in either modality is treated as missing.
            r = np.corrcoef(x[valid], y[valid])[0, 1] if valid.sum() >= 3 else np.nan
            rows.append({"participant": config.LABELS[subject], "subject": subject, "ROI": roi,
                         "r": r, "fisher_z": np.arctanh(r), "n_voxels": int(valid.sum())})
            print(f"{config.LABELS[subject]} {roi}: r = {r:.3f} ({valid.sum()} voxels)")
    pd.DataFrame(rows).to_csv(config.out("rsa", "rsa_participant_values.csv"), index=False)


if __name__ == "__main__":
    main()
