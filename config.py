"""Shared configuration: paths, participants, task labels, ROI definitions.

All paths can be overridden with environment variables so that the pipeline can
be run on another machine without editing this file:

    FMRIPREP_DIR   fMRIPrep derivatives (contains sub-XXX/func/...)
    ATLAS_DIR      directory holding the atlas files listed below
    OUTPUT_DIR     where every script writes its outputs
"""
import os
from pathlib import Path

import numpy as np

REPO_DIR = Path(__file__).resolve().parent

FMRIPREP_DIR = Path(os.environ.get("FMRIPREP_DIR", REPO_DIR / "data" / "fmriprep"))
ATLAS_DIR = Path(os.environ.get("ATLAS_DIR", REPO_DIR / "atlas" / "files"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", REPO_DIR / "outputs"))

# HCP multi-modal parcellation (Glasser et al., 2016), volumetric MNI version.
# Labels 1-180 = right hemisphere, 181-360 = left hemisphere.
GLASSER_ATLAS = Path(os.environ.get("GLASSER_ATLAS", ATLAS_DIR / "glasser360MNI.nii.gz"))
# Benson et al. (2014) retinotopic template on fsaverage, exported as volumes
# (benson14_{varea,angle,eccen}.mgz). Used to build the V1 mask (atlas/make_v1_mask.py).
BENSON_DIR = Path(os.environ.get("BENSON_DIR", ATLAS_DIR / "benson14_fsaverage"))
V1_MASK = OUTPUT_DIR / "atlas" / "V1_benson14_fsaverage_volume.nii.gz"

# --------------------------------------------------------------------------
# Participants
# --------------------------------------------------------------------------
# Early-blind participants EB1-EB6 and sighted controls C1-C6 (Table S1).
BLIND = ["sub-032", "sub-033", "sub-034", "sub-035", "sub-036", "sub-037"]
CONTROL = ["sub-007", "sub-008", "sub-009", "sub-010", "sub-011", "sub-012"]
GROUPS = {"Blind": BLIND, "Control": CONTROL}
LABELS = {s: f"EB{i + 1}" for i, s in enumerate(BLIND)}
LABELS.update({s: f"C{i + 1}" for i, s in enumerate(CONTROL)})


def group_of(subject):
    return "Blind" if subject in BLIND else "Control"


# --------------------------------------------------------------------------
# Tasks (BIDS task labels) and design
# --------------------------------------------------------------------------
# PS = passive sensing, OBT = one-back task. All runs were acquired with eyes closed.
MODALITIES = ["tactile", "auditory"]
CONDITIONS = ["PS", "OBT"]
TASK_LABEL = {
    ("tactile", "PS"): "tactilepvclosed",
    ("tactile", "OBT"): "tactileobtclosed",
    ("auditory", "PS"): "audiopvclosed",
    ("auditory", "OBT"): "audioobtclosed",
}

TR = 3.0
N_VOLUMES = 100            # volumes per run
BLOCK_ONSETS = np.arange(0, 300, 30.0)   # 10 stimulation blocks per run (s)
BLOCK_DURATION = 15.0      # 15-s ON / 15-s OFF

# Every voxel-wise analysis is carried out in MNI152NLin2009cAsym space.
SPACE = "MNI152NLin2009cAsym"

# Common 2-mm isotropic MNI152 grid used for the RSA (fMRIPrep res-2 field of view).
COMMON_GRID_SHAPE = (77, 95, 82)
COMMON_GRID_AFFINE = np.array([[2.0, 0, 0, -76.0],
                               [0, 2.0, 0, -112.0],
                               [0, 0, 2.0, -76.0],
                               [0, 0, 0, 1.0]])

# --------------------------------------------------------------------------
# ROIs (Glasser parcel indices, right + left hemisphere)
# --------------------------------------------------------------------------
GLASSER_ROIS = {
    "FEF": [10, 190],                      # FEF
    "A1/2": [24, 204],                     # A1 (auditory core)
    "S1": [9, 189],                        # area 3b
    "IOG": [6, 186],                       # V4
    "SOG": [13, 193],                      # V3A
    "IPS": [17, 197,                       # IPS1
            50, 230,                       # MIP
            48, 228,                       # LIPv
            95, 275,                       # LIPd
            117, 297,                      # AIP
            144, 324],                     # IP2
}
# V1 is not a Glasser parcel here: it comes from the Benson template (V1_MASK).

RSA_ROIS = ["V1", "FEF", "A1/2", "S1"]
DCM_NODES = {"tactile": ["V1", "IPS", "FEF", "SOG", "IOG", "S1"],
             "auditory": ["V1", "IPS", "FEF", "SOG", "IOG", "A1/2"]}
SENSORY_ROI = {"tactile": "S1", "auditory": "A1/2"}

DCM_SMOOTHING_FWHM = 6.0   # mm, DCM time series only (RSA/GLM use unsmoothed data)


# --------------------------------------------------------------------------
# File helpers
# --------------------------------------------------------------------------
def bold_runs(subject, task):
    """Preprocessed BOLD runs (MNI152NLin2009cAsym) for one subject/task, sorted by run."""
    func = FMRIPREP_DIR / subject / "func"
    runs = sorted(func.glob(f"{subject}_task-{task}_*space-{SPACE}_desc-preproc_bold.nii.gz"))
    if not runs:
        runs = sorted(func.glob(f"{subject}_task-{task}_space-{SPACE}_desc-preproc_bold.nii.gz"))
    return runs


def brain_mask_for(bold_file):
    """fMRIPrep run-specific functional (coverage) mask matching a BOLD run."""
    return Path(str(bold_file).replace("desc-preproc_bold", "desc-brain_mask"))


def confounds_for(bold_file):
    name = str(bold_file).replace(f"space-{SPACE}_desc-preproc_bold.nii.gz",
                                  "desc-confounds_timeseries.tsv")
    return Path(name)


def out(*parts):
    p = OUTPUT_DIR.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
