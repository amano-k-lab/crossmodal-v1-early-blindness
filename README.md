# Cross-modal V1 signals in human early blindness depend on task, not stimulus — analysis code

Analysis code for:

> Masuda Y, Watanabe R, Yamashita A, Terao M, Iida M, Kinjo T, Tohma A, Horiguchi H,
> Matsumoto K, Nakano T, Nakadomari S, Wandell BA, Amano K.
> *Cross-modal V1 Signals in Human Early Blindness Depend on Task, not Stimulus.*
> (submitted to *Current Biology*).

The repository contains the custom scripts for the representational similarity
analysis (RSA), dynamic causal modeling (DCM) family comparison, GLM-based
characterisation of the DCM nodes, statistical analysis of phase-specified coherence,
and figure generation. Section and figure numbers below refer to the manuscript.

**No data are included.** Raw and minimally processed MRI data of the blind
participants are available on request (see *Data and code availability* in the
manuscript). ROI-level numerical source data are provided with the paper as Data S1.

## Repository layout

| Path | Manuscript item | What it does |
|------|-----------------|--------------|
| `config.py` | — | Paths, participants, task labels, design, ROI definitions |
| `roi_utils.py` | — | ROI and coverage masks on any MNI152 grid |
| `atlas/make_v1_mask.py` | STAR Methods, ROI definition | V1 mask from the Benson et al. (2014) fsaverage template |
| `beta_estimation/run_glmsingle.py` | RSA and DCM preprocessing | GLMsingle block betas on unsmoothed fMRIPrep data |
| `rsa/crossmodal_rsa.py` | Fig. 3, Table S4 | OBT − PS maps, tactile–auditory Pearson r per ROI |
| `rsa/rsa_stats.py` | Fig. 3, Table S4 | Fisher-z one-sample t-tests, back-transformed means/CIs |
| `glm_characterization/roi_effect_size.py` | Fig. S2, Table S6 | Voxel-wise Cohen's d (OBT > PS) averaged in the DCM nodes |
| `dcm/extract_roi_timeseries.py` | Fig. 4 | Node time series (6-mm smoothing, parcel means within coverage mask) |
| `dcm/models.py` | Fig. 4A–B | Six-node model space: input (sensory vs FEF) × FEF–V1 link (A0 vs A1) |
| `dcm/estimate_dcm.py` | Fig. 4 | Model inversion with pydcm (SPM12 r7487 port); free energies |
| `dcm/family_bms.py` | Fig. 4C–F, Table S5 | Variational RFX-BMS (spm_BMS) and input-family inference |
| `coherence/coherence_stats.py` | Fig. 2, Table S3, Results | Planned contrasts, 2 × 2 mixed ANOVA, FDR on coherence values |
| `figures/make_figures.py` | Figs. 2, 3, 4C–F, S2 | Plots from the outputs above |
| `third_party/pydcm/` | — | pydcm (GPL-3.0) with local bug fixes, see below |

## Requirements

* Python 3.12 with the packages in `requirements.txt` (`pip install -r requirements.txt`).
* Upstream processing (not part of this repository): fMRIPrep 24.0.0 (MNI152NLin2009cAsym,
  2 mm), FreeSurfer, and mrVista/vistasoft for the phase-specified coherence.
* Atlases (public, not redistributed here):
  * HCP multi-modal parcellation, volumetric MNI version `glasser360MNI.nii.gz`
    (labels 1–180 right hemisphere, 181–360 left hemisphere).
  * Benson et al. (2014) retinotopic template on fsaverage exported to volume
    (`benson14_varea.mgz`, `benson14_angle.mgz`, `benson14_eccen.mgz`, e.g. with neuropythy).

## Configuration

Paths are set through environment variables (defaults in brackets):

```bash
export FMRIPREP_DIR=/path/to/fmriprep      # [./data/fmriprep] contains sub-XXX/func/
export ATLAS_DIR=/path/to/atlases          # [./atlas/files] glasser360MNI.nii.gz, benson14_fsaverage/
export OUTPUT_DIR=/path/to/outputs         # [./outputs]
```

