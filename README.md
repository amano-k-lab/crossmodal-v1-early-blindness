# Cross-modal V1 signals in human early blindness depend on task, not stimulus — analysis code

Background, repository layout, method notes and third-party code are described in [`docs/`](docs/).

## Setup

### 1. Python environment

Python 3.12 is required.

```bash
git clone https://github.com/amano-k-lab/crossmodal-v1-early-blindness.git
cd crossmodal-v1-early-blindness
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`third_party/pydcm` is imported directly from the repository and needs no separate installation.

### 2. Input data

The scripts expect fMRIPrep 24.0.0 outputs (MNI152NLin2009cAsym, 2 mm) in BIDS derivative layout, e.g.

```
<FMRIPREP_DIR>/sub-032/func/sub-032_task-tactileobtclosed_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
<FMRIPREP_DIR>/sub-032/func/sub-032_task-tactileobtclosed_run-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz
<FMRIPREP_DIR>/sub-032/func/sub-032_task-tactileobtclosed_run-01_desc-confounds_timeseries.tsv
```

### 3. Atlases

Download the following public atlases (not redistributed here) and place them in `ATLAS_DIR`:

```
<ATLAS_DIR>/glasser360MNI.nii.gz              # HCP-MMP1.0, volumetric MNI version
<ATLAS_DIR>/benson14_fsaverage/benson14_varea.mgz
<ATLAS_DIR>/benson14_fsaverage/benson14_angle.mgz
<ATLAS_DIR>/benson14_fsaverage/benson14_eccen.mgz
```

### 4. Paths

Paths are set through environment variables (defaults in brackets):

```bash
export FMRIPREP_DIR=/path/to/fmriprep      # [./data/fmriprep]
export ATLAS_DIR=/path/to/atlases          # [./atlas/files]
export OUTPUT_DIR=/path/to/outputs         # [./outputs]
```

## Running

### A. From Data S1 (no imaging data needed)

The group statistics and figures below start from the ROI-level values in the Data S1
workbook that accompanies the paper. Give the workbook with `--input` and the sheet
with `--sheet` (a CSV export of the sheet also works without `--sheet`; running a
script without `--sheet` lists the available sheets).

```bash
# Phase-specified coherence: Table S3 and the V1 statistics in the Results
python coherence/coherence_stats.py --input DataS1.xlsx --sheet "<coherence sheet>"

# Cross-modal RSA: Table S4 (group mean r, 95% CI, t, p)
python rsa/rsa_stats.py --input DataS1.xlsx --sheet "<RSA sheet>"

# Figures 2 and 3
python figures/make_figures.py --data-s1 DataS1.xlsx \
    --coherence-sheet "<coherence sheet>" --rsa-sheet "<RSA sheet>"
```

Outputs are written to `OUTPUT_DIR/coherence/`, `OUTPUT_DIR/rsa/` and `OUTPUT_DIR/figures/`.

### B. Full pipeline from fMRIPrep outputs

Run the steps in this order from the repository root. All results are written to `OUTPUT_DIR`.

```bash
# V1 mask and single-trial betas
python atlas/make_v1_mask.py
python beta_estimation/run_glmsingle.py --n-jobs 8

# Cross-modal RSA (Fig. 3, Table S4)
python rsa/crossmodal_rsa.py
python rsa/rsa_stats.py

# GLM characterisation of the DCM nodes (Fig. S2, Table S6)
python glm_characterization/roi_effect_size.py

# DCM and family-level BMS (Fig. 4C-F, Table S5)
python dcm/extract_roi_timeseries.py
python dcm/estimate_dcm.py --n-jobs 32
python dcm/family_bms.py

# Figures 3, 4C-F and S2
python figures/make_figures.py
```

The phase-specified coherence values themselves were computed in mrVista (see
[`docs/methods.md`](docs/methods.md)); their statistics are run as in A.
