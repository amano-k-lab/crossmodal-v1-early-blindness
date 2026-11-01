"""Extract DCM node time series (Figure 4).

For every participant, modality and condition (PS / OBT), each preprocessed run
(fMRIPrep, MNI152NLin2009cAsym) is smoothed with a 6-mm FWHM Gaussian kernel. No
confound regression or high-pass filtering is applied. A node's time series is the
mean over its constituent Glasser parcels of the parcel-wise mean signal; only voxels
inside the run-specific fMRIPrep functional mask are used. V1 uses the Benson
template mask. Runs of the same condition are concatenated.

If a node lies entirely outside the acquired partial-brain slab in any run of a
participant x modality, that participant is excluded from the DCM for this modality
(logged in OUTPUT_DIR/dcm/excluded.csv).

Output: OUTPUT_DIR/dcm/timeseries/{subject}_{modality}_{condition}.npz
"""
import argparse
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn.image import smooth_img

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
import roi_utils  # noqa: E402


class NoCoverage(Exception):
    pass


def node_timeseries(data, labels, coverage, node, ref):
    if node == "V1":
        voxels = roi_utils.roi_mask("V1", ref) & coverage
        if not voxels.any():
            raise NoCoverage(node)
        return data[voxels].mean(axis=0)
    parcel_means = []
    for label in config.GLASSER_ROIS[node]:
        voxels = (labels == label) & coverage
        if voxels.any():
            parcel_means.append(data[voxels].mean(axis=0))
    if not parcel_means:
        raise NoCoverage(node)
    return np.mean(parcel_means, axis=0)


def extract_run(bold_file, nodes):
    img = smooth_img(str(bold_file), fwhm=config.DCM_SMOOTHING_FWHM)
    data = img.get_fdata(dtype=np.float32)
    if data.shape[3] != config.N_VOLUMES:
        raise ValueError(f"{bold_file}: expected {config.N_VOLUMES} volumes")
    coverage = roi_utils.coverage_mask(bold_file)
    labels = roi_utils.glasser_labels(img)
    return np.column_stack([node_timeseries(data, labels, coverage, n, img) for n in nodes])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", nargs="+", default=config.BLIND + config.CONTROL)
    args = parser.parse_args()

    excluded = []
    for subject in args.subjects:
        for modality in config.MODALITIES:
            nodes = config.DCM_NODES[modality]
            try:
                series = {c: [extract_run(r, nodes)
                              for r in config.bold_runs(subject, config.TASK_LABEL[modality, c])]
                          for c in config.CONDITIONS}
            except NoCoverage as exc:
                excluded.append({"subject": subject, "participant": config.LABELS[subject],
                                 "modality": modality, "node_without_coverage": str(exc)})
                print(f"{subject} {modality}: node {exc} outside the acquired slab -> excluded")
                continue
            for condition, runs in series.items():
                Y = np.vstack(runs)
                path = config.out("dcm", "timeseries", f"{subject}_{modality}_{condition}.npz")
                np.savez(path, Y=Y, nodes=np.array(nodes), n_runs=len(runs))
                print(f"{subject} {modality} {condition}: {len(runs)} run(s), Y {Y.shape}")
    pd.DataFrame(excluded, columns=["subject", "participant", "modality", "node_without_coverage"]
                 ).to_csv(config.out("dcm", "excluded.csv"), index=False)


if __name__ == "__main__":
    main()
