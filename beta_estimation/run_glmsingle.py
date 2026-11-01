"""Single-block beta estimates with GLMsingle (input to the RSA and Fig. S2 / Table S6).

Each preprocessed run (fMRIPrep, MNI152NLin2009cAsym, 2 mm) is fitted separately,
without spatial smoothing. Every 15-s stimulation block is one "trial" (10 per
run); the six rigid-body motion parameters are included as extra regressors. The
betas of the library-HRF model (GLMsingle type B, FITHRF) are kept. Voxels outside
the run-specific fMRIPrep functional mask are set to NaN.

Output: OUTPUT_DIR/betas/{subject}/{task}/beta_run-XX.nii.gz   (x, y, z, 10 blocks)
"""
import argparse
import os
import sys
import tempfile
from multiprocessing import Pool
from pathlib import Path

for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import nibabel as nib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from glmsingle.glmsingle import GLM_single  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
import roi_utils  # noqa: E402

MOTION = ["trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z"]


def fit_run(job):
    subject, task, run_index, bold_file = job
    img = nib.load(bold_file)
    data = img.get_fdata(dtype=np.float32)
    if data.shape[3] != config.N_VOLUMES:
        raise ValueError(f"{bold_file}: expected {config.N_VOLUMES} volumes")

    design = np.zeros((data.shape[3], 1))
    design[(config.BLOCK_ONSETS / config.TR).astype(int), 0] = 1
    motion = pd.read_csv(config.confounds_for(bold_file), sep="\t")[MOTION].to_numpy()

    opt = {"wantlibrary": 1, "wantglmdenoise": 1, "wantfracridge": 1,
           "wantfileoutputs": [0, 0, 0, 0], "wantmemoryoutputs": [1, 1, 1, 1],
           "extra_regressors": [motion]}
    # No diagnostic figures (figuredir=None); GLMsingle still creates an empty figure
    # folder in the working directory, so each fit runs inside its own temporary dir.
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            results = GLM_single(opt).fit([design], [data], config.BLOCK_DURATION, config.TR,
                                          outputdir=os.path.join(tmp, "glmsingle"))
        finally:
            os.chdir(cwd)
    betas = np.asarray(results["typeb"]["betasmd"], dtype=np.float32).reshape(data.shape[:3] + (-1,))
    betas[~roi_utils.coverage_mask(bold_file)] = np.nan

    path = config.out("betas", subject, task, f"beta_run-{run_index:02d}.nii.gz")
    nib.save(nib.Nifti1Image(betas, img.affine), path)
    return f"{subject} {task} run {run_index}: {betas.shape}"


def safe_fit_run(job):
    try:
        return fit_run(job)
    except Exception as exc:  # report and continue with the other runs
        return f"FAILED {job[:3]}: {exc!r}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", nargs="+", default=config.BLIND + config.CONTROL)
    parser.add_argument("--n-jobs", type=int, default=16)
    args = parser.parse_args()

    jobs = [(s, task, i + 1, str(f)) for s in args.subjects for task in config.TASK_LABEL.values()
            for i, f in enumerate(config.bold_runs(s, task))
            if not (config.OUTPUT_DIR / "betas" / s / task / f"beta_run-{i + 1:02d}.nii.gz").exists()]
    with Pool(args.n_jobs) as pool:
        for msg in pool.imap_unordered(safe_fit_run, jobs):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