Participants are EB1–EB6 (`sub-032`–`sub-037`) and C1–C6 (`sub-007`–`sub-012`).
BIDS task labels: `tactilepvclosed`, `tactileobtclosed`, `audiopvclosed`,
`audioobtclosed` (PS = passive sensing, OBT = one-back task; "pv" in the file names
denotes PS). Each run has 100 volumes (TR = 3 s) with ten 15-s stimulation blocks
alternating with 15-s rest.

## Running the pipeline

```bash
python atlas/make_v1_mask.py                       # V1 mask (same for all participants)
python beta_estimation/run_glmsingle.py            # GLMsingle betas

python rsa/crossmodal_rsa.py                       # Figure 3 / Table S4
python rsa/rsa_stats.py

python glm_characterization/roi_effect_size.py     # Figure S2 / Table S6

python dcm/extract_roi_timeseries.py               # Figure 4 / Table S5
python dcm/estimate_dcm.py --n-jobs 32             # 192 model inversions
python dcm/family_bms.py

python coherence/coherence_stats.py --input DataS1_phase_specified_coherence.csv  # Table S3
python figures/make_figures.py --coherence DataS1_phase_specified_coherence.csv
```

`rsa/rsa_stats.py` and `coherence/coherence_stats.py` also run directly on the
corresponding Data S1 tables (`--input`), so the group statistics can be checked
without the imaging data.

## Method summary

**ROIs.** RSA and DCM ROIs are defined in MNI152 space and are identical for all
participants: FEF = Glasser 10/190; A1/2 = A1 (24/204); S1 = 3b (9/189);
IOG = V4 (6/186); SOG = V3A (13/193); IPS = IPS1, MIP, LIPv, LIPd, AIP and IP2
(both hemispheres); V1 = varea 1 of the Benson template resampled to MNI152. Only
voxels inside the participant- and run-specific fMRIPrep functional masks are used.
Because acquisition used partial-brain coverage, an ROI that lies entirely outside
the acquired slab is treated as missing (participant × modality combinations
excluded from the DCM are listed in `OUTPUT_DIR/dcm/excluded.csv`).

**GLMsingle.** Unsmoothed runs are fitted one at a time; each stimulation block is a
trial; six motion parameters are extra regressors; library-HRF betas (type B) are
used.

**RSA.** Betas are averaged over blocks, then runs; OBT − PS maps for each modality
are resampled to a common 2-mm grid and correlated (Pearson) within each ROI over
voxels covered in every tactile and auditory run. Fisher z is used for inference.

**DCM.** Six nodes (V1, IPS, FEF, SOG, IOG and S1 or A1/2) with fixed bidirectional
connections V1–IOG, V1–SOG, IOG–IPS, SOG–IPS, IPS–FEF and sensory–IPS. Four models
cross the driving input (sensory cortex vs FEF) with the absence/presence of a
bidirectional FEF–V1 connection. The input is the stimulus-block regressor; PS and
OBT runs are fitted separately (runs of one condition concatenated). Group inference
uses variational RFX-BMS (Stephan et al., 2009) with a family prior of α₀ = 1 per
input family (0.5 per model); participant-level family probabilities g_nk are summed
over the A0/A1 variants, α_k = α₀ + Σₙ g_nk, and exceedance probabilities are
computed from the Dirichlet posterior.

**Phase-specified coherence.** Coherence at the block frequency (1/30 Hz) was
computed in mrVista following Masuda et al. (2021, *Curr. Biol.* 31, 406–412) using
the standard vistasoft coherence analysis; `coherence/coherence_stats.py` reproduces
the statistics in Table S3 and the Results from the ROI-level values in Data S1.

## Third-party code

`third_party/pydcm` is pydcm (https://github.com/tmdemelo/pydcm, commit `1b4d7eb`),
a Python port of SPM12 r7487 DCM, distributed under GPL-3.0 (see its `LICENSE`).
Local changes (Python-3/NumPy compatibility fixes in `spm_diff`, `spm_cat`, `spm_dx`,
`spm_bireduce`, `spm_Ce`, the Gauss–Newton update in `spm_nlsi_GN`, and use of the
unmodified A matrix for the prior covariance in `spm_dcm_fmri_priors`) are listed in
`third_party/pydcm/LOCAL_MODIFICATIONS.diff`.

## Contact

Yoichiro Masuda (ymasuda@jikei.ac.jp) — lead contact.
Code: Ryutaro Watanabe, The University of Tokyo.
