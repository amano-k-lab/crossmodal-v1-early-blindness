"""Fit the four DCMs to every participant x modality x condition (Figure 4).

Models are inverted with pydcm (Python port of SPM12 r7487 DCM for fMRI;
spm_dcm_estimate, variational Laplace). The negative free energy F is stored as the
approximation to the log model evidence.

Output: OUTPUT_DIR/dcm/free_energy.csv (one row per fitted model) and the
posterior estimates in OUTPUT_DIR/dcm/fits/.
"""
import argparse
import contextlib
import copy
import io
import os
import sys
from multiprocessing import Pool
from pathlib import Path

for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "third_party" / "pydcm"))
import config  # noqa: E402
from dcm import models  # noqa: E402


def estimate(job):
    subject, modality, condition, driving_input, connection = job
    from pydcm.spm.estimation import spm_dcm_estimate
    from pydcm.spm.models import spm_dcm_fmri_priors

    ts = np.load(config.OUTPUT_DIR / "dcm" / "timeseries" / f"{subject}_{modality}_{condition}.npz")
    DCM = models.dcm_structure(ts["Y"], driving_input, connection, config.TR)

    # Start the optimiser from a small positive driving-input weight so that the
    # driven node is not stuck at the prior mean of zero.
    pE, _, _ = spm_dcm_fmri_priors(DCM["a"], DCM["b"], DCM["c"], DCM["d"], DCM["options"])
    P = copy.deepcopy(pE)
    P["C"][DCM["c"] > 0] = 0.01
    DCM["options"]["P"] = P

    with contextlib.redirect_stdout(io.StringIO()):
        fit = spm_dcm_estimate(DCM)

    path = config.out("dcm", "fits", f"{subject}_{modality}_{condition}_{driving_input}_{connection}.npz")
    np.savez(path, F=fit["F"], A=fit["Ep"]["A"], C=fit["Ep"]["C"])
    return {"subject": subject, "group": config.group_of(subject), "modality": modality,
            "condition": condition, "input": driving_input, "connection": connection,
            "F": float(fit["F"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", nargs="+", default=config.BLIND + config.CONTROL)
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count())
    args = parser.parse_args()

    ts_dir = config.OUTPUT_DIR / "dcm" / "timeseries"
    jobs = [(s, m, c, i, a) for s in args.subjects for m in config.MODALITIES
            for c in config.CONDITIONS for i, a in models.MODELS
            if (ts_dir / f"{s}_{m}_{c}.npz").exists()]
    with Pool(args.n_jobs) as pool:
        rows = []
        for row in pool.imap_unordered(estimate, jobs):
            rows.append(row)
            print(f"[{len(rows)}/{len(jobs)}] {row['subject']} {row['modality']} {row['condition']} "
                  f"{row['input']}-{row['connection']}: F = {row['F']:.2f}", flush=True)

    df = pd.DataFrame(rows).sort_values(["group", "subject", "modality", "condition", "input", "connection"])
    df.to_csv(config.out("dcm", "free_energy.csv"), index=False)


if __name__ == "__main__":
    main()
