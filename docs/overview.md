# Overview

Analysis code for:

> Masuda Y, Watanabe R, Yamashita A, Terao M, Iida M, Kinjo T, Tohma A, Horiguchi H,
> Matsumoto K, Nakano T, Nakadomari S, Wandell BA, Amano K.
> *Cross-modal V1 Signals in Human Early Blindness Depend on Task, not Stimulus.*
> (submitted to *Current Biology*).

The repository contains the custom scripts for the representational similarity
analysis (RSA), dynamic causal modeling (DCM) family comparison, GLM-based
characterisation of the DCM nodes, statistical analysis of phase-specified coherence,
and figure generation. Section, figure and table numbers refer to the manuscript.

## Data

No data are included. Raw and minimally processed MRI data of the blind participants
are available on request (see *Data and code availability* in the manuscript).
ROI-level numerical source data are provided with the paper as Data S1.

Participants are EB1–EB6 (`sub-032`–`sub-037`) and C1–C6 (`sub-007`–`sub-012`).
BIDS task labels are `tactilepvclosed`, `tactileobtclosed`, `audiopvclosed` and
`audioobtclosed` (PS = passive sensing, OBT = one-back task; "pv" in the file names
denotes PS). Each run has 100 volumes (TR = 3 s) with ten 15-s stimulation blocks
alternating with 15-s rest.

## Upstream processing (not part of this repository)

* fMRIPrep 24.0.0 (MNI152NLin2009cAsym, 2 mm) and FreeSurfer.
* mrVista/vistasoft for the phase-specified coherence (Fig. 1, Fig. S1 and the values in Data S1).

## Repository layout

| Path | Manuscript item | What it does |
|------|-----------------|--------------|
| `config.py` | — | Paths, participants, task labels, design, ROI definitions |
| `roi_utils.py` | — | ROI and coverage masks on any MNI152 grid |
| `atlas/make_v1_mask.py` | STAR Methods, ROI definition | V1 mask from the Benson et al. (2014) fsaverage template |
| `beta_estimation/run_glmsingle.py` | RSA and GLM preprocessing | GLMsingle block betas on unsmoothed fMRIPrep data |
| `rsa/crossmodal_rsa.py` | Fig. 3, Table S4 | OBT − PS maps, tactile–auditory Pearson r per ROI |
| `rsa/rsa_stats.py` | Fig. 3, Table S4 | Fisher-z one-sample t-tests, back-transformed means/CIs |
| `glm_characterization/roi_effect_size.py` | Fig. S2, Table S6 | Voxel-wise Cohen's d (OBT > PS) averaged in the DCM nodes |
| `dcm/extract_roi_timeseries.py` | Fig. 4 | Node time series (6-mm smoothing, parcel means within coverage mask) |
| `dcm/models.py` | Fig. 4A–B | Six-node model space: input (sensory vs FEF) × FEF–V1 link (A0 vs A1) |
| `dcm/estimate_dcm.py` | Fig. 4 | Model inversion with pydcm (SPM12 r7487 port); free energies |
| `dcm/family_bms.py` | Fig. 4C–F, Table S5 | Variational RFX-BMS (spm_BMS) and input-family inference |
| `coherence/coherence_stats.py` | Fig. 2, Table S3, Results | Planned contrasts, 2 × 2 mixed ANOVA, FDR on coherence values |
| `figures/make_figures.py` | Figs. 2, 3, 4C–F, S2 | Plots from the outputs above |
| `third_party/pydcm/` | — | pydcm (GPL-3.0) with local fixes, see [third_party.md](third_party.md) |

Figure 1, Fig. S1 (surface coherence maps and time courses) were produced in mrVista,
and Fig. 4A–B are schematics; these are not regenerated here.

## Contact

Yoichiro Masuda (ymasuda@jikei.ac.jp) — lead contact.
Code: Ryutaro Watanabe, The University of Tokyo.
